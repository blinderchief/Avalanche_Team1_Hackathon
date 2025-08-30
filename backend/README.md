# SpectraQ Agent Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-0.4+-purple.svg)](https://modelcontextprotocol.io/)

A high-performance FastAPI backend powering the SpectraQ AI Agent with advanced MCP (Model Context Protocol) integration, real-time market data processing, and intelligent prediction market analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- UV package manager (recommended) or pip
- Redis (optional, for production caching)
- PostgreSQL (optional, defaults to SQLite)

### Installation

```bash
# Using UV (recommended)
uv sync

# Using pip + venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
uv run alembic upgrade head

# Start development server
uv run python app/main.py
```

**Server will be available at**: http://localhost:8000
**API Documentation**: http://localhost:8000/docs

## 🔧 Features

### Core Capabilities
- 🤖 **AI Agent Integration**: Advanced query processing with Gemini AI and Comput3.ai
- 📊 **Multi-Source Data**: Real-time market data from CoinGecko, CCXT, Fear & Greed Index  
- 💬 **Real-time Communication**: WebSocket support for streaming responses
- 🔗 **MCP Protocol**: Extensible data source integration via Model Context Protocol
- 📈 **Market Analysis**: Sophisticated cryptocurrency and sentiment analysis
- 🗄️ **Database Management**: SQLAlchemy with async support and migrations
- ⚡ **High Performance**: Async/await throughout, Redis caching, optimized queries

### AI Agent Capabilities
- **Price Analysis**: Real-time cryptocurrency price tracking and analysis
- **Sentiment Analysis**: Market sentiment using Fear & Greed Index
- **News Integration**: Latest crypto news with sentiment scoring  
- **Technical Analysis**: Chart patterns and trading indicators
- **Market Intelligence**: Cross-asset correlation and trend analysis
- **Personalized Insights**: Context-aware responses based on user history

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/v1/                 # API endpoint definitions
│   │   ├── agent.py           # AI agent endpoints (/query, /session)
│   │   ├── chat.py            # Chat and streaming endpoints
│   │   └── context.py         # Context management endpoints
│   ├── core/                   # Core configuration and utilities
│   │   ├── config.py          # Application settings and environment
│   │   ├── database.py        # Database configuration and connection
│   │   ├── redis_client.py    # Redis client setup
│   │   └── exceptions.py      # Custom exception classes
│   ├── models/                 # Database models (SQLAlchemy)
│   │   ├── agent.py           # Agent and conversation models
│   │   ├── session.py         # Session management models
│   │   ├── user.py            # User and authentication models
│   │   └── models_mvp.py      # Simplified MVP models
│   ├── schemas/                # Pydantic models for API
│   │   ├── agent.py           # Agent request/response schemas
│   │   ├── chat.py            # Chat message schemas
│   │   └── context.py         # Context management schemas
│   ├── services/               # Business logic and external integrations
│   │   ├── agent_service.py   # Full agent service with AI processing
│   │   ├── agent_service_mvp.py # Simplified MVP agent service
│   │   ├── gemini_client.py   # Google Gemini AI client
│   │   ├── mcp_manager.py     # MCP server management and tool calling
│   │   ├── mcp_manager_mvp.py # Simplified MCP manager for MVP
│   │   └── websocket_manager.py # WebSocket connection management
│   └── middleware/             # Custom middleware
│       ├── logging.py         # Request/response logging
│       └── rate_limiting.py   # API rate limiting
├── config/
│   └── mcp_servers.json       # MCP server configurations
├── tests/                      # Test files and fixtures
├── migrations/                 # Database migration files
├── pyproject.toml             # Python project configuration
├── uv.lock                    # Dependency lock file
└── run_dev.py                 # Development server runner
```

## 🔌 API Endpoints

### AI Agent API

#### POST `/api/v1/agent/query`
Process user queries through the AI agent:

```python
# Request
{
    "query": "What's Bitcoin's price and market sentiment?",
    "session_id": "session_abc123",  # Optional
    "user_id": "user_xyz",           # Optional  
    "context": {"topic": "crypto"}   # Optional
}

# Response
{
    "id": "resp_def456",
    "response": "📊 **Bitcoin Analysis Report**\n\n**Current Price:** $43,250.50\n**24h Change:** +2.45% 📈\n**Market Sentiment:** Fear (Index: 45)\n\n**Analysis:** Bitcoin is showing moderate bullish momentum...",
    "session_id": "session_abc123",
    "query_type": "PRICE_PREDICTION",
    "confidence_score": 0.87,
    "tools_used": [
        {
            "tool_name": "coingecko.get_coin_price",
            "parameters": {"symbol": "BTC"},
            "result": {"price_usd": 43250.50, "price_change_24h": 2.45},
            "execution_time_ms": 150,
            "error": null
        }
    ],
    "data_sources": [
        {
            "name": "CoinGecko",
            "type": "mcp", 
            "last_updated": "2024-01-15T10:30:00Z",
            "reliability_score": 0.95
        }
    ],
    "processing_time_ms": 1250,
    "follow_up_suggestions": [
        "What factors are driving this price movement?",
        "How does this compare to Ethereum?",
        "Show me technical analysis"
    ]
}
```

#### POST `/api/v1/agent/session`
Create new agent session:

```python
# Request
{
    "user_id": "user_123",     # Optional
    "initial_context": {}      # Optional
}

# Response  
{
    "session_id": "session_abc123",
    "status": "active",
    "created_at": "2024-01-15T10:00:00Z",
    "message_count": 0
}
```

#### GET `/api/v1/agent/session/{session_id}`
Retrieve session details and history:

```python
# Response
{
    "session_id": "session_abc123",
    "user_id": "user_123",
    "status": "active", 
    "created_at": "2024-01-15T10:00:00Z",
    "last_activity": "2024-01-15T10:15:00Z",
    "message_count": 5,
    "context": {
        "history": [
            {
                "query": "Bitcoin price?",
                "response": "Bitcoin is currently $43,250...",
                "timestamp": "2024-01-15T10:05:00Z",
                "tools_used": ["coingecko.get_coin_price"]
            }
        ]
    }
}
```

### WebSocket API

#### WS `/ws/agent/{session_id}`
Real-time bidirectional communication:

```python
# Client -> Server
{
    "type": "query",
    "data": {
        "query": "Stream Bitcoin analysis",
        "stream": true,
        "format": "markdown"
    }
}

# Server -> Client (streaming chunks)
{
    "type": "stream_chunk", 
    "data": {
        "content": "📊 **Bitcoin Analysis**\n\nCurrent price: $43,250",
        "chunk_id": 1,
        "is_final": false
    }
}

# Server -> Client (completion)
{
    "type": "stream_complete",
    "data": {
        "response_id": "resp_123",
        "tools_used": [...],
        "processing_time_ms": 2100,
        "confidence_score": 0.89
    }
}
```

### Market Data API

#### GET `/api/v1/market/prices?symbols=BTC,ETH,ADA`
Get cryptocurrency prices:

```python
# Response
{
    "data": {
        "BTC": {
            "price_usd": 43250.50,
            "price_change_24h": 2.45,
            "price_change_7d": -1.23,
            "market_cap": 847500000000,
            "volume_24h": 28500000000,
            "circulating_supply": 19800000
        }
    },
    "source": "coingecko",
    "last_updated": "2024-01-15T10:30:00Z",
    "cache_expires": "2024-01-15T10:35:00Z"
}
```

#### GET `/api/v1/market/sentiment`
Get market sentiment indicators:

```python
# Response
{
    "fear_greed_index": {
        "value": 45,
        "classification": "Fear",
        "trend": "decreasing",
        "previous_value": 52,
        "change": -7
    },
    "news_sentiment": {
        "overall_score": 0.35,
        "positive_ratio": 0.25,
        "negative_ratio": 0.35,
        "neutral_ratio": 0.40,
        "trending_topics": ["regulation", "etf", "halving"]
    },
    "social_sentiment": {
        "twitter_sentiment": 0.42,
        "reddit_sentiment": 0.38,
        "trending_coins": ["BTC", "ETH", "SOL"]
    }
}
```

## 🛠️ Development

### Environment Setup

#### Required Environment Variables
```env
# Core Settings
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
RELOAD=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./spectraq.db
# Production: DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# AI Services
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  
COMPUT3_API_KEY=your_comput3_api_key_here

# MCP Server API Keys
COINGECKO_API_KEY=demo_key_for_testing
CRYPTOPANIC_API_KEY=your_cryptopanic_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Security
SECRET_KEY=your-super-secret-key-for-jwt-signing
CORS_ORIGINS=["http://localhost:8080", "http://localhost:3000"]
```

### Development Commands

```bash
# Start development server with auto-reload
uv run python run_dev.py

# Alternative: Direct uvicorn
uv run uvicorn app.main:app --reload --port 8000

# Run tests
uv run pytest                    # All tests
uv run pytest tests/unit/       # Unit tests only
uv run pytest tests/integration/ # Integration tests only
uv run pytest --cov=app        # With coverage

# Code quality
uv run black app/               # Format code
uv run isort app/               # Sort imports
uv run mypy app/                # Type checking
uv run flake8 app/              # Linting

# Database operations
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head     # Apply migrations
uv run alembic downgrade -1     # Rollback one migration
uv run alembic current          # Show current revision
```

### Testing MCP Integration

```bash
# Test individual MCP servers
uv run python -c "
from app.services.mcp_manager_mvp import MCPManagerMVP
import asyncio

async def test():
    manager = MCPManagerMVP()
    result = await manager.call_tool('coingecko', 'get_coin_price', {'symbol': 'BTC'})
    print(result)

asyncio.run(test())
"

# Test agent service
uv run python -c "
from app.services.agent_service_mvp import AgentServiceMVP
from app.services.mcp_manager_mvp import MCPManagerMVP
import asyncio

async def test():
    mcp = MCPManagerMVP()
    agent = AgentServiceMVP(mcp)
    response = await agent.process_query('Bitcoin price?')
    print(response.response)

asyncio.run(test())
"
```

## 🔧 Configuration Details

### MCP Server Configuration

The backend integrates with multiple MCP servers defined in `config/mcp_servers.json`:

```json
{
  "mcpServers": {
    "coingecko": {
      "url": "https://api.coingecko.com/api/v3",
      "type": "http",
      "description": "CoinGecko market data and cryptocurrency information",
      "tools": [
        "get_coin_price",     // Get current price for any cryptocurrency
        "get_market_data",    // Get overall market statistics
        "get_trending_coins", // Get trending cryptocurrencies
        "get_coin_history"    // Get historical price data
      ],
      "rate_limit": "100/minute",
      "timeout": "10s",
      "status": "available"
    },
    "ccxt": {
      "command": "npx",
      "args": ["-y", "@nayshins/mcp-server-ccxt"],
      "type": "process", 
      "description": "CCXT exchange data and trading information",
      "tools": [
        "get_ticker",         // Get ticker data from exchanges
        "get_orderbook",      // Get order book depth
        "get_trades",         // Get recent trades
        "get_ohlcv"          // Get OHLCV candlestick data
      ],
      "status": "available"
    },
    "feargreed": {
      "command": "uv",
      "args": ["--directory", "/path/to/crypto-feargreed-mcp", "run", "main.py"],
      "type": "process",
      "description": "Crypto Fear & Greed Index sentiment indicator", 
      "tools": [
        "get_fear_greed_index",    // Current F&G index
        "get_historical_index"     // Historical F&G data
      ],
      "status": "available"
    },
    "cryptopanic": {
      "command": "uv",
      "args": ["--directory", "/path/to/cryptopanic-mcp-server", "run", "main.py"],
      "type": "process",
      "env": {
        "CRYPTOPANIC_API_PLAN": "free",
        "CRYPTOPANIC_API_KEY": "YOUR_API_KEY"
      },
      "description": "Cryptocurrency news aggregation and sentiment analysis",
      "tools": [
        "get_news",              // Latest crypto news
        "get_posts",             // Social media posts
        "search_news"            // Search specific news topics
      ],
      "status": "available"
    }
  },
  "toolCategories": {
    "market_data": ["coingecko", "ccxt"],
    "sentiment": ["feargreed", "cryptopanic"],  
    "web_crawling": ["firecrawl"]
  },
  "defaultTools": ["coingecko", "feargreed"],
  "retryConfig": {
    "maxRetries": 3,
    "retryDelayMs": 1000,
    "timeoutMs": 30000
  }
}
```

### Database Models

#### Session Management
```python
# app/models/models_mvp.py
class SessionMVP(Base):
    """Agent session tracking"""
    __tablename__ = "sessions_mvp"
    
    id = Column(String, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
    config = Column(JSON)                    # Session configuration
    context_data = Column(JSON)              # Conversation context
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### Query Logging
```python
class QueryLogMVP(Base):
    """Query analytics and logging"""
    __tablename__ = "query_logs_mvp"
    
    id = Column(String, primary_key=True)
    session_id = Column(String(255))
    user_id = Column(String(255))
    query_text = Column(Text, nullable=False)
    response_length = Column(Integer)
    query_type = Column(String(100))         # PRICE_PREDICTION, MARKET_ANALYSIS, etc.
    processing_time_ms = Column(Integer)
    tools_used = Column(JSON)                # List of MCP tools called
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Agent Service Architecture

The agent service processes queries through multiple stages:

```python
# Query Processing Pipeline
class AgentServiceMVP:
    async def process_query(self, query: str) -> AgentQueryResponse:
        # 1. Query Analysis - Determine intent and required tools
        analysis = await self._analyze_query(query)
        
        # 2. Tool Execution - Call relevant MCP servers
        tool_results = {}
        for tool_info in analysis["tools"]:
            result = await self.mcp_manager.call_tool(
                tool_info["server"], 
                tool_info["tool"],
                tool_info["parameters"]
            )
            tool_results[tool_info["tool"]] = result
        
        # 3. Response Generation - Create intelligent response
        response = await self._generate_response(query, tool_results)
        
        # 4. Confidence Scoring - Calculate response reliability
        confidence = self._calculate_confidence(tools_used, query_type)
        
        return AgentQueryResponse(
            response=response,
            confidence_score=confidence,
            tools_used=tools_used,
            processing_time_ms=processing_time
        )
```

## 🧪 Testing & Quality Assurance

### Running Tests

```bash
# Unit tests - Fast, isolated tests
uv run pytest tests/unit/ -v

# Integration tests - Test MCP integration
uv run pytest tests/integration/ -v  

# End-to-end tests - Full workflow tests
uv run pytest tests/e2e/ -v

# Performance tests - Load and stress testing
uv run pytest tests/performance/ -v

# Test with coverage report
uv run pytest --cov=app --cov-report=html --cov-report=term-missing

# Test specific modules
uv run pytest tests/unit/test_agent_service.py -v
uv run pytest tests/integration/test_mcp_integration.py -v
```

### Code Quality Tools

```bash
# Formatting
uv run black app/ tests/                    # Format Python code
uv run isort app/ tests/                    # Sort imports

# Type checking  
uv run mypy app/                            # Static type analysis
uv run mypy --strict app/                   # Strict mode

# Linting
uv run flake8 app/ tests/                   # Style and error checking
uv run pylint app/                          # Advanced linting

# Security scanning
uv run bandit -r app/                       # Security vulnerability scan
uv run safety check                         # Dependency security check
```

### Performance Monitoring

```bash
# Profile API endpoints
uv run python -m cProfile -o profile.stats app/main.py

# Memory usage analysis
uv run py-spy record -o profile.svg -- python app/main.py

# Database query analysis
uv run python -c "
from app.core.database import engine
from sqlalchemy import text
import asyncio

async def analyze():
    async with engine.begin() as conn:
        result = await conn.execute(text('EXPLAIN ANALYZE SELECT * FROM sessions_mvp'))
        print(result.fetchall())

asyncio.run(analyze())
"
```

## 🚀 Deployment & Production

### Production Configuration

#### Environment Variables for Production
```env
# Production settings
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
RELOAD=false
LOG_LEVEL=WARNING

# Production database with connection pooling
DATABASE_URL=postgresql://username:password@prod-db-host:5432/spectraq_prod?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Production Redis cluster
REDIS_URL=redis://prod-redis-host:6379/0
REDIS_POOL_SIZE=10

# Production AI APIs
GEMINI_API_KEY=prod_gemini_key_here
COMPUT3_API_KEY=prod_comput3_key_here

# Security settings
SECRET_KEY=ultra-secure-production-secret-key-min-32-chars
CORS_ORIGINS=["https://spectraq.io", "https://app.spectraq.io"]
ALLOWED_HOSTS=["api.spectraq.io", "backend.spectraq.io"]

# Monitoring and logging
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
LOGURU_LEVEL=INFO
METRICS_ENABLED=true
PROMETHEUS_PORT=9090
```

#### Docker Production Setup
```dockerfile
# Optimized production Dockerfile
FROM python:3.12-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy dependencies and application
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

# Set ownership and permissions
RUN chown -R app:app /app
USER app

# Environment setup
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application with production settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Monitoring & Observability

#### Application Metrics
```python
# Prometheus metrics integration
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('api_request_duration_seconds', 'Request latency')
ACTIVE_SESSIONS = Gauge('agent_active_sessions', 'Number of active agent sessions')
MCP_TOOL_CALLS = Counter('mcp_tool_calls_total', 'MCP tool calls', ['server', 'tool', 'status'])

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

#### Structured Logging
```python
# app/core/logging.py
import structlog

logger = structlog.get_logger()

# Usage in services
logger.info(
    "Agent query processed",
    session_id=session_id,
    query_type=query_type,
    processing_time_ms=processing_time,
    tools_used=len(tools_used),
    confidence_score=confidence_score
)
```

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. MCP Server Connection Failures
```bash
# Symptoms: Tools returning None or timeout errors
# Check MCP server status
curl http://localhost:8000/api/v1/health/mcp

# Debug specific server
uv run python -c "
from app.services.mcp_manager_mvp import MCPManagerMVP
import asyncio
manager = MCPManagerMVP()
asyncio.run(manager.test_server('coingecko'))
"

# Common fixes:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uv sync --force                           # Reinstall dependencies
```

#### 2. Database Connection Issues
```bash
# SQLite permission issues
chmod 664 spectraq.db
chown $(whoami):$(whoami) spectraq.db

# PostgreSQL connection testing
psql -h localhost -p 5432 -U username -d spectraq -c "SELECT 1;"

# Migration conflicts
uv run alembic stamp head                 # Force current revision
uv run alembic revision --autogenerate    # Generate new migration
```

#### 3. Redis Connection Problems
```bash
# Test Redis connectivity
redis-cli ping
redis-cli info server

# Check Redis logs
redis-cli monitor

# Fallback to in-memory (development only)
export REDIS_URL=""  # Application will use in-memory storage
```

#### 4. API Performance Issues  
```bash
# Enable query logging
export DATABASE_ECHO=true

# Profile slow endpoints
uv run python -m cProfile -o profile.stats -m uvicorn app.main:app

# Analyze profile
uv run python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"

# Database query optimization
uv run python -c "
from sqlalchemy import text
from app.core.database import engine
# Add EXPLAIN ANALYZE to slow queries
"
```

### Error Code Reference

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `AGT001` | MCP server unavailable | Check MCP server configuration and network |
| `AGT002` | Query processing timeout | Increase timeout or optimize query |
| `AGT003` | Invalid session ID | Create new session or check session status |
| `AGT004` | AI model rate limit exceeded | Implement request queuing or upgrade plan |
| `DB001` | Database connection failed | Check DATABASE_URL and database status |
| `RDS001` | Redis connection failed | Check REDIS_URL or disable Redis caching |
| `WS001` | WebSocket authentication failed | Verify session ID and authentication |

### Performance Tuning

#### Database Optimization
```python
# Connection pool tuning
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Query optimization
# Use indexes for frequently queried columns
session_id_idx = Index('idx_session_id', SessionMVP.session_id)
created_at_idx = Index('idx_created_at', QueryLogMVP.created_at)

# Async query patterns
async def get_recent_queries(session_id: str, limit: int = 10):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(QueryLogMVP)
            .where(QueryLogMVP.session_id == session_id)
            .order_by(QueryLogMVP.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
```

#### Redis Caching Strategy
```python
# app/core/redis_client.py
import json
from typing import Optional, Any

class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def cache_market_data(self, symbol: str, data: dict, ttl: int = 300):
        """Cache market data with 5-minute TTL"""
        key = f"market:{symbol}"
        await self.redis.setex(key, ttl, json.dumps(data))
    
    async def get_cached_data(self, symbol: str) -> Optional[dict]:
        """Retrieve cached market data"""
        key = f"market:{symbol}"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None
```

## 📚 API Examples & Integrations

### Frontend Integration Examples

#### Agent Query Integration
```typescript
// React hook for agent queries
import { useState, useCallback } from 'react';

interface UseAgentQueryReturn {
  query: (question: string) => Promise<void>;
  response: string | null;
  isLoading: boolean;
  error: Error | null;
  confidence: number;
}

export const useAgentQuery = (sessionId: string): UseAgentQueryReturn => {
  const [response, setResponse] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [confidence, setConfidence] = useState(0);

  const query = useCallback(async (question: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const res = await fetch('/api/v1/agent/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: question,
          session_id: sessionId
        })
      });
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const data = await res.json();
      setResponse(data.response);
      setConfidence(data.confidence_score);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  return { query, response, isLoading, error, confidence };
};
```

#### WebSocket Streaming Integration
```typescript
// React hook for streaming responses
export const useAgentStream = (sessionId: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/agent/${sessionId}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Agent WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'stream_chunk':
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage?.role === 'assistant' && !lastMessage.complete) {
              // Append to existing message
              return prev.map((msg, idx) => 
                idx === prev.length - 1 
                  ? { ...msg, content: msg.content + message.data.content }
                  : msg
              );
            } else {
              // New message
              return [...prev, {
                id: `msg_${Date.now()}`,
                role: 'assistant',
                content: message.data.content,
                complete: false
              }];
            }
          });
          break;
          
        case 'stream_complete':
          setMessages(prev => 
            prev.map((msg, idx) => 
              idx === prev.length - 1 
                ? { ...msg, complete: true, metadata: message.data }
                : msg
            )
          );
          break;
      }
    };
    
    ws.onclose = () => setIsConnected(false);
    ws.onerror = (error) => console.error('WebSocket error:', error);
    
    wsRef.current = ws;
  }, [sessionId]);

  const sendMessage = useCallback((query: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'query',
        data: { query, stream: true }
      }));
      
      // Add user message to UI
      setMessages(prev => [...prev, {
        id: `msg_${Date.now()}`,
        role: 'user',
        content: query,
        complete: true
      }]);
    }
  }, []);

  return { messages, isConnected, connect, sendMessage };
};
```

### External API Integration Examples

#### Custom MCP Server Creation
```python
# Example: Custom News MCP Server
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("custom-news")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_crypto_headlines",
            description="Get latest cryptocurrency headlines",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["bitcoin", "ethereum", "defi", "nft"]},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_crypto_headlines":
        # Implement news fetching logic
        headlines = await fetch_crypto_news(
            category=arguments.get("category", "bitcoin"),
            limit=arguments.get("limit", 10)
        )
        return TextContent(text=json.dumps(headlines))
    
    raise ValueError(f"Tool {name} not found")

# Register with main application
async def startup():
    await mcp_manager.register_server("custom-news", server)
```

## 📈 Performance Benchmarks

### Typical Performance Metrics

| Metric | Development | Production |
|--------|-------------|------------|
| **API Response Time** | 50-200ms | 25-100ms |
| **Agent Query Processing** | 1-3 seconds | 0.5-2 seconds |
| **WebSocket Latency** | <50ms | <25ms |
| **Database Query Time** | 5-20ms | 2-10ms |
| **MCP Tool Call Time** | 100-500ms | 50-300ms |
| **Memory Usage** | 100-200MB | 200-500MB |
| **Concurrent Users** | 10-50 | 100-1000 |

### Load Testing
```python
# locustfile.py for load testing
from locust import HttpUser, task, between

class AgentUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Create session
        response = self.client.post("/api/v1/agent/session")
        self.session_id = response.json()["session_id"]
    
    @task(3)
    def query_bitcoin_price(self):
        self.client.post("/api/v1/agent/query", json={
            "query": "What's Bitcoin's current price?",
            "session_id": self.session_id
        })
    
    @task(2) 
    def query_market_sentiment(self):
        self.client.post("/api/v1/agent/query", json={
            "query": "Show me market sentiment",
            "session_id": self.session_id
        })
    
    @task(1)
    def complex_analysis(self):
        self.client.post("/api/v1/agent/query", json={
            "query": "Compare Bitcoin and Ethereum performance with market analysis",
            "session_id": self.session_id
        })

# Run load test
# uv run locust -f locustfile.py --host http://localhost:8000
```

## 🔧 Advanced Configuration

### Custom AI Model Integration
```python
# app/services/custom_ai_client.py
from typing import Dict, Any, AsyncGenerator
from openai import AsyncOpenAI

class CustomAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_response(
        self, 
        query: str, 
        context: Dict[str, Any],
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        messages = [
            {
                "role": "system", 
                "content": self._build_system_prompt(context)
            },
            {"role": "user", "content": query}
        ]
        
        if stream:
            return self._stream_response(messages)
        else:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        return f"""
        You are SpectraQ AI Agent, an expert cryptocurrency and prediction market analyst.
        
        Current market context:
        {json.dumps(context, indent=2)}
        
        Provide detailed, accurate analysis with:
        - Current price data and trends
        - Market sentiment interpretation
        - Risk assessment and recommendations
        - Clear, actionable insights
        
        Format responses in markdown with appropriate emojis.
        """
```

### Database Schema Extensions
```python
# app/models/analytics.py
class MarketAnalytics(Base):
    """Track market prediction accuracy and performance"""
    __tablename__ = "market_analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    market_id = Column(String, nullable=False)
    prediction_accuracy = Column(Float)        # 0.0 to 1.0
    confidence_score = Column(Float)           # Agent confidence
    actual_outcome = Column(Boolean)           # True/False market resolution
    predicted_outcome = Column(Boolean)        # Agent prediction
    factors_analyzed = Column(JSON)            # Data sources used
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_market_analytics_market_id', 'market_id'),
        Index('idx_market_analytics_created_at', 'created_at'),
    )

class UserInteraction(Base):
    """Track user engagement and query patterns"""
    __tablename__ = "user_interactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    session_id = Column(String, nullable=False)
    interaction_type = Column(String)          # query, click, scroll, etc.
    query_category = Column(String)            # price, sentiment, news, etc.
    response_rating = Column(Integer)          # 1-5 user rating
    time_spent_seconds = Column(Integer)       # Time spent reading response
    follow_up_clicked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### WebSocket Advanced Features
```python
# app/services/websocket_manager.py
from typing import Dict, Set
import json
import asyncio
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.session_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        
        # Send welcome message
        await self.send_to_session(session_id, {
            "type": "connection_established",
            "data": {
                "session_id": session_id,
                "features": ["streaming", "real_time_updates", "multi_tool"]
            }
        })
    
    async def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                if session_id in self.session_metadata:
                    del self.session_metadata[session_id]
    
    async def send_to_session(self, session_id: str, message: dict):
        """Send message to all connections in a session"""
        if session_id in self.active_connections:
            disconnected = set()
            
            for websocket in self.active_connections[session_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.active_connections[session_id].discard(ws)
    
    async def broadcast_market_update(self, market_data: dict):
        """Broadcast market updates to all active sessions"""
        message = {
            "type": "market_update",
            "data": market_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for session_id in self.active_connections:
            await self.send_to_session(session_id, message)
```

## 🎓 Learning Resources

### Understanding MCP (Model Context Protocol)
- **[MCP Documentation](https://modelcontextprotocol.io/)** - Official protocol documentation
- **[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)** - Python implementation
- **[MCP Server Examples](https://github.com/modelcontextprotocol/servers)** - Reference implementations

### FastAPI & Python Resources
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Comprehensive FastAPI guide
- **[SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)** - Modern ORM patterns
- **[Async Python](https://docs.python.org/3/library/asyncio.html)** - Async programming guide

### Prediction Markets & Blockchain
- **[Avalanche Documentation](https://docs.avax.network/)** - Avalanche development guide
- **[Uniswap V4](https://docs.uniswap.org/contracts/v4/overview)** - DEX integration
- **[Prediction Market Theory](https://en.wikipedia.org/wiki/Prediction_market)** - Economic foundations

---

<div align="center">

### 🔗 Quick Links

**[🌐 Frontend README](../frontend/README.md)** | **[🤖 Agent Documentation](./docs/agent.md)** | **[📊 API Reference](http://localhost:8000/docs)** | **[🐛 Issue Tracker](https://github.com/blinderchief/Avalanche_Team1_Hackathon/issues)**

**Built for Avalanche Hackathon 2024** 🏔️

</div>
