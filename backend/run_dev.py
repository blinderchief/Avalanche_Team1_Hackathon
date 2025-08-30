#!/usr/bin/env python3
"""
Development server startup script
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path  
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    # Set development environment
    os.environ.setdefault("ENVIRONMENT", "development")
    
    print(f"""
🚀 Starting SpectraQ Agent Backend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Environment: development
Host: 0.0.0.0:8000
Docs: http://localhost:8000/docs
Health: http://localhost:8000/health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
