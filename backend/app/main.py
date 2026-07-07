"""
Main FastAPI Application.
Entry point for the AI-BI Genie backend.
Serves both the API and the React frontend.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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


@app.get("/api/health")
def health_check():
    return {
        "status": "running",
        "app": "AI-BI Genie",
        "version": "1.0.0"
    }


# Serve React frontend (only in production when static folder exists)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

if os.path.exists(static_dir):
    # Serve static files (JS, CSS, images)
    app.mount("/static", StaticFiles(directory=os.path.join(static_dir, "static")), name="static")

    # Serve React index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))
