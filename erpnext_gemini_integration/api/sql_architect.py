import frappe
import json
import re
import decimal
import google.generativeai as genai

# The absolute "Do Not Touch" list. Even the CEO doesn't need to query the session logs directly.
BLACKLIST = ["tabUser", "tabHas Role", "tabSystem Settings", "tabDocField", "tabDocType", "tabDefaultValue"]

def generate_and_run_sql(user_message):
    """
    The Master Architect. 
    1. Scouts the required tables.
    2. Injects the live database schema.
    3. Writes the MariaDB query.
    4. Executes it and determines the best UI render type.
    """
    api_key = frappe.conf.get("gemini_api_key")
    if not api_key:
        return {"error": "API Key missing. I can't do my job without caffeine or an API key."}
        
    genai.configure(api_key=api_key)
    fast_model = genai.GenerativeModel('gemini-2.5-flash')
    smart_model = genai.GenerativeModel('gemini-2.5-pro')

    # --- STEP 1: THE SCOUT ---
    # Fast, cheap model figures out which tables we actually need.
    scout_prompt = f"""
    The user is asking an ERP system: "{user_message}"
    Return ONLY a JSON list of the core Frappe DocType names required to answer this. 
    Do not include child tables unless specifically asked.
    Example: ["Employee", "Project"]
    """
    try:
        scout_response = fast_model.generate_content(scout_prompt).text
        clean_json = scout_response.replace("```json", "").replace("```", "").strip()
        required_doctypes = json.loads(clean_json)
    except Exception as e:
        frappe.log_error(f"SQL Scout Failed: {str(e)}", "AI SQL Architect")
        return {"error": "I couldn't figure out which database tables to look at."}

    # --- STEP 2: SCHEMA INJECTION & PERMISSION CHECK ---
    schema_context = ""
    valid_doctypes = []
    
    for doctype in required_doctypes:
        table_name = f"tab{doctype}"
        
        # 1. The Hard Blacklist
        if table_name in BLACKLIST:
            return {"error": f"Security restriction: Access to {doctype} is blacklisted."}
            
        # 2. The RBAC Bouncer (CRITICAL)
        if not frappe.has_permission(doctype, "read"):
            return {"error": f"Access Denied. You do not have the required role to view '{doctype}' data."}
        
        try:
            meta = frappe.get_meta(doctype)
            fields = [f"{f.fieldname} ({f.fieldtype})" for f in meta.fields if f.fieldtype not in ['Section Break', 'Column Break', 'HTML']]
            schema_context += f"Table: {table_name}\nFields: {', '.join(fields)}\n\n"
            valid_doctypes.append(doctype)
        except frappe.DoesNotExistError:
            continue

    if not schema_context:
        return {"error": "I couldn't map your request to any valid system data you have access to."}

    # --- STEP 3: SQL GENERATION ---
    sql_prompt = f"""
    You are an elite MariaDB data analyst for a Frappe ERP system.
    Translate the user's request into a highly optimized, raw SQL SELECT query.

    CRITICAL RULES:
    1. Output ONLY the raw SQL string. No markdown, no explanations, no formatting blocks.
    2. ALWAYS use the 'tab' prefix for tables (e.g., 'tabEmployee').
    3. NEVER use DROP, UPDATE, DELETE, INSERT, or ALTER. Only SELECT.
    4. To calculate tenure, age, or metrics, use CURRENT_DATE.
    5. If aggregating, always provide clean aliases using AS (e.g., SUM(base) AS total_salary).
    6. ALWAYS filter out deleted records by adding `docstatus < 2` to your WHERE clause.

    AVAILABLE SCHEMA:
    {schema_context}

    USER REQUEST: "{user_message}"
    """
    try:
        raw_sql = smart_model.generate_content(sql_prompt).text.strip()
        raw_sql = re.sub(r"```sql|```", "", raw_sql).strip()
    except Exception as e:
        frappe.log_error(f"SQL Generation Failed: {str(e)}", "AI SQL Architect")
        return {"error": "My brain cramped while trying to write the database query."}

    # --- STEP 4: THE IRON BOUNCER ---
    # Gemini loves adding trailing semicolons. Strip them off before validating!
    raw_sql = raw_sql.strip().rstrip(";")
    safe_sql = raw_sql.upper()
    
    if not safe_sql.startswith("SELECT"):
        return {"error": "Query rejected. I only run SELECT queries."}
        
    # Block chained statements and destructive keywords
    destructive_keywords = ["UPDATE ", "DELETE ", "INSERT ", "DROP ", "ALTER ", "TRUNCATE ", ";"]
    if any(evil_word in safe_sql for evil_word in destructive_keywords):
        # THE FIX: Explicit kwargs so Frappe doesn't try to cram the whole query into the Title
        frappe.log_error(title="AI Security", message=f"Malicious AI Query Blocked: {raw_sql}")
        return {"error": "Query rejected. Destructive commands or chained statements are strictly forbidden."}
    
    for table in BLACKLIST:
        if table.upper() in safe_sql:
            return {"error": "A blacklisted table was detected in the query. Request denied."}

    # --- STEP 5: EXECUTION ---
    try:
        # as_dict=True gives us beautiful JSON-ready rows
        data = frappe.db.sql(raw_sql, as_dict=True)
        
        # Analyze the shape of the data so the Vue frontend knows what component to render
        render_type = determine_render_type(data)

        return {
            "status": "success",
            "query": raw_sql,
            "render_type": render_type,
            # Cap at 100 rows! We do not want to blow up the Gemini context window with 50,000 invoices.
            "data": data[:100] 
        }
    except Exception as e:
        frappe.log_error(f"SQL Execution Failed. Query: {raw_sql} | Error: {str(e)}", "AI SQL Architect")
        return {"error": "The query was generated, but the database rejected it. Could be a complex join issue.", "failed_query": raw_sql}

def determine_render_type(data):
    """
    A smart helper that looks at the data array and guesses the best UI.
    """
    if not data:
        return "table"
    
    row = data[0]
    keys = list(row.keys())
    
    # Helper to check if a value is numeric (handles MariaDB decimals flawlessly)
    def is_numeric(val):
        return isinstance(val, (int, float, decimal.Decimal))
    
    # 1 Row, 1 Column -> Number Card
    if len(data) == 1 and len(keys) == 1:
        if is_numeric(row[keys[0]]):
            return "number_card"
            
    # Multiple rows, exactly 2 columns, at least one is a number -> Bar Chart
    if len(data) > 1 and len(keys) == 2:
        if is_numeric(row[keys[0]]) or is_numeric(row[keys[1]]):
            return "chart"
            
    return "table"