import { Navigation } from '@/components/layout/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MagnifyingGlassIcon, PlusIcon } from '@heroicons/react/24/outline';
import { COMMUNITIES } from '@/lib/contracts';
import { useAccount, useReadContract } from 'wagmi';
import { MarketCard } from '@/components/markets/MarketCard';
import { CommunityChat } from '@/components/communities/CommunityChat';
import { CreateCommunity } from '@/components/communities/CreateCommunity';

const Communities = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const { address } = useAccount();

  // Mock data for demonstration - replace with real contract calls
  const mockMarkets = [
    {
      id: '1',
      title: 'Will Bitcoin reach $100,000 by end of 2024?',
      description: 'Prediction market for Bitcoin price milestone',
      category: 'crypto',
      endDate: '2024-12-31',
      volume: '$2.4M',
      participants: 1247,
      yesPrice: 0.65,
      noPrice: 0.35,
      status: 'active' as const,
    },
    {
      id: '2',
      title: 'Will Team Liquid win The International 2024?',
      description: 'Esports prediction for Dota 2 championship',
      category: 'gamers',
      endDate: '2024-10-15',
      volume: '$850K',
      participants: 892,
      yesPrice: 0.32,
      noPrice: 0.68,
      status: 'active' as const,
    },
    {
      id: '3',
      title: 'Will S&P 500 close above 5000 this year?',
      description: 'Stock market index prediction',
      category: 'traders',
      endDate: '2024-12-31',
      volume: '$1.8M',
      participants: 2156,
      yesPrice: 0.78,
      noPrice: 0.22,
      status: 'active' as const,
    }
  ];

  const filteredMarkets = mockMarkets.filter(market => {
    const matchesSearch = market.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         market.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || market.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-28">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-4">
            Prediction Communities
          </h1>
          <p className="text-xl text-muted-foreground">
            Join specialized communities and create prediction markets
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              placeholder="Search markets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-card border-border"
            />
          </div>
          
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              variant={selectedCategory === null ? 'default' : 'outline'}
              onClick={() => setSelectedCategory(null)}
              className={selectedCategory === null ? 'btn-quantum' : 'btn-outline-quantum'}
            >
              All Categories
            </Button>
            {COMMUNITIES.map((community) => (
              <Button
                key={community.id}
                variant={selectedCategory === community.id ? 'default' : 'outline'}
                onClick={() => setSelectedCategory(community.id)}
                className={selectedCategory === community.id ? 'btn-quantum' : 'btn-outline-quantum'}
              >
                <span className="mr-1">{community.icon}</span>
                {community.name}
              </Button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Communities Sidebar */}
          <div className="space-y-6">
            <Card className="gradient-card border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Communities
                  <Badge className="bg-primary/20 text-primary">
                    {COMMUNITIES.length}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {COMMUNITIES.map((community) => (
                  <div
                    key={community.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-smooth ${
                      selectedCategory === community.id
                        ? 'bg-primary/10 border-primary/30'
                        : 'bg-muted/20 border-border/50 hover:bg-muted/40'
                    }`}
                    onClick={() => setSelectedCategory(community.id)}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{community.icon}</span>
                      <div className="flex-1">
                        <h3 className={`font-medium ${community.color}`}>
                          {community.name}
                        </h3>
                        <p className="text-xs text-muted-foreground">
                          {community.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="gradient-card border-border/50">
              <CardContent className="pt-6 space-y-3">
                <CreateCommunity />
                {address && (
                  <Link to="/create">
                    <Button className="w-full btn-quantum">
                      <PlusIcon className="w-4 h-4 mr-2" />
                      Create Market
                    </Button>
                  </Link>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Markets Grid and Chat */}
          <div className="lg:col-span-3 space-y-6">
            {/* Community Chat */}
            {selectedCategory && (
              <CommunityChat 
                communityId={selectedCategory}
                communityName={COMMUNITIES.find(c => c.id === selectedCategory)?.name || 'Community'}
              />
            )}
            
            {/* Markets */}
            {filteredMarkets.length === 0 ? (
              <Card className="gradient-card border-border/50">
                <CardContent className="text-center py-12">
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold text-foreground mb-2">
                    No markets found
                  </h3>
                  <p className="text-muted-foreground">
                    Try adjusting your search or category filter
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {filteredMarkets.map((market) => (
                  <MarketCard key={market.id} market={market} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Communities;