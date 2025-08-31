# ComplAI Integration for SpectraQAgent

This document describes the ComplAI feature integration into SpectraQAgent, a web-based AI agent for crypto trading and event predictions.

## Overview

ComplAI is an AI-powered compliance auditor that checks smart contracts and interchain interactions for regulatory compliance (AML, GDPR, KYC, eERC) before predictions or trades.

## Architecture

### Components

1. **ComplAI MCP Server** (`backend/complai_server/`)
   - Python-based MCP server using FastAPI
   - Uses Gemini API for AI analysis
   - Supports Avalanche C-Chain integration
   - Runs as microservice on port 5000

2. **Agent Service Updates** (`backend/app/services/`)
   - Enhanced agent service with compliance detection
   - LangGraph integration for stateful compliance workflows
   - Automatic compliance audit triggering

3. **Frontend Updates** (`frontend/src/`)
   - ComplianceDisplay component for audit results
   - Enhanced chat interface with compliance badges
   - Interactive fix suggestions

## Setup Instructions

### 1. Environment Setup

Set the required environment variables:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export COMPLAI_PORT="5000"
export AVALANCHE_RPC_URL="https://api.avax.network/ext/bc/C/rpc"
```

### 2. Install Dependencies

For the ComplAI server:

```bash
cd backend
pip install fastapi uvicorn httpx pydantic python-multipart
```

### 3. Start ComplAI Server

```bash
python run_complai.py
```

The server will start on http://localhost:5000

### 4. Update MCP Configuration

The ComplAI server is already configured in `config/mcp_servers.json`:

```json
{
  "complai": {
    "name": "ComplAI Compliance Auditor",
    "description": "AI-powered compliance auditor for smart contracts",
    "url": "http://localhost:5000",
    "status": "active",
    "type": "http"
  }
}
```

### 5. Start Main Backend

```bash
cd backend
python -m app.main
```

### 6. Start Frontend

```bash
cd frontend
npm run dev
```

## Usage

### Basic Compliance Audit

Ask the agent to audit a smart contract:

```
Audit this smart contract for AML and GDPR compliance:

pragma solidity ^0.8.0;

contract SimpleToken {
    mapping(address => uint256) public balances;
    
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount);
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}
```

### Trading with Compliance Check

```
Predict BTC price and audit this trade contract for compliance
```

### Standards Supported

- **AML**: Anti-Money Laundering
- **GDPR**: General Data Protection Regulation
- **KYC**: Know Your Customer
- **eERC**: Enhanced ERC standards for Avalanche

## API Endpoints

### ComplAI Server

- `POST /tools/compliance_audit` - Perform compliance audit
- `GET /health` - Health check
- `GET /tools/list` - List available tools

### Request Format

```json
{
  "contract_code": "pragma solidity ^0.8.0; contract MyContract { ... }",
  "standards": ["AML", "GDPR", "KYC"],
  "contract_address": "0x..."
}
```

### Response Format

```json
{
  "risk_score": 0.3,
  "issues": ["Missing KYC verification", "No data privacy controls"],
  "fixes": ["Add KYC verification function", "Implement data encryption"],
  "standards_checked": ["AML", "GDPR", "KYC"],
  "timestamp": "2025-08-31T12:00:00Z",
  "contract_address": "0x..."
}
```

## Security Features

- **Data Encryption**: HTTPS for MCP server communication
- **Input Validation**: Contract code validation and sanitization
- **Rate Limiting**: Built into FastAPI
- **Audit Logging**: All compliance checks are logged

## LangGraph Integration

The system uses LangGraph for stateful conversation management with compliance:

1. **Query Analysis** → Determine if compliance check needed
2. **Data Gathering** → Fetch market/crypto data
3. **Compliance Check** → Run ComplAI audit
4. **Response Generation** → Generate final response with audit results

## Development Notes

### Adding New Compliance Standards

1. Update the prompt in `complai_server.py`
2. Add standard detection in agent service
3. Update frontend display components

### Customizing Risk Scoring

Modify the `calculate_confidence_score` method in the LangGraph service to include compliance factors.

### Testing

Run the ComplAI server independently:

```bash
python -m pytest backend/complai_server/ -v
```

## Troubleshooting

### Common Issues

1. **Gemini API Key Missing**: Ensure `GEMINI_API_KEY` is set
2. **Port Conflicts**: Change `COMPLAI_PORT` if 5000 is in use
3. **MCP Server Not Found**: Check `config/mcp_servers.json` configuration

### Logs

Check logs for detailed error information:
- ComplAI server logs in terminal
- Backend logs in main application
- Frontend console for UI errors

## Future Enhancements

- Real-time compliance monitoring
- Integration with regulatory APIs
- Multi-chain compliance support
- Automated fix implementation
- Compliance reporting dashboard
