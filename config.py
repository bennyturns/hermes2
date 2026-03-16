"""
Hermes Configuration Management

Environment-based configuration using Pydantic Settings.
Supports multiple deployment modes with sensible defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Configuration Modes:
    -------------------
    1. FULL MOCK (Development/Demo):
       - MOCK_MODE=true, MOCK_AGENTS=true, MOCK_EXECUTION=true
       - No real AI calls, no file execution
       - Uses canned responses and UI-only interactions
       - Perfect for UI development and stakeholder demos

    2. REAL AI (Testing):
       - MOCK_MODE=false, MOCK_AGENTS=false, MOCK_EXECUTION=true
       - Real Vertex AI agents generate responses
       - No actual file execution (dry-run mode)
       - Good for testing agent prompts and workflows

    3. FULL PRODUCTION (Deployment):
       - MOCK_MODE=false, MOCK_AGENTS=false, MOCK_EXECUTION=false
       - Real AI agents + real file execution
       - Writes artifacts to output/ directory
       - Production mode for actual prototype generation
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ============================================================================
    # Application Settings
    # ============================================================================

    app_name: str = Field(default="Hermes", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment: development|staging|production")
    debug: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level: DEBUG|INFO|WARNING|ERROR")

    # ============================================================================
    # Server Settings
    # ============================================================================

    host: str = Field(default="0.0.0.0", description="Server bind host")
    port: int = Field(default=8000, description="Server bind port")
    reload: bool = Field(default=True, description="Enable auto-reload (development only)")

    # ============================================================================
    # Mock Mode Flags
    # ============================================================================

    mock_mode: bool = Field(
        default=True,
        description="Master mock switch - if true, entire system uses mock data"
    )

    mock_agents: bool = Field(
        default=True,
        description="Use mock AI responses instead of real Vertex AI calls"
    )

    mock_execution: bool = Field(
        default=True,
        description="Use dry-run mode for file execution (no actual writes)"
    )

    # ============================================================================
    # Database Settings
    # ============================================================================

    database_path: Path = Field(
        default=Path(__file__).parent / "hermes.db",
        description="SQLite database file path"
    )

    database_echo: bool = Field(
        default=False,
        description="Echo SQL queries to console (debugging)"
    )

    # ============================================================================
    # Google Cloud Vertex AI Settings
    # ============================================================================

    vertex_project_id: Optional[str] = Field(
        default=None,
        description="Google Cloud project ID for Vertex AI"
    )

    vertex_region: str = Field(
        default="us-east5",
        description="Vertex AI region (us-east5 for Claude)"
    )

    vertex_model: str = Field(
        default="claude-sonnet-4-5@20250929",
        description="Claude model version for Vertex AI"
    )

    vertex_max_tokens: int = Field(
        default=8192,
        description="Maximum tokens for agent responses"
    )

    vertex_temperature: float = Field(
        default=0.7,
        description="Temperature for agent responses (0.0-1.0)"
    )

    # ============================================================================
    # File System Settings
    # ============================================================================

    output_base_path: Path = Field(
        default=Path(__file__).parent / "output",
        description="Base directory for generated artifacts"
    )

    artifacts_path: Path = Field(
        default=Path(__file__).parent / "output" / "artifacts",
        description="Code/container/deployment artifacts directory"
    )

    communications_path: Path = Field(
        default=Path(__file__).parent / "output" / "communications",
        description="Emails/calendar/blog posts directory"
    )

    logs_path: Path = Field(
        default=Path(__file__).parent / "output" / "logs",
        description="Execution logs directory"
    )

    # ============================================================================
    # Agent Prompt Paths
    # ============================================================================

    prompts_base_path: Path = Field(
        default=Path(__file__).parent / "prompts",
        description="Base directory for agent system prompts"
    )

    ideabot_prompt_path: Path = Field(
        default=Path(__file__).parent / "prompts" / "ideabot" / "prompt.txt",
        description="IdeaBot system prompt file"
    )

    protobot_prompts_path: Path = Field(
        default=Path(__file__).parent / "prompts" / "protobot" / "protobot-prompts.md",
        description="ProtoBot system prompts file"
    )

    octo_definition_path: Path = Field(
        default=Path(__file__).parent / "prompts" / "context" / "octo-definition.md",
        description="OCTO team context definition"
    )

    strategic_focus_path: Path = Field(
        default=Path(__file__).parent / "prompts" / "context" / "strategic-focus.txt",
        description="Strategic priorities context"
    )

    # ============================================================================
    # Mock Data Paths (Phase 0 compatibility)
    # ============================================================================

    mocks_base_path: Path = Field(
        default=Path(__file__).parent / "mocks",
        description="Base directory for mock JSON files"
    )

    # ============================================================================
    # Feature Flags
    # ============================================================================

    enable_chat: bool = Field(
        default=True,
        description="Enable chat panel functionality"
    )

    enable_streaming: bool = Field(
        default=True,
        description="Enable streaming responses from agents"
    )

    enable_field_aware_chat: bool = Field(
        default=False,
        description="Enable field-aware chat (Phase 5 feature)"
    )

    enable_real_time_updates: bool = Field(
        default=False,
        description="Enable WebSocket/SSE for real-time progress (Phase 5 feature)"
    )

    # ============================================================================
    # Security Settings
    # ============================================================================

    allowed_origins: list[str] = Field(
        default=["http://localhost:8000", "http://127.0.0.1:8000"],
        description="CORS allowed origins"
    )

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def is_mock_mode(self) -> bool:
        """Check if any mock mode is enabled"""
        return self.mock_mode or self.mock_agents or self.mock_execution

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production" and not self.is_mock_mode()

    def ensure_directories(self):
        """Create required directories if they don't exist"""
        for path in [
            self.output_base_path,
            self.artifacts_path,
            self.communications_path,
            self.logs_path,
            self.prompts_base_path,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def model_post_init(self, __context):
        """Post-initialization hook"""
        # Ensure output directories exist
        self.ensure_directories()


# ============================================================================
# Settings Singleton
# ============================================================================

# Global settings instance - accessible throughout the application
settings = Settings()


# ============================================================================
# Example Configurations
# ============================================================================

def get_config_examples():
    """
    Return example configurations for different deployment scenarios.

    Usage:
        # Create .env file with one of these configurations
        # Then restart the application
    """
    return {
        "full_mock": """
# Full Mock Mode (UI Development & Demos)
MOCK_MODE=true
MOCK_AGENTS=true
MOCK_EXECUTION=true
DEBUG=true
LOG_LEVEL=DEBUG
        """.strip(),

        "real_ai_testing": """
# Real AI Testing (Prompt Development)
MOCK_MODE=false
MOCK_AGENTS=false
MOCK_EXECUTION=true
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_REGION=us-east5
DEBUG=true
LOG_LEVEL=INFO
        """.strip(),

        "full_production": """
# Full Production (Live Deployment)
MOCK_MODE=false
MOCK_AGENTS=false
MOCK_EXECUTION=false
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_REGION=us-east5
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000
RELOAD=false
        """.strip(),

        "openshift": """
# OpenShift Deployment
MOCK_MODE=false
MOCK_AGENTS=false
MOCK_EXECUTION=false
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_REGION=us-east5
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
RELOAD=false
DATABASE_PATH=/data/hermes.db
OUTPUT_BASE_PATH=/output
        """.strip()
    }
