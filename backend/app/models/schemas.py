"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    question: str = Field(..., description="User question in plain English")
    session_id: str = Field(default="default", description="Session ID for conversation memory")


class ChatResponse(BaseModel):
    question: str = Field(..., description="Original user question")
    answer: str = Field(..., description="Natural language answer from AI")
    sql_query: str = Field(default="", description="Generated SQL query")
    chart_type: str = Field(default="none", description="Chart type: bar, line, pie, or none")
    chart_data: dict = Field(default_factory=dict, description="Data for chart rendering")
    error: Optional[str] = Field(default=None, description="Error message if something went wrong")
