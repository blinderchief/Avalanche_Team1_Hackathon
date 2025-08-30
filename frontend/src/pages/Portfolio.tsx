import { Navigation } from '@/components/layout/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, ClockIcon } from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

const Portfolio = () => {
  // Mock portfolio data
  const portfolioStats = {
    totalValue: '$2,457.80',
    totalPnL: '+$342.15',
    winRate: '68%',
    activePositions: 12,
  };

  const positions = [
    {
      id: '1',
      marketTitle: 'Will Bitcoin reach $100,000 by end of 2024?',
      position: 'YES',
      amount: 100,
      avgPrice: 0.65,
      currentPrice: 0.67,
      value: '$67.00',
      pnl: '+$2.00',
      pnlPercentage: '+3.08%',
      status: 'active',
    },
    {
      id: '2',
      marketTitle: 'Will OpenAI release GPT-5 in 2024?',
      position: 'NO',
      amount: 200,
      avgPrice: 0.58,
      currentPrice: 0.55,
      value: '$110.00',
      pnl: '+$6.00',
      pnlPercentage: '+5.17%',
      status: 'active',
    },
  ];

  const transactions = [
    {
      id: '1',
      type: 'buy',
      market: 'Bitcoin $100K',
      position: 'YES',
      amount: 50,
      price: 0.65,
      timestamp: '2024-01-20 14:30',
    },
    {
      id: '2',
      type: 'sell',
      market: 'GPT-5 Release',
      position: 'NO',
      amount: 25,
      price: 0.58,
      timestamp: '2024-01-19 09:15',
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-28">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-4">Portfolio</h1>
          <p className="text-lg text-muted-foreground">
            Track your positions and performance across all markets
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="gradient-card border-border/50">
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-foreground mb-2">
                {portfolioStats.totalValue}
              </div>
              <div className="text-muted-foreground">Total Value</div>
            </CardContent>
          </Card>
          
          <Card className="gradient-card border-border/50">
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-success mb-2 flex items-center justify-center">
                <ArrowTrendingUpIcon className="w-5 h-5 mr-1" />
                {portfolioStats.totalPnL}
              </div>
              <div className="text-muted-foreground">Total P&L</div>
            </CardContent>
          </Card>
          
          <Card className="gradient-card border-border/50">
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-foreground mb-2">
                {portfolioStats.winRate}
              </div>
              <div className="text-muted-foreground">Win Rate</div>
            </CardContent>
          </Card>
          
          <Card className="gradient-card border-border/50">
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-foreground mb-2">
                {portfolioStats.activePositions}
              </div>
              <div className="text-muted-foreground">Active Positions</div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="positions" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-card border-border">
            <TabsTrigger value="positions" className="text-foreground">Positions</TabsTrigger>
            <TabsTrigger value="history" className="text-foreground">History</TabsTrigger>
            <TabsTrigger value="rewards" className="text-foreground">Rewards</TabsTrigger>
          </TabsList>
          
          <TabsContent value="positions" className="mt-6">
            <Card className="gradient-card border-border/50">
              <CardHeader>
                <CardTitle>Active Positions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {positions.map((position) => (
                    <Card key={position.id} className="bg-muted/20 border-border/50">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <Link 
                              to={`/markets/${position.id}`}
                              className="text-foreground font-medium hover:text-primary transition-smooth"
                            >
                              {position.marketTitle}
                            </Link>
                            <div className="flex items-center gap-2 mt-2">
                              <Badge 
                                className={position.position === 'YES' ? 'bg-success text-success-foreground' : 'bg-destructive text-destructive-foreground'}
                              >
                                {position.position}
                              </Badge>
                              <span className="text-sm text-muted-foreground">
                                {position.amount} shares @ ${position.avgPrice}
                              </span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-semibold text-foreground">
                              {position.value}
                            </div>
                            <div className={`text-sm flex items-center ${
                              position.pnl.startsWith('+') ? 'text-success' : 'text-destructive'
                            }`}>
                              {position.pnl.startsWith('+') ? 
                                <ArrowTrendingUpIcon className="w-4 h-4 mr-1" /> : 
                                <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />
                              }
                              {position.pnl} ({position.pnlPercentage})
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="history" className="mt-6">
            <Card className="gradient-card border-border/50">
              <CardHeader>
                <CardTitle>Transaction History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {transactions.map((tx) => (
                    <Card key={tx.id} className="bg-muted/20 border-border/50">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <Badge 
                              variant={tx.type === 'buy' ? 'default' : 'outline'}
                              className={tx.type === 'buy' ? 'bg-primary text-primary-foreground' : 'border-muted-foreground'}
                            >
                              {tx.type.toUpperCase()}
                            </Badge>
                            <div>
                              <div className="font-medium text-foreground">
                                {tx.amount} {tx.position} • {tx.market}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                @ ${tx.price} per share
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium text-foreground">
                              ${(tx.amount * tx.price).toFixed(2)}
                            </div>
                            <div className="text-sm text-muted-foreground flex items-center">
                              <ClockIcon className="w-4 h-4 mr-1" />
                              {tx.timestamp}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="rewards" className="mt-6">
            <Card className="gradient-card border-border/50">
              <CardHeader>
                <CardTitle>Claimable Rewards</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <div className="text-3xl font-bold text-foreground mb-2">$0.00</div>
                  <p className="text-muted-foreground mb-4">No rewards available to claim</p>
                  <Button className="btn-quantum" disabled>
                    Claim Rewards
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Portfolio;