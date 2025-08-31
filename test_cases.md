# 🧪 Support Ticket Resolution Agent - Test Cases

## ✅ **APPROVED SCENARIOS** (Should get approved on first try)

### 1. **Billing Issue - Simple**
```
Subject: Invoice not received
Description: I haven't received my invoice for this month. My account shows a pending charge but no invoice in my billing section.
```

### 2. **Technical Issue - Clear**
```
Subject: Cannot login to account
Description: I keep getting 'invalid credentials' error when trying to log in. I'm sure my password is correct.
```

### 3. **Security Issue - Standard**
```
Subject: Suspicious login activity
Description: I got an email about a login from Russia but I'm in the US. I never logged in from there.
```

### 4. **General Issue - FAQ-like**
```
Subject: How to change my password
Description: I want to update my account password. Can you guide me through the process?
```

## 🔄 **RETRY SCENARIOS** (Should trigger retry mechanism)

### 5. **Complex Multi-Category Issue**
```
Subject: Complex billing and technical issue
Description: My payment failed, but I was charged twice. Now I can't log in to my account to check my billing status. The mobile app also crashes when I try to access billing info. This started after the recent system update. I need immediate help as this is affecting my business operations.
```

### 6. **Vague Issue**
```
Subject: System not working
Description: Something is broken. Please fix it ASAP. Very urgent!!!
```

### 7. **Mixed Technical Issues**
```
Subject: Multiple problems with my account
Description: I can't access my dashboard, the API is returning errors, and my webhook notifications stopped working. Also, my billing shows incorrect charges. This is affecting my entire business workflow.
```

## ⚠️ **ESCALATION SCENARIOS** (Should escalate to human after 2 attempts)

### 8. **Complex Security Breach**
```
Subject: Potential data breach and account compromise
Description: I think my account has been hacked. I see transactions I didn't make, my password was changed without my consent, and I'm getting emails about account changes I didn't authorize. I also suspect my personal data might have been accessed. This could be a serious security breach affecting multiple accounts. I need immediate legal and technical assistance.
```

### 9. **Legal/Compliance Issue**
```
Subject: GDPR compliance and data deletion request
Description: I need to exercise my right to be forgotten under GDPR. I want all my personal data deleted from your systems, including backups and third-party integrations. I also need documentation of what data you have on me. This is a legal requirement and I need immediate action.
```

### 10. **Critical Business Impact**
```
Subject: Complete system failure affecting production
Description: Our entire production system is down. We're losing thousands of dollars per hour. The API is completely unresponsive, all integrations have failed, and our customers are complaining. This is a critical business emergency requiring immediate escalation to senior technical staff.
```

## 🎯 **QUICK TEST SEQUENCE**

### **Start with these 3 for basic testing:**

1. **Simple Test:**
```
Subject: Password reset needed
Description: I forgot my password and need to reset it.
```

2. **Medium Test:**
```
Subject: API rate limiting issues
Description: I'm getting 429 errors from your API. My application is hitting rate limits even though I'm within the documented limits. This is affecting my service reliability.
```

3. **Complex Test:**
```
Subject: Integration failure with multiple systems
Description: Our webhook integration stopped working, the OAuth flow is broken, and we're getting authentication errors. This affects our entire customer onboarding process. We've tried the troubleshooting steps but nothing works.
```

## 🚀 **HOW TO TEST**

### **Option 1: Direct Python**
```bash
python main.py
```
Then enter the subject and description when prompted.

### **Option 2: LangGraph Dev Server**
```bash
langgraph dev
```
Then visit: http://localhost:8123

### **Option 3: JSON Input**
```bash
python main.py '{"subject": "Invoice not received", "description": "I haven\'t received my invoice for this month."}'
```

## 📊 **EXPECTED OUTCOMES**

- **Approved Cases**: Should get score ≥ 0.75 and be approved immediately
- **Retry Cases**: Should get score < 0.75, trigger retry, then either approve or escalate
- **Escalation Cases**: Should fail 2 attempts and escalate to human review

## 🎪 **DEMO RECOMMENDATIONS**

For client demonstrations, use these in order:
1. **Simple billing issue** (shows quick approval)
2. **Complex multi-issue** (shows retry mechanism)
3. **Security breach** (shows escalation system)

This demonstrates the full workflow capabilities!
