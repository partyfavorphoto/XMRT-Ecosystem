import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Send, Bot, User, Loader2, MessageCircle, Sparkles } from 'lucide-react'

const API_BASE_URL = 'http://localhost:5000/api/eliza'

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [suggestedQuestions, setSuggestedQuestions] = useState([])
  const [showWelcome, setShowWelcome] = useState(true)
  const [investorInfo, setInvestorInfo] = useState({
    name: '',
    email: '',
    company: ''
  })
  
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const startConversation = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${API_BASE_URL}/start-conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(investorInfo)
      })

      const data = await response.json()
      
      if (data.success) {
        setSessionId(data.session_id)
        setMessages([{
          id: 1,
          role: 'assistant',
          content: data.welcome_message,
          timestamp: new Date().toISOString()
        }])
        setSuggestedQuestions(data.suggested_questions || [])
        setShowWelcome(false)
      } else {
        console.error('Failed to start conversation:', data.error)
      }
    } catch (error) {
      console.error('Error starting conversation:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const sendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || !sessionId || isLoading) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/send-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: messageText
        })
      })

      const data = await response.json()
      
      if (data.success) {
        const assistantMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString(),
          metadata: data.metadata
        }

        setMessages(prev => [...prev, assistantMessage])
        setSuggestedQuestions(data.suggested_questions || [])
      } else {
        console.error('Failed to send message:', data.error)
        // Add error message
        const errorMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'I apologize, but I encountered an error. Please try again.',
          timestamp: new Date().toISOString(),
          isError: true
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'I apologize, but I encountered a connection error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleSuggestedQuestion = (question) => {
    sendMessage(question)
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  if (showWelcome) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Welcome to XMRT DAO
            </CardTitle>
            <p className="text-muted-foreground mt-2">
              Chat with Eliza, your AI guide to our revolutionary ecosystem
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <Input
                placeholder="Your name (optional)"
                value={investorInfo.name}
                onChange={(e) => setInvestorInfo(prev => ({ ...prev, name: e.target.value }))}
              />
              <Input
                placeholder="Email (optional)"
                type="email"
                value={investorInfo.email}
                onChange={(e) => setInvestorInfo(prev => ({ ...prev, email: e.target.value }))}
              />
              <Input
                placeholder="Company (optional)"
                value={investorInfo.company}
                onChange={(e) => setInvestorInfo(prev => ({ ...prev, company: e.target.value }))}
              />
            </div>
            <Button 
              onClick={startConversation} 
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Starting conversation...
                </>
              ) : (
                <>
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Start Chat with Eliza
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto max-w-4xl h-screen flex flex-col p-4">
        {/* Header */}
        <Card className="mb-4">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-xl">Eliza - XMRT DAO AI Assistant</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Your guide to autonomous organizations and AI governance
                </p>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Chat Messages */}
        <Card className="flex-1 flex flex-col">
          <CardContent className="flex-1 p-0">
            <ScrollArea className="h-full p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                          : message.isError
                          ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                          : 'bg-muted'
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.role === 'assistant' && (
                          <Bot className="w-5 h-5 mt-0.5 flex-shrink-0" />
                        )}
                        {message.role === 'user' && (
                          <User className="w-5 h-5 mt-0.5 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <p className="whitespace-pre-wrap">{message.content}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className={`text-xs ${
                              message.role === 'user' ? 'text-blue-100' : 'text-muted-foreground'
                            }`}>
                              {formatTimestamp(message.timestamp)}
                            </span>
                            {message.metadata && (
                              <div className="flex space-x-1">
                                {message.metadata.model_used && (
                                  <Badge variant="outline" className="text-xs">
                                    {message.metadata.model_used}
                                  </Badge>
                                )}
                                {message.metadata.response_time_ms && (
                                  <Badge variant="outline" className="text-xs">
                                    {message.metadata.response_time_ms}ms
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-lg p-3 max-w-[80%]">
                      <div className="flex items-center space-x-2">
                        <Bot className="w-5 h-5" />
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </ScrollArea>
          </CardContent>

          {/* Suggested Questions */}
          {suggestedQuestions.length > 0 && (
            <>
              <Separator />
              <div className="p-4">
                <p className="text-sm text-muted-foreground mb-2">Suggested questions:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestedQuestions.map((question, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => handleSuggestedQuestion(question)}
                      disabled={isLoading}
                      className="text-xs"
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Input Area */}
          <Separator />
          <div className="p-4">
            <div className="flex space-x-2">
              <Input
                ref={inputRef}
                placeholder="Ask Eliza about XMRT DAO..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={() => sendMessage()}
                disabled={isLoading || !inputMessage.trim()}
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

