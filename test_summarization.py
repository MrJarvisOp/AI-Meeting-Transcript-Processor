"""
Test script for meeting transcript summarization.

Tests the summarization function in isolation without PDF generation or blob upload.

Usage:
    python src/meeting_processor/test_summarization.py
    python src/meeting_processor/test_summarization.py --transcript "path/to/transcript.txt"
"""

import argparse
import sys
from pathlib import Path

from .pipeline import _summarize_transcript
from .config import load_config


# Default transcript file path
DEFAULT_TRANSCRIPT_FILE = Path(__file__).parent / "sample_hoa_transcript.txt"


def test_summarization(transcript: str, save_output: bool = True):
    """
    Test the summarization function with a transcript.

    Args:
        transcript: The meeting transcript text
        save_output: Whether to save output to a file
    """
    print("=" * 80)
    print("MEETING TRANSCRIPT SUMMARIZATION TEST")
    print("=" * 80)
    print(f"\nTranscript length: {len(transcript)} characters")
    print(f"Transcript word count: ~{len(transcript.split())} words")
    print("\n" + "=" * 80)
    print("ORIGINAL TRANSCRIPT")
    print("=" * 80)
    print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
    print("\n" + "=" * 80)
    print("CALLING AZURE OPENAI FOR SUMMARIZATION...")
    print("=" * 80)

    # Load config
    config = load_config()

    # Call summarization function
    try:
        summary = _summarize_transcript(transcript, config)

        print("\n" + "=" * 80)
        print("✅ SUMMARIZATION SUCCESSFUL")
        print("=" * 80)
        print(f"\nSummary length: {len(summary)} characters")
        print(f"Summary word count: ~{len(summary.split())} words")
        print(f"Compression ratio: {len(summary)/len(transcript)*100:.1f}%")
        print("\n" + "=" * 80)
        print("GENERATED SUMMARY")
        print("=" * 80)
        print(summary)
        print("\n" + "=" * 80)

        # Save to file if requested
        if save_output:
            output_file = Path(__file__).parent / "test_summary_output.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("MEETING TRANSCRIPT SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Generated: {Path(__file__).name}\n")
                f.write(f"Transcript length: {len(transcript)} characters\n")
                f.write(f"Summary length: {len(summary)} characters\n")
                f.write(f"Compression ratio: {len(summary)/len(transcript)*100:.1f}%\n\n")
                f.write("=" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                f.write(summary)
                f.write("\n\n" + "=" * 80 + "\n")
                f.write("End of Summary\n")

            print(f"✅ Output saved to: {output_file}")

        return summary

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ SUMMARIZATION FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point for test script."""
    parser = argparse.ArgumentParser(
        description="Test meeting transcript summarization",
        epilog=f"Default transcript: {DEFAULT_TRANSCRIPT_FILE.name}"
    )
    parser.add_argument(
        "--transcript",
        "-t",
        help="Path to transcript file (uses sample_hoa_transcript.txt if not provided)",
        default=None
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save output to file"
    )

    args = parser.parse_args()

    # Load transcript
    if args.transcript:
        transcript_path = Path(args.transcript)
        if not transcript_path.exists():
            print(f"❌ Error: Transcript file not found: {transcript_path}")
            sys.exit(1)
    else:
        # Use default HOA transcript file
        transcript_path = DEFAULT_TRANSCRIPT_FILE
        if not transcript_path.exists():
            print(f"❌ Error: Default transcript file not found: {transcript_path}")
            print("   Please ensure sample_hoa_transcript.txt exists in the meeting_processor directory")
            sys.exit(1)

    # Read transcript file
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        print(f"📄 Loaded transcript from: {transcript_path}")
    except Exception as e:
        print(f"❌ Error reading transcript file: {e}")
        sys.exit(1)

    # Run test
    summary = test_summarization(transcript, save_output=not args.no_save)

    if summary:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
