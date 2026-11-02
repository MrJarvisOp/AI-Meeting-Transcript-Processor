"""
FastAPI endpoints for meeting transcript processing
"""

import logging
import time
from fastapi import APIRouter, HTTPException

from .models import ProcessTranscriptRequest, ProcessTranscriptResponse
from .pipeline import process_meeting_transcript

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/meeting", tags=["Meeting Transcript Processing"])


@router.post("/process", response_model=ProcessTranscriptResponse)
async def process_transcript(request: ProcessTranscriptRequest):
    """
    Process MS Teams meeting transcript and generate summary PDF.

    This endpoint:
    1. Takes a meeting transcript from MS Teams
    2. Uses Azure OpenAI to summarize main topics and key points
    3. Generates a PDF document with the summary
    4. Uploads to blob storage with metadata (client_id, CommitteeKey, CompanyKey)

    **Example Usage (curl)**:
    ```bash
    curl -X POST "http://localhost:8000/api/meeting/process" \\
      -H "Content-Type: application/json" \\
      -d '{
        "client_id": "acme-corp",
        "CommitteeKey": "COMM123",
        "CompanyKey": "COMP789",
        "transcript": "Full meeting transcript text here..."
      }'
    ```

    **Example Usage (Python requests)**:
    ```python
    import requests

    data = {
        "client_id": "acme-corp",
        "CommitteeKey": "COMM123",
        "CompanyKey": "COMP789",
        "transcript": "Meeting transcript..."
    }

    response = requests.post(
        "http://localhost:8000/api/meeting/process",
        json=data
    )
    ```
    """
    start_time = time.time()

    try:
        logger.info(f"API: Processing meeting transcript for client: {request.client_id}")
        logger.info(f"   Transcript length: {len(request.transcript)} characters")
        logger.info(f"   Committee: {request.committee_key}, Company: {request.company_key}")

        # Call main pipeline function
        result = process_meeting_transcript(
            client_id=request.client_id,
            committee_key=request.committee_key,
            company_key=request.company_key,
            transcript=request.transcript
        )

        execution_time = time.time() - start_time

        return ProcessTranscriptResponse(
            status="success",
            message=f"Meeting transcript processed successfully for client {request.client_id}",
            data=result,
            execution_time_seconds=round(execution_time, 2)
        )

    except Exception as e:
        logger.error(
            f"API: Failed to process transcript for client {request.client_id}: {str(e)}",
            exc_info=True
        )
        execution_time = time.time() - start_time

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Failed to process meeting transcript for client {request.client_id}",
                "error": str(e),
                "execution_time_seconds": round(execution_time, 2)
            }
        )
