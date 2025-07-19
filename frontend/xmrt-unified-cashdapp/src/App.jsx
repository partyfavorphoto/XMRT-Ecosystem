import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Wallet, Bot, TrendingUp, Vote, Shield, Zap } from 'lucide-react'
import './App.css'

function App() {
  const [balance, setBalance] = useState(0)
  const [elizaStatus, setElizaStatus] = useState('active')
  const [proposals, setProposals] = useState([])

  useEffect(() => {
    // Simulate fetching data from backend
    setBalance(1250.75)
    setProposals([
      { id: 1, title: 'Treasury Rebalancing', status: 'active', votes: 234 },
      { id: 2, title: 'Cross-chain Integration', status: 'pending', votes: 156 }
    ])
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto p-6">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Wallet className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">XMRT CashDapp</h1>
                <p className="text-gray-400">Unified DAO Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={elizaStatus === 'active' ? 'default' : 'secondary'}>
                <Bot className="w-4 h-4 mr-1" />
                Eliza AI {elizaStatus}
              </Badge>
            </div>
          </div>
        </header>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Balance Card */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Total Balance</CardTitle>
              <Wallet className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">${balance.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                +20.1% from last month
              </p>
            </CardContent>
          </Card>

          {/* Trading Card */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Trading</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">$2,350</div>
              <p className="text-xs text-muted-foreground">
                24h volume
              </p>
            </CardContent>
          </Card>

          {/* Governance Card */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Active Proposals</CardTitle>
              <Vote className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{proposals.length}</div>
              <p className="text-xs text-muted-foreground">
                Awaiting your vote
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Eliza AI Chat Section */}
        <Card className="bg-slate-800 border-slate-700 mb-8">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Bot className="w-5 h-5 mr-2" />
              Chat with Eliza AI
            </CardTitle>
            <CardDescription>
              Your AI assistant for DAO operations and insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-slate-900 rounded-lg p-4 mb-4 min-h-[200px]">
              <div className="text-gray-300 mb-2">
                <strong>Eliza:</strong> Hello! I'm monitoring the DAO operations. The treasury is healthy, and I've identified 2 optimization opportunities. Would you like me to explain?
              </div>
            </div>
            <div className="flex space-x-2">
              <input 
                type="text" 
                placeholder="Ask Eliza anything about the DAO..."
                className="flex-1 bg-slate-700 border-slate-600 text-white placeholder-gray-400 rounded-md px-3 py-2"
              />
              <Button className="bg-purple-600 hover:bg-purple-700">
                Send
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button className="bg-slate-700 hover:bg-slate-600 text-white h-16 flex flex-col items-center justify-center">
            <Wallet className="w-5 h-5 mb-1" />
            Wallet
          </Button>
          <Button className="bg-slate-700 hover:bg-slate-600 text-white h-16 flex flex-col items-center justify-center">
            <TrendingUp className="w-5 h-5 mb-1" />
            Trade
          </Button>
          <Button className="bg-slate-700 hover:bg-slate-600 text-white h-16 flex flex-col items-center justify-center">
            <Vote className="w-5 h-5 mb-1" />
            Governance
          </Button>
          <Button className="bg-slate-700 hover:bg-slate-600 text-white h-16 flex flex-col items-center justify-center">
            <Zap className="w-5 h-5 mb-1" />
            Mining
          </Button>
        </div>
      </div>
    </div>
  )
}

export default App
