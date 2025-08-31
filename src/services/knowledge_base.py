"""
Mock knowledge base for different ticket categories.
In a real implementation, this would be replaced with a vector database or document store.
"""

from typing import List, Dict
from src.models.models import TicketCategory, ContextSnippet


class MockKnowledgeBase:
    """Mock knowledge base with category-specific information."""
    
    def __init__(self):
        """Initialize the knowledge base with mock data."""
        self.knowledge = {
            TicketCategory.BILLING: [
                {
                    "content": "For billing inquiries, customers can view their invoices in the account dashboard under 'Billing & Payments'. Payment methods can be updated in the same section.",
                    "source": "billing_faq.md",
                    "keywords": ["invoice", "payment", "billing", "account", "dashboard"]
                },
                {
                    "content": "Refunds are processed within 5-7 business days. Customers must request refunds within 30 days of purchase. Contact billing@company.com for refund requests.",
                    "source": "refund_policy.md",
                    "keywords": ["refund", "return", "money back", "cancel"]
                },
                {
                    "content": "Subscription changes take effect at the next billing cycle. Upgrades are prorated, downgrades take effect at cycle end to avoid partial charges.",
                    "source": "subscription_management.md",
                    "keywords": ["subscription", "upgrade", "downgrade", "plan", "billing cycle"]
                },
                {
                    "content": "Failed payments will retry automatically after 3 days. Update payment method to avoid service interruption. Account may be suspended after 3 failed attempts.",
                    "source": "payment_failures.md",
                    "keywords": ["failed payment", "declined", "card", "suspended", "retry"]
                }
            ],
            
            TicketCategory.TECHNICAL: [
                {
                    "content": "For login issues, first try clearing browser cache and cookies. If problem persists, reset password using 'Forgot Password' link on login page.",
                    "source": "login_troubleshooting.md",
                    "keywords": ["login", "password", "authentication", "cache", "cookies"]
                },
                {
                    "content": "API rate limits are 1000 requests per hour for standard accounts, 5000 for premium. Use exponential backoff for retry logic when hitting rate limits.",
                    "source": "api_documentation.md",
                    "keywords": ["api", "rate limit", "requests", "429", "quota"]
                },
                {
                    "content": "Mobile app crashes can often be resolved by updating to the latest version. Force close the app and restart. Clear app cache if issues persist.",
                    "source": "mobile_troubleshooting.md",
                    "keywords": ["mobile", "app", "crash", "update", "restart"]
                },
                {
                    "content": "Database connection timeouts indicate high server load. Wait 5-10 minutes and retry. Check status page for ongoing incidents at status.company.com",
                    "source": "server_status.md",
                    "keywords": ["timeout", "database", "connection", "server", "status"]
                },
                {
                    "content": "Email notifications may be delayed up to 30 minutes during peak hours. Check spam folder if emails are missing. Verify email address in account settings.",
                    "source": "notification_issues.md",
                    "keywords": ["email", "notification", "spam", "delayed", "missing"]
                }
            ],
            
            TicketCategory.SECURITY: [
                {
                    "content": "Enable two-factor authentication (2FA) in account security settings. Use authenticator app for best security. SMS backup is available but less secure.",
                    "source": "2fa_setup.md",
                    "keywords": ["2fa", "two-factor", "authentication", "security", "authenticator"]
                },
                {
                    "content": "Suspicious account activity should be reported immediately. Change password and review recent login history in security settings. Contact security@company.com for urgent issues.",
                    "source": "security_incidents.md",
                    "keywords": ["suspicious", "activity", "breach", "unauthorized", "security"]
                },
                {
                    "content": "Password requirements: minimum 12 characters, include uppercase, lowercase, numbers, and symbols. Avoid common passwords and personal information.",
                    "source": "password_policy.md",
                    "keywords": ["password", "requirements", "strong", "secure", "policy"]
                },
                {
                    "content": "Data export requests are processed within 48 hours. Submit request through account settings > Privacy > Export Data. Files are available for 7 days.",
                    "source": "data_privacy.md",
                    "keywords": ["data export", "gdpr", "privacy", "download", "personal data"]
                }
            ],
            
            TicketCategory.GENERAL: [
                {
                    "content": "Account deletion is permanent and cannot be undone. Export your data first. Contact support to initiate deletion process. Allow 30 days for complete removal.",
                    "source": "account_deletion.md",
                    "keywords": ["delete account", "close", "remove", "permanent", "export"]
                },
                {
                    "content": "Feature requests can be submitted through the feedback form in app settings. Popular requests are reviewed monthly by the product team.",
                    "source": "feature_requests.md",
                    "keywords": ["feature", "request", "suggestion", "feedback", "product"]
                },
                {
                    "content": "Business hours support: Monday-Friday 9AM-6PM EST. Premium customers have 24/7 phone support. Response time: 4 hours for urgent, 24 hours for normal.",
                    "source": "support_hours.md",
                    "keywords": ["support", "hours", "contact", "response time", "urgent"]
                },
                {
                    "content": "Account information updates (name, email, phone) can be made in profile settings. Email changes require verification. Some changes may require identity verification.",
                    "source": "profile_management.md",
                    "keywords": ["profile", "update", "personal", "information", "verification"]
                }
            ]
        }
    
    def retrieve(self, query: str, category: TicketCategory, max_results: int = 3) -> List[ContextSnippet]:
        """
        Retrieve relevant context snippets for a query and category.
        
        Args:
            query: Search query
            category: Ticket category
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant context snippets
        """
        if category not in self.knowledge:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each snippet based on keyword matches
        scored_snippets = []
        for snippet_data in self.knowledge[category]:
            # Calculate relevance score based on keyword matches
            keyword_matches = sum(1 for keyword in snippet_data["keywords"] 
                                if any(word in keyword.lower() for word in query_words))
            
            # Also check for direct content matches
            content_matches = sum(1 for word in query_words 
                                if word in snippet_data["content"].lower())
            
            # Combined score (normalize by keyword count)
            total_score = (keyword_matches * 2 + content_matches) / (len(snippet_data["keywords"]) + 1)
            relevance_score = min(total_score, 1.0)  # Cap at 1.0
            
            if relevance_score > 0:  # Only include relevant snippets
                snippet = ContextSnippet(
                    content=snippet_data["content"],
                    source=snippet_data["source"],
                    relevance_score=relevance_score
                )
                scored_snippets.append((relevance_score, snippet))
        
        # Sort by relevance score (descending) and return top results
        scored_snippets.sort(key=lambda x: x[0], reverse=True)
        return [snippet for _, snippet in scored_snippets[:max_results]]


# Global knowledge base instance
_knowledge_base = None

def get_knowledge_base() -> MockKnowledgeBase:
    """Get the global knowledge base instance."""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = MockKnowledgeBase()
    return _knowledge_base
