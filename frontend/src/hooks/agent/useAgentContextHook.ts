import { useContext } from 'react';
import { AgentContext } from './useAgentContext';

// Custom hook to use the agent context
export function useAgentContext() {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error('useAgentContext must be used within an AgentProvider');
  }
  return context;
}
