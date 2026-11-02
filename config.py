"""
Meeting Processor Configuration Module.

Handles configuration loading for the meeting transcript processing pipeline.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class MeetingProcessorConfig:
    """Configuration for meeting transcript processor."""

    # Required fields
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_chat_deployment: str
    azure_storage_connection_string: str

    # Optional fields with defaults
    azure_openai_api_version: str = "2024-02-01"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "MeetingProcessorConfig":
        """
        Load configuration from environment variables or .env file.

        Args:
            env_file: Path to .env file (default: .env in this directory)
        """
        # Load .env file if it exists
        if env_file is None:
            env_file = Path(__file__).parent / ".env"

        if Path(env_file).exists():
            _load_env_file(env_file)

        return cls(
            # Azure OpenAI
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            azure_openai_chat_deployment=os.getenv(
                "AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4"
            ),
            azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),

            # Azure Blob Storage
            azure_storage_connection_string=os.getenv(
                "AZURE_STORAGE_CONNECTION_STRING", ""
            ),

            # LLM parameters
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
        )

    def validate(self) -> None:
        """Validate required configuration fields."""
        required_fields = [
            ("azure_openai_endpoint", "AZURE_OPENAI_ENDPOINT"),
            ("azure_openai_api_key", "AZURE_OPENAI_API_KEY"),
            ("azure_openai_chat_deployment", "AZURE_OPENAI_CHAT_DEPLOYMENT"),
            ("azure_storage_connection_string", "AZURE_STORAGE_CONNECTION_STRING"),
        ]

        missing = []
        for field, env_var in required_fields:
            value = getattr(self, field)
            if not value or value == "":
                missing.append(env_var)

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please create a .env file in src/meeting_processor/ with these variables."
            )


def _load_env_file(env_file: str) -> None:
    """Load environment variables from .env file."""
    env_path = Path(env_file)
    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse KEY=VALUE
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value


def load_config() -> MeetingProcessorConfig:
    """
    Load and validate configuration.

    Returns:
        MeetingProcessorConfig instance

    Raises:
        ValueError: If required environment variables are missing
    """
    config = MeetingProcessorConfig.from_env()
    config.validate()
    return config
