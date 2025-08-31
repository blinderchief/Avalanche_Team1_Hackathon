import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ArrowUpIcon, ChartBarIcon, CurrencyDollarIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import { useAccount } from 'wagmi';
import { AgentMessage } from './AgentMessage';
import { AgentToolDisplay } from './AgentToolDisplay';
import { ComplianceDisplay } from './ComplianceDisplay';
import { AgentProvider } from '@/providers/AgentProvider';
import { useAgentContextHelper } from '@/hooks/useAgentContextHelper';

export function SpectraQAgent() {
  const { address } = useAccount();
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    messages, 
    sendMessage, 
    agentState,
    resetAgent,
    connectedTools 
  } = useAgentContextHelper();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isProcessing) return;
    
    // Add user message to the chat
    const userMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    };
    
    setIsProcessing(true);
    setIsStreaming(true);
    
    try {
      await sendMessage(query);
    } catch (error) {
      console.error('Error sending message to agent:', error);
    } finally {
      setIsProcessing(false);
      setIsStreaming(false);
      setQuery('');
    }
  };

  const suggestionQueries = [
    "What's the predicted price of Bitcoin next week?",
    "Analyze the current sentiment for Ethereum",
    "Show me the top trending crypto news today",
    "Track large whale movements in the last 24 hours",
    "Compare BTC and ETH price correlation",
    "What's the Fear & Greed index today?"
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Agent Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card/80">
        <div className="flex items-center space-x-3">
          <Avatar className="h-10 w-10 bg-primary/20 text-primary avatar-centered">
            <img src="/logo-colored.svg" alt="SpectraQ Agent" className="w-6 h-6" />
          </Avatar>
          <div>
            <h3 className="font-medium">SpectraQAgent</h3>
            <div className="flex items-center text-xs text-muted-foreground">
              <span className="flex items-center">
                <span className="w-2 h-2 rounded-full bg-green-500 mr-1 animate-pulse"></span>
                Online
              </span>
              <span className="mx-2">•</span>
              <span>Powered by Comput3.ai</span>
            </div>
          </div>
        </div>
        <div>
          <Button variant="outline" size="sm" className="text-xs" onClick={resetAgent}>
            New Chat
          </Button>
        </div>
      </div>

      {/* Agent Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="mb-6">
              <div className="w-16 h-16 mx-auto mb-4 avatar-centered">
                <img src="/logo-colored.svg" alt="SpectraQ Agent" className="w-16 h-16" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Welcome to SpectraQAgent</h2>
              <p className="text-muted-foreground max-w-md">
                Your AI assistant for crypto market insights, predictions, and analysis.
                Ask me anything about crypto markets, news, or trends.
              </p>
            </div>
            
            <div className="w-full max-w-md grid grid-cols-1 gap-2 mt-4">
              <p className="text-sm font-medium text-center mb-2">Try asking about:</p>
              {suggestionQueries.map((suggestion, index) => (
                <Button 
                  key={index} 
                  variant="outline" 
                  className="justify-start text-left text-sm h-auto py-2" 
                  onClick={() => setQuery(suggestion)}
                >
                  <ChartBarIcon className="w-4 h-4 mr-2 text-primary" />
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index}>
              <AgentMessage
                message={message}
                isStreaming={isStreaming && index === messages.length - 1 && message.role === 'assistant'}
              />
              
              {/* Display compliance audit results if available */}
              {message.role === 'assistant' && message.compliance_audit && (
                <div className="ml-10">
                  <ComplianceDisplay 
                    auditResult={message.compliance_audit}
                    onFixClick={(fix) => {
                      // Handle fix application
                      console.log('Apply fix:', fix);
                      // You could add logic here to apply the fix or show more details
                    }}
                  />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Connected Tools Display */}
      <div className="border-t border-border py-2 px-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            <span className="text-xs font-medium mr-2">Connected Data Sources</span>
            <Badge variant="outline" className="text-xs">
              {connectedTools.length}
            </Badge>
          </div>
          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
            <ChevronDownIcon className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex items-center space-x-2 overflow-x-auto pb-1">
          <AgentToolDisplay />
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-border">
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about crypto markets, news, or predictions..."
            disabled={isProcessing}
            className="flex-1"
          />
          <Button 
            type="submit" 
            disabled={!query.trim() || isProcessing}
            className="btn-quantum"
          >
            {isProcessing ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            ) : (
              <ArrowUpIcon className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
