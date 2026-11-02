"""
Meeting Transcript Processing Module

Provides API endpoints and pipeline for processing MS Teams meeting transcripts.
"""

from .api import router
from .pipeline import process_meeting_transcript

__all__ = ["router", "process_meeting_transcript"]
