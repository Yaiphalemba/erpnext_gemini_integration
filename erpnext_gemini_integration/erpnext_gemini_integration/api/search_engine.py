import frappe
import json
from rapidfuzz import process, fuzz
import google.generativeai as genai

# --- 1. THE SNIPER (Exact @ Tag Matching) ---

def fetch_doc_by_prefix(doc_name):
    """
    Instantly fetches a Frappe document based on its naming prefix.
    Bypasses AI entirely for blazing fast data retrieval.
    """
    # The hardcoded dictionary mapping. Faster than querying Frappe's naming series.
    prefix_map = {
        "PROJ": "Project",
        "EMP": "Employee",
        "CUST": "Customer",
        "SINV": "Sales Invoice",
        "PINV": "Purchase Invoice",
        "TASK": "Task",
        "EXP": "Expense Claim",
        "LEV": "Leave Application"
    }

    if "-" not in doc_name:
        return None 
        
    prefix = doc_name.split("-")[0].upper()
    target_doctype = prefix_map.get(prefix)

    # If the prefix isn't in our dictionary, gracefully back out
    if not target_doctype:
        return None

    try:
        # Check if it actually exists before fetching to avoid tracebacks
        if not frappe.db.exists(target_doctype, doc_name):
            return {"error": f"{target_doctype} {doc_name} does not exist. Did you make that up?"}
            
        doc_data = frappe.get_doc(target_doctype, doc_name).as_dict()
        
        # --- THE TOKEN SAVER DIET ---
        # Stripping Frappe's internal metadata saves massive amounts of LLM context window.
        useless_fields = [
            'creation', 'modified', 'modified_by', 'owner', 'idx', 
            'docstatus', '_user_tags', '_comments', '_assign', '_liked_by'
        ]
        
        for field in useless_fields:
            doc_data.pop(field, None)

        # Remove nulls and empty lists to keep the JSON payload microscopic
        clean_data = {k: v for k, v in doc_data.items() if v not in (None, "", [])}

        return clean_data

    except Exception as e:
        frappe.log_error(f"Failed to fetch @ tag {doc_name}: {str(e)}", "AI Search Engine")
        return {"error": "Tried to fetch that exact record, but the database threw a fit."}


# --- 2. THE TYPO FORGIVER (Fuzzy Search) ---

def run_fuzzy_search(user_message):
    """
    Extracts the target DocType and the messy search string using AI, 
    then uses C++ powered Levenshtein distance to find the best match.
    """
    api_key = frappe.conf.get("gemini_api_key")
    if not api_key:
        return {"error": "API Key missing."}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.1-flash')

    # Step A: The Extractor Prompt
    extract_prompt = f"""
    The user is trying to search the ERP system. Extract the target DocType and the search string.
    Map their intent to one of these core DocTypes ONLY: ['Employee', 'Customer', 'Project', 'Sales Invoice', 'Task']
    
    Output ONLY valid JSON: {{"doctype": "DocType", "search_string": "what they typed"}}
    User Message: "{user_message}"
    """
    
    try:
        response = model.generate_content(extract_prompt).text
        clean_json = response.replace("```json", "").replace("```", "").strip()
        search_params = json.loads(clean_json)
        target_doctype = search_params.get("doctype")
        search_string = search_params.get("search_string")
    except Exception:
        return {"error": "Could not determine what specific record you are looking for."}

    if not target_doctype or not search_string:
        return {"error": "Not enough info to perform a targeted search."}

    # Step B: Fetch the Haystack
    try:
        meta = frappe.get_meta(target_doctype)
        # We need something descriptive to search against, usually the 'name' or a title field
        title_field = meta.title_field or "name"
        
        # Limit 5000 is our safety valve so we don't load a million rows into RAM
        candidates = frappe.get_all(
            target_doctype, 
            fields=["name", title_field],
            limit_page_length=5000 
        )
    except Exception as e:
        return {"error": f"Failed to fetch {target_doctype} records for searching: {str(e)}"}

    if not candidates:
        return {"message": f"No {target_doctype} records exist in the system to search through."}

    # Step C: The C++ Magic (RapidFuzz)
    # We map the candidates into a dictionary of { "ID": "ID - Title" }
    choices = {doc.name: f"{doc.name} - {doc.get(title_field, '')}" for doc in candidates}
    
    # fuzz.WRatio handles word-order changes and casing beautifully
    top_matches = process.extract(
        search_string, 
        choices, 
        scorer=fuzz.WRatio, 
        limit=3
    )

    # Step D: Assemble the Context
    results_context = []
    for match_string, score, doc_name in top_matches:
        # Ignore terrible matches (under 50% confidence)
        if score < 50:
            continue 
            
        # Fetch the full document data for the good matches, using our token saver logic
        full_doc = frappe.get_doc(target_doctype, doc_name).as_dict()
        for field in ['creation', 'modified', 'modified_by', 'owner', 'idx']:
            full_doc.pop(field, None)
            
        results_context.append({
            "match_confidence": f"{round(score)}%",
            "document": full_doc
        })

    if not results_context:
        return {"message": f"I dug through the {target_doctype} records, but couldn't find anything close to '{search_string}'."}

    return {
        "search_type": "fuzzy",
        "target": target_doctype,
        "results": results_context
    }