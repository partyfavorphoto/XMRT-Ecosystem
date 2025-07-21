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
  Sparkles
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
    lastAction: 'Analyzed governance proposal'
  });
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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
        lastAction: `Responded to ${elizaResponse.context} query`
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
      case 'governance': return <Settings className="h-4 w-4" />;
      case 'trading': return <TrendingUp className="h-4 w-4" />;
      case 'privacy': return <Shield className="h-4 w-4" />;
      case 'memory': return <Database className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  const getContextColor = (context) => {
    switch (context) {
      case 'governance': return 'bg-blue-100 text-blue-800';
      case 'trading': return 'bg-green-100 text-green-800';
      case 'privacy': return 'bg-purple-100 text-purple-800';
      case 'memory': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const quickActions = [
    { label: 'Governance Status', query: 'What is the current governance status?' },
    { label: 'Trading Insights', query: 'Show me current trading opportunities' },
    { label: 'Privacy Check', query: 'How is my privacy protection?' },
    { label: 'System Status', query: 'What is the current system status?' }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Eliza Status Header */}
      <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Eliza AI Assistant</h3>
                <p className="text-sm text-gray-600">ElizaOS v1.2.9 with XMRT Memory Integration</p>
              </div>
            </div>
            <Badge className="bg-green-100 text-green-800 border-green-300">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Online
              </div>
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Cpu className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Confidence</span>
              </div>
              <p className="text-lg font-bold text-blue-600">{(elizaStatus.confidence * 100).toFixed(1)}%</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Database className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-medium">Memory</span>
              </div>
              <p className="text-lg font-bold text-purple-600">{elizaStatus.memoryItems.toLocaleString()}</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Network className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium">Agents</span>
              </div>
              <p className="text-lg font-bold text-green-600">{elizaStatus.activeAgents}</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Clock className="h-4 w-4 text-indigo-600" />
                <span className="text-sm font-medium">Last Action</span>
              </div>
              <p className="text-xs text-indigo-600 font-medium">{elizaStatus.lastAction}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Chat Interface */}
      <Card className="h-[600px] flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Chat with Eliza
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col p-0">
          {/* Messages Area */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {message.type === 'eliza' && (
                        <Bot className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                      )}
                      {message.type === 'user' && (
                        <User className="h-5 w-5 text-white mt-0.5 flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <p className="text-sm">{message.content}</p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs opacity-70">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                          {message.type === 'eliza' && (
                            <div className="flex items-center gap-2">
                              {message.context && (
                                <Badge className={`text-xs ${getContextColor(message.context)}`}>
                                  <div className="flex items-center gap-1">
                                    {getContextIcon(message.context)}
                                    {message.context}
                                  </div>
                                </Badge>
                              )}
                              {message.confidence && (
                                <span className="text-xs opacity-70">
                                  {(message.confidence * 100).toFixed(0)}%
                                </span>
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
                  <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                    <div className="flex items-center gap-2">
                      <Bot className="h-5 w-5 text-blue-600" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-sm text-gray-600">Eliza is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Quick Actions */}
          <div className="p-4 border-t bg-gray-50">
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-2">Quick Actions:</p>
              <div className="flex flex-wrap gap-2">
                {quickActions.map((action, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => setInputMessage(action.query)}
                    className="text-xs"
                  >
                    <Sparkles className="h-3 w-3 mr-1" />
                    {action.label}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* Input Area */}
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Eliza about governance, trading, privacy, or anything else..."
                className="flex-1"
                disabled={isTyping}
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isTyping}
                className="px-4"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Capabilities Info */}
      <Alert className="border-blue-200 bg-blue-50">
        <Brain className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>Eliza's Capabilities:</strong> I can help with autonomous governance analysis, intelligent trading insights, 
          privacy optimization, community management, cross-chain operations, and more. My responses are powered by 
          ElizaOS v1.2.9 with advanced memory integration using XMRT Langchain and Langflow.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default ElizaChatbot;

