# SpectraQ

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue.svg)](https://www.typescriptlang.org/)
[![Avalanche](https://img.shields.io/badge/Avalanche-Fuji-red.svg)](https://docs.avax.network/)

## 🚀 Overview

SpectraQ is a next-generation prediction markets platform that enables users to trade on the outcomes of real-world events with high accuracy and security. Built on Avalanche blockchain with custom smart contracts, the platform covers predictions on crypto prices, global events, and more, allowing users to make informed decisions and earn real rewards.

The platform features the revolutionary **SpectraQAgent** - an AI-powered assistant that leverages advanced AI capabilities to answer user queries, analyze market data, provide predictions, and facilitate trade executions. This intelligent agent uses distributed AI inference powered by **Comput3.ai**, integrated with the **ElizaOS agent framework** and **Model Context Protocol (MCP)** for accessing external data sources.

SpectraQ operates with its own purpose-built smart contracts deployed on Avalanche, where all trades and market operations are executed directly on-chain, ensuring transparency, security, and decentralized governance.

### ✨ Key Features

- **🤖 AI-Powered Agent**: SpectraQ AI Agent with real-time market analysis using multiple data sources
- **🏗️ Custom Smart Contracts**: Purpose-built contracts for prediction markets with Uniswap V4 integration
- **💱 Automated Market Making**: YES/NO token pools powered by Uniswap V4 for seamless trading
- **🪙 Virtual USD (vUSD)**: Synthetic stable token for liquidity and trading within markets
- **🔗 Oracle Integration**: Reliable event verification and automatic market settlement
- **⚖️ ComplAI Compliance Auditor**: AI-powered compliance checking for smart contracts (AML, GDPR, KYC, eERC)
- **📊 Real-time Market Data**: Live cryptocurrency prices, sentiment analysis, and market indicators
- **🎯 Prediction Markets**: Create and participate in prediction markets on crypto, sports, politics, and tech
- **💰 Avalanche Integration**: Built on Avalanche Fuji testnet with optimized smart contracts
- **📱 Modern UI/UX**: Quantum-themed design with responsive interface and smooth animations
- **🌐 Community Features**: Social prediction communities and collaborative market analysis
- **📈 Portfolio Management**: Track positions, performance, P&L, and transaction history
- **🔮 Market Intelligence**: Fear & Greed Index, news sentiment, and technical analysis

## 🔗 Smart Contracts Overview

SpectraQ operates on a sophisticated smart contract architecture built specifically for prediction markets, leveraging the power of Avalanche blockchain and Uniswap V4 for optimal performance and liquidity.

### Core Contract Components

#### **Market Contract**
- **Purpose**: Core contract where markets are created, managed, and settled
- **Functions**: Market creation, proposal submissions, trading logic, and payout/redemption
- **Security**: Multi-signature governance and time-locked operations
- **Integration**: Direct interface with Uniswap V4 pools and oracle systems

#### **Uniswap V4 Pools**
For every proposal, two main automated market maker (AMM) pools are created:
- **YES/vUSD Pool**: Trading pool for YES-side outcome tokens
- **NO/vUSD Pool**: Trading pool for NO-side outcome tokens
- **Features**: Accept liquidity from anyone, powered by Uniswap V4's advanced AMM logic
- **Benefits**: Deep liquidity, minimal slippage, and fair price discovery

#### **Decision Tokens (YES/NO)**
Each market/proposal issues unique ERC20 tokens:
- **YES Token**: Represents a share in the proposed outcome occurring
- **NO Token**: Represents a share in the outcome not occurring  
- **Mechanics**: Minted/burned based on trading activity and freely tradable
- **Settlement**: Winning tokens redeemable for payouts after market resolution

#### **Virtual USD (vUSD)**
- **Purpose**: Synthetic stable token for liquidity and trading within each market
- **Stability**: Pegged to USD value through algorithmic mechanisms
- **Usage**: Base currency for all market operations and settlements
- **Liquidity**: Backed by collateral reserves and market maker activities

#### **Hooks / SwapHook**
Custom Uniswap V4 hooks add sophisticated logic:
- **Market Resolution**: Automated settlement based on oracle data
- **Fee Management**: Dynamic fee structures based on market conditions
- **Oracle Integration**: Secure price feeds and event outcome verification
- **Outcome Security**: Multi-layer validation for result integrity

#### **Resolver/Oracle**
- **Function**: Verifies real-world event outcomes and triggers correct settlement
- **Security**: Multiple data source validation and dispute resolution mechanism
- **Automation**: Automated settlement once outcome is confirmed
- **Governance**: Community-driven dispute resolution for edge cases

### Pool Creation Flow

#### **1. Market Creation**
```solidity
// User calls createMarket with details
createMarket({
  question: "Will Bitcoin reach $100,000 by end of 2024?",
  asset: "BTC",
  deadline: 1735689600, // Unix timestamp
  category: "cryptocurrency",
  minDeposit: 0.1 ether
})
```

#### **2. Proposal Submission**
- User submits a proposal, triggering deployment of new YES/NO/vUSD tokens
- Uniswap V4 pools for YES/vUSD and NO/vUSD are automatically created
- Initial liquidity from `minDeposit` is seeded automatically to bootstrap trading

#### **3. Liquidity Provision**
- Anyone can add (and remove) liquidity to the pools for earning trading fees
- Pools price YES/NO tokens using standard Uniswap V4 AMM logic
- Liquidity providers earn fees from trading volume and can exit anytime

#### **4. Trading & Resolution**
- Traders buy/sell YES/NO tokens based on their belief or for hedging purposes
- Real-time price discovery through AMM mechanics reflects market sentiment
- After deadline, market is resolved via oracle/hook system
- Winning tokens become redeemable for payouts proportional to their holdings

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Market Contract                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Market Creator │  │  Proposal Logic │  │  Settlement     │ │
│  │  & Manager      │  │  & Validation   │  │  & Payouts      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Uniswap V4 Integration                     │
│  ┌─────────────────┐              │              ┌─────────────┐ │
│  │   YES/vUSD      │◄─────────────┼─────────────►│  NO/vUSD    │ │
│  │   AMM Pool      │              │              │  AMM Pool   │ │
│  │                 │              │              │             │ │
│  │ • Liquidity     │              │              │ • Liquidity │ │
│  │ • Price Discovery│             │              │ • Trading   │ │
│  │ • Fee Collection │              │              │ • Arbitrage │ │
│  └─────────────────┘              │              └─────────────┘ │
└────────────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Oracle & Hook System                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Data Feed     │  │   SwapHook      │  │   Resolver      │ │
│  │   Aggregation   │  │   Logic         │  │   & Settlement  │ │
│  │                 │  │                 │  │                 │ │
│  │ • Price Feeds   │  │ • Fee Logic     │  │ • Event Verify  │ │
│  │ • Event Data    │  │ • Resolution    │  │ • Auto Settle   │ │
│  │ • Multi-Source  │  │ • Security      │  │ • Dispute Res.  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Security & Governance

- **Multi-Signature**: Critical functions require multiple signatures
- **Time Locks**: Important changes have mandatory delay periods
- **Audit Trail**: All operations are logged and verifiable on-chain
- **Upgrade Mechanism**: Secure proxy pattern for contract upgrades
- **Emergency Pause**: Circuit breakers for emergency situations
- **Community Governance**: Token holders vote on key parameters and disputes

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend        │    │   MCP Servers   │
│   React + TS    │◄──►│   FastAPI        │◄──►│   Data Sources  │
│   Web3 + Wagmi  │    │   + AI Agent     │    │   • CoinGecko   │
│                 │    │   + WebSocket    │    │   • CCXT        │
│                 │    │   + PostgreSQL   │    │   • Fear&Greed  │
│                 │    │   + Redis        │    │   • CryptoPanic │
│                 │    │   + LangGraph    │    │   • ComplAI     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Avalanche     │    │   Gemini AI      │    │   External APIs │
│   Smart         │    │   + Comput3.ai   │    │   + Web Crawlers│
│   Contracts     │    │   Processing     │    │   + News Feeds  │
│   + ComplAI     │    │   + Compliance   │    │   + Reg. APIs   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🛡️ ComplAI Compliance Auditor

SpectraQ integrates ComplAI, an AI-powered compliance auditor that checks smart contracts and interchain interactions for regulatory compliance before predictions or trades.

#### Key Features
- **Multi-Standard Support**: AML, GDPR, KYC, eERC compliance checking
- **AI-Powered Analysis**: Uses Google Gemini AI for intelligent contract analysis
- **Avalanche Integration**: On-chain contract data fetching via C-Chain RPC
- **Real-time Auditing**: Automatic compliance checks during agent interactions
- **Interactive Fixes**: Clickable suggestions for compliance improvements

#### Usage Examples
```bash
# Audit a smart contract
"Audit this smart contract for AML and GDPR compliance"

# Compliance-aware trading
"Predict BTC price and audit this trade contract"

# Multi-standard compliance
"Check contract compliance for AML, KYC, and eERC standards"
```

#### Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───►│   Agent Service  │───►│   ComplAI MCP   │
│                 │    │   + LangGraph    │    │   Server        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Compliance    │◄───│   Gemini AI      │◄───│   Avalanche     │
│   Audit Result  │    │   Analysis       │    │   C-Chain RPC   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Backend Architecture (FastAPI + Python)
- **AI Agent Service**: Processes user queries using MCP tools and Gemini AI
- **MCP Integration**: Multiple MCP servers for market data (CoinGecko, CCXT, Fear & Greed Index)
- **ComplAI Integration**: AI-powered compliance auditing for smart contracts
- **LangGraph Workflows**: Stateful conversation management with compliance checks
- **WebSocket Support**: Real-time agent communication and market updates
- **Database Layer**: SQLAlchemy with PostgreSQL/SQLite support
- **Caching**: Redis for session management and data caching
- **API**: RESTful endpoints with automatic OpenAPI documentation

### Frontend Architecture (React + TypeScript)
- **Modern Stack**: Vite, React 18, TypeScript 5.8+, TailwindCSS
- **Web3 Integration**: Wagmi v2, Viem for Avalanche blockchain interaction
- **UI Framework**: Shadcn/ui with Radix UI primitives and custom components
- **State Management**: TanStack Query for server state, Zustand for client state
- **Design System**: Quantum-themed with custom animations, gradients, and glassmorphism

## 📋 Prerequisites

### Backend Requirements
- Python 3.12+ (using uv package manager)
- Redis 5.0+ (for caching and sessions)
- PostgreSQL 13+ (optional, defaults to SQLite for development)
- OpenAI/Gemini API keys for AI functionality

### Frontend Requirements
- Node.js 18+ with npm/bun
- Modern browser with Web3 wallet support (MetaMask, WalletConnect)
- Avalanche Fuji testnet configuration

## 🛠️ Installation & Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/blinderchief/Avalanche_Team1_Hackathon.git
cd Avalanche_Team1_Hackathon
```

### 2. Backend Setup

#### Option A: Using UV (Recommended)
```bash
cd backend

# Install Python dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database configuration

# Initialize database (SQLite for development)
uv run alembic upgrade head

# Start backend server (http://localhost:8000)
uv run python app/main.py
```

#### Option B: Using pip + venv
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Initialize database and start server
python app/main.py
```

### 3. Frontend Setup

#### Option A: Using npm
```bash
cd frontend

# Install dependencies
npm install

# Start development server (http://localhost:8080)
npm run dev
```

#### Option B: Using bun
```bash
cd frontend

# Install dependencies (faster alternative)
bun install

# Start development server
bun run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/redoc

## ⚙️ Configuration

### Backend Environment Variables (.env)
```env
# Core Application Settings
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
RELOAD=true
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=sqlite:///./spectraq.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/spectraq

# Redis Configuration (optional for development)
REDIS_URL=redis://localhost:6379/0

# AI Service API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
COMPUT3_API_KEY=your_comput3_api_key_here

# MCP Server API Keys
COINGECKO_API_KEY=your_coingecko_api_key
CRYPTOPANIC_API_KEY=your_cryptopanic_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Security & CORS
SECRET_KEY=your-ultra-secure-secret-key-here
CORS_ORIGINS=["http://localhost:8080", "http://localhost:3000"]

# Optional: External Service URLs
WEBHOOK_URL=https://your-domain.com/webhooks
METRICS_ENABLED=true
```

### MCP (Model Context Protocol) Configuration
The AI agent integrates with multiple MCP servers for comprehensive market data:

```json
{
  "mcpServers": {
    "coingecko": {
      "description": "Real-time cryptocurrency prices and market data",
      "tools": ["get_coin_price", "get_market_data", "get_trending_coins", "get_coin_history"],
      "status": "available"
    },
    "ccxt": {
      "description": "Exchange data and trading information",
      "tools": ["get_ticker", "get_orderbook", "get_trades", "get_ohlcv"],
      "status": "available"
    },
    "feargreed": {
      "description": "Crypto Fear & Greed Index sentiment analysis",
      "tools": ["get_fear_greed_index", "get_historical_index"],
      "status": "available"
    },
    "cryptopanic": {
      "description": "Cryptocurrency news aggregation and sentiment",
      "tools": ["get_news", "get_posts", "search_news"],
      "status": "available"
    }
  }
}
```

### Smart Contract Configuration (Avalanche Fuji)
```typescript
// frontend/src/lib/contracts.ts
export const CONTRACT_ADDRESSES = {
  MARKET: '0x...', // Main prediction market contract
  BASIC_MARKET_RESOLVER: '0x...', // Market resolution contract
  VUSD: '0x...', // Virtual USD token for betting
  POSITION_MANAGER: '0x...', // Uniswap V4 position manager
  POOL_MANAGER: '0x...', // Uniswap V4 pool manager
} as const;

export const AVALANCHE_FUJI = {
  id: 43113,
  name: 'Avalanche Fuji',
  rpcUrl: 'https://api.avax-test.network/ext/bc/C/rpc',
  blockExplorer: 'https://testnet.snowtrace.io'
};
```

## 🎯 Core Features & Usage

### 1. AI Agent Interaction

The SpectraQ AI Agent provides intelligent market analysis:

```bash
# Example queries the agent can handle:
"What's the current Bitcoin price and market sentiment?"
"Show me the Fear & Greed Index and latest crypto news"
"Compare Ethereum and Bitcoin performance today"
"What factors are driving the current market movement?"
```

**Frontend Integration:**
```javascript
// Real-time agent communication
const response = await fetch('/api/v1/agent/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Analyze Bitcoin's price movement today",
    session_id: sessionId,
    user_id: userId
  })
});

const data = await response.json();
console.log(data.response); // Formatted AI analysis
console.log(data.tools_used); // Data sources used
console.log(data.confidence_score); // Analysis confidence
```

### 2. Prediction Market Creation

Create markets on any verifiable future event:

```javascript
// Smart contract interaction for market creation
const market = await writeContract({
  address: CONTRACT_ADDRESSES.MARKET,
  abi: MARKET_ABI,
  functionName: 'createMarket',
  args: [{
    title: "Will Bitcoin reach $100,000 by end of 2024?",
    description: "Market resolves YES if BTC closes above $100,000 on any major exchange",
    category: "crypto",
    resolver: CONTRACT_ADDRESSES.BASIC_MARKET_RESOLVER,
    endTime: BigInt(Math.floor(new Date('2024-12-31').getTime() / 1000)),
    minDeposit: parseEther("0.1"),
    marketToken: CONTRACT_ADDRESSES.VUSD
  }]
});
```

### 3. Web3 Wallet Integration

Seamless connection to Avalanche network:

```typescript
// Wagmi configuration for multiple wallets
const config = createConfig({
  chains: [avalancheFuji, mainnet, polygon, arbitrum],
  connectors: [
    injected(), // MetaMask, Brave, etc.
    walletConnect({ projectId: 'your-project-id' }),
  ],
  transports: {
    [avalancheFuji.id]: http(),
  },
});
```

### 4. Real-time Market Updates

WebSocket integration for live data:

```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket(`ws://localhost:8000/ws/agent/${sessionId}`);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'market_update') {
    updateMarketData(data.payload);
  } else if (data.type === 'agent_response') {
    displayAgentMessage(data.payload);
  }
};
```

## 🧪 Development Workflow

### Backend Development

```bash
# Run with auto-reload during development
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Run comprehensive tests
uv run pytest tests/ -v --cov=app

# Code formatting and quality
uv run black app/        # Format code
uv run isort app/        # Sort imports  
uv run mypy app/         # Type checking
uv run flake8 app/       # Linting

# Database operations
uv run alembic revision --autogenerate -m "Add new model"
uv run alembic upgrade head
uv run alembic downgrade -1
```

### Frontend Development

```bash
cd frontend

# Development with hot reload
npm run dev

# Code quality checks
npm run lint          # ESLint
npm run lint:fix      # Fix ESLint issues
npm run type-check    # TypeScript checking
npm run format        # Prettier formatting

# Testing
npm run test          # Run tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report

# Build for production
npm run build         # Optimized production build
npm run preview       # Preview production build
```

### Full-Stack Development

```bash
# Terminal 1: Backend
cd backend && uv run python app/main.py

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: Database (if using PostgreSQL)
docker run -d -p 5432:5432 -e POSTGRES_DB=spectraq -e POSTGRES_USER=dev -e POSTGRES_PASSWORD=dev postgres:15

# Terminal 4: Redis (if needed)
docker run -d -p 6379:6379 redis:alpine
```

## 📝 API Documentation

### Core AI Agent Endpoints

#### POST `/api/v1/agent/query`
Process user queries through the AI agent:

```json
// Request
{
  "query": "What's the current market sentiment?",
  "session_id": "session_abc123", 
  "user_id": "user_xyz789",
  "context": {"previous_topic": "bitcoin_analysis"}
}

// Response
{
  "id": "resp_def456",
  "response": "Based on current data, market sentiment is...",
  "session_id": "session_abc123",
  "query_type": "MARKET_ANALYSIS",
  "confidence_score": 0.87,
  "tools_used": [
    {
      "tool_name": "feargreed.get_fear_greed_index",
      "parameters": {},
      "result": {"index": 45, "classification": "Fear"},
      "execution_time_ms": 230
    }
  ],
  "data_sources": [
    {
      "name": "Fear & Greed Index",
      "type": "mcp",
      "last_updated": "2024-01-15T10:30:00Z",
      "reliability_score": 0.9
    }
  ],
  "processing_time_ms": 1450,
  "follow_up_suggestions": [
    "What's driving this fearful sentiment?",
    "How does this compare to last month?",
    "Show me Bitcoin's price reaction"
  ]
}
```

#### WebSocket `/ws/agent/{session_id}`
Real-time bidirectional communication:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/agent/session_123');

// Send message
ws.send(JSON.stringify({
  type: 'query',
  data: {
    query: "Stream Bitcoin analysis",
    stream: true
  }
}));

// Receive streaming response
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'stream_chunk') {
    appendToResponse(message.data.content);
  } else if (message.type === 'stream_complete') {
    finalizaResponse(message.data);
  }
};
```

### Market Data Endpoints

#### GET `/api/v1/market/prices`
Get real-time cryptocurrency prices:

```json
// Response
{
  "data": {
    "BTC": {
      "price_usd": 43250.50,
      "price_change_24h": 2.45,
      "market_cap": 847500000000,
      "volume_24h": 28500000000,
      "last_updated": "2024-01-15T10:30:00Z"
    },
    "ETH": {
      "price_usd": 2650.75,
      "price_change_24h": -1.23,
      "market_cap": 318750000000,
      "volume_24h": 15200000000,
      "last_updated": "2024-01-15T10:30:00Z"
    }
  },
  "source": "coingecko",
  "cache_expires": "2024-01-15T10:35:00Z"
}
```

#### GET `/api/v1/market/sentiment`
Get market sentiment indicators:

```json
// Response
{
  "fear_greed_index": {
    "value": 45,
    "classification": "Fear",
    "trend": "decreasing",
    "last_updated": "2024-01-15T09:00:00Z"
  },
  "news_sentiment": {
    "overall_score": 0.35,
    "positive_articles": 12,
    "negative_articles": 18,
    "neutral_articles": 25,
    "trending_topics": ["regulation", "etf", "halving"]
  }
}
```

## 🌐 Deployment

### Production Environment Setup

#### Backend Deployment (Docker + Cloud)

```dockerfile
# Dockerfile for backend
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml for full stack
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/spectraq
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    
  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend
    
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=spectraq
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Frontend Deployment (Static Hosting)

```dockerfile
# Multi-stage build for frontend
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf for SPA routing
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Handle SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Deployment Platforms

#### Option 1: Vercel + Railway
```bash
# Frontend to Vercel
cd frontend
vercel --prod

# Backend to Railway
cd backend
railway login
railway init
railway deploy
```

#### Option 2: AWS/GCP/Azure
```bash
# Build and push to container registry
docker build -t spectraq-backend ./backend
docker tag spectraq-backend:latest your-registry/spectraq-backend:latest  
docker push your-registry/spectraq-backend:latest

# Deploy using cloud-specific tools (ECS, Cloud Run, Container Apps)
```

#### Option 3: Self-Hosted VPS
```bash
# Clone and setup on server
git clone https://github.com/blinderchief/Avalanche_Team1_Hackathon.git
cd Avalanche_Team1_Hackathon

# Setup with Docker Compose
docker-compose up -d --build

# Or setup with process manager
sudo systemctl enable spectraq-backend
sudo systemctl start spectraq-backend
```

### Environment-Specific Configurations

| Environment | Database | Cache | Logging | AI Provider |
|-------------|----------|-------|---------|-------------|
| **Development** | SQLite | In-memory | DEBUG | Local/Mock |
| **Staging** | PostgreSQL | Redis | INFO | Gemini API |
| **Production** | RDS/CloudSQL | ElastiCache | WARN | Comput3.ai |

## 🔧 Technology Deep Dive

### Backend Stack Details

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Web Framework** | FastAPI | 0.104+ | High-performance async API |
| **Language** | Python | 3.12+ | Modern Python with type hints |
| **Database ORM** | SQLAlchemy | 2.0+ | Async database operations |
| **Migrations** | Alembic | 1.13+ | Database schema versioning |
| **Caching** | Redis | 5.0+ | Session storage and caching |
| **WebSockets** | FastAPI WebSocket | Latest | Real-time communication |
| **AI Integration** | OpenAI/Gemini | Latest | Language model processing |
| **MCP Protocol** | MCP Python SDK | 0.4+ | Data source integration |
| **Task Queue** | Celery | 5.3+ | Background task processing |
| **Monitoring** | Prometheus | Latest | Metrics and monitoring |

### Frontend Stack Details

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 18.3+ | Modern React with Hooks |
| **Language** | TypeScript | 5.8+ | Type-safe JavaScript |
| **Build Tool** | Vite | 5.4+ | Fast dev server and bundler |
| **Styling** | TailwindCSS | 3.4+ | Utility-first CSS framework |
| **UI Components** | Shadcn/ui | Latest | Accessible component library |
| **Web3** | Wagmi | 2.16+ | React hooks for Ethereum |
| **Ethereum Client** | Viem | 2.34+ | TypeScript Ethereum client |
| **State Management** | TanStack Query | 5.85+ | Server state management |
| **Routing** | React Router | 6.30+ | Client-side routing |
| **Animations** | Framer Motion | 12.23+ | Smooth animations |
| **Form Handling** | React Hook Form | 7.62+ | Performant forms |
| **Icons** | Heroicons | 2.2+ | Beautiful SVG icons |

### Blockchain Integration

| Component | Details | Network |
|-----------|---------|---------|
| **Primary Chain** | Avalanche Fuji Testnet | Chain ID: 43113 |
| **RPC Endpoint** | https://api.avax-test.network/ext/bc/C/rpc | Official |
| **Block Explorer** | https://testnet.snowtrace.io | Snowtrace |
| **Wallet Support** | MetaMask, WalletConnect, Coinbase | Universal |
| **Token Standard** | ERC-20 for market tokens | VUSD, YES/NO |
| **DEX Integration** | Uniswap V4 on Avalanche | Liquidity pools |

## 🔒 Security Considerations

### Backend Security
- **API Rate Limiting**: Per-user and per-endpoint limits
- **Input Validation**: Pydantic schemas for all inputs
- **Authentication**: JWT tokens with refresh mechanism  
- **Database Security**: SQL injection prevention, encrypted connections
- **Environment Variables**: Secure secret management
- **CORS Configuration**: Restricted origin policy

### Frontend Security  
- **CSP Headers**: Content Security Policy implementation
- **XSS Prevention**: Sanitized user inputs and outputs
- **CSRF Protection**: Anti-CSRF tokens for state changes
- **Web3 Security**: Secure wallet connection, transaction validation
- **Environment Variables**: Public vs private variable separation

### Smart Contract Security
- **Reentrancy Protection**: ReentrancyGuard implementation
- **Access Control**: Role-based permissions
- **Oracle Security**: Reliable price feeds and data sources
- **Upgrade Patterns**: Proxy contracts for upgradeability
- **Testing**: Comprehensive test coverage including edge cases

## 🧪 Testing Strategy

### Backend Testing
```bash
# Unit tests
uv run pytest tests/unit/ -v

# Integration tests  
uv run pytest tests/integration/ -v

# E2E tests
uv run pytest tests/e2e/ -v

# Load testing
uv run locust -f tests/load/locustfile.py

# Security testing
uv run bandit -r app/
uv run safety check
```

### Frontend Testing
```bash
# Unit tests (Jest + Testing Library)
npm run test

# Component tests (Storybook)
npm run storybook

# E2E tests (Playwright)
npm run test:e2e

# Visual regression tests
npm run test:visual

# Accessibility tests
npm run test:a11y
```

### Smart Contract Testing
```bash
# Foundry tests
forge test -vvv

# Gas optimization
forge test --gas-report

# Fuzzing tests
forge test --fuzz-runs 10000

# Coverage report
forge coverage
```

## 📊 Performance Optimization

### Backend Optimization
- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: SQLAlchemy async connection pools
- **Caching Strategy**: Redis for frequently accessed data
- **Background Tasks**: Celery for heavy computations
- **Response Compression**: Gzip middleware for API responses
- **Query Optimization**: Efficient database queries with minimal N+1

### Frontend Optimization
- **Code Splitting**: Dynamic imports for route-based splitting
- **Bundle Analysis**: Optimized chunk sizes with Rollup
- **Image Optimization**: WebP format with lazy loading
- **Caching Strategy**: Service worker for offline functionality
- **Tree Shaking**: Unused code elimination
- **Preloading**: Critical resource preloading

### Blockchain Optimization
- **Gas Optimization**: Efficient smart contract functions
- **Batch Operations**: Multiple operations in single transaction
- **State Management**: Minimal on-chain storage
- **Event Indexing**: Efficient event filtering and querying

## 🐛 Common Issues & Troubleshooting

### Backend Issues

#### MCP Server Connection Problems
```bash
# Check MCP server status
curl http://localhost:8000/api/v1/health/mcp

# Debug MCP configuration
uv run python -m app.services.mcp_manager --test

# Common fixes:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uv run pip install --upgrade mcp
```

#### Database Connection Issues
```bash
# SQLite permissions
chmod 664 spectraq.db

# PostgreSQL connection
pg_isready -h localhost -p 5432

# Migration issues
uv run alembic stamp head
uv run alembic revision --autogenerate -m "Fix schema"
```

#### Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping

# Check Redis logs
redis-cli monitor

# Alternative: Use in-memory storage
export REDIS_URL=""  # Falls back to in-memory
```

### Frontend Issues

#### Build/Compilation Errors
```bash
# Clear caches and reinstall
rm -rf node_modules package-lock.json .vite
npm install

# TypeScript errors
npm run type-check
npx tsc --noEmit

# ESLint issues
npm run lint:fix
```

#### Web3 Connection Issues
```bash
# Check network configuration
console.log(window.ethereum.networkVersion)

# Switch to Avalanche Fuji
await window.ethereum.request({
  method: 'wallet_switchEthereumChain',
  params: [{ chainId: '0xA869' }], // 43113 in hex
});

# Add Avalanche network
await window.ethereum.request({
  method: 'wallet_addEthereumChain',
  params: [{
    chainId: '0xA869',
    chainName: 'Avalanche Fuji Testnet',
    nativeCurrency: { name: 'AVAX', symbol: 'AVAX', decimals: 18 },
    rpcUrls: ['https://api.avax-test.network/ext/bc/C/rpc'],
    blockExplorerUrls: ['https://testnet.snowtrace.io/']
  }]
});
```

#### Performance Issues
```bash
# Bundle analysis
npm run build -- --analyze

# Memory leaks
npm run dev -- --profile

# Lighthouse audit
lighthouse http://localhost:8080 --output=html
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'app'` | PYTHONPATH not set | `export PYTHONPATH="${PYTHONPATH}:$(pwd)"` |
| `Connection refused on port 5432` | PostgreSQL not running | Start PostgreSQL or use SQLite |
| `WebSocket connection failed` | CORS/Network issue | Check backend CORS settings |
| `Transaction reverted` | Smart contract error | Check gas limit and contract state |
| `Chunk load error` | Build cache issue | Clear .vite cache and rebuild |

## 🤝 Contributing

We welcome contributions to SpectraQ! Here's how to get involved:

### Development Process

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/your-username/Avalanche_Team1_Hackathon.git`
3. **Create** feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes following our coding standards
5. **Test** your changes thoroughly
6. **Commit** with conventional commits: `git commit -m 'feat: add amazing feature'`
7. **Push** to your branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request with detailed description

### Coding Standards

#### Backend (Python)
- Follow **PEP 8** style guidelines
- Use **type hints** for all function parameters and returns
- Write **docstrings** for all public functions and classes
- Maintain **90%+ test coverage** for new features
- Use **async/await** for I/O operations

```python
# Example: Good function with type hints and docstring
async def get_market_sentiment(
    symbol: str,
    timeframe: str = "24h"
) -> Dict[str, Any]:
    """
    Retrieve market sentiment for a given cryptocurrency symbol.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        timeframe: Analysis timeframe ('24h', '7d', '30d')
    
    Returns:
        Dictionary containing sentiment score and related metrics
        
    Raises:
        ValueError: If symbol is not supported
        APIError: If external API call fails
    """
    # Implementation here
```

#### Frontend (TypeScript/React)
- Use **ESLint** and **Prettier** configurations
- Follow **React best practices** (hooks, functional components)
- Write **TypeScript interfaces** for all data structures
- Use **semantic HTML** and ensure accessibility
- Implement **proper error boundaries**

```typescript
// Example: Well-typed React component
interface MarketCardProps {
  market: {
    id: string;
    title: string;
    price: number;
    change24h: number;
  };
  onSelect: (marketId: string) => void;
}

export const MarketCard: React.FC<MarketCardProps> = ({ 
  market, 
  onSelect 
}) => {
  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-shadow"
      onClick={() => onSelect(market.id)}
    >
      <CardContent>
        <h3 className="font-semibold">{market.title}</h3>
        <div className={`text-sm ${market.change24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {market.change24h >= 0 ? '↗' : '↘'} {Math.abs(market.change24h).toFixed(2)}%
        </div>
      </CardContent>
    </Card>
  );
};
```

### Areas for Contribution

- 🤖 **AI Agent**: Enhance query understanding and response generation
- 📊 **Data Sources**: Add new MCP servers and market data providers  
- 🎨 **UI/UX**: Improve design, accessibility, and user experience
- ⛓️ **Smart Contracts**: Optimize gas usage and add new market types
- 🧪 **Testing**: Increase test coverage and add integration tests
- 📚 **Documentation**: Improve API docs and user guides
- 🔧 **DevOps**: Enhance deployment and monitoring setup

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(agent): add real-time streaming responses
fix(ui): resolve mobile layout issues on markets page  
docs(api): update authentication endpoint documentation
refactor(database): optimize query performance for large datasets
test(frontend): add integration tests for wallet connection
chore(deps): update dependencies to latest versions
```

## 🎯 Roadmap & Future Plans

### Phase 1: Foundation (Current)
- ✅ Core AI agent with MCP integration
- ✅ Basic prediction market functionality
- ✅ Avalanche Fuji testnet deployment
- ✅ Modern React frontend with Web3 integration

### Phase 2: Enhancement (Q1 2024)
- 🔄 Advanced market types (multi-outcome, conditional)
- 🔄 Mobile app development (React Native)
- 🔄 Social features (following, leaderboards)
- 🔄 Advanced analytics and reporting

### Phase 3: Scale (Q2 2024)
- ⏳ Mainnet deployment on Avalanche C-Chain
- ⏳ Institutional API access
- ⏳ Cross-chain market integration
- ⏳ Advanced AI models and predictions

### Phase 4: Ecosystem (Q3-Q4 2024)
- ⏳ Third-party developer API
- ⏳ Market maker integration
- ⏳ Governance token and DAO structure
- ⏳ Educational content and tutorials

## 🙏 Acknowledgments & Credits

### Core Technologies
- **[Avalanche](https://www.avax.network/)** - High-performance blockchain platform
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[React](https://reactjs.org/)** - UI library for building user interfaces
- **[Wagmi](https://wagmi.sh/)** - React hooks for Ethereum development
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Shadcn/ui](https://ui.shadcn.com/)** - Beautiful and accessible component library

### AI & Data Providers
- **[OpenAI](https://openai.com/)** - GPT models for natural language processing
- **[Google Gemini](https://deepmind.google/technologies/gemini/)** - Advanced AI capabilities
- **[Comput3.ai](https://comput3.ai/)** - Distributed AI inference platform
- **[CoinGecko](https://www.coingecko.com/)** - Cryptocurrency data API
- **[CryptoPanic](https://cryptopanic.com/)** - Crypto news aggregation

### Development Tools
- **[Vite](https://vitejs.dev/)** - Fast build tool and development server
- **[TypeScript](https://www.typescriptlang.org/)** - Typed superset of JavaScript
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit and ORM
- **[Redis](https://redis.io/)** - In-memory data structure store
- **[Radix UI](https://www.radix-ui.com/)** - Low-level UI primitives

### Special Thanks
- **Avalanche Foundation** for hosting this hackathon
- **Open Source Community** for providing amazing tools and libraries
- **Contributors** who help improve the platform
- **Early Users** providing valuable feedback

---

<div align="center">

### 🌟 Built with passion for Avalanche Hackathon 2024 🌟

**SpectraQ Team** | **Prediction Markets Reimagined with AI**

[![GitHub stars](https://img.shields.io/github/stars/blinderchief/Avalanche_Team1_Hackathon?style=social)](https://github.com/blinderchief/Avalanche_Team1_Hackathon/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/blinderchief/Avalanche_Team1_Hackathon?style=social)](https://github.com/blinderchief/Avalanche_Team1_Hackathon/network/members)
[![GitHub issues](https://img.shields.io/github/issues/blinderchief/Avalanche_Team1_Hackathon)](https://github.com/blinderchief/Avalanche_Team1_Hackathon/issues)

*Made with ❤️ and ☕ by the SpectraQ development team*

</div>
