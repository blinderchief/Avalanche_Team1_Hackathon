import { Navigation } from '@/components/layout/Navigation';
import { MarketCard } from '@/components/markets/MarketCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { 
  ArrowRightIcon, 
  ChartBarSquareIcon, 
  UsersIcon, 
  CurrencyDollarIcon,
  ShieldCheckIcon,
  LightBulbIcon,
  BoltIcon,
  ChartPieIcon,
  ArrowTrendingUpIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { useEffect, useState } from 'react';

// Mock data for demonstration
const trendingMarkets = [
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
  },
  {
    id: '3',
    title: 'Will Tesla stock hit $300 before Q2 2024?',
    description: 'Market for Tesla stock price prediction reaching $300 per share before Q2 2024.',
    category: 'Stocks',
    endDate: '2024-06-30',
    volume: '$956K',
    participants: 567,
    yesPrice: 0.28,
    noPrice: 0.72,
    status: 'active' as const,
  },
  {
    id: '4',
    title: 'Will SpaceX successfully land on Mars by 2026?',
    description: 'Prediction for SpaceX achieving the first successful Mars landing mission by 2026.',
    category: 'Space',
    endDate: '2026-12-31',
    volume: '$3.2M',
    participants: 2134,
    yesPrice: 0.15,
    noPrice: 0.85,
    status: 'active' as const,
  },
  {
    id: '5',
    title: 'Will the Fed cut rates by 50bp in next meeting?',
    description: 'Federal Reserve interest rate cut prediction for the upcoming FOMC meeting.',
    category: 'Economics',
    endDate: '2024-03-20',
    volume: '$1.2M',
    participants: 743,
    yesPrice: 0.73,
    noPrice: 0.27,
    status: 'active' as const,
  },
  {
    id: '6',
    title: 'Will Ethereum 2.0 staking exceed 40M ETH?',
    description: 'Prediction for total Ethereum staked in ETH 2.0 to surpass 40 million ETH.',
    category: 'Crypto',
    endDate: '2024-09-30',
    volume: '$842K',
    participants: 421,
    yesPrice: 0.89,
    noPrice: 0.11,
    status: 'active' as const,
  },
  {
    id: '7',
    title: 'Will Apple announce VR headset successor in 2024?',
    description: 'Market for Apple announcing a new VR/AR headset product in 2024.',
    category: 'Tech',
    endDate: '2024-12-31',
    volume: '$1.5M',
    participants: 689,
    yesPrice: 0.56,
    noPrice: 0.44,
    status: 'active' as const,
  },
  {
    id: '8',
    title: 'Will global inflation drop below 3% by mid-2024?',
    description: 'Prediction for global average inflation rate dropping below 3% by June 2024.',
    category: 'Economics',
    endDate: '2024-06-30',
    volume: '$2.1M',
    participants: 1543,
    yesPrice: 0.61,
    noPrice: 0.39,
    status: 'active' as const,
  },
];

const stats = [
  { name: 'Total Value Locked', value: '$24.7M', icon: CurrencyDollarIcon, change: '+12.4%' },
  { name: 'Active Traders', value: '12,847', icon: UsersIcon, change: '+8.3%' },
  { name: 'Markets Created', value: '1,247', icon: ChartBarSquareIcon, change: '+15.2%' },
];

const features = [
  {
    icon: ShieldCheckIcon,
    title: 'Secure Transactions',
    description: 'All transactions are secured on the Avalanche blockchain with state-of-the-art cryptography.'
  },
  {
    icon: LightBulbIcon,
    title: 'Collective Intelligence',
    description: 'Harness the wisdom of crowds to discover the most accurate predictions for future events.'
  },
  {
    icon: BoltIcon,
    title: 'Instant Settlement',
    description: 'Markets resolve instantly once outcomes are determined, with automatic payouts to winners.'
  },
  {
    icon: ArrowTrendingUpIcon,
    title: 'Real Yield',
    description: 'Earn real returns on your predictions while participating in market price discovery.'
  },
];

const categories = [
  { name: 'Crypto', count: 124, color: 'bg-blue-500/10 text-blue-500 border-blue-500/20' },
  { name: 'Economics', count: 97, color: 'bg-green-500/10 text-green-500 border-green-500/20' },
  { name: 'Politics', count: 83, color: 'bg-red-500/10 text-red-500 border-red-500/20' },
  { name: 'Sports', count: 112, color: 'bg-amber-500/10 text-amber-500 border-amber-500/20' },
  { name: 'Technology', count: 76, color: 'bg-purple-500/10 text-purple-500 border-purple-500/20' },
  { name: 'Entertainment', count: 62, color: 'bg-pink-500/10 text-pink-500 border-pink-500/20' },
];

const Index = () => {
  const [marketCount, setMarketCount] = useState(0);
  
  // Animate market count on load
  useEffect(() => {
    const target = 1247;
    const duration = 2000; // 2 seconds
    const stepTime = 20; // Update every 20ms
    const steps = duration / stepTime;
    const increment = target / steps;
    let current = 0;
    let timer: NodeJS.Timeout;
    
    const updateCount = () => {
      current += increment;
      if (current >= target) {
        setMarketCount(target);
        clearInterval(timer);
      } else {
        setMarketCount(Math.floor(current));
      }
    };
    
    timer = setInterval(updateCount, stepTime);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative pt-20 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/20 via-background to-background z-0"></div>
        <div className="absolute top-0 left-0 right-0 h-[500px] bg-[url('/hero-grid.svg')] bg-center opacity-10 z-0"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-20 z-10">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            <div className="lg:w-1/2 text-left lg:pr-8">
              <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary/10 text-primary mb-6">
                <BoltIcon className="w-4 h-4 mr-2" />
                Powered by Avalanche Blockchain
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
                The Future of <span className="text-primary">Prediction Markets</span> is Here
              </h1>
              <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
                Trade on the outcomes of real-world events with unprecedented accuracy and security. From crypto prices to global events, make informed predictions and earn real rewards on SpectraQ.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/markets">
                  <Button size="lg" className="btn-quantum px-8 py-4 text-lg group relative overflow-hidden">
                    <span className="relative z-10 flex items-center">
                      Explore Markets
                      <ArrowRightIcon className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                    </span>
                    <span className="absolute inset-0 bg-gradient-to-r from-primary to-red-600 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  </Button>
                </Link>
                <Link to="/create">
                  <Button size="lg" variant="outline" className="btn-outline-quantum px-8 py-4 text-lg">
                    Create Market
                  </Button>
                </Link>
              </div>
              
              <div className="mt-12 grid grid-cols-3 gap-4">
                {stats.map((stat, i) => (
                  <div key={i} className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border/50">
                    <p className="text-sm text-muted-foreground mb-1 flex items-center">
                      <stat.icon className="w-4 h-4 mr-1 text-primary" />
                      {stat.name}
                    </p>
                    <p className="text-2xl font-bold text-foreground">{stat.value}</p>
                    <p className="text-xs text-success flex items-center">
                      {stat.change}
                      <ArrowTrendingUpIcon className="w-3 h-3 ml-1" />
                    </p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="lg:w-1/2 relative">
              <div className="relative bg-card rounded-xl border border-border/50 p-8 shadow-xl">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-red-600 rounded-xl blur opacity-20"></div>
                <div className="relative">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-lg font-semibold text-foreground">Featured Market</h3>
                      <p className="text-sm text-muted-foreground">Will Bitcoin reach $100K in 2024?</p>
                    </div>
                    <Badge className="bg-success text-success-foreground">Active</Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-success/10 border border-success/20 rounded-lg p-3">
                      <div className="text-xs text-success font-medium mb-1">YES</div>
                      <div className="text-2xl font-bold text-success">$0.65</div>
                      <div className="text-xs text-success/80">65% probability</div>
                    </div>
                    <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3">
                      <div className="text-xs text-destructive font-medium mb-1">NO</div>
                      <div className="text-2xl font-bold text-destructive">$0.35</div>
                      <div className="text-xs text-destructive/80">35% probability</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-muted-foreground mb-6">
                    <div className="flex items-center space-x-1">
                      <UsersIcon className="w-4 h-4" />
                      <span>1,247 traders</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <CurrencyDollarIcon className="w-4 h-4" />
                      <span>$2.4M volume</span>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <Link to="/markets/1">
                      <Button className="w-full">Trade Now</Button>
                    </Link>
                  </div>
                </div>
              </div>
              
              <div className="absolute -bottom-4 -right-4 w-20 h-20 bg-primary/20 rounded-full blur-3xl"></div>
              <div className="absolute -top-4 -left-4 w-32 h-32 bg-primary/10 rounded-full blur-3xl"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16 bg-card/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">Explore Market Categories</h2>
            <p className="text-muted-foreground mt-2">Discover prediction markets across different domains</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {categories.map((category, i) => (
              <Link to={`/markets?category=${category.name}`} key={i}>
                <div className={`border ${category.color} rounded-xl p-4 text-center hover:scale-105 transition-all`}>
                  <p className="font-bold">{category.name}</p>
                  <p className="text-sm">{category.count} markets</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Trending Markets */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-12">
            <div>
              <h2 className="text-3xl font-bold text-foreground">Trending Markets</h2>
              <p className="text-muted-foreground mt-2">The most active prediction markets right now</p>
            </div>
            <Link to="/markets">
              <Button variant="outline" className="btn-outline-quantum">
                View All Markets
                <ArrowRightIcon className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {trendingMarkets.map((market) => (
              <MarketCard key={market.id} market={market} />
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-card/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">Why Choose SpectraQ</h2>
            <p className="text-muted-foreground mt-2">The most advanced prediction market platform on Avalanche</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <Card key={i} className="bg-card/50 backdrop-blur-sm border-border/50 hover:border-primary/50 transition-all">
                <CardContent className="pt-6">
                  <div className="rounded-full bg-primary/10 w-12 h-12 flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-bold text-foreground mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Recent Activity Feed */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row gap-8">
            <div className="lg:w-2/3">
              <Card className="gradient-card border-border/50 h-full">
                <CardHeader>
                  <CardTitle className="text-2xl text-foreground flex items-center">
                    <ChartPieIcon className="w-5 h-5 text-primary mr-2" />
                    Live Activity
                  </CardTitle>
                  <CardDescription>Real-time trading activity across all markets</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Mock activity items */}
                    <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg border border-border/30 hover:border-primary/30 transition-all">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold mr-3">A</div>
                        <div>
                          <span className="font-medium text-foreground">Alice</span>
                          <span className="text-muted-foreground"> bought </span>
                          <span className="text-success font-medium">100 YES</span>
                          <span className="text-muted-foreground"> tokens in </span>
                          <span className="font-medium text-foreground">Bitcoin $100K</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-sm text-muted-foreground">2m ago</span>
                        <span className="text-xs text-success">+$65.00</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg border border-border/30 hover:border-primary/30 transition-all">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold mr-3">B</div>
                        <div>
                          <span className="font-medium text-foreground">Bob</span>
                          <span className="text-muted-foreground"> sold </span>
                          <span className="text-destructive font-medium">50 NO</span>
                          <span className="text-muted-foreground"> tokens in </span>
                          <span className="font-medium text-foreground">GPT-5 Release</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-sm text-muted-foreground">5m ago</span>
                        <span className="text-xs text-destructive">-$29.00</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg border border-border/30 hover:border-primary/30 transition-all">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold mr-3">C</div>
                        <div>
                          <span className="font-medium text-foreground">Charlie</span>
                          <span className="text-muted-foreground"> created market </span>
                          <span className="font-medium text-foreground">Tesla Stock Prediction</span>
                        </div>
                      </div>
                      <span className="text-sm text-muted-foreground">10m ago</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg border border-border/30 hover:border-primary/30 transition-all">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold mr-3">D</div>
                        <div>
                          <span className="font-medium text-foreground">Diana</span>
                          <span className="text-muted-foreground"> resolved market </span>
                          <span className="font-medium text-foreground">ETH Price $3000+</span>
                          <span className="text-success font-medium"> YES</span>
                        </div>
                      </div>
                      <span className="text-sm text-muted-foreground">22m ago</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div className="lg:w-1/3">
              <Card className="bg-card border-border/50 h-full">
                <CardHeader>
                  <CardTitle className="text-2xl text-foreground flex items-center">
                    <LockClosedIcon className="w-5 h-5 text-primary mr-2" />
                    Security
                  </CardTitle>
                  <CardDescription>Your funds are always secure</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col space-y-4">
                  <div className="flex items-center space-x-4 p-4 bg-muted/50 rounded-lg">
                    <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center">
                      <ShieldCheckIcon className="w-6 h-6 text-success" />
                    </div>
                    <div>
                      <h4 className="font-medium">Blockchain Secured</h4>
                      <p className="text-sm text-muted-foreground">All transactions secured by Avalanche's C-Chain</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4 p-4 bg-muted/50 rounded-lg">
                    <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                      <LockClosedIcon className="w-6 h-6 text-blue-500" />
                    </div>
                    <div>
                      <h4 className="font-medium">Non-Custodial</h4>
                      <p className="text-sm text-muted-foreground">You always control your own funds</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4 p-4 bg-muted/50 rounded-lg">
                    <div className="w-12 h-12 rounded-full bg-amber-500/10 flex items-center justify-center">
                      <ChartBarSquareIcon className="w-6 h-6 text-amber-500" />
                    </div>
                    <div>
                      <h4 className="font-medium">Transparent Oracles</h4>
                      <p className="text-sm text-muted-foreground">Fair and verifiable market resolutions</p>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <Button variant="outline" className="w-full">Learn More About Security</Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-background"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-foreground mb-6">Ready to Predict the Future?</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Join thousands of traders on SpectraQ and start earning from your predictions today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/markets">
              <Button size="lg" className="btn-quantum px-8 py-4 text-lg shadow-xl">
                Start Trading Now
                <ArrowRightIcon className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </div>
          <div className="mt-12 flex justify-center">
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-foreground">{marketCount.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">Markets Created</div>
              </div>
              <div className="h-12 w-px bg-border"></div>
              <div className="text-center">
                <div className="text-4xl font-bold text-foreground">$24.7M</div>
                <div className="text-sm text-muted-foreground">Total Value Locked</div>
              </div>
              <div className="h-12 w-px bg-border"></div>
              <div className="text-center">
                <div className="text-4xl font-bold text-foreground">12,847</div>
                <div className="text-sm text-muted-foreground">Active Traders</div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-1">
              <Link to="/" className="flex items-center space-x-3 group">
                <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-glow">
                  <img src="/logo.png" alt="SpectraQ Logo" className="w-6 h-6" />
                </div>
                <div className="flex flex-col">
                  <span className="text-xl font-bold text-foreground">
                    SpectraQ
                  </span>
                  <span className="text-xs text-primary -mt-1">Prediction Markets</span>
                </div>
              </Link>
              <p className="text-muted-foreground mt-4">The next generation of decentralized prediction markets on Avalanche.</p>
            </div>
            
            <div>
              <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase mb-4">Markets</h3>
              <ul className="space-y-2">
                <li><Link to="/markets" className="text-muted-foreground hover:text-primary">Explore Markets</Link></li>
                <li><Link to="/create" className="text-muted-foreground hover:text-primary">Create Market</Link></li>
                <li><Link to="/markets?category=Crypto" className="text-muted-foreground hover:text-primary">Crypto Markets</Link></li>
                <li><Link to="/markets?category=Politics" className="text-muted-foreground hover:text-primary">Politics Markets</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase mb-4">Resources</h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-muted-foreground hover:text-primary">Documentation</a></li>
                <li><a href="#" className="text-muted-foreground hover:text-primary">API</a></li>
                <li><a href="#" className="text-muted-foreground hover:text-primary">FAQ</a></li>
                <li><a href="#" className="text-muted-foreground hover:text-primary">Tutorials</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-sm font-semibold text-foreground tracking-wider uppercase mb-4">Company</h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-muted-foreground hover:text-primary">About</a></li>
                <li><a href="#" className="text-muted-foreground hover:text-primary">Blog</a></li>
                <li><a href="#" className="text-muted-foreground hover:text-primary">Careers</a></li>
                <li><a href="#" className="text-muted-foreground hover:text-primary">Contact</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center">
            <p className="text-muted-foreground text-sm">© 2025 SpectraQ. All rights reserved.</p>
            <div className="mt-4 md:mt-0 flex space-x-6">
              <a href="#" className="text-muted-foreground hover:text-primary">Terms</a>
              <a href="#" className="text-muted-foreground hover:text-primary">Privacy</a>
              <a href="#" className="text-muted-foreground hover:text-primary">Cookies</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
