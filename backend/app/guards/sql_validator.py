"""
SQL Validator Guard.
Blocks INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE.
"""

import re

BLOCKED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "CREATE", "TRUNCATE", "MERGE", "REPLACE",
    "GRANT", "REVOKE", "EXEC", "EXECUTE"
]


def validate_sql(sql_query: str) -> dict:
    if not sql_query or not sql_query.strip():
        return {"is_valid": False, "reason": "Empty SQL query"}

    # Remove comments
    cleaned = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

    upper_sql = cleaned.upper().strip()

    # Must start with SELECT or WITH
    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        return {"is_valid": False, "reason": "Query must start with SELECT or WITH"}

    # Check for blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, upper_sql):
            return {"is_valid": False, "reason": f"Blocked keyword found: {keyword}"}

    # Check for multiple statements
    stripped = upper_sql.rstrip(';').strip()
    if ';' in stripped:
        return {"is_valid": False, "reason": "Multiple SQL statements not allowed"}

    return {"is_valid": True, "reason": "Query is safe"}
