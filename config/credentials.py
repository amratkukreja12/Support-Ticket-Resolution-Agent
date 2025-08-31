"""
AWS Bedrock credentials and configuration.
Replace these with your actual AWS credentials and configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "your-access-key-id")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "your-secret-access-key")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Bedrock Model Configuration
BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
BEDROCK_MODEL_KWARGS = {
    "max_tokens": 4000,
    "temperature": 0.1,
    "top_p": 0.9
}

def get_bedrock_config():
    """Return the configuration dictionary for AWS Bedrock."""
    return {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region_name": AWS_REGION,
        "model_id": BEDROCK_MODEL_ID,
        "model_kwargs": BEDROCK_MODEL_KWARGS
    }
