import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Bot, 
  Brain, 
  Shield, 
  TrendingUp, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  Zap,
  Eye,
  Settings
} from 'lucide-react';

const AutonomousGovernance = () => {
  const [elizaStatus, setElizaStatus] = useState({
    active: true,
    confidence: 0.92,
    model: 'GPT-4',
    gpt5Ready: true,
    lastAction: '2 minutes ago',
    actionsToday: 47
  });

  const [autonomousActions, setAutonomousActions] = useState([
    {
      id: 1,
      type: 'proposal_analysis',
      title: 'Analyzed Proposal #127: Treasury Rebalancing',
      confidence: 0.94,
      decision: 'APPROVE',
      reasoning: 'Strong financial metrics, low risk, aligns with DAO objectives',
      timestamp: '2 minutes ago',
      status: 'executed'
    },
    {
      id: 2,
      type: 'community_response',
      title: 'Responded to 12 community questions',
      confidence: 0.89,
      decision: 'AUTONOMOUS',
      reasoning: 'Standard queries about staking rewards and governance process',
      timestamp: '5 minutes ago',
      status: 'executed'
    },
    {
      id: 3,
      type: 'risk_assessment',
      title: 'Security Scan: All Systems Normal',
      confidence: 0.96,
      decision: 'MONITOR',
      reasoning: 'No threats detected, treasury secure, contracts functioning normally',
      timestamp: '10 minutes ago',
      status: 'executed'
    },
    {
      id: 4,
      type: 'treasury_optimization',
      title: 'Treasury Optimization Recommendation',
      confidence: 0.87,
      decision: 'ADVISORY',
      reasoning: 'Suggests 15% reallocation to stablecoins for risk management',
      timestamp: '15 minutes ago',
      status: 'pending_approval'
    }
  ]);

  const [proposals, setProposals] = useState([
    {
      id: 127,
      title: 'Treasury Rebalancing Strategy',
      description: 'Rebalance treasury allocation across multiple chains',
      elizaAnalysis: {
        recommendation: 'APPROVE',
        confidence: 0.94,
        riskLevel: 'LOW',
        reasoning: 'Excellent risk-reward ratio, improves diversification, aligns with long-term strategy',
        autonomousVote: true
      },
      votes: { for: 1247, against: 23, abstain: 45 },
      status: 'active',
      timeLeft: '2 days 14 hours'
    },
    {
      id: 128,
      title: 'Cross-Chain Bridge Upgrade',
      description: 'Upgrade LayerZero integration for better security',
      elizaAnalysis: {
        recommendation: 'APPROVE',
        confidence: 0.91,
        riskLevel: 'MEDIUM',
        reasoning: 'Security improvements outweigh upgrade risks, thorough audit completed',
        autonomousVote: true
      },
      votes: { for: 892, against: 156, abstain: 78 },
      status: 'active',
      timeLeft: '4 days 8 hours'
    }
  ]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'executed': return 'bg-green-100 text-green-800';
      case 'pending_approval': return 'bg-yellow-100 text-yellow-800';
      case 'monitoring': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDecisionColor = (decision) => {
    switch (decision) {
      case 'APPROVE': return 'text-green-600';
      case 'REJECT': return 'text-red-600';
      case 'ADVISORY': return 'text-yellow-600';
      case 'AUTONOMOUS': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* ElizaOS Status Header */}
      <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Bot className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold">Autonomous ElizaOS</span>
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
              <Brain className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">AI Model</p>
                <p className="font-semibold">{elizaStatus.model}</p>
                {elizaStatus.gpt5Ready && (
                  <Badge className="text-xs bg-purple-100 text-purple-800">GPT-5 Ready</Badge>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Confidence</p>
                <p className="font-semibold">{(elizaStatus.confidence * 100).toFixed(1)}%</p>
                <Progress value={elizaStatus.confidence * 100} className="w-16 h-2" />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Zap className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm text-gray-600">Actions Today</p>
                <p className="font-semibold">{elizaStatus.actionsToday}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Clock className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Last Action</p>
                <p className="font-semibold">{elizaStatus.lastAction}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Autonomous Actions Feed */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Recent Autonomous Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {autonomousActions.map((action) => (
              <div key={action.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold">{action.title}</h4>
                      <Badge className={getStatusColor(action.status)}>
                        {action.status.replace('_', ' ').toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{action.reasoning}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>Confidence: {(action.confidence * 100).toFixed(1)}%</span>
                      <span>Decision: <span className={getDecisionColor(action.decision)}>{action.decision}</span></span>
                      <span>{action.timestamp}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {action.status === 'executed' ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-yellow-600" />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Autonomous Proposal Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            ElizaOS Proposal Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {proposals.map((proposal) => (
              <div key={proposal.id} className="border rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">#{proposal.id}: {proposal.title}</h3>
                    <p className="text-gray-600 mb-3">{proposal.description}</p>
                    <Badge className="bg-blue-100 text-blue-800">
                      Time Left: {proposal.timeLeft}
                    </Badge>
                  </div>
                </div>

                {/* ElizaOS Analysis */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Bot className="h-5 w-5 text-blue-600" />
                    <span className="font-semibold text-blue-800">ElizaOS Analysis</span>
                    <Badge className={`${proposal.elizaAnalysis.autonomousVote ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {proposal.elizaAnalysis.autonomousVote ? 'AUTONOMOUS VOTE' : 'ADVISORY'}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                    <div>
                      <p className="text-sm text-gray-600">Recommendation</p>
                      <p className={`font-semibold ${getDecisionColor(proposal.elizaAnalysis.recommendation)}`}>
                        {proposal.elizaAnalysis.recommendation}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Confidence</p>
                      <div className="flex items-center gap-2">
                        <p className="font-semibold">{(proposal.elizaAnalysis.confidence * 100).toFixed(1)}%</p>
                        <Progress value={proposal.elizaAnalysis.confidence * 100} className="w-16 h-2" />
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Risk Level</p>
                      <Badge className={`${proposal.elizaAnalysis.riskLevel === 'LOW' ? 'bg-green-100 text-green-800' : 
                        proposal.elizaAnalysis.riskLevel === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                        {proposal.elizaAnalysis.riskLevel}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded p-3">
                    <p className="text-sm"><strong>AI Reasoning:</strong> {proposal.elizaAnalysis.reasoning}</p>
                  </div>
                </div>

                {/* Voting Results */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{proposal.votes.for.toLocaleString()}</p>
                    <p className="text-sm text-gray-600">For</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-600">{proposal.votes.against.toLocaleString()}</p>
                    <p className="text-sm text-gray-600">Against</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-600">{proposal.votes.abstain.toLocaleString()}</p>
                    <p className="text-sm text-gray-600">Abstain</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* GPT-5 Migration Alert */}
      <Alert className="border-purple-200 bg-purple-50">
        <AlertTriangle className="h-4 w-4 text-purple-600" />
        <AlertDescription className="text-purple-800">
          <strong>GPT-5 Integration Ready:</strong> ElizaOS is prepared for seamless GPT-5 migration when available. 
          Enhanced reasoning, multimodal support, and improved autonomous decision-making capabilities will be automatically activated.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default AutonomousGovernance;

