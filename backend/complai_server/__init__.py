"""
ComplAI MCP Server - AI-powered compliance auditor for smart contracts
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
AVALANCHE_RPC_URL = os.getenv("AVALANCHE_RPC_URL", "https://api.avax.network/ext/bc/C/rpc")

# Pydantic models
class ComplianceAuditRequest(BaseModel):
    contract_code: str
    standards: List[str]  # e.g., ['AML', 'GDPR', 'KYC', 'eERC']
    contract_address: Optional[str] = None  # For on-chain data

class ComplianceAuditResponse(BaseModel):
    risk_score: float  # 0-1, where 1 is highest risk
    issues: List[str]
    fixes: List[str]
    standards_checked: List[str]
    timestamp: str
    contract_address: Optional[str] = None

# FastAPI app
app = FastAPI(
    title="ComplAI MCP Server",
    description="AI-powered compliance auditor for smart contracts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP client
client = httpx.AsyncClient(timeout=30.0)

class ComplAIAuditor:
    """Main compliance auditor class"""

    def __init__(self):
        self.gemini_api_key = GEMINI_API_KEY
        self.avalanche_rpc = AVALANCHE_RPC_URL

    async def audit_contract(
        self,
        contract_code: str,
        standards: List[str],
        contract_address: Optional[str] = None
    ) -> ComplianceAuditResponse:
        """
        Perform compliance audit on smart contract code

        Args:
            contract_code: The smart contract source code
            standards: List of compliance standards to check
            contract_address: Optional Avalanche C-Chain address for on-chain data

        Returns:
            ComplianceAuditResponse with audit results
        """

        # Get on-chain data if address provided
        on_chain_data = ""
        if contract_address:
            on_chain_data = await self._get_on_chain_data(contract_address)

        # Prepare audit prompt
        prompt = self._build_audit_prompt(contract_code, standards, on_chain_data)

        # Call Gemini AI for analysis
        audit_result = await self._call_gemini_api(prompt)

        # Parse and structure the response
        parsed_result = self._parse_audit_response(audit_result, standards)

        return ComplianceAuditResponse(
            risk_score=parsed_result["risk_score"],
            issues=parsed_result["issues"],
            fixes=parsed_result["fixes"],
            standards_checked=standards,
            timestamp=datetime.utcnow().isoformat(),
            contract_address=contract_address
        )

    async def _get_on_chain_data(self, contract_address: str) -> str:
        """Fetch on-chain contract data from Avalanche"""
        try:
            # Get contract bytecode
            bytecode_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_getCode",
                "params": [contract_address, "latest"]
            }

            response = await client.post(self.avalanche_rpc, json=bytecode_payload)
            if response.status_code == 200:
                data = response.json()
                bytecode = data.get("result", "")

                return f"Contract Bytecode: {bytecode[:1000]}..."  # Truncate for API limits
            else:
                logger.warning(f"Failed to fetch bytecode for {contract_address}")
                return ""

        except Exception as e:
            logger.error(f"Error fetching on-chain data: {e}")
            return ""

    def _build_audit_prompt(
        self,
        contract_code: str,
        standards: List[str],
        on_chain_data: str = ""
    ) -> str:
        """Build the audit prompt for Gemini AI"""

        standards_text = ", ".join(standards)

        prompt = f"""
You are ComplAI, an expert AI compliance auditor specializing in blockchain and cryptocurrency regulations.

Please analyze the following smart contract code for compliance with these standards: {standards_text}

CONTRACT CODE:
```solidity
{contract_code}
```

{on_chain_data}

Your task is to:
1. Identify potential compliance violations or risks
2. Assess the overall risk score (0.0 = no risk, 1.0 = highest risk)
3. Provide specific recommendations for fixes

Please respond in the following JSON format:
{{
    "risk_score": 0.0,
    "issues": ["List specific compliance issues found"],
    "fixes": ["List recommended fixes for each issue"],
    "analysis": "Brief explanation of your assessment"
}}

Focus on these compliance areas:
- AML (Anti-Money Laundering): Check for KYC requirements, transaction monitoring, suspicious activity reporting
- GDPR: Data privacy, user consent, data minimization, right to erasure
- KYC (Know Your Customer): Identity verification, customer due diligence
- eERC (Enhanced ERC standards): Avalanche-specific compliance, cross-chain security
- General smart contract security: Reentrancy, overflow/underflow, access control

Be thorough but practical in your analysis.
"""

        return prompt

    async def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Call Gemini API for compliance analysis"""
        try:
            url = f"{GEMINI_BASE_URL}?key={self.gemini_api_key}"

            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }

            response = await client.post(url, json=payload)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Gemini API error: {response.text}"
                )

            data = response.json()

            # Extract the response text
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0]["text"]
                    return {"response": text}
            else:
                raise HTTPException(status_code=500, detail="Invalid Gemini API response")

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    def _parse_audit_response(
        self,
        api_response: Dict[str, Any],
        standards: List[str]
    ) -> Dict[str, Any]:
        """Parse the Gemini API response into structured format"""
        try:
            response_text = api_response.get("response", "")

            # Try to extract JSON from the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)

                # Validate and ensure required fields
                risk_score = min(1.0, max(0.0, float(parsed.get("risk_score", 0.5))))
                issues = parsed.get("issues", [])
                fixes = parsed.get("fixes", [])

                # Ensure issues and fixes are lists
                if not isinstance(issues, list):
                    issues = [str(issues)] if issues else []
                if not isinstance(fixes, list):
                    fixes = [str(fixes)] if fixes else []

                return {
                    "risk_score": risk_score,
                    "issues": issues,
                    "fixes": fixes
                }
            else:
                # Fallback parsing if JSON not found
                return self._fallback_parse(response_text)

        except Exception as e:
            logger.error(f"Failed to parse audit response: {e}")
            return self._fallback_parse(api_response.get("response", ""))

    def _fallback_parse(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        # Simple keyword-based risk assessment
        risk_keywords = ["violation", "non-compliant", "risk", "issue", "problem"]
        risk_score = min(1.0, len([k for k in risk_keywords if k in response_text.lower()]) * 0.2)

        return {
            "risk_score": risk_score,
            "issues": ["Manual review required - AI parsing failed"],
            "fixes": ["Please consult with compliance experts for detailed analysis"]
        }

# Global auditor instance
auditor = ComplAIAuditor()

# API Routes
@app.post("/tools/compliance_audit", response_model=ComplianceAuditResponse)
async def compliance_audit_tool(request: ComplianceAuditRequest):
    """MCP tool for compliance auditing smart contracts"""
    try:
        result = await auditor.audit_contract(
            request.contract_code,
            request.standards,
            request.contract_address
        )
        return result
    except Exception as e:
        logger.error(f"Compliance audit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "complai-mcp-server"}

@app.get("/tools/list")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "compliance_audit",
                "description": "Audit smart contracts for regulatory compliance (AML, GDPR, KYC, eERC)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "contract_code": {
                            "type": "string",
                            "description": "Smart contract source code to audit"
                        },
                        "standards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of compliance standards to check"
                        },
                        "contract_address": {
                            "type": "string",
                            "description": "Optional Avalanche C-Chain contract address"
                        }
                    },
                    "required": ["contract_code", "standards"]
                }
            }
        ]
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await client.aclose()

if __name__ == "__main__":
    port = int(os.getenv("COMPLAI_PORT", "5000"))
    uvicorn.run(
        "complai_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
