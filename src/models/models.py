"""
Data models for the Support Ticket Resolution Agent.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TicketCategory(str, Enum):
    """Supported ticket categories."""
    BILLING = "billing"
    TECHNICAL = "technical"
    SECURITY = "security"
    GENERAL = "general"


class SupportTicket(BaseModel):
    """Input support ticket model."""
    subject: str = Field(description="Short description of the issue")
    description: str = Field(description="Detailed description of the issue")


class ClassificationResult(BaseModel):
    """Result of ticket classification."""
    category: TicketCategory = Field(description="Classified category")
    confidence: float = Field(description="Classification confidence score", ge=0.0, le=1.0)


class ContextSnippet(BaseModel):
    """A snippet of retrieved context."""
    content: str = Field(description="Content of the context snippet")
    source: str = Field(description="Source of the context (e.g., doc name, section)")
    relevance_score: float = Field(description="Relevance score", ge=0.0, le=1.0)


class RetrievalResult(BaseModel):
    """Result of context retrieval."""
    snippets: List[ContextSnippet] = Field(description="Retrieved context snippets")
    query_used: str = Field(description="Query used for retrieval")


class DraftResponse(BaseModel):
    """Draft response to the ticket."""
    content: str = Field(description="Draft response content")
    generated_at: str = Field(description="Timestamp of generation")
    attempt_number: int = Field(description="Attempt number (1, 2, or 3)")


class ReviewResult(BaseModel):
    """Result of draft review."""
    approved: bool = Field(description="Whether the draft is approved")
    score: float = Field(description="Review score", ge=0.0, le=1.0)
    feedback: str = Field(description="Reviewer feedback")
    criteria_scores: Dict[str, float] = Field(description="Scores for individual criteria")


class EscalationDetails(BaseModel):
    """Escalation details when all attempts fail."""
    needed: bool = Field(description="Whether escalation is needed")
    details: Optional[str] = Field(description="Escalation details", default=None)
    original_ticket: Optional[SupportTicket] = Field(description="Original ticket", default=None)
    failed_drafts: List[DraftResponse] = Field(description="All failed drafts", default_factory=list)
    reviewer_feedback: List[str] = Field(description="All reviewer feedback", default_factory=list)


class AgentState(BaseModel):
    """State of the support agent workflow."""
    # Input
    ticket: SupportTicket
    
    # Processing states
    classification: Optional[ClassificationResult] = None
    retrieval: Optional[RetrievalResult] = None
    draft: Optional[DraftResponse] = None
    review: Optional[ReviewResult] = None
    
    # Retry tracking
    attempt_count: int = 0
    max_attempts: int = 2
    all_drafts: List[DraftResponse] = Field(default_factory=list)
    all_reviews: List[ReviewResult] = Field(default_factory=list)
    
    # Final output
    final_response: Optional[str] = None
    escalation: Optional[EscalationDetails] = None
    
    # Metadata
    workflow_complete: bool = False
    needs_escalation: bool = False


class FinalOutput(BaseModel):
    """Final JSON output format as specified in requirements."""
    category: str = Field(description="Ticket category")
    context: List[str] = Field(description="Retrieved context snippets")
    draft: str = Field(description="Final or last draft reply")
    approved: bool = Field(description="Whether the draft was approved")
    score: float = Field(description="Review score")
    feedback: str = Field(description="Reviewer feedback or 'approved'")
    escalation: Dict[str, Any] = Field(description="Escalation details")
