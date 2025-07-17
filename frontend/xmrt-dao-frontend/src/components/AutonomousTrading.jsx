import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Bot, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart3, 
  Zap,
  Shield,
  Target,
  Clock,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

const AutonomousTrading = () => {
  const [elizaStatus, setElizaStatus] = useState({
    active: true,
    tradingEnabled: true,
    confidence: 0.89,
    model: 'GPT-4',
    gpt5Ready: true,
    totalTrades: 1247,
    successRate: 0.87,
    profitToday: 2847.32
  });

  const [autonomousTrades, setAutonomousTrades] = useState([
    {
      id: 1,
      pair: 'XMRT/USDC',
      type: 'BUY',
      amount: '1,500 XMRT',
      price: '$0.245',
      confidence: 0.92,
      reasoning: 'Strong support level, positive sentiment analysis, low volatility',
      timestamp: '2 minutes ago',
      status: 'executed',
      profit: '+$127.50'
    },
    {
      id: 2,
      pair: 'XMRT/ETH',
      type: 'SELL',
      amount: '800 XMRT',
      price: '0.000156 ETH',
      confidence: 0.85,
      reasoning: 'Resistance level reached, profit-taking opportunity, risk management',
      timestamp: '8 minutes ago',
      status: 'executed',
      profit: '+$89.23'
    },
    {
      id: 3,
      pair: 'XMRT/BNB',
      type: 'BUY',
      amount: '2,200 XMRT',
      price: '$0.243',
      confidence: 0.78,
      reasoning: 'Cross-chain arbitrage opportunity detected, price discrepancy',
      timestamp: '15 minutes ago',
      status: 'pending',
      profit: 'Pending'
    }
  ]);

  const [marketAnalysis, setMarketAnalysis] = useState({
    sentiment: 'BULLISH',
    volatility: 'LOW',
    volume: 'HIGH',
    trend: 'UPWARD',
    riskLevel: 'MEDIUM',
    recommendations: [
      'Increase XMRT position by 15% based on technical indicators',
      'Monitor BTC correlation for potential market shifts',
      'Consider cross-chain arbitrage opportunities on Polygon'
    ]
  });

  const [portfolioOptimization, setPortfolioOptimization] = useState({
    currentAllocation: {
      XMRT: 45,
      USDC: 30,
      ETH: 15,
      BTC: 10
    },
    recommendedAllocation: {
      XMRT: 50,
      USDC: 25,
      ETH: 15,
      BTC: 10
    },
    rebalanceNeeded: true,
    expectedReturn: '+12.3%',
    riskReduction: '-8.7%'
  });

  const getTradeTypeColor = (type) => {
    return type === 'BUY' ? 'text-green-600' : 'text-red-600';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'executed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'BULLISH': return 'text-green-600';
      case 'BEARISH': return 'text-red-600';
      case 'NEUTRAL': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* ElizaOS Trading Status */}
      <Card className="border-2 border-green-200 bg-gradient-to-r from-green-50 to-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Bot className="h-8 w-8 text-green-600" />
              <span className="text-2xl font-bold">Autonomous Trading</span>
            </div>
            <Badge className="bg-green-100 text-green-800 border-green-300">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                ACTIVE
              </div>
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="font-semibold">{(elizaStatus.successRate * 100).toFixed(1)}%</p>
                <Progress value={elizaStatus.successRate * 100} className="w-16 h-2" />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <DollarSign className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Profit Today</p>
                <p className="font-semibold text-green-600">+${elizaStatus.profitToday.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Zap className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm text-gray-600">Total Trades</p>
                <p className="font-semibold">{elizaStatus.totalTrades.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Target className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Confidence</p>
                <p className="font-semibold">{(elizaStatus.confidence * 100).toFixed(1)}%</p>
                <Progress value={elizaStatus.confidence * 100} className="w-16 h-2" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Market Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            ElizaOS Market Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Sentiment</p>
              <p className={`font-bold text-lg ${getSentimentColor(marketAnalysis.sentiment)}`}>
                {marketAnalysis.sentiment}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Volatility</p>
              <Badge className={marketAnalysis.volatility === 'LOW' ? 'bg-green-100 text-green-800' : 
                marketAnalysis.volatility === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}>
                {marketAnalysis.volatility}
              </Badge>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Volume</p>
              <Badge className="bg-blue-100 text-blue-800">{marketAnalysis.volume}</Badge>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Trend</p>
              <div className="flex items-center justify-center gap-1">
                {marketAnalysis.trend === 'UPWARD' ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600" />
                )}
                <span className={marketAnalysis.trend === 'UPWARD' ? 'text-green-600' : 'text-red-600'}>
                  {marketAnalysis.trend}
                </span>
              </div>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Risk Level</p>
              <Badge className="bg-yellow-100 text-yellow-800">{marketAnalysis.riskLevel}</Badge>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-3">AI Recommendations</h4>
            <ul className="space-y-2">
              {marketAnalysis.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Recent Autonomous Trades */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Recent Autonomous Trades
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {autonomousTrades.map((trade) => (
              <div key={trade.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-semibold">{trade.pair}</span>
                      <Badge className={getTradeTypeColor(trade.type) === 'text-green-600' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {trade.type}
                      </Badge>
                      <Badge className={getStatusColor(trade.status)}>
                        {trade.status.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <p className="text-sm text-gray-600">Amount</p>
                        <p className="font-semibold">{trade.amount}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Price</p>
                        <p className="font-semibold">{trade.price}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Profit/Loss</p>
                        <p className={`font-semibold ${trade.profit.startsWith('+') ? 'text-green-600' : 'text-gray-600'}`}>
                          {trade.profit}
                        </p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{trade.reasoning}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>Confidence: {(trade.confidence * 100).toFixed(1)}%</span>
                      <span>{trade.timestamp}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Portfolio Optimization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Portfolio Optimization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3">Current Allocation</h4>
              <div className="space-y-2">
                {Object.entries(portfolioOptimization.currentAllocation).map(([asset, percentage]) => (
                  <div key={asset} className="flex items-center justify-between">
                    <span className="text-sm">{asset}</span>
                    <div className="flex items-center gap-2">
                      <Progress value={percentage} className="w-20 h-2" />
                      <span className="text-sm font-medium w-8">{percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Recommended Allocation</h4>
              <div className="space-y-2">
                {Object.entries(portfolioOptimization.recommendedAllocation).map(([asset, percentage]) => (
                  <div key={asset} className="flex items-center justify-between">
                    <span className="text-sm">{asset}</span>
                    <div className="flex items-center gap-2">
                      <Progress value={percentage} className="w-20 h-2" />
                      <span className="text-sm font-medium w-8">{percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {portfolioOptimization.rebalanceNeeded && (
            <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <span className="font-semibold text-yellow-800">Rebalancing Recommended</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Expected Return: </span>
                  <span className="font-semibold text-green-600">{portfolioOptimization.expectedReturn}</span>
                </div>
                <div>
                  <span className="text-gray-600">Risk Reduction: </span>
                  <span className="font-semibold text-blue-600">{portfolioOptimization.riskReduction}</span>
                </div>
              </div>
              <Button className="mt-3 bg-yellow-600 hover:bg-yellow-700">
                Execute Autonomous Rebalancing
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* GPT-5 Trading Enhancement Alert */}
      <Alert className="border-purple-200 bg-purple-50">
        <Bot className="h-4 w-4 text-purple-600" />
        <AlertDescription className="text-purple-800">
          <strong>GPT-5 Trading Enhancement Ready:</strong> Advanced market prediction models, improved risk assessment, 
          and enhanced cross-chain arbitrage detection will be automatically activated when GPT-5 becomes available.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default AutonomousTrading;

