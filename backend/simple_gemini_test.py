#!/usr/bin/env python3
"""
Simple Gemini API test
"""

import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    api_key = os.getenv('GEMINI_API_KEY')
    print(f'API Key length: {len(api_key) if api_key else 0}')

    if not api_key:
        print("No API key found")
        return

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}'
    print(f'URL: {url[:80]}...')

    payload = {
        'contents': [{
            'role': 'user',
            'parts': [{'text': 'Hello, just testing the API'}]
        }],
        'generationConfig': {
            'temperature': 0.7,
            'maxOutputTokens': 50
        }
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            print("Making request...")
            response = await client.post(url, json=payload)
            print(f'Status: {response.status_code}')
            if response.status_code == 200:
                print('✅ Success!')
                print(f'Response: {response.text[:300]}...')
            else:
                print(f'❌ Error response: {response.text}')
        except Exception as e:
            print(f'❌ Exception: {e}')

if __name__ == "__main__":
    asyncio.run(test())
