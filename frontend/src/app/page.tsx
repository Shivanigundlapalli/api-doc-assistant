"use client"

import * as React from "react"
import { Sparkles } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { ChatInput } from "@/components/chat/chat-input"
import { AnswerPage } from "@/components/chat/answer-page"
import { ScrollArea } from "@/components/ui/scroll-area"

export default function EnterpriseChat() {
  const [query, setQuery] = React.useState("")
  const [messages, setMessages] = React.useState<any[]>([])
  const [isStreaming, setIsStreaming] = React.useState(false)

  const handleSubmit = async () => {
    if (!query.trim()) return

    const userMessage = { role: "user", content: query }
    setMessages((prev) => [...prev, userMessage])
    setQuery("")
    setIsStreaming(true)

    try {
      const res = await fetch("http://localhost:8000/api/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage.content }),
      })

      if (!res.body) throw new Error("No response body")
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      
      let assistantMessage: any = { role: "assistant", content: "", metadata: { confidence: 95, latency: "1.2s" }, sources: [] }
      setMessages((prev) => [...prev, assistantMessage])

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          setIsStreaming(false)
          break
        }
        
        const chunk = decoder.decode(value)
        const lines = chunk.split("\n\n")
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "")
            if (dataStr === "[DONE]") {
              setIsStreaming(false)
              break
            }
            try {
              const data = JSON.parse(dataStr)
              if (data.type === "metadata") {
                assistantMessage.metadata = data.content
              } else if (data.type === "content") {
                assistantMessage.content += data.content
              } else if (data.type === "sources") {
                assistantMessage.sources = data.content
              }
              setMessages((prev) => [...prev.slice(0, -1), { ...assistantMessage }])
            } catch (e) {
              console.error(e)
            }
          }
        }
      }
    } catch (err) {
      console.error(err)
      setIsStreaming(false)
    }
  }

  return (
    <AppLayout>
      <div className="flex-1 flex flex-col h-full bg-background relative">
        <ScrollArea className="flex-1">
          <div className="mx-auto w-full max-w-4xl pb-32">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
                <div className="h-16 w-16 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mb-6 border border-primary/20 shadow-sm">
                  <Sparkles className="h-8 w-8" />
                </div>
                <h1 className="text-3xl font-semibold tracking-tight text-foreground mb-3">
                  How can I help you build?
                </h1>
                <p className="text-muted-foreground text-lg mb-8 max-w-md">
                  Ask anything about the documentation, SDKs, or API architecture.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
                  <div 
                    className="p-4 border border-border rounded-xl hover:border-primary/50 hover:bg-accent/50 cursor-pointer transition text-left shadow-sm group"
                    onClick={() => setQuery("How do I implement OAuth2?")}
                  >
                    <span className="font-semibold block mb-1 text-foreground group-hover:text-primary transition-colors">Authentication</span>
                    <span className="text-muted-foreground text-sm">How do I implement OAuth2?</span>
                  </div>
                  <div 
                    className="p-4 border border-border rounded-xl hover:border-primary/50 hover:bg-accent/50 cursor-pointer transition text-left shadow-sm group"
                    onClick={() => setQuery("What are the API rate limits?")}
                  >
                    <span className="font-semibold block mb-1 text-foreground group-hover:text-primary transition-colors">Rate Limits</span>
                    <span className="text-muted-foreground text-sm">What are the API thresholds?</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col">
                {messages.map((msg, i) => (
                  <AnswerPage key={i} message={msg} />
                ))}
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-background via-background to-transparent pt-10 pb-6 px-4 md:px-8">
          <div className="mx-auto w-full max-w-3xl">
            <ChatInput 
              query={query} 
              setQuery={setQuery} 
              onSubmit={handleSubmit} 
              isStreaming={isStreaming} 
            />
            <div className="text-center mt-3 text-xs text-muted-foreground">
              DocuMind AI can make mistakes. Verify critical code before deploying.
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
