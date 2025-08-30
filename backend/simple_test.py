#!/usr/bin/env python3
"""
Simple test for updated Gemini integration
"""

import asyncio
from app.services.gemini_client import GeminiClient

async def test():
    client = GeminiClient()
    try:
        print("Testing health check...")
        health = await client.health_check()
        print("Health check result:", health)

        if health.get('healthy'):
            print("\nTesting chat completion...")
            messages = [{"role": "user", "content": "Hello! Explain AI in one sentence."}]
            response = await client.chat_completion(messages=messages)
            print("Response:", response['choices'][0]['message']['content'][:100] + "...")
        else:
            print("Health check failed")
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test())
