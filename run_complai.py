#!/usr/bin/env python3
"""
Run script for ComplAI MCP Server
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import and run the server
from complai_server.complai_server import app

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("COMPLAI_PORT", "5000"))
    print(f"Starting ComplAI MCP Server on port {port}")
    print("Make sure GEMINI_API_KEY is set in your environment")
    
    uvicorn.run(
        "complai_server.complai_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
