import frappe
import json
import google.generativeai as genai

def determine_intent(user_message):
    """
    The Receptionist. Uses a blazing-fast model to classify the user's intent 
    so we don't waste time or tokens on the wrong backend logic.
    """
    # Grab the API key securely from Site Config
    api_key = frappe.conf.get("gemini_api_key")
    if not api_key:
        frappe.log_error("Missing Gemini API Key in Site Config.", "AI Switchboard")
        return "chat" # Safe fallback

    genai.configure(api_key=api_key)
    
    # We specifically use Flash here. It's built for speed and high-frequency tasks.
    model = genai.GenerativeModel('gemini-3.1-flash')

    # The Prompt: We put the model in a strict JSON straightjacket.
    routing_prompt = f"""
    You are an ultra-fast intent classification router for an ERP system.
    Analyze the following user message and categorize it into EXACTLY ONE of these intents:
    
    1. "data_request": The user wants metrics, reports, charts, counts, or database queries. 
       (e.g., "Show me Q1 revenue", "How many employees?", "Expense chart")
    2. "search": The user is looking for a specific document, person, or record but doesn't have the exact ID. 
       (e.g., "Find the invoice for Acme Corp", "Search for John's leave app")
    3. "chat": The user is chatting, asking a general question, asking for analysis of existing data, or giving a command not related to fetching new data. 
       (e.g., "Summarize this", "What's up?", "Draft an email")

    Output ONLY a valid JSON object in this exact format, with no markdown formatting:
    {{"intent": "category_name"}}
    
    User Message: "{user_message}"
    """

    try:
        # Fire the request
        response = model.generate_content(routing_prompt).text
        
        # LLMs love to wrap JSON in markdown blockticks, even when you tell them not to.
        # This regex-free scrub guarantees we can parse it.
        clean_json = response.replace("```json", "").replace("```", "").strip()
        parsed_data = json.loads(clean_json)
        
        # Extract the intent, default to 'chat' if it hallucinates a weird category
        intent = parsed_data.get("intent", "chat")
        
        # Double check it gave us an allowed category
        if intent not in ["data_request", "search", "chat"]:
            return "chat"
            
        return intent
        
    except json.JSONDecodeError:
        # If the AI completely fails to write JSON, we log it but don't crash the app.
        frappe.log_error(f"Switchboard JSON Parse Failed. Response: {response}", "AI Switchboard")
        return "chat"
        
    except Exception as e:
        frappe.log_error(f"Switchboard API Error: {str(e)}", "AI Switchboard")
        return "chat"