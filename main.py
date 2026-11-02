"""
Standalone FastAPI application for Meeting Transcript Processing.

Run with:
    uvicorn src.meeting_processor.main:app --reload --port 8001

API Documentation:
    http://localhost:8001/docs (Swagger UI)
    http://localhost:8001/redoc (ReDoc)
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Meeting Transcript Processing API",
    description="""
    REST API for processing MS Teams meeting transcripts.

    ## Features

    * **AI-Powered Summarization**: Uses Azure OpenAI to extract key points
    * **PDF Generation**: Creates professional summary documents
    * **Blob Storage Integration**: Automatically uploads with metadata
    * **Multi-Tenant Support**: Client-specific containers and metadata

    ## Workflow

    1. Submit meeting transcript via POST /api/meeting/process
    2. AI summarizes main topics, decisions, and action items
    3. PDF document generated with summary and metadata
    4. Uploaded to client-specific blob container
    5. Returns blob URL and processing details
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "service": "Meeting Transcript Processing API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "process_transcript": "POST /api/meeting/process"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Actions to perform on API startup."""
    logger.info("=" * 80)
    logger.info("Meeting Transcript Processing API Starting")
    logger.info("=" * 80)
    logger.info("API Version: 1.0.0")
    logger.info("Documentation: http://localhost:8001/docs")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on API shutdown."""
    logger.info("API shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
