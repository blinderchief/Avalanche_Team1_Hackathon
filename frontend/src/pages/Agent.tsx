import { ReactElement } from 'react';
import { Card } from '@/components/ui/card';
import { SpectraQAgent } from '@/components/agent/SpectraQAgent';
import { AgentProvider } from '@/providers/AgentProvider';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';

// Create a client
const queryClient = new QueryClient();

export default function AgentPage(): ReactElement {
  return (
    <div className="container pt-28 pb-8">
      <h1 className="text-2xl font-bold mb-6">SpectraQ Agent</h1>
      <div className="grid grid-cols-1 gap-4">
        <Card className="p-0 overflow-hidden">
          <QueryClientProvider client={queryClient}>
            <AgentProvider>
              <SpectraQAgent />
            </AgentProvider>
          </QueryClientProvider>
        </Card>
      </div>
    </div>
  );
}
