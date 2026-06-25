"use client"

import * as React from "react"
import { CheckCircle2, AlertTriangle, Book, Sparkles, TerminalSquare, Copy, Share, ThumbsUp, ThumbsDown } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"

interface AnswerPageProps {
  message: {
    role: "user" | "assistant"
    content: string
    metadata?: any
    sources?: any[]
  }
}

export function AnswerPage({ message }: AnswerPageProps) {
  if (message.role === "user") {
    return (
      <div className="flex gap-4 py-6 px-4 md:px-8">
        <Avatar className="h-8 w-8 border">
          <AvatarFallback className="bg-background text-xs font-semibold">U</AvatarFallback>
        </Avatar>
        <div className="flex-1 mt-1 font-medium text-base text-foreground leading-relaxed">
          {message.content}
        </div>
      </div>
    )
  }

  // Basic parsing logic
  const isLowConfidence = message.metadata?.confidence < 50
  const isNotFound = message.content.toLowerCase().includes("not found") || message.content.toLowerCase().includes("no supporting documentation")
  const hideToolbar = isLowConfidence || isNotFound || message.sources?.length === 0

  return (
    <div className="flex gap-4 py-6 px-4 md:px-8 border-t border-border/50 bg-muted/20">
      <div className="h-8 w-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0 border border-primary/20 mt-1">
        <Sparkles className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0 space-y-4">
        {/* Metadata Header */}
        {message.metadata && !isNotFound && (
          <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
            <Badge variant={message.metadata.confidence >= 90 ? "default" : isLowConfidence ? "destructive" : "secondary"} className="gap-1 rounded-sm px-2 font-medium">
              <CheckCircle2 className="h-3 w-3" />
              Confidence: {message.metadata.confidence}%
            </Badge>
            <span className="flex items-center gap-1"><Book className="h-3 w-3" /> {message.sources?.length || 0} Sources</span>
            <span>{message.metadata.latency}</span>
          </div>
        )}

        {/* Empty State / Not Found */}
        {isNotFound ? (
          <div className="space-y-4">
            <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-4 py-4 rounded-xl">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 mb-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" />
                No supporting documentation found.
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
                We couldn't find an exact match in your current knowledge base.
              </p>
              
              <div className="space-y-2">
                <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Try asking:</p>
                <ul className="text-sm text-blue-600 dark:text-blue-400 space-y-1.5 list-disc pl-5">
                  <li className="cursor-pointer hover:underline">How do I authenticate?</li>
                  <li className="cursor-pointer hover:underline">What are the rate limits?</li>
                  <li className="cursor-pointer hover:underline">Why am I getting 401?</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <>
            {isLowConfidence && (
              <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 text-amber-800 dark:text-amber-200 px-4 py-3 rounded-lg flex gap-3 text-sm">
                <AlertTriangle className="h-5 w-5 shrink-0" />
                <p>I could not confidently find this information in the documentation. The following is a best-effort answer.</p>
              </div>
            )}

            {/* Main Content */}
            <div className="text-base text-foreground leading-7 whitespace-pre-wrap">
              {message.content || <span className="animate-pulse">Thinking...</span>}
            </div>

            {/* Developer Actions Mockup */}
            {message.content.includes("Action:") && (
              <div className="mt-6 border border-border rounded-lg overflow-hidden">
                <div className="bg-muted px-4 py-2 border-b border-border flex items-center gap-2">
                  <TerminalSquare className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-semibold">Developer Actions</span>
                </div>
                <div className="p-4 bg-card text-sm text-muted-foreground">
                  Run the following command to proceed.
                </div>
              </div>
            )}
          </>
        )}

        {/* Action Toolbar */}
        {!hideToolbar && message.content && (
          <div className="flex items-center gap-2 pt-2 mt-4">
            <Button variant="ghost" size="sm" className="h-8 text-muted-foreground hover:text-foreground hover:bg-slate-100 dark:hover:bg-slate-800">
              <Copy className="mr-1.5 h-3.5 w-3.5" />
              Copy
            </Button>
            <Button variant="ghost" size="sm" className="h-8 text-muted-foreground hover:text-foreground hover:bg-slate-100 dark:hover:bg-slate-800">
              <Share className="mr-1.5 h-3.5 w-3.5" />
              Share
            </Button>
            <div className="h-4 w-[1px] bg-border mx-1" />
            <Button variant="ghost" size="sm" className="h-8 px-2 text-muted-foreground hover:text-foreground hover:bg-slate-100 dark:hover:bg-slate-800">
              <ThumbsUp className="h-3.5 w-3.5" />
              <span className="sr-only">Thumbs up</span>
            </Button>
            <Button variant="ghost" size="sm" className="h-8 px-2 text-muted-foreground hover:text-foreground hover:bg-slate-100 dark:hover:bg-slate-800">
              <ThumbsDown className="h-3.5 w-3.5" />
              <span className="sr-only">Thumbs down</span>
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
