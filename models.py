"""
Hermes Data Models

Pydantic models for request/response validation and database mapping.
All models include validation rules and type hints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums for Status Fields
# ============================================================================

class IdeaBotStatus(str, Enum):
    """IdeaBot evaluation status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProtoBotStatus(str, Enum):
    """ProtoBot execution status"""
    NA = "n/a"  # IdeaBot not approved yet
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class AgentContext(str, Enum):
    """Agent conversation context"""
    IDEABOT = "ideabot"
    BLUEPRINT = "blueprint"
    ORCHESTRATOR = "orchestrator"


class MessageRole(str, Enum):
    """Chat message role"""
    USER = "user"
    ASSISTANT = "assistant"


class ArtifactType(str, Enum):
    """Generated artifact type"""
    CODE = "code"
    CONTAINER = "container"
    DEPLOYMENT = "deployment"
    EMAIL = "email"
    CALENDAR = "calendar"
    BLOG = "blog"


# ============================================================================
# Project Models
# ============================================================================

class ProjectBase(BaseModel):
    """Base project fields"""
    id: str = Field(..., description="Unique project identifier (e.g. 'vllm-cpu')")
    name: str = Field(..., description="Project name")
    lead: str = Field(..., description="Project lead name")
    strategic_priority: Optional[str] = Field(None, description="Strategic priority area")
    catcher_org: Optional[str] = Field(None, description="Catching organization")
    catcher_product: Optional[str] = Field(None, description="Catching product")
    catcher_pm: Optional[str] = Field(None, description="Catching Product Manager")
    catcher_em: Optional[str] = Field(None, description="Catching Engineering Manager")
    catcher_tl: Optional[str] = Field(None, description="Catching Technical Lead")
    slack_channel: Optional[str] = Field(None, description="Slack channel (e.g. '#ai-inference')")

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate project ID format"""
        if not v or not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Project ID must be alphanumeric (hyphens/underscores allowed)")
        return v.lower()


class ProjectCreate(ProjectBase):
    """Project creation request"""
    ideabot_status: IdeaBotStatus = Field(default=IdeaBotStatus.NOT_STARTED)
    protobot_status: ProtoBotStatus = Field(default=ProtoBotStatus.NA)


class Project(ProjectBase):
    """Complete project model (from database)"""
    ideabot_status: IdeaBotStatus
    protobot_status: ProtoBotStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# IdeaBot Models
# ============================================================================

class IdeaBotAnswers(BaseModel):
    """IdeaBot Q&A answers"""
    q1_name: Optional[str] = Field(None, description="Question 1: What is your name?")
    q2_idea: Optional[str] = Field(None, description="Question 2: What is the idea?")
    q3_project_name: Optional[str] = Field(None, description="Question 3: What is the project name?")
    q4_market_relevance: Optional[str] = Field(None, description="Question 4: Why is this relevant to Red Hat's market?")
    q5_strategic_priority: Optional[str] = Field(None, description="Question 5: Does this contribute to a strategic priority?")
    q6_catcher_product: Optional[str] = Field(None, description="Question 6: Which product will receive these capabilities?")
    q7_catcher_pm: Optional[str] = Field(None, description="Question 7: Who is the catching Product Manager?")
    q8_catcher_em: Optional[str] = Field(None, description="Question 8: Who is the catching Engineering Manager?")
    q9_catcher_tl: Optional[str] = Field(None, description="Question 9: Who is the catching technical lead?")
    q10_existing_work: Optional[str] = Field(None, description="Question 10: Have you checked that catchers aren't already working on this?")
    q11_technical_approach: Optional[str] = Field(None, description="Question 11: Have you discussed technical approach with catching TL?")


class IdeaBotEvaluation(BaseModel):
    """IdeaBot evaluation result"""
    decision: str = Field(..., description="Decision: approved|rejected")
    rationale: str = Field(..., description="Detailed rationale for decision")

    @field_validator('decision')
    @classmethod
    def validate_decision(cls, v: str) -> str:
        """Validate decision value"""
        if v not in ["approved", "rejected"]:
            raise ValueError("Decision must be 'approved' or 'rejected'")
        return v


class IdeaBotData(BaseModel):
    """Complete IdeaBot session data"""
    project_id: str
    answers: IdeaBotAnswers = Field(default_factory=IdeaBotAnswers)
    evaluation: Optional[IdeaBotEvaluation] = None


class IdeaBotSessionUpdate(BaseModel):
    """IdeaBot session update request"""
    answers: Optional[IdeaBotAnswers] = None
    evaluation: Optional[IdeaBotEvaluation] = None


# ============================================================================
# ProtoBot Models
# ============================================================================

class ResearchLead(BaseModel):
    """Single research lead generated from IdeaBot answers"""
    source: str = Field(..., description="Source field from IdeaBot (e.g. 'Project Name')")
    lead: str = Field(..., description="Extracted lead/keyword")
    action: str = Field(..., description="Recommended research action")


class ResearchFindings(BaseModel):
    """Research findings for one vector"""
    findings: List[str] = Field(default_factory=list, description="Key findings")
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    open_questions: List[str] = Field(default_factory=list, description="Questions requiring follow-up")


class FollowUpQA(BaseModel):
    """Follow-up Q&A pair"""
    question: str = Field(..., description="Follow-up question")
    answer: str = Field(default="", description="HIL answer")


class BlueprintSection(BaseModel):
    """Blueprint section for one research vector"""
    summary: str = Field(..., description="Executive summary")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    risks_mitigations: List[str] = Field(default_factory=list, description="Risks and mitigations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class CodeArtifact(BaseModel):
    """Generated code artifact"""
    filename: str
    content: str
    artifact_type: str = Field(default="source", description="source|test|config|doc")
    language: Optional[str] = None


class InfraArtifact(BaseModel):
    """Generated infrastructure artifact"""
    filename: str
    content: str
    artifact_type: str = Field(default="container", description="container|deployment|security")


class CommsArtifacts(BaseModel):
    """Generated communications artifacts"""
    email: Optional[str] = Field(None, description="Email to catcher team (RFC 822 format)")
    calendar: Optional[str] = Field(None, description="Calendar invite (.ics format)")
    blog: Optional[str] = Field(None, description="Blog post (Markdown with frontmatter)")


class ValidationCheck(BaseModel):
    """Cross-validation check result"""
    check: str = Field(..., description="Check name")
    status: str = Field(..., description="pass|fail|warning")
    details: str = Field(default="", description="Check details")


class ProtoBotData(BaseModel):
    """Complete ProtoBot session data"""
    project_id: str
    current_step: int = Field(default=1, ge=1, le=8, description="Current execution step (1-8)")

    # Step data
    step1_research_leads: List[ResearchLead] = Field(default_factory=list)
    step2_research_findings: Dict[str, ResearchFindings] = Field(default_factory=dict)
    step3_followup_qa: List[FollowUpQA] = Field(default_factory=list)
    step4_blueprint: Dict[str, BlueprintSection] = Field(default_factory=dict)
    step5_hil_approved: bool = Field(default=False)
    step6_code_artifacts: List[CodeArtifact] = Field(default_factory=list)
    step6_infra_artifacts: List[InfraArtifact] = Field(default_factory=list)
    step6_comms_artifacts: CommsArtifacts = Field(default_factory=CommsArtifacts)
    step7_validation: List[ValidationCheck] = Field(default_factory=list)
    step8_final_config: Dict[str, Any] = Field(default_factory=dict)


class ProtoBotSessionUpdate(BaseModel):
    """ProtoBot session update request"""
    current_step: Optional[int] = Field(None, ge=1, le=8)
    step1_research_leads: Optional[List[ResearchLead]] = None
    step2_research_findings: Optional[Dict[str, ResearchFindings]] = None
    step3_followup_qa: Optional[List[FollowUpQA]] = None
    step4_blueprint: Optional[Dict[str, BlueprintSection]] = None
    step5_hil_approved: Optional[bool] = None
    step6_code_artifacts: Optional[List[CodeArtifact]] = None
    step6_infra_artifacts: Optional[List[InfraArtifact]] = None
    step6_comms_artifacts: Optional[CommsArtifacts] = None
    step7_validation: Optional[List[ValidationCheck]] = None
    step8_final_config: Optional[Dict[str, Any]] = None


# ============================================================================
# Chat Models
# ============================================================================

class ChatMessage(BaseModel):
    """Single chat message"""
    role: MessageRole
    content: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Chat message request"""
    project_id: str
    context: AgentContext
    message: str
    fields: Optional[Dict[str, Any]] = Field(None, description="Field values for field-aware chat")


class ChatResponse(BaseModel):
    """Chat message response"""
    role: MessageRole = Field(default=MessageRole.ASSISTANT)
    content: str
    field_updates: Optional[Dict[str, Any]] = Field(None, description="Field updates for UI")


# ============================================================================
# Artifact Models
# ============================================================================

class ArtifactMetadata(BaseModel):
    """Artifact metadata"""
    language: Optional[str] = None
    size: Optional[int] = None
    lines: Optional[int] = None
    type: Optional[str] = None


class Artifact(BaseModel):
    """Generated artifact record"""
    id: int
    project_id: str
    artifact_type: ArtifactType
    filename: str
    file_path: str
    content_hash: Optional[str] = None
    metadata: Optional[ArtifactMetadata] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ArtifactCreate(BaseModel):
    """Artifact creation request"""
    project_id: str
    artifact_type: ArtifactType
    filename: str
    file_path: str
    content_hash: Optional[str] = None
    metadata: Optional[ArtifactMetadata] = None


# ============================================================================
# API Response Models
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="healthy|unhealthy")
    service: str = Field(default="hermes")
    version: str = Field(default="1.0.0")
    database: str = Field(..., description="connected|error")
    vertex_ai: str = Field(..., description="configured|not_configured|error")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Generic success response"""
    status: str = Field(default="success")
    message: str
    data: Optional[Dict[str, Any]] = None
