import frappe
import json
# Importing the modules we mapped out in our architecture
# (We will build the actual logic for these in their respective files next)
from erpnext_gemini_integration.api.search_engine import fetch_doc_by_prefix, run_fuzzy_search
from erpnext_gemini_integration.api.switchboard import determine_intent
from erpnext_gemini_integration.api.sql_architect import generate_and_run_sql
import google.generativeai as genai

@frappe.whitelist()
def process_user_message(user_message, session_id=None):
    """
    The Grand Orchestrator. Takes the Vue frontend's request, routes it, 
    fetches data, asks Gemini for a summary, saves the history, and returns the payload.
    """
    # 1. Session Management (Create one if it doesn't exist)
    if not session_id:
        session_doc = frappe.new_doc("AI Chat Session")
        # Generate a quick title based on the first message
        session_doc.session_title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        session_doc.user = frappe.session.user
        session_doc.insert(ignore_permissions=True)
        session_id = session_doc.name

    # Log the user's message into the database memory
    add_message_to_session(session_id, "user", user_message)

    context_block = []
    render_type = "text"
    render_data = None
    raw_sql = None

    # --- THE PIPELINE ---
    
    # Step 2: The Regex Interceptor (Fast @ tags)
    import re
    explicit_refs = re.findall(r'@([A-Z0-9-]+)', user_message)
    if explicit_refs:
        for ref in explicit_refs:
            doc_data = fetch_doc_by_prefix(ref)
            if doc_data:
                context_block.append(f"Data for {ref}:\n{json.dumps(doc_data, default=str)}")

    # Step 3: Intent Routing
    intent = determine_intent(user_message)
    
    if intent == "data_request":
        sql_payload = generate_and_run_sql(user_message)
        if "error" not in sql_payload:
            context_block.append(f"Database Query Results:\n{json.dumps(sql_payload.get('data'), default=str)}")
            render_type = sql_payload.get("render_type", "table")
            render_data = sql_payload.get("data")
            raw_sql = sql_payload.get("query")
        else:
            context_block.append(f"System Error: {sql_payload.get('error')}")
            
    elif intent == "search":
        search_results = run_fuzzy_search(user_message)
        context_block.append(f"Fuzzy Search Results:\n{json.dumps(search_results, default=str)}")

    # Step 4: The Final Brain (Gemini Pro)
    # We fetch the history from the DB so Gemini remembers the conversation
    chat_history = get_gemini_formatted_history(session_id)
    
    system_prompt = f"""
    You are an elite ERP data analyst for the C-Suite. Be confident, witty, and concise. 
    If context data is provided below, summarize it or answer the user's prompt based on it.
    
    --- START ASSEMBLED CONTEXT ---
    {chr(10).join(context_block)}
    --- END ASSEMBLED CONTEXT ---
    """
    
    genai.configure(api_key=frappe.conf.get("gemini_api_key"))
    model = genai.GenerativeModel('gemini-3.1-pro', system_instruction=system_prompt)
    
    try:
        chat = model.start_chat(history=chat_history)
        final_response = chat.send_message(user_message).text
    except Exception as e:
        frappe.log_error(f"Gemini API Error: {str(e)}", "AI Engine")
        final_response = "I hit a snag trying to process that. My neural net must be on a coffee break."

    # Step 5: Save AI's response to the database memory
    add_message_to_session(session_id, "model", final_response, render_type, raw_sql, render_data)

    # Step 6: Return the beautiful payload to Vue
    return {
        "status": "success",
        "session_id": session_id,
        "reply": final_response,
        "render_type": render_type,
        "render_data": render_data,
        "raw_sql": raw_sql
    }

@frappe.whitelist()
def pin_ai_widget(widget_name, render_type, raw_sql, chart_config=None):
    """
    Saves the AI-generated SQL query into a Dashboard Widget DocType.
    """
    if not raw_sql or not raw_sql.upper().strip().startswith("SELECT"):
        frappe.throw("Only SELECT queries can be pinned to the dashboard.")
        
    try:
        doc = frappe.new_doc("AI Dashboard Widget")
        doc.widget_name = widget_name
        doc.render_type = render_type
        doc.raw_sql = raw_sql
        if chart_config:
            doc.chart_config = json.dumps(chart_config)
            
        doc.insert(ignore_permissions=True)
        return {"status": "success", "message": f"Widget '{widget_name}' pinned successfully!"}
    except frappe.DuplicateEntryError:
        return {"status": "error", "message": "A widget with this name already exists. Try a different name."}

# --- HELPER FUNCTIONS ---

def add_message_to_session(session_id, role, content, render_type="text", raw_sql=None, raw_data=None):
    """Appends a message to the AI Chat Session child table."""
    doc = frappe.get_doc("AI Chat Session", session_id)
    doc.append("messages", {
        "role": role,
        "content": content,
        "render_type": render_type,
        "raw_sql": raw_sql,
        "raw_data": json.dumps(raw_data, default=str) if raw_data else None
    })
    doc.save(ignore_permissions=True)
    frappe.db.commit() # Force commit so the next API call sees it

def get_gemini_formatted_history(session_id):
    """Pulls the last 6 messages and formats them for the Gemini API."""
    messages = frappe.get_all(
        "AI Chat Message",
        filters={"parent": session_id},
        fields=["role", "content"],
        order_by="idx desc",
        limit_page_length=6
    )
    messages.reverse()
    
    history = []
    for msg in messages:
        # Avoid passing the current user message twice, just the history
        history.append({
            "role": "user" if msg.role == "user" else "model",
            "parts": [msg.content]
        })
    return history