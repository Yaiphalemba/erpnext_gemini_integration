import frappe
import json
from rapidfuzz import process, fuzz
import google.generativeai as genai

# --- HELPER: THE TOKEN SAVER ---
def clean_document_for_llm(doc_data):
    """
    Recursively strips Frappe's internal metadata and empty values 
    from the parent doc AND all child tables to save LLM tokens.
    """
    if not isinstance(doc_data, dict):
        return doc_data

    useless_fields = [
        'creation', 'modified', 'modified_by', 'owner', 'idx', 
        'docstatus', '_user_tags', '_comments', '_assign', '_liked_by'
    ]
    
    clean_dict = {}
    for k, v in doc_data.items():
        if k in useless_fields:
            continue
            
        # Recursively clean lists of child dicts
        if isinstance(v, list):
            cleaned_list = [clean_document_for_llm(item) for item in v if isinstance(item, dict)]
            if cleaned_list: # Only keep the list if it has items
                clean_dict[k] = cleaned_list
        # Keep values that aren't empty
        elif v not in (None, "", []):
            clean_dict[k] = v
            
    return clean_dict


# --- 1. THE SNIPER (Exact @ Tag Matching) ---

def fetch_doc_by_prefix(doc_name):
    """
    Instantly fetches a Frappe document based on its naming prefix.
    """
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

    if not target_doctype:
        return None

    try:
        # THE FIX: Check permissions first, then fetch!
        if not frappe.has_permission(target_doctype, "read"):
            return {"error": f"You don't have permission to read {target_doctype} records."}

        if not frappe.db.exists(target_doctype, doc_name):
            return {"error": f"{target_doctype} {doc_name} does not exist. Did you make that up?"}
            
        # THE FIX: Actually fetch the document
        raw_doc = frappe.get_doc(target_doctype, doc_name).as_dict()
        
        # THE FIX: Use our new recursive cleaner
        return clean_document_for_llm(raw_doc)

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
    model = genai.GenerativeModel('gemini-2.5-flash')

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
    except Exception as e:
        # THE FIX: Actually log the error!
        frappe.log_error(f"AI Extraction Failed: {str(e)}\nResponse: {response}", "AI Fuzzy Search")
        return {"error": "Could not determine what specific record you are looking for."}

    if not target_doctype or not search_string:
        return {"error": "Not enough info to perform a targeted search."}

    # THE FIX: Check permissions before querying 5000 rows!
    if not frappe.has_permission(target_doctype, "read"):
         return {"error": f"You do not have permission to search {target_doctype} records."}

    try:
        meta = frappe.get_meta(target_doctype)
        title_field = meta.title_field or "name"
        
        candidates = frappe.get_all(
            target_doctype, 
            fields=["name", title_field],
            limit_page_length=5000 
        )
    except Exception as e:
        frappe.log_error(f"Database fetch failed: {str(e)}", "AI Fuzzy Search")
        return {"error": f"Failed to fetch {target_doctype} records for searching."}

    if not candidates:
        return {"message": f"No {target_doctype} records exist in the system to search through."}

    # Step C: The C++ Magic
    choices = {doc.name: f"{doc.name} - {doc.get(title_field, '')}" for doc in candidates}
    
    # process.extract returns a list of tuples: (match_string, score, key)
    # The key is our doc.name!
    top_matches = process.extract(
        search_string, 
        choices, 
        scorer=fuzz.WRatio, 
        limit=3
    )

    # Step D: Assemble the Context
    results_context = []
    for match_string, score, doc_name in top_matches:
        if score < 50:
            continue 
            
        try:
            raw_doc = frappe.get_doc(target_doctype, doc_name).as_dict()
            # THE FIX: Use our recursive cleaner here too!
            clean_doc = clean_document_for_llm(raw_doc)
            
            results_context.append({
                "match_confidence": f"{round(score)}%",
                "document": clean_doc
            })
        except Exception as e:
             frappe.log_error(f"Failed to load matched doc {doc_name}: {str(e)}", "AI Fuzzy Search")
             continue # If one doc fails, keep trying the others

    if not results_context:
        return {"message": f"I dug through the {target_doctype} records, but couldn't find anything close to '{search_string}'."}

    return {
        "search_type": "fuzzy",
        "target": target_doctype,
        "results": results_context
    }