"""
Main FastAPI Application.
Entry point for the AI-BI Genie backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router

# Create the FastAPI app
app = FastAPI(
    title="AI-BI Genie",
    description="Conversational Analytics on E-Commerce Data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the chat router
app.include_router(chat_router)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "app": "AI-BI Genie",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "bigquery": "configured",
            "vertex_ai": "configured"
        }
    }
