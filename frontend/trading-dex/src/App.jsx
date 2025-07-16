import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  ArrowUpDown, 
  Wallet, 
  BarChart3,
  Activity,
  DollarSign,
  Droplets,
  Settings
} from 'lucide-react';
import './App.css';

const XMRT_TOKEN_ADDRESS = '0x77307dfbc436224d5e6f2048d2b6bdfa66998a15';

function App() {
  const [fromToken, setFromToken] = useState('ETH');
  const [toToken, setToToken] = useState('XMRT');
  const [fromAmount, setFromAmount] = useState('');
  const [toAmount, setToAmount] = useState('');

  const tokens = [
    { symbol: 'ETH', name: 'Ethereum', price: 2340.50, change: 2.4 },
    { symbol: 'XMRT', name: 'XMRT Token', price: 0.85, change: -1.2 },
    { symbol: 'USDC', name: 'USD Coin', price: 1.00, change: 0.1 },
    { symbol: 'WBTC', name: 'Wrapped Bitcoin', price: 43250.00, change: 3.8 }
  ];

  const pools = [
    { pair: 'ETH/XMRT', tvl: '$1.2M', apr: '24.5%', volume: '$450K' },
    { pair: 'XMRT/USDC', tvl: '$850K', apr: '18.2%', volume: '$320K' },
    { pair: 'ETH/USDC', tvl: '$2.1M', apr: '12.8%', volume: '$890K' }
  ];

  const handleSwap = () => {
    // Simulate swap
    alert(`Swapping ${fromAmount} ${fromToken} for ${toAmount} ${toToken}`);
  };

  const calculateToAmount = (amount) => {
    if (!amount) return '';
    // Simple mock calculation
    const rate = fromToken === 'ETH' ? 2753 : 0.85;
    return (parseFloat(amount) * rate).toFixed(6);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-cyan-600 bg-clip-text text-transparent">
                  XMRT DEX
                </h1>
              </div>
              <Badge variant="secondary">Trading</Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Wallet className="w-4 h-4 mr-2" />
                Connect Wallet
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="swap" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="swap">Swap</TabsTrigger>
            <TabsTrigger value="pools">Liquidity Pools</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="swap" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Swap Interface */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Swap Tokens</CardTitle>
                    <CardDescription>Trade tokens instantly with best rates</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* From Token */}
                    <div className="space-y-2">
                      <Label>From</Label>
                      <div className="flex space-x-2">
                        <div className="flex-1">
                          <Input
                            placeholder="0.0"
                            value={fromAmount}
                            onChange={(e) => {
                              setFromAmount(e.target.value);
                              setToAmount(calculateToAmount(e.target.value));
                            }}
                          />
                        </div>
                        <Button variant="outline" className="min-w-[100px]">
                          {fromToken}
                        </Button>
                      </div>
                    </div>

                    {/* Swap Button */}
                    <div className="flex justify-center">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          const temp = fromToken;
                          setFromToken(toToken);
                          setToToken(temp);
                        }}
                      >
                        <ArrowUpDown className="w-4 h-4" />
                      </Button>
                    </div>

                    {/* To Token */}
                    <div className="space-y-2">
                      <Label>To</Label>
                      <div className="flex space-x-2">
                        <div className="flex-1">
                          <Input
                            placeholder="0.0"
                            value={toAmount}
                            readOnly
                          />
                        </div>
                        <Button variant="outline" className="min-w-[100px]">
                          {toToken}
                        </Button>
                      </div>
                    </div>

                    <Button onClick={handleSwap} className="w-full" size="lg">
                      Swap Tokens
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* Market Info */}
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Market Prices</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {tokens.map((token) => (
                      <div key={token.symbol} className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{token.symbol}</div>
                          <div className="text-sm text-muted-foreground">{token.name}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium">${token.price.toLocaleString()}</div>
                          <div className={`text-sm flex items-center ${
                            token.change > 0 ? 'text-green-500' : 'text-red-500'
                          }`}>
                            {token.change > 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                            {Math.abs(token.change)}%
                          </div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">XMRT Token</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="text-sm">
                      <div className="font-medium">Contract Address:</div>
                      <code className="text-xs bg-muted p-1 rounded">{XMRT_TOKEN_ADDRESS}</code>
                    </div>
                    <div className="text-sm">
                      <div className="font-medium">Network:</div>
                      <div>Sepolia Testnet</div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="pools" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Add Liquidity</CardTitle>
                  <CardDescription>Provide liquidity and earn fees</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Token A</Label>
                    <div className="flex space-x-2">
                      <Input placeholder="0.0" />
                      <Button variant="outline">ETH</Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Token B</Label>
                    <div className="flex space-x-2">
                      <Input placeholder="0.0" />
                      <Button variant="outline">XMRT</Button>
                    </div>
                  </div>
                  <Button className="w-full">
                    <Droplets className="w-4 h-4 mr-2" />
                    Add Liquidity
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Your Positions</CardTitle>
                  <CardDescription>Manage your liquidity positions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center text-muted-foreground py-8">
                    No liquidity positions found
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Available Pools</CardTitle>
                <CardDescription>Explore liquidity pools and their performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {pools.map((pool, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border border-border rounded-lg">
                      <div>
                        <div className="font-medium">{pool.pair}</div>
                        <div className="text-sm text-muted-foreground">TVL: {pool.tvl}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-green-500">{pool.apr} APR</div>
                        <div className="text-sm text-muted-foreground">Vol: {pool.volume}</div>
                      </div>
                      <Button variant="outline" size="sm">
                        Add Liquidity
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Volume (24h)</p>
                      <p className="text-2xl font-bold">$1.2M</p>
                    </div>
                    <BarChart3 className="w-8 h-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total TVL</p>
                      <p className="text-2xl font-bold">$4.1M</p>
                    </div>
                    <DollarSign className="w-8 h-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Active Traders</p>
                      <p className="text-2xl font-bold">2.4K</p>
                    </div>
                    <Activity className="w-8 h-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Trading Chart</CardTitle>
                <CardDescription>XMRT/ETH Price Chart</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-muted-foreground">
                  Chart placeholder - Trading view integration would go here
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

