"""
Gemini AI API client for Google's Gemini AI models
"""

import httpx
import json
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import logging

from app.core.config import get_settings
from app.core.exceptions import GeminiAPIError

settings = get_settings()
logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google's Gemini AI API"""

    def __init__(self):
        self.base_url = settings.GEMINI_BASE_URL
        self.api_key = settings.GEMINI_API_KEY
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Content-Type": "application/json"
            }
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a chat completion using Google's Gemini AI

        Args:
            messages: List of chat messages
            model: Model to use for completion (gemini-pro, gemini-pro-vision)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            tools: Available tools/functions
            tool_choice: Tool choice strategy

        Returns:
            Chat completion response
        """
        try:
            # Convert OpenAI format messages to Gemini format
            gemini_contents = self._convert_messages_to_gemini(messages)

            # Build Gemini request payload
            payload = {
                "contents": gemini_contents,
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": max_tokens or 2048,
                    "stopSequences": []
                }
            }

            # Add safety settings
            payload["safetySettings"] = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]

            # Use v1beta for the latest API features
            url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            # Convert Gemini response to OpenAI-like format for compatibility
            gemini_response = response.json()
            return self._convert_gemini_to_openai_format(gemini_response)

        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
            raise GeminiAPIError(
                f"API request failed: {e.response.status_code}",
                e.response.status_code
            )
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise GeminiAPIError(f"API request failed: {str(e)}")

    def _convert_messages_to_gemini(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI format messages to Gemini format"""
        gemini_contents = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            # Map OpenAI roles to Gemini roles
            if role == "system":
                # Gemini doesn't have a system role, so we'll prepend system message to first user message
                continue
            elif role == "assistant":
                gemini_role = "model"
            elif role == "user":
                gemini_role = "user"
            else:
                gemini_role = "user"  # Default to user

            # Handle different content types
            if isinstance(content, str):
                gemini_content = {
                    "role": gemini_role,
                    "parts": [{"text": content}]
                }
            elif isinstance(content, list):
                # Handle multimodal content (images, etc.)
                parts = []
                for item in content:
                    if item.get("type") == "text":
                        parts.append({"text": item.get("text", "")})
                    elif item.get("type") == "image_url":
                        # Gemini handles images differently - would need implementation
                        continue
                gemini_content = {
                    "role": gemini_role,
                    "parts": parts
                }
            else:
                gemini_content = {
                    "role": gemini_role,
                    "parts": [{"text": str(content)}]
                }

            gemini_contents.append(gemini_content)

        # If first message is not from user, add a placeholder user message
        if gemini_contents and gemini_contents[0].get("role") != "user":
            gemini_contents.insert(0, {
                "role": "user",
                "parts": [{"text": "Hello"}]
            })

        return gemini_contents

    def _convert_gemini_to_openai_format(self, gemini_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Gemini response to OpenAI-like format for compatibility"""
        try:
            candidates = gemini_response.get("candidates", [])
            if not candidates:
                return {
                    "choices": [{
                        "message": {"content": "No response generated"},
                        "finish_reason": "stop"
                    }],
                    "usage": {"total_tokens": 0}
                }

            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            # Extract text from parts
            text_content = ""
            for part in parts:
                if "text" in part:
                    text_content += part["text"]

            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": text_content
                    },
                    "finish_reason": candidate.get("finishReason", "stop")
                }],
                "usage": {
                    "prompt_tokens": gemini_response.get("usageMetadata", {}).get("promptTokenCount", 0),
                    "completion_tokens": gemini_response.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                    "total_tokens": gemini_response.get("usageMetadata", {}).get("totalTokenCount", 0)
                }
            }
        except Exception as e:
            logger.error(f"Error converting Gemini response: {e}")
            return {
                "choices": [{
                    "message": {"content": "Error processing response"},
                    "finish_reason": "error"
                }],
                "usage": {"total_tokens": 0}
            }

    async def stream_completion(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat completion responses (not fully implemented for Gemini)

        Yields:
            Streaming response chunks
        """
        # For now, just yield the full response as a single chunk
        try:
            response = await self.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                tools=tools
            )

            yield {
                "choices": [{
                    "delta": {"content": response["choices"][0]["message"]["content"]},
                    "finish_reason": "stop"
                }],
                "usage": response.get("usage", {})
            }

        except Exception as e:
            yield {
                "choices": [{"delta": {"content": ""}, "finish_reason": "error"}],
                "error": str(e)
            }
    
    async def deploy_agent(
        self,
        agent_config: Dict[str, Any],
        deployment_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy agent (not supported by Gemini API)

        Returns:
            Not implemented response
        """
        return {
            "error": "Agent deployment not supported by Gemini API",
            "status": "not_implemented"
        }
    
    async def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent context (not supported by Gemini API)

        Returns:
            Not implemented response
        """
        return {
            "error": "Agent context not supported by Gemini API",
            "status": "not_implemented"
        }
    
    async def update_agent_context(
        self,
        agent_id: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update agent context (not supported by Gemini API)

        Returns:
            Not implemented response
        """
        return {
            "error": "Agent context update not supported by Gemini API",
            "status": "not_implemented"
        }
    
    async def get_network_status(self) -> Dict[str, Any]:
        """
        Get network status (not applicable for Gemini API)

        Returns:
            Basic status
        """
        return {
            "status": "active",
            "provider": "Google Gemini AI",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of Gemini API

        Returns:
            Health status
        """
        try:
            # Try a simple request to check API availability
            test_payload = {
                "contents": [{
                    "parts": [{
                        "text": "Hello"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 50
                }
            }

            # Use v1beta instead of v1 for the latest API
            url = f"{self.base_url}/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.api_key}"
            logger.info(f"Health check URL: {url}")
            
            response = await self.client.post(url, json=test_payload, timeout=10.0)
            logger.info(f"Health check response status: {response.status_code}")
            
            if response.status_code == 200:
                return {
                    "healthy": True,
                    "status_code": response.status_code,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "provider": "Google Gemini AI",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "healthy": False,
                    "status_code": response.status_code,
                    "error": f"API returned {response.status_code}",
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "provider": "Google Gemini AI",
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "provider": "Google Gemini AI",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available Gemini models

        Returns:
            List of available models
        """
        try:
            url = f"{self.base_url}/v1beta/models?key={self.api_key}"
            response = await self.client.get(url)
            response.raise_for_status()

            models_data = response.json()
            models = models_data.get("models", [])

            return [
                {
                    "id": model.get("name", "").replace("models/", ""),
                    "object": "model",
                    "owned_by": "google",
                    "permission": []
                }
                for model in models
                if "gemini" in model.get("name", "").lower()
            ]

        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            # Return default Gemini models if API call fails
            return [
                {
                    "id": "gemini-pro",
                    "object": "model",
                    "owned_by": "google",
                    "permission": []
                },
                {
                    "id": "gemini-pro-vision",
                    "object": "model",
                    "owned_by": "google",
                    "permission": []
                }
            ]
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
