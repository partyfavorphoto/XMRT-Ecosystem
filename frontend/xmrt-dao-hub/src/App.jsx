import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { 
  Wallet, 
  TrendingUp, 
  Vote, 
  Coins, 
  Image, 
  CreditCard,
  Droplets,
  ExternalLink,
  Github,
  Twitter,
  Globe,
  Users,
  Activity,
  BarChart3,
  Shield,
  Zap
} from 'lucide-react';
import './App.css';

// XMRT Token Contract Address on Sepolia
const XMRT_TOKEN_ADDRESS = '0x77307dfbc436224d5e6f2048d2b6bdfa66998a15';

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [walletAddress, setWalletAddress] = useState('');
  const [faucetAddress, setFaucetAddress] = useState('');
  const [faucetStatus, setFaucetStatus] = useState('');

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  const dapps = [
    {
      id: 'cashdapp',
      name: 'CashDapp',
      description: 'Complete financial ecosystem with payments, banking, and asset management',
      icon: <Wallet className="w-8 h-8" />,
      status: 'Live',
      branch: 'ux/cashdapp',
      features: ['Payments', 'Banking', 'Terminal', 'Assets'],
      color: 'bg-gradient-to-br from-green-500 to-emerald-600'
    },
    {
      id: 'trading',
      name: 'Trading DEX',
      description: 'Decentralized exchange for XMRT and other tokens',
      icon: <TrendingUp className="w-8 h-8" />,
      status: 'Coming Soon',
      branch: 'ux/trading-dapp',
      features: ['Spot Trading', 'Liquidity Pools', 'Yield Farming'],
      color: 'bg-gradient-to-br from-blue-500 to-cyan-600'
    },
    {
      id: 'governance',
      name: 'DAO Governance',
      description: 'Participate in XMRTNET DAO governance and voting',
      icon: <Vote className="w-8 h-8" />,
      status: 'Coming Soon',
      branch: 'ux/governance-dapp',
      features: ['Proposals', 'Voting', 'Treasury'],
      color: 'bg-gradient-to-br from-purple-500 to-violet-600'
    },
    {
      id: 'staking',
      name: 'Staking Platform',
      description: 'Stake XMRT tokens and earn rewards',
      icon: <Coins className="w-8 h-8" />,
      status: 'Coming Soon',
      branch: 'ux/staking-dapp',
      features: ['Staking', 'Rewards', 'Validators'],
      color: 'bg-gradient-to-br from-orange-500 to-red-600'
    },
    {
      id: 'nft',
      name: 'NFT Marketplace',
      description: 'Trade and manage NFTs within the XMRT ecosystem',
      icon: <Image className="w-8 h-8" />,
      status: 'Coming Soon',
      branch: 'ux/nft-marketplace',
      features: ['Marketplace', 'Minting', 'Collections'],
      color: 'bg-gradient-to-br from-pink-500 to-rose-600'
    },
    {
      id: 'lending',
      name: 'DeFi Lending',
      description: 'Decentralized lending and borrowing platform',
      icon: <CreditCard className="w-8 h-8" />,
      status: 'Coming Soon',
      branch: 'ux/lending-dapp',
      features: ['Lending', 'Borrowing', 'Collateral'],
      color: 'bg-gradient-to-br from-teal-500 to-green-600'
    }
  ];

  const stats = [
    { label: 'Total Value Locked', value: '$2.4M', icon: <BarChart3 className="w-5 h-5" /> },
    { label: 'Active Users', value: '12.5K', icon: <Users className="w-5 h-5" /> },
    { label: 'Transactions', value: '847K', icon: <Activity className="w-5 h-5" /> },
    { label: 'XMRT Staked', value: '1.2M', icon: <Coins className="w-5 h-5" /> }
  ];

  const handleFaucetRequest = async () => {
    if (!faucetAddress) {
      setFaucetStatus('Please enter a wallet address');
      return;
    }

    setFaucetStatus('Requesting XMRT tokens...');
    
    // Simulate faucet request
    setTimeout(() => {
      setFaucetStatus(`✅ Successfully sent 100 XMRT to ${faucetAddress.slice(0, 6)}...${faucetAddress.slice(-4)}`);
      setTimeout(() => setFaucetStatus(''), 5000);
    }, 2000);
  };

  return (
    <Router>
      <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'dark' : ''}`}>
        <div className="bg-background text-foreground">
          {/* Header */}
          <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-sm">X</span>
                    </div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-green-500 to-blue-600 bg-clip-text text-transparent">
                      XMRTNET
                    </h1>
                  </div>
                  <Badge variant="secondary" className="hidden sm:inline-flex">
                    DAO Hub
                  </Badge>
                </div>
                
                <div className="flex items-center space-x-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setDarkMode(!darkMode)}
                  >
                    {darkMode ? '☀️' : '🌙'}
                  </Button>
                  <Button variant="outline" size="sm">
                    <Wallet className="w-4 h-4 mr-2" />
                    Connect Wallet
                  </Button>
                </div>
              </div>
            </div>
          </header>

          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={
                <div className="space-y-8">
                  {/* Hero Section */}
                  <div className="text-center space-y-4">
                    <h2 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-green-500 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                      XMRTNET Ecosystem
                    </h2>
                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                      A comprehensive decentralized ecosystem built on privacy, security, and innovation
                    </p>
                    <div className="flex flex-wrap justify-center gap-4 mt-6">
                      <Button size="lg" className="bg-gradient-to-r from-green-500 to-blue-600">
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Explore dApps
                      </Button>
                      <Button variant="outline" size="lg">
                        <Github className="w-4 h-4 mr-2" />
                        View on GitHub
                      </Button>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {stats.map((stat, index) => (
                      <Card key={index} className="text-center">
                        <CardContent className="pt-6">
                          <div className="flex items-center justify-center mb-2">
                            {stat.icon}
                          </div>
                          <div className="text-2xl font-bold">{stat.value}</div>
                          <div className="text-sm text-muted-foreground">{stat.label}</div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {/* dApps Grid */}
                  <div>
                    <h3 className="text-3xl font-bold mb-6 text-center">Ecosystem dApps</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {dapps.map((dapp) => (
                        <Card key={dapp.id} className="group hover:shadow-lg transition-all duration-300 border-2 hover:border-primary/20">
                          <CardHeader>
                            <div className="flex items-center justify-between">
                              <div className={`p-3 rounded-lg ${dapp.color} text-white`}>
                                {dapp.icon}
                              </div>
                              <Badge variant={dapp.status === 'Live' ? 'default' : 'secondary'}>
                                {dapp.status}
                              </Badge>
                            </div>
                            <CardTitle className="text-xl">{dapp.name}</CardTitle>
                            <CardDescription>{dapp.description}</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              <div className="flex flex-wrap gap-2">
                                {dapp.features.map((feature, index) => (
                                  <Badge key={index} variant="outline" className="text-xs">
                                    {feature}
                                  </Badge>
                                ))}
                              </div>
                              <div className="flex space-x-2">
                                <Button 
                                  className="flex-1" 
                                  disabled={dapp.status !== 'Live'}
                                  asChild={dapp.status === 'Live'}
                                >
                                  {dapp.status === 'Live' ? (
                                    <a href={`/${dapp.id}`} target="_blank" rel="noopener noreferrer">
                                      Launch App
                                    </a>
                                  ) : (
                                    'Coming Soon'
                                  )}
                                </Button>
                                <Button variant="outline" size="sm" asChild>
                                  <a href={`https://github.com/DevGruGold/XMRT-Ecosystem/tree/${dapp.branch}`} target="_blank" rel="noopener noreferrer">
                                    <Github className="w-4 h-4" />
                                  </a>
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>

                  {/* Faucet Section */}
                  <Card className="max-w-2xl mx-auto">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Droplets className="w-6 h-6 mr-2 text-blue-500" />
                        XMRT Sepolia Testnet Faucet
                      </CardTitle>
                      <CardDescription>
                        Get test XMRT tokens for development and testing on Sepolia testnet
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="faucet-address">Wallet Address</Label>
                        <Input
                          id="faucet-address"
                          placeholder="0x..."
                          value={faucetAddress}
                          onChange={(e) => setFaucetAddress(e.target.value)}
                        />
                      </div>
                      <div className="bg-muted p-3 rounded-lg text-sm">
                        <div className="font-medium mb-1">Token Details:</div>
                        <div>Contract: <code className="bg-background px-1 rounded">{XMRT_TOKEN_ADDRESS}</code></div>
                        <div>Network: Sepolia Testnet</div>
                        <div>Amount: 100 XMRT per request</div>
                      </div>
                      <Button onClick={handleFaucetRequest} className="w-full" disabled={!faucetAddress}>
                        <Droplets className="w-4 h-4 mr-2" />
                        Request Test Tokens
                      </Button>
                      {faucetStatus && (
                        <div className={`text-sm p-3 rounded-lg ${
                          faucetStatus.includes('✅') ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                          'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                        }`}>
                          {faucetStatus}
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Features */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card>
                      <CardHeader>
                        <Shield className="w-8 h-8 text-green-500 mb-2" />
                        <CardTitle>Privacy First</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-muted-foreground">
                          Built with privacy and security at its core, leveraging advanced cryptographic techniques.
                        </p>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <Zap className="w-8 h-8 text-blue-500 mb-2" />
                        <CardTitle>High Performance</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-muted-foreground">
                          Optimized for speed and efficiency with low transaction costs and fast confirmations.
                        </p>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <Users className="w-8 h-8 text-purple-500 mb-2" />
                        <CardTitle>Community Driven</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-muted-foreground">
                          Governed by the community through decentralized autonomous organization (DAO) mechanisms.
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              } />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="border-t border-border bg-card/50 mt-16">
            <div className="container mx-auto px-4 py-8">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                  <h4 className="font-bold mb-4">XMRTNET</h4>
                  <p className="text-sm text-muted-foreground">
                    Building the future of decentralized finance with privacy and security.
                  </p>
                </div>
                <div>
                  <h4 className="font-bold mb-4">dApps</h4>
                  <ul className="space-y-2 text-sm">
                    {dapps.slice(0, 3).map((dapp) => (
                      <li key={dapp.id}>
                        <Link to={`/${dapp.id}`} className="text-muted-foreground hover:text-foreground">
                          {dapp.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold mb-4">Resources</h4>
                  <ul className="space-y-2 text-sm">
                    <li><a href="#" className="text-muted-foreground hover:text-foreground">Documentation</a></li>
                    <li><a href="#" className="text-muted-foreground hover:text-foreground">Whitepaper</a></li>
                    <li><a href="#" className="text-muted-foreground hover:text-foreground">API</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold mb-4">Community</h4>
                  <div className="flex space-x-4">
                    <a href="#" className="text-muted-foreground hover:text-foreground">
                      <Twitter className="w-5 h-5" />
                    </a>
                    <a href="#" className="text-muted-foreground hover:text-foreground">
                      <Github className="w-5 h-5" />
                    </a>
                    <a href="#" className="text-muted-foreground hover:text-foreground">
                      <Globe className="w-5 h-5" />
                    </a>
                  </div>
                </div>
              </div>
              <div className="border-t border-border mt-8 pt-8 text-center text-sm text-muted-foreground">
                © 2024 XMRTNET. All rights reserved.
              </div>
            </div>
          </footer>
        </div>
      </div>
    </Router>
  );
}

export default App;

