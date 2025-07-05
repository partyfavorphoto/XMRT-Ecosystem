import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Brain, Coins, Users, MessageSquare, TrendingUp, Shield } from 'lucide-react'
import './App.css'

function App() {
  const [message, setMessage] = useState('')
  const [proposal, setProposal] = useState('')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">XMRT DAO</h1>
              <Badge variant="secondary">Prototype</Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline">Sepolia Testnet</Badge>
              <Button variant="outline">Connect Wallet</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            The World's First AI-Powered DAO
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-6">
            Powered by Eliza AI for intelligent governance and treasury management
          </p>
          <div className="flex justify-center space-x-4">
            <Card className="w-48">
              <CardContent className="p-4 text-center">
                <Coins className="h-8 w-8 mx-auto mb-2 text-yellow-600" />
                <p className="font-semibold">21M XMRT</p>
                <p className="text-sm text-gray-600">Total Supply</p>
              </CardContent>
            </Card>
            <Card className="w-48">
              <CardContent className="p-4 text-center">
                <Users className="h-8 w-8 mx-auto mb-2 text-green-600" />
                <p className="font-semibold">3 AI Agents</p>
                <p className="text-sm text-gray-600">Active</p>
              </CardContent>
            </Card>
            <Card className="w-48">
              <CardContent className="p-4 text-center">
                <Shield className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                <p className="font-semibold">Sepolia</p>
                <p className="text-sm text-gray-600">Testnet</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Main Interface */}
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="governance">Governance</TabsTrigger>
            <TabsTrigger value="eliza">Chat with Eliza</TabsTrigger>
            <TabsTrigger value="agents">AI Agents</TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Coins className="h-5 w-5 mr-2" />
                    Your Balance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">0 XMRT</p>
                  <p className="text-sm text-gray-600">Connect wallet to view balance</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="h-5 w-5 mr-2" />
                    Staked Amount
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">0 XMRT</p>
                  <p className="text-sm text-gray-600">No active stakes</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Brain className="h-5 w-5 mr-2" />
                    Eliza Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Badge variant="default" className="bg-green-600">Active</Badge>
                  <p className="text-sm text-gray-600 mt-2">AI agent online and ready</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="governance" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Submit Proposal</CardTitle>
                <CardDescription>
                  Describe your proposal in natural language. Eliza will analyze and format it for governance.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Describe your proposal here..."
                  value={proposal}
                  onChange={(e) => setProposal(e.target.value)}
                  className="min-h-32"
                />
                <Button className="w-full">Submit to Eliza for Analysis</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Active Proposals</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">No active proposals. Submit the first one above!</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="eliza" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MessageSquare className="h-5 w-5 mr-2" />
                  Chat with Eliza
                </CardTitle>
                <CardDescription>
                  Ask Eliza about governance, treasury management, or DAO operations.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="h-64 border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                  <p className="text-gray-600 dark:text-gray-400">
                    Eliza: Hello! I'm the AI brain behind XMRT DAO. How can I help you today?
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Input
                    placeholder="Type your message..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="flex-1"
                  />
                  <Button>Send</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="agents" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Governance Agent</CardTitle>
                  <CardDescription>Handles proposals and voting operations</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="default" className="bg-blue-600">Active</Badge>
                  <p className="text-sm text-gray-600 mt-2">Processing governance decisions</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Treasury Agent</CardTitle>
                  <CardDescription>Manages financial operations and yield optimization</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="default" className="bg-green-600">Active</Badge>
                  <p className="text-sm text-gray-600 mt-2">Monitoring treasury performance</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Community Agent</CardTitle>
                  <CardDescription>Handles community interactions and support</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="default" className="bg-purple-600">Active</Badge>
                  <p className="text-sm text-gray-600 mt-2">Providing 24/7 support</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm dark:bg-gray-900/80 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              XMRT DAO Prototype - Powered by Eliza AI
            </p>
            <div className="flex space-x-4">
              <Badge variant="outline">Contract: 0x77307...a15</Badge>
              <Badge variant="outline">Sepolia Testnet</Badge>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
