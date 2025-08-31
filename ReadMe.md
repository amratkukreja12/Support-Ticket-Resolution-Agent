# Setup Instructions

## 1. Environment Variables Setup

Create a `.env` file in the project root with your AWS credentials:

```bash
# AWS Bedrock Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# Optional: AWS Session Token (if using temporary credentials)
# AWS_SESSION_TOKEN=your_session_token_here
```

## 2. Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install LangGraph CLI:
```bash
pip install "langgraph-cli[inmem]"
```

## 3. Running the Agent

### Option 1: Direct Python
```bash
python main.py
```

### Option 2: LangGraph Development Server
```bash
langgraph dev
```
Then visit: http://localhost:8123

## 4. AWS Bedrock Access

Make sure you have:
- AWS account with Bedrock access
- Claude 3.5 Sonnet model enabled in your region
- Proper IAM permissions for Bedrock

## 5. Testing

The agent will process support tickets and demonstrate:
- ✅ Approval workflow (high-quality responses)
- 🔄 Retry workflow (refinement and re-drafting)
- ⚠️ Escalation workflow (human handoff after 2 attempts)
