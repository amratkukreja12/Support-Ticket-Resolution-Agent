"""
Data models and schemas for the Support Ticket Resolution Agent.
"""

from .models import (
    SupportTicket,
    TicketCategory,
    ClassificationResult,
    ContextSnippet,
    RetrievalResult,
    DraftResponse,
    ReviewResult,
    EscalationDetails,
    AgentState,
    FinalOutput
)

__all__ = [
    "SupportTicket",
    "TicketCategory", 
    "ClassificationResult",
    "ContextSnippet",
    "RetrievalResult",
    "DraftResponse",
    "ReviewResult",
    "EscalationDetails",
    "AgentState",
    "FinalOutput"
]
