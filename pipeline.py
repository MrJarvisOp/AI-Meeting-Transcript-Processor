"""
Meeting Transcript Processing Pipeline

Main pipeline that:
1. Summarizes MS Teams meeting transcript using Azure OpenAI
2. Generates PDF document from the summary
3. Uploads PDF to blob storage with metadata
"""

import logging
from datetime import datetime
from io import BytesIO
from typing import Dict, Any

from openai import AzureOpenAI
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from azure.storage.blob import BlobServiceClient

from .config import load_config

logger = logging.getLogger(__name__)


def process_meeting_transcript(
    client_id: str,
    committee_key: str,
    company_key: str,
    transcript: str
) -> Dict[str, Any]:
    """
    Main pipeline function to process meeting transcript.

    Args:
        client_id: Unique client identifier
        committee_key: Committee identifier
        company_key: Company identifier
        transcript: Full MS Teams meeting transcript text

    Returns:
        Dict containing processing results and blob URL
    """
    logger.info(f"Processing meeting transcript for client: {client_id}")

    # Load config
    config = load_config()

    # Step 1: Summarize transcript using Azure OpenAI
    logger.info("Step 1: Summarizing transcript with Azure OpenAI")
    summary = _summarize_transcript(transcript, config)

    # Step 2: Generate PDF from summary
    logger.info("Step 2: Generating PDF document")
    pdf_bytes = _generate_pdf(summary, client_id, committee_key, company_key)

    # Step 3: Upload to blob storage
    logger.info("Step 3: Uploading to blob storage")
    blob_url = _upload_to_blob(
        pdf_bytes,
        client_id,
        committee_key,
        company_key,
        config
    )

    logger.info(f"✅ Pipeline completed successfully. Blob URL: {blob_url}")

    return {
        "client_id": client_id,
        "committee_key": committee_key,
        "company_key": company_key,
        "summary_length": len(summary),
        "pdf_size_bytes": len(pdf_bytes),
        "blob_url": blob_url,
        "timestamp": datetime.utcnow().isoformat()
    }


def _summarize_transcript(transcript: str, config) -> str:
    """Use Azure OpenAI to summarize the meeting transcript."""

    client = AzureOpenAI(
        api_key=config.azure_openai_api_key,
        api_version=config.azure_openai_api_version,
        azure_endpoint=config.azure_openai_endpoint
    )

    # Create summarization prompt
    prompt = f"""You are an expert meeting analyst. Analyze this MS Teams meeting transcript and provide a comprehensive summary.

Include:
1. **Main Topics Discussed**: List the primary subjects covered
2. **Key Points**: Important points made during the meeting
3. **Decisions Made**: Any decisions or conclusions reached
4. **Action Items**: Tasks or follow-ups mentioned
5. **Participants' Contributions**: Notable contributions from attendees

Transcript:
{transcript}

Provide a well-structured summary in markdown format."""

    logger.info(f"Calling Azure OpenAI for summarization (model: {config.azure_openai_chat_deployment})")

    response = client.chat.completions.create(
        model=config.azure_openai_chat_deployment,
        messages=[
            {"role": "system", "content": "You are an expert meeting analyst who creates clear, concise summaries."},
            {"role": "user", "content": prompt}
        ],
        temperature=config.llm_temperature,
        max_tokens=config.llm_max_tokens
    )

    summary = response.choices[0].message.content
    logger.info(f"Summary generated: {len(summary)} characters")

    return summary


def _generate_pdf(summary: str, client_id: str, committee_key: str, company_key: str) -> bytes:
    """Generate PDF document from the summary."""

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30
    )

    # Build document content
    story = []

    # Title
    story.append(Paragraph("Meeting Summary", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Metadata
    story.append(Paragraph(f"<b>Client ID:</b> {client_id}", styles['Normal']))
    story.append(Paragraph(f"<b>Committee:</b> {committee_key}", styles['Normal']))
    story.append(Paragraph(f"<b>Company:</b> {company_key}", styles['Normal']))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # Summary content (convert markdown-style headers to PDF formatting)
    for line in summary.split('\n'):
        if line.strip():
            if line.startswith('# '):
                story.append(Paragraph(line[2:], styles['Heading1']))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], styles['Heading2']))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], styles['Heading3']))
            elif line.startswith('**') or line.startswith('*'):
                story.append(Paragraph(line, styles['Normal']))
            else:
                story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))

    # Build PDF
    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info(f"PDF generated: {len(pdf_bytes)} bytes")

    return pdf_bytes


def _upload_to_blob(
    pdf_bytes: bytes,
    client_id: str,
    committee_key: str,
    company_key: str,
    config
) -> str:
    """Upload PDF to blob storage with metadata."""

    # Create blob service client
    blob_service = BlobServiceClient.from_connection_string(
        config.azure_storage_connection_string
    )

    # Container name is client_id
    container_name = client_id.lower()

    # Ensure container exists
    container_client = blob_service.get_container_client(container_name)
    try:
        container_client.create_container()
        logger.info(f"Created container: {container_name}")
    except Exception:
        logger.info(f"Container already exists: {container_name}")

    # Generate blob name with timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    blob_name = f"meeting_summary_{timestamp}.pdf"

    # Upload with metadata
    blob_client = blob_service.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    metadata = {
        "committeekey": committee_key,
        "companykey": company_key,
        "document_type": "meeting_summary",
        "generated_date": datetime.utcnow().isoformat()
    }

    blob_client.upload_blob(
        pdf_bytes,
        overwrite=True,
        metadata=metadata
    )

    blob_url = blob_client.url
    logger.info(f"Uploaded to blob: {blob_url}")

    return blob_url
