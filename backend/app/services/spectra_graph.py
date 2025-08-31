"""
LangGraph integration for SpectraQ Agent with ComplAI compliance checking
"""

import asyncio
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
import logging

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from app.services.mcp_manager import MCPManager
from app.services.gemini_client import GeminiClient
from app.schemas.agent import QueryType

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the SpectraQ Agent LangGraph"""
    query: str
    query_type: Optional[QueryType]
    messages: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    compliance_audit: Optional[Dict[str, Any]]
    final_response: Optional[str]
    confidence_score: float
    processing_steps: List[str]

class SpectraQGraph:
    """LangGraph implementation for SpectraQ Agent with compliance integration"""
    
    def __init__(self, mcp_manager: MCPManager, gemini_client: GeminiClient):
        self.mcp_manager = mcp_manager
        self.gemini_client = gemini_client
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("gather_data", self._gather_data)
        workflow.add_node("compliance_check", self._compliance_check)
        workflow.add_node("generate_response", self._generate_response)
        
        # Define the flow
        workflow.set_entry_point("analyze_query")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_query",
            self._should_gather_data,
            {
                "gather": "gather_data",
                "skip": "compliance_check"
            }
        )
        
        workflow.add_edge("gather_data", "compliance_check")
        
        workflow.add_conditional_edges(
            "compliance_check",
            self._should_generate_response,
            {
                "generate": "generate_response",
                "end": END
            }
        )
        
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a query through the LangGraph workflow"""
        initial_state: AgentState = {
            "query": query,
            "query_type": None,
            "messages": [],
            "tool_results": {},
            "compliance_audit": None,
            "final_response": None,
            "confidence_score": 0.5,
            "processing_steps": []
        }
        
        try:
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            return {
                "response": result.get("final_response", "Unable to generate response"),
                "compliance_audit": result.get("compliance_audit"),
                "confidence_score": result.get("confidence_score", 0.5),
                "processing_steps": result.get("processing_steps", []),
                "tool_results": result.get("tool_results", {})
            }
        except Exception as e:
            logger.error(f"LangGraph processing failed: {e}")
            return {
                "response": f"Error processing query: {str(e)}",
                "compliance_audit": None,
                "confidence_score": 0.0,
                "processing_steps": ["error"],
                "tool_results": {}
            }
    
    async def _analyze_query(self, state: AgentState) -> AgentState:
        """Analyze the user query to determine type and requirements"""
        query = state["query"]
        query_lower = query.lower()
        
        # Determine query type
        query_type = QueryType.GENERAL_CRYPTO
        
        if any(word in query_lower for word in ["price", "cost", "value", "$"]):
            query_type = QueryType.PRICE_PREDICTION
        elif any(word in query_lower for word in ["sentiment", "fear", "greed", "news"]):
            query_type = QueryType.NEWS_SENTIMENT
        elif any(word in query_lower for word in ["whale", "on-chain", "transaction"]):
            query_type = QueryType.ON_CHAIN_ANALYSIS
        elif any(word in query_lower for word in ["audit", "compliance", "contract", "regulatory"]):
            query_type = QueryType.COMPLIANCE_AUDIT
        
        # Update state
        state["query_type"] = query_type
        state["processing_steps"].append("query_analysis")
        
        logger.info(f"Analyzed query type: {query_type}")
        return state
    
    def _should_gather_data(self, state: AgentState) -> str:
        """Determine if we need to gather data before compliance check"""
        query_type = state.get("query_type")
        
        # For compliance audits, we might not need external data first
        if query_type == QueryType.COMPLIANCE_AUDIT:
            return "skip"
        
        # For other queries, gather data first
        return "gather"
    
    async def _gather_data(self, state: AgentState) -> AgentState:
        """Gather data from MCP tools based on query type"""
        query = state["query"]
        query_type = state["query_type"]
        
        tools_to_call = []
        
        if query_type == QueryType.PRICE_PREDICTION:
            tools_to_call.append({
                "server": "coingecko",
                "tool": "get_coin_price",
                "parameters": {"symbol": "bitcoin"}
            })
        elif query_type == QueryType.NEWS_SENTIMENT:
            tools_to_call.extend([
                {
                    "server": "feargreed",
                    "tool": "get_fear_greed_index",
                    "parameters": {}
                },
                {
                    "server": "cryptopanic",
                    "tool": "get_news",
                    "parameters": {"filter": "hot"}
                }
            ])
        
        tool_results = {}
        for tool_info in tools_to_call:
            try:
                result = await self.mcp_manager.call_tool(
                    tool_info["server"],
                    tool_info["tool"],
                    tool_info["parameters"]
                )
                tool_results[f"{tool_info['server']}.{tool_info['tool']}"] = result
                logger.info(f"Successfully called {tool_info['server']}.{tool_info['tool']}")
            except Exception as e:
                logger.warning(f"Failed to call {tool_info['server']}.{tool_info['tool']}: {e}")
        
        state["tool_results"] = tool_results
        state["processing_steps"].append("data_gathering")
        
        return state
    
    async def _compliance_check(self, state: AgentState) -> AgentState:
        """Perform compliance audit if relevant"""
        query = state["query"]
        query_type = state["query_type"]
        
        # Check if compliance audit is needed
        if query_type == QueryType.COMPLIANCE_AUDIT or self._needs_compliance_check(query):
            try:
                # Extract contract code and standards
                contract_code = self._extract_contract_code(query)
                standards = self._extract_standards(query)
                
                if contract_code:
                    audit_result = await self.mcp_manager.call_tool(
                        "complai",
                        "compliance_audit",
                        {
                            "contract_code": contract_code,
                            "standards": standards
                        }
                    )
                    
                    state["compliance_audit"] = audit_result
                    state["processing_steps"].append("compliance_audit")
                    
                    logger.info("Compliance audit completed successfully")
                else:
                    logger.info("No contract code found for compliance audit")
                    
            except Exception as e:
                logger.error(f"Compliance audit failed: {e}")
                state["compliance_audit"] = {
                    "error": str(e),
                    "risk_score": 1.0,
                    "issues": ["Audit failed - manual review required"],
                    "fixes": ["Please consult compliance experts"]
                }
        
        return state
    
    def _should_generate_response(self, state: AgentState) -> str:
        """Determine if we should generate the final response"""
        # Always generate a response
        return "generate"
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate the final response using Gemini AI"""
        query = state["query"]
        tool_results = state["tool_results"]
        compliance_audit = state["compliance_audit"]
        
        # Build context for LLM
        context_parts = []
        
        if tool_results:
            context_parts.append(f"Available data: {tool_results}")
        
        if compliance_audit:
            context_parts.append(f"Compliance audit results: {compliance_audit}")
        
        context = "\n".join(context_parts) if context_parts else "No additional data available"
        
        # Create prompt
        prompt = f"""
You are SpectraQ AI Agent, an expert in cryptocurrency markets and compliance.

Query: {query}

{context}

Please provide a comprehensive response. If compliance audit results are available, include them prominently in your analysis.
"""
        
        try:
            # Call Gemini AI
            messages = [{"role": "user", "content": prompt}]
            llm_response = await self.gemini_client.chat_completion(
                messages=messages,
                model="gemini-2.0-flash-exp",
                temperature=0.7,
                max_tokens=2000
            )
            
            response_content = llm_response["choices"][0]["message"]["content"]
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(state)
            
            state["final_response"] = response_content
            state["confidence_score"] = confidence_score
            state["processing_steps"].append("response_generation")
            
            logger.info("Response generated successfully")
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            state["final_response"] = "I apologize, but I encountered an error generating the response. Please try again."
            state["confidence_score"] = 0.0
        
        return state
    
    def _needs_compliance_check(self, query: str) -> bool:
        """Determine if a query needs compliance checking"""
        query_lower = query.lower()
        compliance_keywords = [
            "trade", "transaction", "contract", "smart contract", 
            "regulatory", "compliance", "audit", "risk"
        ]
        
        return any(keyword in query_lower for keyword in compliance_keywords)
    
    def _extract_contract_code(self, query: str) -> Optional[str]:
        """Extract smart contract code from query"""
        import re
        
        # Check for Solidity code blocks
        code_match = re.search(r'```solidity\s*(.*?)\s*```', query, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Check for generic code blocks
        code_match = re.search(r'```\s*(.*?)\s*```', query, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        return None
    
    def _extract_standards(self, query: str) -> List[str]:
        """Extract compliance standards from query"""
        standards = []
        query_lower = query.lower()
        
        if 'aml' in query_lower:
            standards.append('AML')
        if 'gdpr' in query_lower:
            standards.append('GDPR')
        if 'kyc' in query_lower:
            standards.append('KYC')
        if 'eerc' in query_lower:
            standards.append('eERC')
        
        # Default standards
        if not standards:
            standards = ['AML', 'GDPR']
        
        return standards
    
    def _calculate_confidence_score(self, state: AgentState) -> float:
        """Calculate confidence score based on available data"""
        score = 0.5  # Base score
        
        if state.get("tool_results"):
            score += 0.2
        
        if state.get("compliance_audit"):
            audit = state["compliance_audit"]
            if isinstance(audit, dict) and "risk_score" in audit:
                # Lower risk score from audit means higher confidence
                audit_confidence = 1.0 - audit.get("risk_score", 0.5)
                score += audit_confidence * 0.3
        
        return min(1.0, score)
