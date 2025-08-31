"""
Main entry point for the Support Ticket Resolution Agent.
"""

import json
import sys
from typing import Optional

from src.models.models import SupportTicket
from src.core.agent import create_agent


def process_ticket_from_json(ticket_json: str) -> dict:
    """
    Process a ticket from JSON string input.
    
    Args:
        ticket_json: JSON string containing ticket data
        
    Returns:
        Result dictionary
    """
    try:
        ticket_data = json.loads(ticket_json)
        ticket = SupportTicket(**ticket_data)
        
        agent = create_agent()
        result = agent.process_ticket(ticket)
        
        return result.dict()
        
    except Exception as e:
        return {
            "error": str(e),
            "category": "general",
            "context": [],
            "draft": "Error processing ticket",
            "approved": False,
            "score": 0.0,
            "feedback": f"Processing error: {str(e)}",
            "escalation": {"needed": True, "details": f"Error: {str(e)}"}
        }


def interactive_mode():
    """Run the agent in interactive mode."""
    print("🎫 Support Ticket Resolution Agent - Interactive Mode")
    print("="*60)
    print("Enter ticket details (or 'quit' to exit):\n")
    
    agent = create_agent()
    
    while True:
        try:
            print("📝 New Ticket:")
            subject = input("Subject: ").strip()
            
            if subject.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not subject:
                print("❌ Subject cannot be empty. Please try again.\n")
                continue
            
            description = input("Description: ").strip()
            
            if not description:
                print("❌ Description cannot be empty. Please try again.\n")
                continue
            
            # Create and process ticket
            ticket = SupportTicket(subject=subject, description=description)
            
            print(f"\n🚀 Processing ticket: {subject}")
            print("-" * 50)
            
            result = agent.process_ticket(ticket)
            
            print("\n📊 RESULT:")
            print("-" * 20)
            print(json.dumps(result.dict(), indent=2))
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        # No arguments - run interactive mode
        interactive_mode()
        
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['-h', '--help']:
            print("""
Support Ticket Resolution Agent

Usage:
    python main.py                          # Interactive mode
    python main.py '{"subject": "...", "description": "..."}'  # Process JSON ticket
    python main.py --help                   # Show this help

Examples:
    python main.py '{"subject": "Login issue", "description": "Cannot access my account"}'
    
For testing and demos:
    python test_examples.py                 # Quick demo
    python test_examples.py all             # Full demo
    python test_examples.py billing         # Billing tickets only
    python test_examples.py retry           # Retry mechanism demo
    python test_examples.py workflow        # Show workflow diagram
            """)
        else:
            # Assume it's a JSON ticket
            ticket_json = sys.argv[1]
            result = process_ticket_from_json(ticket_json)
            print(json.dumps(result, indent=2))
    
    else:
        print("❌ Too many arguments. Use --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
