import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Progress } from './components/ui/progress';
import { 
  Smartphone, 
  Cpu, 
  Zap, 
  Users, 
  Download,
  Activity,
  Wallet,
  Globe,
  Shield,
  TrendingUp,
  Clock,
  Hash,
  Copy,
  ExternalLink,
  Play,
  Pause,
  Settings
} from 'lucide-react';
import './App.css';

// Pool and wallet configuration from the script
const POOL_WALLET = "46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxzDQtNLf2bsp2DX2qCCgC5mg";
const POOL_URL = "pool.supportxmr.com:3333";

function App() {
  const [minerData, setMinerData] = useState(null);
  const [isRegistered, setIsRegistered] = useState(false);
  const [miningStats, setMiningStats] = useState({
    hashrate: 0,
    shares: 0,
    uptime: 0,
    earnings: 0
  });
  const [username, setUsername] = useState('');

  // Simulate mining stats
  useEffect(() => {
    if (isRegistered) {
      const interval = setInterval(() => {
        setMiningStats(prev => ({
          hashrate: Math.floor(Math.random() * 500) + 100,
          shares: prev.shares + Math.floor(Math.random() * 3),
          uptime: prev.uptime + 1,
          earnings: prev.earnings + (Math.random() * 0.001)
        }));
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isRegistered]);

  const generateUserNumber = (username) => {
    const seed = `${username}-${Date.now()}-${Math.floor(Math.random() * 9999)}`;
    return btoa(seed).slice(0, 8).toUpperCase();
  };

  const handleRegistration = () => {
    if (!username.trim()) return;
    
    const userData = {
      username: username.trim(),
      userNumber: generateUserNumber(username),
      timestamp: Date.now(),
      poolWallet: POOL_WALLET
    };
    
    setMinerData(userData);
    setIsRegistered(true);
    localStorage.setItem('xmrt_miner_data', JSON.stringify(userData));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const downloadScript = () => {
    const scriptContent = `#!/bin/bash
# XMRT DAO Mobile Mining Setup Script
# Generated for user: ${minerData?.username || 'anonymous'}

echo "Setting up XMRT DAO Mobile Mining..."
curl -s https://gist.githubusercontent.com/DevGruGold/dc22c5bf983663e36394af8565218d82/raw/ | python3
`;
    
    const blob = new Blob([scriptContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'xmrt-mobile-mining-setup.sh';
    a.click();
    URL.revokeObjectURL(url);
  };

  const globalStats = [
    { label: 'Active Miners', value: '2,847', icon: <Users className="w-5 h-5" /> },
    { label: 'Total Hashrate', value: '1.2 MH/s', icon: <Cpu className="w-5 h-5" /> },
    { label: 'Pool Shares', value: '847K', icon: <Hash className="w-5 h-5" /> },
    { label: 'DAO Contribution', value: '12.5 XMR', icon: <TrendingUp className="w-5 h-5" /> }
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center">
                  <Smartphone className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-500 to-red-600 bg-clip-text text-transparent">
                  MobileMonero
                </h1>
              </div>
              <Badge variant="secondary">Mining</Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Globe className="w-4 h-4 mr-2" />
                MobileMonero.com
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
        {/* Hero Section */}
        <div className="text-center space-y-4 mb-8">
          <h2 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-orange-500 via-red-500 to-pink-600 bg-clip-text text-transparent">
            XMRT DAO Mobile Mining
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Join the global network of Android miners powering the XMRTNET DAO through MobileMonero.com
          </p>
        </div>

        {/* Global Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {globalStats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-xl font-bold">{stat.value}</p>
                  </div>
                  <div className="text-orange-500">
                    {stat.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="setup" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="setup">Setup</TabsTrigger>
            <TabsTrigger value="mining">Mining</TabsTrigger>
            <TabsTrigger value="tracking">Tracking</TabsTrigger>
            <TabsTrigger value="rewards">Rewards</TabsTrigger>
          </TabsList>

          <TabsContent value="setup" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Registration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Smartphone className="w-6 h-6 mr-2 text-orange-500" />
                    DAO Miner Registration
                  </CardTitle>
                  <CardDescription>
                    Create your unique miner identity for the XMRTNET DAO
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {!isRegistered ? (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="username">Mining Alias</Label>
                        <Input
                          id="username"
                          placeholder="Enter your mining alias"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                        />
                      </div>
                      <Button onClick={handleRegistration} className="w-full" disabled={!username.trim()}>
                        <Users className="w-4 h-4 mr-2" />
                        Register as DAO Miner
                      </Button>
                    </>
                  ) : (
                    <div className="space-y-4">
                      <div className="bg-green-100 dark:bg-green-900 p-4 rounded-lg">
                        <div className="flex items-center mb-2">
                          <Shield className="w-5 h-5 text-green-600 mr-2" />
                          <span className="font-medium text-green-800 dark:text-green-200">Registration Complete!</span>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div>Username: <span className="font-mono">{minerData.username}</span></div>
                          <div>Miner ID: <span className="font-mono">{minerData.userNumber}</span></div>
                          <div>Pool Worker: <span className="font-mono">{POOL_WALLET}.{minerData.userNumber}</span></div>
                        </div>
                      </div>
                      <Button onClick={downloadScript} className="w-full">
                        <Download className="w-4 h-4 mr-2" />
                        Download Setup Script
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Instructions */}
              <Card>
                <CardHeader>
                  <CardTitle>Setup Instructions</CardTitle>
                  <CardDescription>3-step process to start mining</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                      <div>
                        <div className="font-medium">Visit MobileMonero.com</div>
                        <div className="text-sm text-muted-foreground">Complete the initial setup process</div>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                      <div>
                        <div className="font-medium">Install Termux</div>
                        <div className="text-sm text-muted-foreground">Download from F-Droid or Google Play</div>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                      <div>
                        <div className="font-medium">Run Setup Script</div>
                        <div className="text-sm text-muted-foreground">Execute the downloaded script in Termux</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-muted p-3 rounded-lg text-sm">
                    <div className="font-medium mb-1">Script Command:</div>
                    <div className="flex items-center justify-between">
                      <code className="bg-background px-2 py-1 rounded">curl -s https://gist.githubusercontent.com/DevGruGold/dc22c5bf983663e36394af8565218d82/raw/ | python3</code>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => copyToClipboard('curl -s https://gist.githubusercontent.com/DevGruGold/dc22c5bf983663e36394af8565218d82/raw/ | python3')}
                      >
                        <Copy className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Pool Configuration */}
            <Card>
              <CardHeader>
                <CardTitle>Pool Configuration</CardTitle>
                <CardDescription>SupportXMR pool settings for XMRTNET DAO</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Pool URL</Label>
                    <div className="flex items-center justify-between bg-muted p-2 rounded">
                      <code className="text-sm">{POOL_URL}</code>
                      <Button size="sm" variant="outline" onClick={() => copyToClipboard(POOL_URL)}>
                        <Copy className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>DAO Wallet</Label>
                    <div className="flex items-center justify-between bg-muted p-2 rounded">
                      <code className="text-sm">{POOL_WALLET.slice(0, 20)}...</code>
                      <Button size="sm" variant="outline" onClick={() => copyToClipboard(POOL_WALLET)}>
                        <Copy className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="mining" className="space-y-6">
            {isRegistered ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Mining Control */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Cpu className="w-6 h-6 mr-2 text-blue-500" />
                      Mining Control
                    </CardTitle>
                    <CardDescription>Control your mobile mining session</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span>Mining Status</span>
                      <Badge className="bg-green-500 text-white">Active</Badge>
                    </div>
                    <div className="flex space-x-2">
                      <Button className="flex-1">
                        <Play className="w-4 h-4 mr-2" />
                        Start Mining
                      </Button>
                      <Button variant="outline" className="flex-1">
                        <Pause className="w-4 h-4 mr-2" />
                        Pause
                      </Button>
                      <Button variant="outline" size="sm">
                        <Settings className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>CPU Usage</span>
                        <span>75%</span>
                      </div>
                      <Progress value={75} className="h-2" />
                    </div>
                  </CardContent>
                </Card>

                {/* Live Stats */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Activity className="w-6 h-6 mr-2 text-green-500" />
                      Live Mining Stats
                    </CardTitle>
                    <CardDescription>Real-time mining performance</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-muted-foreground">Hashrate</div>
                        <div className="text-xl font-bold">{miningStats.hashrate} H/s</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Shares</div>
                        <div className="text-xl font-bold">{miningStats.shares}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Uptime</div>
                        <div className="text-xl font-bold">{Math.floor(miningStats.uptime / 60)}m</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Earnings</div>
                        <div className="text-xl font-bold">{miningStats.earnings.toFixed(6)} XMR</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center py-8">
                    <Smartphone className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Registration Required</h3>
                    <p className="text-muted-foreground mb-4">Please register as a DAO miner to access mining controls</p>
                    <Button onClick={() => document.querySelector('[value="setup"]').click()}>
                      Go to Setup
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="tracking" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Hash className="w-6 h-6 mr-2 text-purple-500" />
                  Miner Tracking
                </CardTitle>
                <CardDescription>Track your contributions to the XMRTNET DAO</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {isRegistered ? (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Your Tracker ID</Label>
                        <div className="flex items-center justify-between bg-muted p-2 rounded">
                          <code className="text-sm font-mono">{minerData.userNumber}</code>
                          <Button size="sm" variant="outline" onClick={() => copyToClipboard(minerData.userNumber)}>
                            <Copy className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>Pool Worker ID</Label>
                        <div className="flex items-center justify-between bg-muted p-2 rounded">
                          <code className="text-sm font-mono">{POOL_WALLET}.{minerData.userNumber}</code>
                          <Button size="sm" variant="outline" onClick={() => copyToClipboard(`${POOL_WALLET}.${minerData.userNumber}`)}>
                            <Copy className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button className="flex-1" asChild>
                        <a href="https://supportxmr.com" target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="w-4 h-4 mr-2" />
                          View on SupportXMR
                        </a>
                      </Button>
                      <Button variant="outline" className="flex-1" asChild>
                        <a href="https://xmrtdao.vercel.app" target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="w-4 h-4 mr-2" />
                          DAO Tracking Portal
                        </a>
                      </Button>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    Register as a miner to access tracking features
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="rewards" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="w-6 h-6 mr-2 text-yellow-500" />
                  DAO Rewards System
                </CardTitle>
                <CardDescription>Earn XMRT tokens for contributing to the DAO</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border border-border rounded-lg">
                    <div className="text-2xl font-bold text-green-500">12.5%</div>
                    <div className="text-sm text-muted-foreground">Mining Rewards</div>
                  </div>
                  <div className="text-center p-4 border border-border rounded-lg">
                    <div className="text-2xl font-bold text-blue-500">5%</div>
                    <div className="text-sm text-muted-foreground">DAO Bonus</div>
                  </div>
                  <div className="text-center p-4 border border-border rounded-lg">
                    <div className="text-2xl font-bold text-purple-500">2.5%</div>
                    <div className="text-sm text-muted-foreground">Mobile Bonus</div>
                  </div>
                </div>
                
                <div className="bg-muted p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Reward Distribution</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• Mining rewards paid in XMR to pool wallet</li>
                    <li>• DAO bonus distributed as XMRT tokens</li>
                    <li>• Mobile mining bonus for Android miners</li>
                    <li>• NFC rewards for verified contributors</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default App;

