"""
LangGraph nodes for the Support Ticket Resolution Agent.
"""

import json
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import os

from src.models.models import (
    AgentState, SupportTicket, ClassificationResult, TicketCategory,
    RetrievalResult, DraftResponse, ReviewResult, EscalationDetails
)
from src.services.llm_client import get_llm_client
from src.services.knowledge_base import get_knowledge_base


def classify_ticket(state: AgentState) -> Dict[str, Any]:
    """
    Classify the support ticket into one of four categories.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with classification result
    """
    llm = get_llm_client()
    
    system_prompt = """You are a support ticket classifier. Classify tickets into exactly ONE category:
- billing: Payment, invoices, refunds, subscriptions, pricing
- technical: Login issues, API problems, bugs, system errors, performance
- security: Password, 2FA, suspicious activity, data privacy, account security  
- general: Account management, feature requests, general inquiries

Respond with JSON format:
{
    "category": "billing|technical|security|general",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}"""

    user_prompt = f"""Classify this support ticket:

Subject: {state.ticket.subject}
Description: {state.ticket.description}

Classify into billing, technical, security, or general."""

    try:
        response = llm.invoke_with_json_response(user_prompt, system_prompt)
        
        # Extract classification
        category_str = response.get("category", "general").lower()
        confidence = float(response.get("confidence", 0.5))
        
        # Validate and convert category
        try:
            category = TicketCategory(category_str)
        except ValueError:
            category = TicketCategory.GENERAL
            confidence = 0.3
        
        classification = ClassificationResult(
            category=category,
            confidence=confidence
        )
        
        print(f"🧠 Classification: {category.value} (confidence: {confidence:.2f})")
        
        return {"classification": classification}
        
    except Exception as e:
        print(f"Error in classification: {e}")
        # Fallback classification
        return {
            "classification": ClassificationResult(
                category=TicketCategory.GENERAL,
                confidence=0.1
            )
        }


def retrieve_context(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve relevant context based on classification and ticket content.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with retrieval result
    """
    if not state.classification:
        raise ValueError("Classification must be completed before retrieval")
    
    kb = get_knowledge_base()
    
    # Create retrieval query from ticket
    query = f"{state.ticket.subject} {state.ticket.description}"
    
    # Use reviewer feedback to refine query if available
    if state.all_reviews and state.attempt_count > 0:
        last_feedback = state.all_reviews[-1].feedback
        query += f" {last_feedback}"
    
    # Retrieve context snippets
    snippets = kb.retrieve(
        query=query,
        category=state.classification.category,
        max_results=3
    )
    
    retrieval = RetrievalResult(
        snippets=snippets,
        query_used=query
    )
    
    print(f"🔍 Retrieved {len(snippets)} context snippets for {state.classification.category.value}")
    for i, snippet in enumerate(snippets):
        print(f"  {i+1}. {snippet.source} (score: {snippet.relevance_score:.2f})")
    
    return {"retrieval": retrieval}


def generate_draft(state: AgentState) -> Dict[str, Any]:
    """
    Generate a draft response using the ticket and retrieved context.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with draft response
    """
    if not state.classification or not state.retrieval:
        raise ValueError("Classification and retrieval must be completed before drafting")
    
    llm = get_llm_client()
    
    # Prepare context snippets
    context_text = "\n\n".join([
        f"Source: {snippet.source}\nContent: {snippet.content}"
        for snippet in state.retrieval.snippets
    ])
    
    # Include reviewer feedback if this is a retry
    feedback_text = ""
    if state.all_reviews and state.attempt_count > 0:
        feedback_text = f"\n\nPREVIOUS REVIEWER FEEDBACK TO ADDRESS:\n{state.all_reviews[-1].feedback}"
    
    system_prompt = f"""You are a customer support agent. Write a helpful, empathetic response to the customer's ticket.

GUIDELINES:
- Be professional, empathetic, and concise
- Use numbered steps for instructions
- Only use information from the provided context
- If context lacks information, politely say you don't have that information
- Don't overpromise refunds or make policy exceptions
- End with a next-step suggestion if the problem might persist
- Keep response under 300 words

CONTEXT INFORMATION:
{context_text}
{feedback_text}"""

    user_prompt = f"""Customer Ticket:
Subject: {state.ticket.subject}
Description: {state.ticket.description}

Write a helpful response based on the provided context."""

    try:
        response = llm.invoke(user_prompt, system_prompt)
        
        draft = DraftResponse(
            content=response.strip(),
            generated_at=datetime.now().isoformat(),
            attempt_number=state.attempt_count + 1
        )
        
        print(f"✍ Generated draft (attempt {draft.attempt_number})")
        
        # Update state
        new_attempt_count = state.attempt_count + 1
        new_all_drafts = state.all_drafts + [draft]
        
        return {
            "draft": draft,
            "attempt_count": new_attempt_count,
            "all_drafts": new_all_drafts
        }
        
    except Exception as e:
        print(f"Error generating draft: {e}")
        # Create a basic fallback draft
        draft = DraftResponse(
            content="I apologize, but I'm having trouble processing your request right now. Please contact our support team directly for immediate assistance.",
            generated_at=datetime.now().isoformat(),
            attempt_number=state.attempt_count + 1
        )
        
        return {
            "draft": draft,
            "attempt_count": state.attempt_count + 1,
            "all_drafts": state.all_drafts + [draft]
        }


def review_draft(state: AgentState) -> Dict[str, Any]:
    """
    Review the draft response for quality and policy compliance.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with review result
    """
    if not state.draft:
        raise ValueError("Draft must be generated before review")
    
    llm = get_llm_client()
    
    system_prompt = """You are a quality assurance reviewer for customer support responses. 
Evaluate the draft response against these criteria:

1. CORRECTNESS (0.0-1.0): Is the response factually accurate and grounded in context?
2. USEFULNESS (0.0-1.0): Does it provide actionable steps and anticipate user needs?
3. TONE (0.0-1.0): Is it professional, empathetic, and appropriately concise?
4. SAFETY (0.0-1.0): Does it avoid risky instructions and overpromising?

APPROVAL THRESHOLD: Overall score >= 0.75

Respond in JSON format:
{
    "approved": true/false,
    "overall_score": 0.0-1.0,
    "criteria_scores": {
        "correctness": 0.0-1.0,
        "usefulness": 0.0-1.0,
        "tone": 0.0-1.0,
        "safety": 0.0-1.0
    },
    "feedback": "specific feedback for improvement or 'approved'"
}"""

    user_prompt = f"""Original Ticket:
Subject: {state.ticket.subject}
Description: {state.ticket.description}

Draft Response to Review:
{state.draft.content}

Available Context:
{chr(10).join([snippet.content for snippet in state.retrieval.snippets]) if state.retrieval else 'No context available'}

Evaluate this draft response."""

    try:
        response = llm.invoke_with_json_response(user_prompt, system_prompt)
        
        # Extract review data
        approved = response.get("approved", False)
        overall_score = float(response.get("overall_score", 0.0))
        criteria_scores = response.get("criteria_scores", {
            "correctness": 0.0,
            "usefulness": 0.0,
            "tone": 0.0,
            "safety": 0.0
        })
        feedback = response.get("feedback", "No feedback provided")
        
        review = ReviewResult(
            approved=approved,
            score=overall_score,
            feedback=feedback,
            criteria_scores=criteria_scores
        )
        
        status = "✅ APPROVED" if approved else "❌ REJECTED"
        print(f"{status} - Score: {overall_score:.2f}")
        if not approved:
            print(f"Feedback: {feedback}")
        
        # Update state
        new_all_reviews = state.all_reviews + [review]
        
        return {
            "review": review,
            "all_reviews": new_all_reviews
        }
        
    except Exception as e:
        print(f"Error in review: {e}")
        # Fallback review - reject with generic feedback
        review = ReviewResult(
            approved=False,
            score=0.3,
            feedback="Unable to complete review due to technical error. Please revise the response.",
            criteria_scores={"correctness": 0.3, "usefulness": 0.3, "tone": 0.3, "safety": 0.3}
        )
        
        return {
            "review": review,
            "all_reviews": state.all_reviews + [review]
        }


def finalize_response(state: AgentState) -> Dict[str, Any]:
    """
    Finalize the approved response.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final response
    """
    if not state.draft or not state.review:
        raise ValueError("Draft and review must be completed before finalization")
    
    print(f"📤 Finalizing approved response (attempt {state.attempt_count})")
    
    return {
        "final_response": state.draft.content,
        "workflow_complete": True
    }


def escalate_ticket(state: AgentState) -> Dict[str, Any]:
    """
    Escalate the ticket when all attempts fail.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with escalation details
    """
    print("⚠ Escalating ticket - all attempts failed")
    
    # Prepare escalation details
    escalation = EscalationDetails(
        needed=True,
        details=f"Ticket failed after {state.attempt_count} attempts. Requires human review.",
        original_ticket=state.ticket,
        failed_drafts=state.all_drafts,
        reviewer_feedback=[review.feedback for review in state.all_reviews]
    )
    
    # Log to CSV file
    try:
        escalation_data = {
            "timestamp": datetime.now().isoformat(),
            "subject": state.ticket.subject,
            "description": state.ticket.description,
            "category": state.classification.category.value if state.classification else "unknown",
            "attempts": state.attempt_count,
            "final_score": state.all_reviews[-1].score if state.all_reviews else 0.0,
            "final_feedback": state.all_reviews[-1].feedback if state.all_reviews else "No feedback"
        }
        
        # Create or append to escalation log
        csv_file = "escalation_log.csv"
        df = pd.DataFrame([escalation_data])
        
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, index=False)
            
        print(f"📝 Logged escalation to {csv_file}")
        
    except Exception as e:
        print(f"Error logging escalation: {e}")
    
    return {
        "escalation": escalation,
        "needs_escalation": True,
        "workflow_complete": True
    }


def should_retry(state: AgentState) -> str:
    """
    Determine if the workflow should retry or escalate.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name ("retrieve_context" for retry, "escalate_ticket" for escalation)
    """
    if not state.review:
        return "escalate_ticket"
    
    if state.review.approved:
        return "finalize_response"
    
    if state.attempt_count >= state.max_attempts:
        return "escalate_ticket"
    
    print(f"🔁 Retrying - attempt {state.attempt_count + 1} of {state.max_attempts}")
    return "retrieve_context"
