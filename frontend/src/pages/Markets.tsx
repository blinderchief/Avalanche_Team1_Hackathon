import { Navigation } from '@/components/layout/Navigation';
import { MarketCard } from '@/components/markets/MarketCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { MagnifyingGlassIcon, FunnelIcon, PlusIcon } from '@heroicons/react/24/outline';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// Mock data - in real app, this would come from API
const allDefaultMarkets = [
  {
    id: '1',
    title: 'Will Bitcoin reach $100,000 by end of 2024?',
    description: 'Market prediction for Bitcoin price reaching six-figure milestone by December 31, 2024.',
    category: 'Crypto',
    endDate: '2024-12-31',
    volume: '$2.4M',
    participants: 1247,
    yesPrice: 0.65,
    noPrice: 0.35,
    status: 'active' as const,
    proposals: [
      {
        id: 'btc-100k',
        title: 'BTC reaches $100,000 by December 2024',
        description: 'Bitcoin will reach or exceed $100,000 USD on major exchanges',
        endDate: '2024-12-31',
        yesPrice: 0.65,
        noPrice: 0.35,
        volume: '$1.2M',
        participants: 623,
        status: 'active' as const
      },
      {
        id: 'btc-80k',
        title: 'BTC reaches $80,000 by November 2024',
        description: 'Bitcoin will reach or exceed $80,000 USD before November 30th',
        endDate: '2024-11-30',
        yesPrice: 0.78,
        noPrice: 0.22,
        volume: '$850K',
        participants: 412,
        status: 'active' as const
      }
    ]
  },
  {
    id: '2',
    title: 'Will OpenAI release GPT-5 in 2024?',
    description: 'Prediction market for the release of GPT-5 by OpenAI within the 2024 calendar year.',
    category: 'AI',
    endDate: '2024-12-31',
    volume: '$1.8M',
    participants: 892,
    yesPrice: 0.42,
    noPrice: 0.58,
    status: 'active' as const,
    proposals: [
      {
        id: 'gpt5-q2',
        title: 'GPT-5 released in Q2 2024',
        description: 'OpenAI will release GPT-5 between April and June 2024',
        endDate: '2024-06-30',
        yesPrice: 0.25,
        noPrice: 0.75,
        volume: '$400K',
        participants: 256,
        status: 'active' as const
      },
      {
        id: 'gpt5-h2',
        title: 'GPT-5 released in H2 2024',
        description: 'OpenAI will release GPT-5 in the second half of 2024',
        endDate: '2024-12-31',
        yesPrice: 0.58,
        noPrice: 0.42,
        volume: '$750K',
        participants: 412,
        status: 'active' as const
      }
    ]
  },
  // Add more markets...
];

const categories = ['All', 'Crypto', 'AI', 'Stocks', 'Economics', 'Politics', 'Sports', 'Tech'];

interface Market {
  id: string;
  title: string;
  description: string;
  category: string;
  endDate: string;
  volume: string;
  participants: number;
  yesPrice: number;
  noPrice: number;
  status: 'active' | 'resolved' | 'upcoming';
  proposals?: Array<{
    id: string;
    title: string;
    description: string;
    endDate: string;
    yesPrice: number;
    noPrice: number;
    volume: string;
    participants: number;
    status: 'active' | 'resolved' | 'upcoming';
  }>;
}

const Markets = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [sortBy, setSortBy] = useState('newest');
  const [userMarkets, setUserMarkets] = useState<Market[]>([]);

  // Load user-created markets from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('userMarkets');
    if (stored) {
      setUserMarkets(JSON.parse(stored));
    }
  }, []);

  // Combine default markets with user-created markets
  const allMarkets = [...allDefaultMarkets, ...userMarkets];

  const filteredMarkets = allMarkets.filter(market => {
    const matchesSearch = market.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         market.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || market.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-28">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-foreground mb-4">Prediction Markets</h1>
              <p className="text-lg text-muted-foreground">
                Discover and trade on real-world event outcomes
              </p>
            </div>
            <Link to="/create">
              <Button className="btn-quantum">
                <PlusIcon className="w-4 h-4 mr-2" />
                Create Market
              </Button>
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-8 space-y-4">
          {/* Search and Sort */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search markets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-card border-border"
              />
            </div>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full md:w-48 bg-card border-border">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-card border-border">
                <SelectItem value="newest">Newest</SelectItem>
                <SelectItem value="ending-soon">Ending Soon</SelectItem>
                <SelectItem value="highest-volume">Highest Volume</SelectItem>
                <SelectItem value="most-participants">Most Participants</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Categories */}
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <Badge
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                className={`cursor-pointer transition-smooth ${
                  selectedCategory === category
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-primary/10'
                }`}
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </Badge>
            ))}
          </div>
        </div>

        {/* Markets Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMarkets.map((market) => (
            <MarketCard key={market.id} market={market} />
          ))}
        </div>

        {/* Empty State */}
        {filteredMarkets.length === 0 && (
          <div className="text-center py-16">
            <FunnelIcon className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">No markets found</h3>
            <p className="text-muted-foreground">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Markets;