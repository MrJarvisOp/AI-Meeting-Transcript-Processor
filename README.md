# Meeting Transcript Processing API

Simple REST API for processing MS Teams meeting transcripts using Azure OpenAI, generating PDF summaries, and storing them in Azure Blob Storage.

## Overview

**Pipeline Flow:**
```
MS Teams Transcript → Azure OpenAI (Summarize) → PDF Generator → Blob Storage
```

## Features

- ✅ **AI-Powered Summarization**: Extracts main topics, key points, decisions, and action items
- ✅ **PDF Generation**: Creates professional summary documents with metadata
- ✅ **Multi-Tenant Support**: Client-specific blob containers
- ✅ **Metadata Tracking**: CommitteeKey, CompanyKey, timestamps

## Quick Start

### 1. Configure Environment

The module has its own configuration in `src/meeting_processor/.env`:

```bash
# Already configured! ✅
# The .env file is ready with your Azure credentials
```

**If you need to modify configuration:**
- Edit `src/meeting_processor/.env`
- See `src/meeting_processor/.env.example` for reference

**Required variables:**
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_STORAGE_CONNECTION_STRING`

### 2. Run the API

**Standalone (Port 8001):**
```bash
cd D:\AI\LLM\Chetu\DEV
uvicorn src.meeting_processor.main:app --reload --port 8001
```

**Integrated with Indexer API:**
See section below.

### 3. Test the Endpoint

```bash
curl -X POST "http://localhost:8001/api/meeting/process" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "acme-corp",
    "CommitteeKey": "COMM123",
    "CompanyKey": "COMP789",
    "transcript": "Meeting started at 10:00 AM. John: We need to discuss the Q4 budget. Sarah: I agree, we should focus on cost reduction..."
  }'
```

**Python Example:**
```python
import requests

data = {
    "client_id": "acme-corp",
    "CommitteeKey": "COMM123",
    "CompanyKey": "COMP789",
    "transcript": "Your full meeting transcript here..."
}

response = requests.post(
    "http://localhost:8001/api/meeting/process",
    json=data
)

print(response.json())
# {
#   "status": "success",
#   "message": "Meeting transcript processed...",
#   "data": {
#     "blob_url": "https://storage.../acme-corp/meeting_summary_20231215_143022.pdf",
#     "summary_length": 1234,
#     "pdf_size_bytes": 45678
#   }
# }
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## File Structure

```
src/meeting_processor/
├── __init__.py              # Package exports
├── config.py                # Configuration management
├── .env                     # Environment variables (configured)
├── .env.example             # Environment template
├── pipeline.py              # Main processing logic ⭐
├── api.py                   # FastAPI endpoints
├── models.py                # Pydantic request/response models
├── main.py                  # Standalone API app
├── test_summarization.py    # Test script for summarization
└── README.md                # This file
```

## How It Works

### 1. Summarization (`_summarize_transcript`)
- Uses Azure OpenAI Chat Completion API
- Analyzes transcript for key topics, decisions, action items
- Returns structured markdown summary

### 2. PDF Generation (`_generate_pdf`)
- Uses ReportLab to create professional PDF
- Includes metadata header (client_id, keys, timestamp)
- Formats summary with proper headings and styling

### 3. Blob Upload (`_upload_to_blob`)
- Creates container named `{client_id}` if doesn't exist
- Uploads PDF with filename: `meeting_summary_{timestamp}.pdf`
- Attaches metadata: CommitteeKey, CompanyKey, document_type

## Integration with Indexer API

To integrate with the existing indexer API at `indexer/deployment/api/main_client.py`:

**Option 1: Add to existing API**

Edit `indexer/deployment/api/main_client.py`:

```python
# Add import
from src.meeting_processor import router as meeting_router

# Add router
app.include_router(meeting_router, tags=["Meeting Processing"])
```

Then access at: `http://localhost:8000/api/meeting/process`

**Option 2: Run standalone**

Keep it separate on port 8001 (as shown in Quick Start)

## Dependencies

Required packages (should already be installed):
- `fastapi`
- `openai` (Azure OpenAI SDK)
- `reportlab` (PDF generation)
- `azure-storage-blob`
- `pydantic`
- `uvicorn`

## Error Handling

The API handles errors gracefully:
- Invalid client_id → 422 error
- Azure OpenAI failures → 500 error with details
- Blob upload failures → 500 error with details

All errors include `execution_time_seconds` and detailed error messages.

## Testing Summarization

A comprehensive HOA meeting transcript is included for testing:

**Test with default HOA transcript (5000+ words):**
```bash
python -m src.meeting_processor.test_summarization
```

**Test with your own transcript:**
```bash
python -m src.meeting_processor.test_summarization --transcript path/to/your/file.txt
```

**Test without saving output:**
```bash
python -m src.meeting_processor.test_summarization --no-save
```

The test script:
- Uses `sample_hoa_transcript.txt` by default (realistic HOA/village management meeting)
- Shows transcript statistics (length, word count)
- Displays the generated summary
- Shows compression ratio
- Saves output to `test_summary_output.txt`

## Sample Transcript Details

`sample_hoa_transcript.txt` contains a realistic 2.5-hour HOA board meeting covering:
- Financial reports and budget discussions
- Maintenance and capital improvements
- Security camera upgrades
- Pool resurfacing projects
- Architectural guidelines
- Pet policies
- EV charging infrastructure
- Community events
- Playground renovation
- Parking and traffic concerns

Perfect for testing summarization of complex, multi-topic meetings!

## Next Steps

- [ ] Add transcript length validation (warn if too large)
- [ ] Support for different summarization styles (brief, detailed, executive)
- [ ] Email notification when processing completes
- [ ] Webhook support for async processing
- [ ] Support for audio file upload (auto-transcribe then summarize)
