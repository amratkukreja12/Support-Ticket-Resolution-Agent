"""
Main Support Ticket Resolution Agent using LangGraph.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.models.models import AgentState, SupportTicket, FinalOutput
from src.core.nodes import (
    classify_ticket, retrieve_context, generate_draft, 
    review_draft, finalize_response, escalate_ticket, should_retry
)


class SupportTicketAgent:
    """Support Ticket Resolution Agent with LangGraph orchestration."""
    
    def __init__(self):
        """Initialize the agent with LangGraph workflow."""
        self.workflow = self._build_workflow()
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the graph with AgentState
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_ticket", classify_ticket)
        workflow.add_node("retrieve_context", retrieve_context)
        workflow.add_node("generate_draft", generate_draft)
        workflow.add_node("review_draft", review_draft)
        workflow.add_node("finalize_response", finalize_response)
        workflow.add_node("escalate_ticket", escalate_ticket)
        
        # Set entry point
        workflow.set_entry_point("classify_ticket")
        
        # Add edges
        workflow.add_edge("classify_ticket", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_draft")
        workflow.add_edge("generate_draft", "review_draft")
        
        # Conditional edge from review_draft
        workflow.add_conditional_edges(
            "review_draft",
            should_retry,
            {
                "retrieve_context": "retrieve_context",  # Retry loop
                "finalize_response": "finalize_response",  # Success
                "escalate_ticket": "escalate_ticket"  # Escalation
            }
        )
        
        # Terminal edges
        workflow.add_edge("finalize_response", END)
        workflow.add_edge("escalate_ticket", END)
        
        return workflow
    
    def process_ticket(self, ticket: SupportTicket, thread_id: str = "default") -> FinalOutput:
        """
        Process a support ticket through the complete workflow.
        
        Args:
            ticket: Input support ticket
            thread_id: Thread ID for conversation tracking
            
        Returns:
            Final output in the specified JSON format
        """
        print(f"📨 Processing ticket: {ticket.subject}")
        print("=" * 50)
        
        # Initialize state
        initial_state = AgentState(ticket=ticket)
        
        # Run the workflow
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Execute the workflow
            final_state = None
            for state in self.app.stream(initial_state.dict(), config):
                final_state = state
                
            if not final_state:
                raise ValueError("Workflow did not produce a final state")
            
            # Get the final state values
            last_node_output = list(final_state.values())[-1]
            
            # Ensure ticket is preserved in the final state
            if "ticket" not in last_node_output:
                last_node_output["ticket"] = initial_state.ticket.dict()
            
            # Reconstruct the final state
            final_agent_state = AgentState(**last_node_output)
            
            print("=" * 50)
            print("📋 WORKFLOW COMPLETE")
            
            # Convert to the required output format
            return self._format_output(final_agent_state)
            
        except Exception as e:
            print(f"Error processing ticket: {e}")
            
            # Return error state
            return FinalOutput(
                category="general",
                context=[],
                draft="I apologize, but there was an error processing your request. Please contact support directly.",
                approved=False,
                score=0.0,
                feedback=f"System error: {str(e)}",
                escalation={
                    "needed": True,
                    "details": f"System error during processing: {str(e)}"
                }
            )
    
    def _format_output(self, state: AgentState) -> FinalOutput:
        """
        Format the final state into the required JSON output format.
        
        Args:
            state: Final agent state
            
        Returns:
            Formatted output
        """
        # Extract context snippets
        context = []
        if state.retrieval and state.retrieval.snippets:
            context = [snippet.content for snippet in state.retrieval.snippets]
        
        # Get final draft content
        draft_content = ""
        if state.final_response:
            draft_content = state.final_response
        elif state.draft:
            draft_content = state.draft.content
        else:
            draft_content = "No response generated"
        
        # Get review results
        approved = False
        score = 0.0
        feedback = "No review completed"
        
        if state.review:
            approved = state.review.approved
            score = state.review.score
            feedback = state.review.feedback if not approved else "approved"
        elif state.final_response:
            # If we have a final response, assume it was approved
            approved = True
            score = 1.0
            feedback = "approved"
        
        # Format escalation
        escalation_dict = {"needed": False, "details": None}
        if state.escalation:
            escalation_dict = {
                "needed": state.escalation.needed,
                "details": state.escalation.details
            }
        elif state.needs_escalation:
            escalation_dict = {
                "needed": True,
                "details": "Ticket escalated after maximum retry attempts"
            }
        
        return FinalOutput(
            category=state.classification.category.value if state.classification else "general",
            context=context,
            draft=draft_content,
            approved=approved,
            score=score,
            feedback=feedback,
            escalation=escalation_dict
        )
    
    def get_workflow_visualization(self) -> str:
        """Get a text representation of the workflow."""
        return """
Support Ticket Resolution Agent Workflow:

📨 INPUT: Support Ticket (subject + description)
    ↓
🧠 CLASSIFY: Determine category (billing/technical/security/general)
    ↓
🔍 RETRIEVE: Get relevant context from knowledge base
    ↓
✍ DRAFT: Generate response using context + ticket
    ↓
✅ REVIEW: Check quality and policy compliance
    ↓
🔀 DECISION:
    ├─ APPROVED → 📤 FINALIZE: Return final response
    ├─ REJECTED & attempts < 2 → 🔁 RETRY: Back to RETRIEVE
    └─ REJECTED & attempts >= 2 → ⚠ ESCALATE: Log for human review

Key Features:
- Category-specific knowledge retrieval
- Feedback-driven retry loop (max 2 attempts)  
- Automated quality assurance review
- CSV logging for escalated cases
- AWS Bedrock Claude 3.5 Sonnet integration
        """


def create_agent() -> SupportTicketAgent:
    """Create and return a new Support Ticket Agent instance."""
    return SupportTicketAgent()


# For LangGraph CLI server
def create_graph():
    """Create the graph for LangGraph CLI server."""
    agent = create_agent()
    return agent.app
