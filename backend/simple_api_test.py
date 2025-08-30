#!/usr/bin/env python3
"""
Simple test for Gemini API key and endpoint
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print(f'API Key length: {len(api_key) if api_key else 0}')
print(f'API Key prefix: {api_key[:10] if api_key else "None"}')

async def test_simple():
    async with httpx.AsyncClient() as client:
        url = f'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}'
        payload = {
            'contents': [{'parts': [{'text': 'Hello'}]}],
            'generationConfig': {'temperature': 0.7, 'maxOutputTokens': 50}
        }
        try:
            resp = await client.post(url, json=payload, timeout=10.0)
            print(f'Status: {resp.status_code}')
            if resp.status_code != 200:
                print(f'Response: {resp.text[:500]}')
            else:
                print('✅ API call successful!')
                print(f'Response preview: {resp.text[:200]}...')
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(test_simple())
