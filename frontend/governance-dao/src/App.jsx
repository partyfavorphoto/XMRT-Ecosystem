import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Progress } from './components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { 
  Vote, 
  Users, 
  Clock, 
  CheckCircle, 
  XCircle, 
  TrendingUp,
  Wallet,
  Plus,
  Calendar,
  DollarSign
} from 'lucide-react';
import './App.css';

function App() {
  const [votingPower, setVotingPower] = useState(1250);

  const proposals = [
    {
      id: 1,
      title: 'Increase Staking Rewards by 2%',
      description: 'Proposal to increase staking rewards from 12% to 14% APY to incentivize more participation',
      status: 'Active',
      endDate: '2024-01-20',
      forVotes: 75420,
      againstVotes: 12340,
      totalVotes: 87760,
      quorum: 100000,
      category: 'Economic'
    },
    {
      id: 2,
      title: 'Add New Trading Pair: XMRT/BTC',
      description: 'Proposal to add XMRT/BTC trading pair to the DEX with initial liquidity incentives',
      status: 'Active',
      endDate: '2024-01-18',
      forVotes: 45230,
      againstVotes: 8760,
      totalVotes: 53990,
      quorum: 100000,
      category: 'Technical'
    },
    {
      id: 3,
      title: 'Treasury Allocation for Marketing',
      description: 'Allocate 500,000 XMRT from treasury for Q1 2024 marketing initiatives',
      status: 'Passed',
      endDate: '2024-01-10',
      forVotes: 120450,
      againstVotes: 15230,
      totalVotes: 135680,
      quorum: 100000,
      category: 'Treasury'
    },
    {
      id: 4,
      title: 'Upgrade Smart Contract Security',
      description: 'Implement additional security measures and audit recommendations',
      status: 'Failed',
      endDate: '2024-01-05',
      forVotes: 35420,
      againstVotes: 85340,
      totalVotes: 120760,
      quorum: 100000,
      category: 'Security'
    }
  ];

  const treasuryStats = [
    { label: 'Total Treasury', value: '2.5M XMRT', icon: <DollarSign className="w-5 h-5" /> },
    { label: 'Active Proposals', value: '2', icon: <Vote className="w-5 h-5" /> },
    { label: 'Total Voters', value: '8.4K', icon: <Users className="w-5 h-5" /> },
    { label: 'Voting Power', value: `${votingPower.toLocaleString()} XMRT`, icon: <TrendingUp className="w-5 h-5" /> }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'bg-blue-500';
      case 'Passed': return 'bg-green-500';
      case 'Failed': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Economic': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'Technical': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'Treasury': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'Security': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const handleVote = (proposalId, vote) => {
    alert(`Voted ${vote} on proposal ${proposalId}`);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-violet-600 rounded-lg flex items-center justify-center">
                  <Vote className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-500 to-violet-600 bg-clip-text text-transparent">
                  XMRTNET DAO
                </h1>
              </div>
              <Badge variant="secondary">Governance</Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Create Proposal
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
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {treasuryStats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-xl font-bold">{stat.value}</p>
                  </div>
                  <div className="text-purple-500">
                    {stat.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="proposals" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="proposals">Proposals</TabsTrigger>
            <TabsTrigger value="treasury">Treasury</TabsTrigger>
            <TabsTrigger value="delegates">Delegates</TabsTrigger>
          </TabsList>

          <TabsContent value="proposals" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Governance Proposals</h2>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">All</Button>
                <Button variant="outline" size="sm">Active</Button>
                <Button variant="outline" size="sm">Passed</Button>
                <Button variant="outline" size="sm">Failed</Button>
              </div>
            </div>

            <div className="space-y-4">
              {proposals.map((proposal) => (
                <Card key={proposal.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <CardTitle className="text-lg">{proposal.title}</CardTitle>
                          <Badge className={getCategoryColor(proposal.category)}>
                            {proposal.category}
                          </Badge>
                        </div>
                        <CardDescription>{proposal.description}</CardDescription>
                      </div>
                      <Badge className={`${getStatusColor(proposal.status)} text-white`}>
                        {proposal.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>For: {proposal.forVotes.toLocaleString()}</span>
                          <span>{((proposal.forVotes / proposal.totalVotes) * 100).toFixed(1)}%</span>
                        </div>
                        <Progress value={(proposal.forVotes / proposal.totalVotes) * 100} className="h-2" />
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Against: {proposal.againstVotes.toLocaleString()}</span>
                          <span>{((proposal.againstVotes / proposal.totalVotes) * 100).toFixed(1)}%</span>
                        </div>
                        <Progress value={(proposal.againstVotes / proposal.totalVotes) * 100} className="h-2" />
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Quorum: {proposal.totalVotes.toLocaleString()}/{proposal.quorum.toLocaleString()}</span>
                          <span>{((proposal.totalVotes / proposal.quorum) * 100).toFixed(1)}%</span>
                        </div>
                        <Progress value={(proposal.totalVotes / proposal.quorum) * 100} className="h-2" />
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                        <div className="flex items-center">
                          <Calendar className="w-4 h-4 mr-1" />
                          Ends: {proposal.endDate}
                        </div>
                        <div className="flex items-center">
                          <Users className="w-4 h-4 mr-1" />
                          {proposal.totalVotes.toLocaleString()} votes
                        </div>
                      </div>
                      
                      {proposal.status === 'Active' && (
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleVote(proposal.id, 'For')}
                            className="text-green-600 border-green-600 hover:bg-green-50"
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Vote For
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleVote(proposal.id, 'Against')}
                            className="text-red-600 border-red-600 hover:bg-red-50"
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            Vote Against
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="treasury" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Treasury Overview</CardTitle>
                <CardDescription>XMRTNET DAO Treasury Management</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Assets</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>XMRT Tokens</span>
                        <span className="font-medium">2,500,000 XMRT</span>
                      </div>
                      <div className="flex justify-between">
                        <span>ETH</span>
                        <span className="font-medium">150 ETH</span>
                      </div>
                      <div className="flex justify-between">
                        <span>USDC</span>
                        <span className="font-medium">500,000 USDC</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Recent Transactions</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Marketing Allocation</span>
                        <span className="text-red-500">-500,000 XMRT</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Staking Rewards</span>
                        <span className="text-red-500">-100,000 XMRT</span>
                      </div>
                      <div className="flex justify-between">
                        <span>DEX Fees</span>
                        <span className="text-green-500">+25,000 XMRT</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="delegates" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Delegate Your Voting Power</CardTitle>
                <CardDescription>Delegate your XMRT tokens to trusted community members</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  Delegation feature coming soon
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

