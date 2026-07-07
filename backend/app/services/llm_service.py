"""
LLM Service.
Handles all interactions with Google Gemini via the new google-genai SDK.
"""

from google import genai
from app.config import GCP_PROJECT, LOCATION, GEMINI_MODEL, BQ_SCHEMA
from app.memory.conversation import get_formatted_history

# Initialize the GenAI client
client = genai.Client(
    vertexai=True,
    project=GCP_PROJECT,
    location=LOCATION
)


def generate_sql(user_question: str, session_id: str) -> dict:
    try:
        history = get_formatted_history(session_id)

        prompt = f"""You are a BigQuery SQL expert. Convert natural language questions into valid BigQuery Standard SQL.

DATABASE SCHEMA:
{BQ_SCHEMA}

CONVERSATION HISTORY:
{history}

RULES:
1. Write ONLY valid BigQuery Standard SQL
2. Use ONLY SELECT statements - never INSERT, UPDATE, DELETE, DROP
3. Always use fully qualified table names: `sada-seed-2025-sandbox.intern_a_ecommerce.table_name`
4. Add LIMIT 100 unless the user asks for all data
5. For category names, JOIN with product_category_name_translation to show English names
6. When user says "filter to..." or "now show...", modify the PREVIOUS SQL based on context
7. Use appropriate aggregations (SUM, COUNT, AVG) based on the question
8. For time-based questions, use DATE_TRUNC or EXTRACT
9. Handle follow-up questions by referencing conversation history
10. Return ONLY the SQL query, no explanations, no markdown, no code blocks

USER QUESTION: {user_question}

SQL QUERY:"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        sql = response.text.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()

        return {"sql": sql, "error": None}

    except Exception as e:
        return {"sql": "", "error": f"Failed to generate SQL: {str(e)}"}


def generate_answer(user_question: str, sql_query: str, query_results: list, chart_type: str) -> dict:
    try:
        display_results = query_results[:50]

        prompt = f"""You are a helpful data analyst. Answer the user's question based on the query results.

USER QUESTION: {user_question}

SQL QUERY EXECUTED:
{sql_query}

QUERY RESULTS (up to 50 rows):
{display_results}

TOTAL ROWS: {len(query_results)}
CHART TYPE: {chart_type}

INSTRUCTIONS:
1. Provide a clear, concise natural language answer
2. Highlight key numbers and insights
3. If a chart is shown ({chart_type}), mention what it visualizes
4. Use bullet points for multiple data points
5. Keep under 200 words
6. Format currency in BRL (R$)
7. Be conversational and helpful

ANSWER:"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        return {"answer": response.text.strip(), "error": None}

    except Exception as e:
        return {"answer": "", "error": f"Failed to generate answer: {str(e)}"}

