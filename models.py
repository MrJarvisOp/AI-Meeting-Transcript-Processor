"""
Pydantic models for meeting processor API
"""

from pydantic import BaseModel, Field
from typing import Any, Dict


class ProcessTranscriptRequest(BaseModel):
    """Request model for processing meeting transcript"""
    client_id: str = Field(..., description="Unique client identifier")
    committee_key: str = Field(..., description="Committee identifier", alias="CommitteeKey")
    company_key: str = Field(..., description="Company identifier", alias="CompanyKey")
    transcript: str = Field(..., description="Full MS Teams meeting transcript")

    class Config:
        populate_by_name = True


class ProcessTranscriptResponse(BaseModel):
    """Response model for meeting transcript processing"""
    status: str
    message: str
    data: Dict[str, Any]
    execution_time_seconds: float
