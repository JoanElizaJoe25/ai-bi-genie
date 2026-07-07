"""
Chat Router with SSE Streaming.
Sends real-time status updates to the frontend as each step completes.
"""

import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest
from app.guards.rate_limiter import check_rate_limit
from app.guards.sql_validator import validate_sql
from app.guards.cost_guard import check_query_cost
from app.services.llm_service import generate_sql, generate_answer
from app.services.bigquery_service import execute_query
from app.services.chart_service import detect_chart_type, format_chart_data
from app.memory.conversation import add_turn

router = APIRouter()


def sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event message."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def chat_stream(question: str, session_id: str):
    """Generator that yields SSE events as each step completes."""

    # STEP 1: Rate Limit Check
    yield sse_event("status", {"step": 1, "message": "Checking rate limit..."})
    await asyncio.sleep(0.1)

    rate_check = check_rate_limit(session_id)
    if not rate_check["is_allowed"]:
        yield sse_event("error", {
            "message": f"Rate limit exceeded. Retry in {rate_check['retry_after_seconds']}s"
        })
        return

    yield sse_event("status", {"step": 1, "message": "✓ Rate limit OK", "done": True})
    await asyncio.sleep(0.1)

    # STEP 2: Generate SQL
    yield sse_event("status", {"step": 2, "message": "🤖 Generating SQL from your question..."})
    await asyncio.sleep(0.1)

    sql_result = generate_sql(question, session_id)
    if sql_result["error"]:
        yield sse_event("error", {
            "message": "Could not understand your question. Please try rephrasing.",
            "detail": sql_result["error"]
        })
        return

    sql_query = sql_result["sql"]
    yield sse_event("sql", {"query": sql_query})
    yield sse_event("status", {"step": 2, "message": "✓ SQL generated", "done": True})
    await asyncio.sleep(0.1)

    # STEP 3: Validate SQL
    yield sse_event("status", {"step": 3, "message": "🔒 Validating SQL safety..."})
    await asyncio.sleep(0.1)

    validation = validate_sql(sql_query)
    if not validation["is_valid"]:
        yield sse_event("error", {
            "message": f"Query not allowed: {validation['reason']}",
            "sql": sql_query
        })
        return

    yield sse_event("status", {"step": 3, "message": "✓ SQL is safe (read-only)", "done": True})
    await asyncio.sleep(0.1)

    # STEP 4: Cost Guard
    yield sse_event("status", {"step": 4, "message": "💰 Checking query cost..."})
    await asyncio.sleep(0.1)

    cost_check = check_query_cost(sql_query)
    if not cost_check["is_within_limit"]:
        yield sse_event("error", {
            "message": f"Query would scan {cost_check['estimated_mb']} MB (limit: {cost_check['limit_mb']} MB). Try a more specific question.",
            "sql": sql_query
        })
        return

    yield sse_event("status", {
        "step": 4,
        "message": f"✓ Cost OK ({cost_check['estimated_mb']} MB / {cost_check['limit_mb']} MB)",
        "done": True
    })
    await asyncio.sleep(0.1)

    # STEP 5: Execute Query
    yield sse_event("status", {"step": 5, "message": "⚡ Running query on BigQuery..."})
    await asyncio.sleep(0.1)

    query_result = execute_query(sql_query)
    if not query_result["success"]:
        yield sse_event("error", {
            "message": f"Query failed: {query_result['error']}",
            "sql": sql_query
        })
        return

    yield sse_event("status", {
        "step": 5,
        "message": f"✓ Got {query_result['row_count']} rows from BigQuery",
        "done": True
    })
    await asyncio.sleep(0.1)

    # STEP 6: Detect Chart
    yield sse_event("status", {"step": 6, "message": "📊 Detecting chart type..."})
    await asyncio.sleep(0.1)

    chart_type = detect_chart_type(
        query_result["columns"],
        query_result["data"],
        sql_query
    )

    chart_data = format_chart_data(
        query_result["columns"],
        query_result["data"],
        chart_type
    )

    if chart_type != "none":
        yield sse_event("chart", {
            "chart_type": chart_type,
            "chart_data": chart_data
        })
        yield sse_event("status", {
            "step": 6,
            "message": f"✓ {chart_type.capitalize()} chart ready",
            "done": True
        })
    else:
        yield sse_event("status", {
            "step": 6,
            "message": "✓ No chart needed",
            "done": True
        })
    await asyncio.sleep(0.1)

    # STEP 7: Generate Answer
    yield sse_event("status", {"step": 7, "message": "🧠 Generating natural language answer..."})
    await asyncio.sleep(0.1)

    answer_result = generate_answer(
        question,
        sql_query,
        query_result["data"],
        chart_type
    )

    answer_text = answer_result["answer"] if not answer_result["error"] else f"Query returned {query_result['row_count']} rows."

    # Save to memory
    add_turn(session_id, question, answer_text, sql_query)

    yield sse_event("status", {"step": 7, "message": "✓ Answer ready!", "done": True})
    await asyncio.sleep(0.1)

    # STEP 8: Send final complete response
    yield sse_event("complete", {
        "question": question,
        "answer": answer_text,
        "sql_query": sql_query,
        "chart_type": chart_type,
        "chart_data": chart_data,
        "error": None
    })


@router.post("/chat/stream")
async def chat_sse(request: ChatRequest):
    """SSE streaming endpoint."""
    return StreamingResponse(
        chat_stream(request.question, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/chat")
async def chat(request: ChatRequest):
    """Original non-streaming endpoint (kept for backward compatibility)."""

    rate_check = check_rate_limit(request.session_id)
    if not rate_check["is_allowed"]:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry in {rate_check['retry_after_seconds']}s"
        )

    sql_result = generate_sql(request.question, request.session_id)
    if sql_result["error"]:
        return {
            "question": request.question,
            "answer": "Sorry, I could not understand your question.",
            "sql_query": "", "chart_type": "none",
            "chart_data": {}, "error": sql_result["error"]
        }

    sql_query = sql_result["sql"]

    validation = validate_sql(sql_query)
    if not validation["is_valid"]:
        return {
            "question": request.question,
            "answer": f"Query not allowed: {validation['reason']}",
            "sql_query": sql_query, "chart_type": "none",
            "chart_data": {}, "error": validation["reason"]
        }

    cost_check = check_query_cost(sql_query)
    if not cost_check["is_within_limit"]:
        return {
            "question": request.question,
            "answer": f"Query would scan {cost_check['estimated_mb']} MB, exceeding {cost_check['limit_mb']} MB limit.",
            "sql_query": sql_query, "chart_type": "none",
            "chart_data": {}, "error": "Cost too high"
        }

    query_result = execute_query(sql_query)
    if not query_result["success"]:
        return {
            "question": request.question,
            "answer": f"Query failed: {query_result['error']}",
            "sql_query": sql_query, "chart_type": "none",
            "chart_data": {}, "error": query_result["error"]
        }

    chart_type = detect_chart_type(query_result["columns"], query_result["data"], sql_query)
    chart_data = format_chart_data(query_result["columns"], query_result["data"], chart_type)

    answer_result = generate_answer(request.question, sql_query, query_result["data"], chart_type)
    answer_text = answer_result["answer"] if not answer_result["error"] else f"Query returned {query_result['row_count']} rows."

    add_turn(request.session_id, request.question, answer_text, sql_query)

    return {
        "question": request.question,
        "answer": answer_text,
        "sql_query": sql_query,
        "chart_type": chart_type,
        "chart_data": chart_data,
        "error": None
    }

