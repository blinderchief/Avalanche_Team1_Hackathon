import { Navigation } from '@/components/layout/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useParams, Link } from 'react-router-dom';
import { ClockIcon, UsersIcon, CurrencyDollarIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import { TokenPrices } from '@/components/markets/TokenPrices';
import { MarketGraduation } from '@/components/markets/MarketGraduation';

const MarketDetail = () => {
  const { id } = useParams();

  // Mock market data - in real app, fetch based on id
  const market = {
    id: id || '1',
    title: 'Will Bitcoin reach $100,000 by end of 2024?',
    description: 'This market resolves to YES if Bitcoin (BTC) reaches or exceeds $100,000 USD on any major exchange by December 31, 2024, 11:59 PM UTC. The price will be determined by the average of Coinbase, Binance, and Kraken at market close.',
    category: 'Crypto',
    endDate: '2024-12-31',
    volume: '$2.4M',
    participants: 1247,
    yesPrice: 0.65,
    noPrice: 0.35,
    status: 'active' as const,
    creator: '0x1234...5678',
    createdAt: '2024-01-15',
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-28">
        {/* Back Button */}
        <Link to="/markets" className="inline-flex items-center text-muted-foreground hover:text-foreground mb-6 transition-smooth">
          <ArrowLeftIcon className="w-4 h-4 mr-2" />
          Back to Markets
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Market Header */}
            <Card className="gradient-card border-border/50">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <Badge className={market.status === 'active' ? 'bg-success text-success-foreground' : 'bg-muted text-muted-foreground'}>
                    {market.status.charAt(0).toUpperCase() + market.status.slice(1)}
                  </Badge>
                  <Badge variant="outline" className="border-quantum-gray-light">
                    {market.category}
                  </Badge>
                </div>
                <h1 className="text-3xl font-bold text-foreground mt-4">
                  {market.title}
                </h1>
                <div className="flex items-center space-x-6 mt-4 text-sm text-muted-foreground">
                  <div className="flex items-center space-x-1">
                    <ClockIcon className="w-4 h-4" />
                    <span>Ends {new Date(market.endDate).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <CurrencyDollarIcon className="w-4 h-4" />
                    <span>{market.volume} volume</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <UsersIcon className="w-4 h-4" />
                    <span>{market.participants} participants</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">
                  {market.description}
                </p>
              </CardContent>
            </Card>

            {/* Trading Chart Placeholder */}
            <Card className="gradient-card border-border/50">
              <CardHeader>
                <CardTitle>Price History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-muted/20 rounded-lg flex items-center justify-center">
                  <p className="text-muted-foreground">Trading chart will be implemented here</p>
                </div>
              </CardContent>
            </Card>

            {/* Activity Feed */}
            <Card className="gradient-card border-border/50">
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-muted/30 rounded">
                    <span className="text-sm">
                      <span className="font-medium">0x1234...5678</span> bought <span className="text-success font-medium">100 YES</span> for $65.00
                    </span>
                    <span className="text-xs text-muted-foreground">2 min ago</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted/30 rounded">
                    <span className="text-sm">
                      <span className="font-medium">0x9876...5432</span> sold <span className="text-destructive font-medium">50 NO</span> for $17.50
                    </span>
                    <span className="text-xs text-muted-foreground">5 min ago</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

            {/* Trading Sidebar */}
          <div className="space-y-6">
            {/* Token Prices Component */}
            <TokenPrices marketId={market.id} />

            {/* Market Info */}
            <Card className="gradient-card border-border/50">
              <CardHeader>
                <CardTitle>Market Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Creator</span>
                  <span className="font-mono text-sm">{market.creator}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Created</span>
                  <span>{new Date(market.createdAt).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Resolution</span>
                  <span>{new Date(market.endDate).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Category</span>
                  <Badge variant="outline">{market.category}</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Market Graduation */}
            <MarketGraduation
              marketId={market.id}
              canGraduate={true}
              liquidityThreshold={1000000}
              currentLiquidity={1250000}
              volumeThreshold={500000}
              currentVolume={680000}
              timeThreshold={168}
              marketAge={240}
            />

            {/* Actions */}
            <Card className="gradient-card border-border/50">
              <CardContent className="pt-6 space-y-3">
                <Link to={`/markets/${market.id}/propose`} className="block">
                  <Button variant="outline" className="w-full btn-outline-quantum">
                    Submit Proposal
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketDetail;