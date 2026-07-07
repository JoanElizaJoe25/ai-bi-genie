"""
Conversation Memory Manager.
Stores chat history per session. Capped at 6 turns.
"""

from collections import defaultdict
from app.config import MAX_CONVERSATION_TURNS

_conversations: dict[str, list[dict]] = defaultdict(list)


def get_history(session_id: str) -> list[dict]:
    return _conversations[session_id].copy()


def add_turn(session_id: str, user_message: str, assistant_message: str, sql_query: str = ""):
    _conversations[session_id].append({
        "role": "user",
        "content": user_message
    })

    _conversations[session_id].append({
        "role": "assistant",
        "content": assistant_message,
        "sql": sql_query
    })

    max_messages = MAX_CONVERSATION_TURNS * 2
    if len(_conversations[session_id]) > max_messages:
        _conversations[session_id] = _conversations[session_id][-max_messages:]


def clear_history(session_id: str):
    _conversations[session_id] = []


def get_formatted_history(session_id: str) -> str:
    history = _conversations[session_id]
    if not history:
        return "No previous conversation."

    formatted = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        content = msg["content"]
        sql = msg.get("sql", "")

        if role == "Assistant" and sql:
            formatted.append(f"{role}: {content}\n[SQL used: {sql}]")
        else:
            formatted.append(f"{role}: {content}")

    return "\n".join(formatted)
