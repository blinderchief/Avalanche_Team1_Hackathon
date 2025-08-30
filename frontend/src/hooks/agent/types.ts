// Define message types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp: string | number;
  tool_name?: string;
  tool_calls?: ToolCall[];
}

// Define the type for tool calls
export type ToolCall = {
  id?: string;
  name?: string;
  function?: {
    name: string;
    arguments: string;
  };
};

// Define the Agent context interface
export interface AgentContextType {
  messages: Message[];
  isProcessing: boolean;
  sendMessage: (content: string) => Promise<void>;
  resetAgent: () => void;
  agentState: 'idle' | 'processing' | 'error';
  connectedTools: string[];
}
