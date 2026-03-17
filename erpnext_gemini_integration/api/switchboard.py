import frappe
import json
import google.generativeai as genai

def determine_intent(user_message):
    """
    The Receptionist. Uses a blazing-fast model to classify the user's intent 
    so we don't waste time or tokens on the wrong backend logic.
    """
    api_key = frappe.conf.get("gemini_api_key")
    if not api_key:
        frappe.log_error("Missing Gemini API Key in Site Config.", "AI Switchboard")
        return "chat" # Safe fallback

    genai.configure(api_key=api_key)
    
    # Put the rules in the System Instruction, not the user prompt
    routing_rules = """
    You are an ultra-fast intent classification router for an ERP system.
    Analyze the user's message and categorize it into EXACTLY ONE of these intents:
    
    1. "data_request": The user wants metrics, reports, charts, counts, or database queries. 
       (e.g., "Show me Q1 revenue", "How many employees?", "Expense chart")
    2. "search": The user is looking for a specific document, person, or record but doesn't have the exact ID. 
       (e.g., "Find the invoice for Acme Corp", "Search for John's leave app")
    3. "chat": The user is chatting, asking a general question, asking for analysis of existing data, or giving a command not related to fetching new data. 
       (e.g., "Summarize this", "What's up?", "Draft an email")

    Output ONLY a valid JSON object in this exact format:
    {"intent": "category_name"}
    """

    # We specifically use Flash here, but we force native JSON output!
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=routing_rules,
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        # Fire the request using ONLY the user's message
        response_text = model.generate_content(user_message).text
        
        # Look mom, no regex! It's guaranteed to be clean JSON.
        parsed_data = json.loads(response_text)
        
        # Extract the intent, default to 'chat' if it hallucinates a weird category
        intent = parsed_data.get("intent", "chat")
        
        if intent not in ["data_request", "search", "chat"]:
            return "chat"
            
        return intent
        
    except Exception as e:
        # One single catch-all since we no longer have to worry about JSONDecodeErrors
        frappe.log_error(title="AI Switchboard Error", message=f"API Error: {str(e)}")
        return "chat"