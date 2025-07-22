import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Bot, 
  Send, 
  User, 
  Brain, 
  Zap, 
  Shield, 
  TrendingUp, 
  Users, 
  Settings,
  MessageCircle,
  Cpu,
  Database,
  Network,
  CheckCircle,
  AlertTriangle,
  Clock,
  Sparkles,
  Activity,
  Eye,
  Lock
} from 'lucide-react';

const ElizaChatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'eliza',
      content: "Hello! I'm Eliza, your autonomous DAO assistant powered by ElizaOS v1.2.9 with advanced memory integration. I can help you with governance, trading, privacy operations, and more. What would you like to know?",
      timestamp: new Date(),
      confidence: 0.95,
      context: 'greeting'
    }
  ]);
  
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [elizaStatus, setElizaStatus] = useState({
    online: true,
    confidence: 0.94,
    memoryItems: 15847,
    activeAgents: 3,
    lastAction: 'Analyzed governance proposal',
    actionsToday: 247,
    successRate: 0.91
  });
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Simulate real-time status updates
  useEffect(() => {
    const interval = setInterval(() => {
      setElizaStatus(prev => ({
        ...prev,
        confidence: 0.88 + Math.random() * 0.1,
        actionsToday: prev.actionsToday + Math.floor(Math.random() * 3),
        memoryItems: prev.memoryItems + Math.floor(Math.random() * 5)
      }));
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  // Simulate Eliza responses with different contexts
  const elizaResponses = {
    governance: {
      keywords: ['proposal', 'vote', 'governance', 'dao', 'treasury', 'decision'],
      responses: [
        "I've analyzed the current governance proposals. Proposal #127 for treasury rebalancing shows strong community support with 94% confidence. Would you like me to provide detailed analysis?",
        "Based on my governance memory, similar proposals have had an 87% success rate. I can help you understand the voting patterns and community sentiment.",
        "I'm currently monitoring 12 active proposals across the DAO. My autonomous governance agent has processed 247 governance actions today with 91% success rate."
      ]
    },
    trading: {
      keywords: ['trade', 'swap', 'price', 'market', 'liquidity', 'defi', 'profit'],
      responses: [
        "My trading analysis shows XMRT/USDC has optimal liquidity for swaps. I've executed 156 trades today with 87% win rate and $8,947 profit. Would you like current market insights?",
        "Based on my market memory patterns, I detect a bullish trend forming. My autonomous trading agent suggests portfolio rebalancing. Shall I provide specific recommendations?",
        "I'm monitoring cross-chain arbitrage opportunities across 6 networks. Current best opportunity shows 2.3% profit potential on Polygon-Arbitrum bridge."
      ]
    },
    privacy: {
      keywords: ['privacy', 'monero', 'anonymous', 'mobile', 'mixing', 'security'],
      responses: [
        "MobileMonero privacy optimization is active with 98% privacy score. I've processed 234 private transactions today with 8 mixing rounds average. Your privacy is secured.",
        "My privacy agent has detected optimal routing paths for anonymous transactions. Current network congestion is low, perfect for high-privacy operations.",
        "Mobile mining privacy features are enhanced with autonomous routing. I can help optimize your privacy settings for maximum anonymity."
      ]
    },
    memory: {
      keywords: ['memory', 'learn', 'remember', 'history', 'context', 'langchain'],
      responses: [
        "My memory system contains 15,847 contextual items using XMRT Langchain integration. I remember our previous conversations and learn from each interaction.",
        "Through Langflow workflows, I've identified patterns in your preferences. My semantic search capabilities help me provide more relevant responses over time.",
        "I maintain long-term memory across all DAO operations. This allows me to provide context-aware decisions and learn from historical patterns."
      ]
    },
    general: {
      keywords: ['help', 'what', 'how', 'status', 'info', 'about'],
      responses: [
        "I'm your autonomous DAO assistant with full access to governance, trading, privacy, and community management systems. I operate with 94% confidence and learn from every interaction.",
        "My capabilities include: autonomous governance analysis, intelligent trading, privacy optimization, community management, and cross-chain operations. What interests you most?",
        "I'm powered by ElizaOS v1.2.9 with advanced memory integration. I can help with any aspect of the XMRT ecosystem. Just ask me anything!"
      ]
    }
  };

  const getElizaResponse = (userMessage) => {
    const message = userMessage.toLowerCase();
    
    // Find matching context
    for (const [context, data] of Object.entries(elizaResponses)) {
      if (data.keywords.some(keyword => message.includes(keyword))) {
        const responses = data.responses;
        const response = responses[Math.floor(Math.random() * responses.length)];
        return {
          content: response,
          context: context,
          confidence: 0.85 + Math.random() * 0.1
        };
      }
    }
    
    // Default response
    const generalResponses = elizaResponses.general.responses;
    return {
      content: generalResponses[Math.floor(Math.random() * generalResponses.length)],
      context: 'general',
      confidence: 0.75 + Math.random() * 0.15
    };
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate Eliza thinking time
    setTimeout(() => {
      const elizaResponse = getElizaResponse(inputMessage);
      
      const elizaMessage = {
        id: Date.now() + 1,
        type: 'eliza',
        content: elizaResponse.content,
        timestamp: new Date(),
        confidence: elizaResponse.confidence,
        context: elizaResponse.context
      };

      setMessages(prev => [...prev, elizaMessage]);
      setIsTyping(false);
      
      // Update Eliza status
      setElizaStatus(prev => ({
        ...prev,
        confidence: elizaResponse.confidence,
        lastAction: `Responded to ${elizaResponse.context} query`,
        actionsToday: prev.actionsToday + 1
      }));
    }, 1000 + Math.random() * 2000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getContextIcon = (context) => {
    switch (context) {
      case 'governance': return <Settings className="h-3 w-3" />;
      case 'trading': return <TrendingUp className="h-3 w-3" />;
      case 'privacy': return <Shield className="h-3 w-3" />;
      case 'memory': return <Database className="h-3 w-3" />;
      default: return <Brain className="h-3 w-3" />;
    }
  };

  const getContextColor = (context) => {
    switch (context) {
      case 'governance': return 'bg-gradient-to-r from-blue-500 to-blue-600 text-white border-0';
      case 'trading': return 'bg-gradient-to-r from-green-500 to-green-600 text-white border-0';
      case 'privacy': return 'bg-gradient-to-r from-purple-500 to-purple-600 text-white border-0';
      case 'memory': return 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white border-0';
      default: return 'bg-gradient-to-r from-gray-500 to-gray-600 text-white border-0';
    }
  };

  const quickActions = [
    { label: 'Governance Status', query: 'What is the current governance status?', icon: Settings, color: 'from-blue-500 to-blue-600' },
    { label: 'Trading Insights', query: 'Show me current trading opportunities', icon: TrendingUp, color: 'from-green-500 to-green-600' },
    { label: 'Privacy Check', query: 'How is my privacy protection?', icon: Shield, color: 'from-purple-500 to-purple-600' },
    { label: 'System Status', query: 'What is the current system status?', icon: Activity, color: 'from-indigo-500 to-indigo-600' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4 md:p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Enhanced Eliza Status Header */}
        <Card className="border-0 shadow-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 text-white overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/90 via-purple-600/90 to-indigo-700/90"></div>
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-32 translate-x-32"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-24 -translate-x-24"></div>
          
          <CardHeader className="relative z-10">
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-white/20 to-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/20">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold mb-1">Eliza AI Assistant</h3>
                  <p className="text-blue-100 font-medium">ElizaOS v1.2.9 with XMRT Memory Integration</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge className="bg-green-500/20 text-green-100 border-green-400/30 backdrop-blur-sm px-3 py-1">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="font-semibold">Online</span>
                  </div>
                </Badge>
              </div>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="relative z-10">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                    <Cpu className="h-4 w-4 text-blue-200" />
                  </div>
                  <span className="text-sm font-medium text-blue-100">Confidence</span>
                </div>
                <p className="text-2xl font-bold text-white">{(elizaStatus.confidence * 100).toFixed(1)}%</p>
                <div className="w-full bg-white/20 rounded-full h-2 mt-2">
                  <div 
                    className="bg-gradient-to-r from-green-400 to-blue-400 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${elizaStatus.confidence * 100}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                    <Database className="h-4 w-4 text-purple-200" />
                  </div>
                  <span className="text-sm font-medium text-purple-100">Memory</span>
                </div>
                <p className="text-2xl font-bold text-white">{elizaStatus.memoryItems.toLocaleString()}</p>
                <p className="text-xs text-purple-200 mt-1">Contextual Items</p>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                    <Activity className="h-4 w-4 text-green-200" />
                  </div>
                  <span className="text-sm font-medium text-green-100">Actions Today</span>
                </div>
                <p className="text-2xl font-bold text-white">{elizaStatus.actionsToday}</p>
                <p className="text-xs text-green-200 mt-1">{(elizaStatus.successRate * 100).toFixed(0)}% Success Rate</p>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                    <Network className="h-4 w-4 text-indigo-200" />
                  </div>
                  <span className="text-sm font-medium text-indigo-100">Active Agents</span>
                </div>
                <p className="text-2xl font-bold text-white">{elizaStatus.activeAgents}</p>
                <p className="text-xs text-indigo-200 mt-1">{elizaStatus.lastAction}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Chat Interface */}
        <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-slate-50 to-blue-50 border-b border-slate-200">
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <MessageCircle className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-800">Chat with Eliza</h3>
                <p className="text-sm text-slate-600">Autonomous DAO Assistant</p>
              </div>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="p-0">
            {/* Messages Area */}
            <ScrollArea className="h-[500px] p-6">
              <div className="space-y-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl p-4 shadow-lg ${
                        message.type === 'user'
                          ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white ml-12'
                          : 'bg-gradient-to-br from-white to-slate-50 text-slate-800 border border-slate-200 mr-12'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {message.type === 'eliza' && (
                          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                            <Bot className="h-4 w-4 text-white" />
                          </div>
                        )}
                        {message.type === 'user' && (
                          <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                            <User className="h-4 w-4 text-white" />
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="text-sm leading-relaxed">{message.content}</p>
                          <div className="flex items-center justify-between mt-3">
                            <span className={`text-xs ${message.type === 'user' ? 'text-blue-100' : 'text-slate-500'}`}>
                              {message.timestamp.toLocaleTimeString()}
                            </span>
                            {message.type === 'eliza' && (
                              <div className="flex items-center gap-2">
                                {message.context && (
                                  <Badge className={`text-xs ${getContextColor(message.context)} shadow-sm`}>
                                    <div className="flex items-center gap-1">
                                      {getContextIcon(message.context)}
                                      <span className="capitalize">{message.context}</span>
                                    </div>
                                  </Badge>
                                )}
                                {message.confidence && (
                                  <div className="flex items-center gap-1">
                                    <Eye className="h-3 w-3 text-slate-400" />
                                    <span className="text-xs text-slate-500 font-medium">
                                      {(message.confidence * 100).toFixed(0)}%
                                    </span>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-2xl p-4 max-w-[80%] shadow-lg mr-12">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                          <Bot className="h-4 w-4 text-white" />
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                          <span className="text-sm text-slate-600 font-medium">Eliza is thinking...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Enhanced Quick Actions */}
            <div className="p-6 bg-gradient-to-r from-slate-50 to-blue-50 border-t border-slate-200">
              <div className="mb-4">
                <p className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-blue-600" />
                  Quick Actions
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                  {quickActions.map((action, index) => {
                    const IconComponent = action.icon;
                    return (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => setInputMessage(action.query)}
                        className={`bg-gradient-to-r ${action.color} text-white border-0 hover:shadow-lg hover:scale-105 transition-all duration-200 h-auto py-3 px-4`}
                      >
                        <div className="flex items-center gap-2">
                          <IconComponent className="h-4 w-4" />
                          <span className="text-xs font-medium">{action.label}</span>
                        </div>
                      </Button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Enhanced Input Area */}
            <div className="p-6 bg-white border-t border-slate-200">
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <Input
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask Eliza about governance, trading, privacy, or anything else..."
                    className="pr-12 h-12 border-2 border-slate-200 focus:border-blue-500 rounded-xl bg-slate-50 focus:bg-white transition-all duration-200"
                    disabled={isTyping}
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <Lock className="h-4 w-4 text-slate-400" />
                  </div>
                </div>
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                  className="h-12 px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 border-0 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
                >
                  {isTyping ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    </div>
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Capabilities Info */}
        <Alert className="border-0 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Brain className="h-4 w-4 text-white" />
          </div>
          <AlertDescription className="text-slate-700 ml-4">
            <div className="space-y-2">
              <p className="font-semibold text-slate-800">🤖 Eliza's Advanced Capabilities</p>
              <p className="text-sm leading-relaxed">
                I can help with <span className="font-medium text-blue-700">autonomous governance analysis</span>, 
                <span className="font-medium text-green-700"> intelligent trading insights</span>, 
                <span className="font-medium text-purple-700"> privacy optimization</span>, 
                <span className="font-medium text-indigo-700"> community management</span>, and 
                <span className="font-medium text-slate-700"> cross-chain operations</span>. 
                My responses are powered by <span className="font-bold">ElizaOS v1.2.9</span> with advanced memory integration using XMRT Langchain and Langflow.
              </p>
            </div>
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
};

export default ElizaChatbot;

