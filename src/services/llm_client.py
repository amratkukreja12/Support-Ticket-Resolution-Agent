"""
AWS Bedrock Claude 3.5 Sonnet client wrapper.
"""

import boto3
import json
from typing import Dict, Any, Optional
from config.credentials import get_bedrock_config


class BedrockLLMClient:
    """Wrapper for AWS Bedrock Claude 3.5 Sonnet."""
    
    def __init__(self):
        """Initialize the Bedrock client."""
        self.config = get_bedrock_config()
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of boto3 client."""
        if self._client is None:
            self._client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=self.config["aws_access_key_id"],
                aws_secret_access_key=self.config["aws_secret_access_key"],
                region_name=self.config["region_name"]
            )
        return self._client
    
    def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Invoke the model with a prompt using direct Bedrock API.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Model response as string
        """
        try:
            # Prepare messages in Claude format
            messages = []
            
            # Add user message
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            })
            
            # Prepare payload for Claude 3.5 Sonnet
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": messages,
                "max_tokens": self.config["model_kwargs"]["max_tokens"],
                "temperature": self.config["model_kwargs"]["temperature"],
                "top_p": self.config["model_kwargs"]["top_p"]
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.config["model_id"],
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            
            # Extract text content from Claude response
            if "content" in response_body and len(response_body["content"]) > 0:
                return response_body["content"][0]["text"]
            else:
                return "No response generated"
            
        except Exception as e:
            print(f"Error invoking Bedrock model: {e}")
            raise
    
    def invoke_with_json_response(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Invoke the model and parse JSON response.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Parsed JSON response
        """
        response = self.invoke(prompt, system_prompt)
        
        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON found, wrap the response
                return {"response": response}
                
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return {"response": response}


# Global client instance
_llm_client = None

def get_llm_client() -> BedrockLLMClient:
    """Get the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = BedrockLLMClient()
    return _llm_client
