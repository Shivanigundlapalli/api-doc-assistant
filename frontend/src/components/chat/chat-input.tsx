"use client"

import * as React from "react"
import { Paperclip, Mic, ArrowUp, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

interface ChatInputProps {
  query: string
  setQuery: (q: string) => void
  onSubmit: () => void
  isStreaming: boolean
}

export function ChatInput({ query, setQuery, onSubmit, isStreaming }: ChatInputProps) {
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)
  const [isRecording, setIsRecording] = React.useState(false)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      onSubmit()
    }
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }

  return (
    <div className="relative border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-sm rounded-xl focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 transition-all p-2 flex flex-col">
      <Textarea
        ref={textareaRef}
        value={query}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about your documentation..."
        disabled={isStreaming}
        className="min-h-[40px] max-h-[200px] border-0 focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent resize-none px-3 py-2 text-base shadow-none mb-10"
        rows={1}
      />
      <div className="absolute bottom-2 left-2 flex items-center gap-1">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button 
                type="button" 
                variant="ghost" 
                size="icon" 
                className="h-10 w-10 text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 rounded-lg transition-colors"
              >
                <Paperclip className="h-5 w-5" />
                <span className="sr-only">Attach documentation</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>Attach documentation</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button 
                type="button" 
                variant="ghost" 
                size="icon" 
                onClick={() => setIsRecording(!isRecording)}
                className={cn(
                  "h-10 w-10 rounded-lg transition-all",
                  isRecording 
                    ? "text-red-500 hover:text-red-600 animate-pulse bg-red-50 dark:bg-red-950/50" 
                    : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
                )}
              >
                <Mic className="h-5 w-5" />
                <span className="sr-only">Voice input</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>Voice input</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
      <div className="absolute bottom-2 right-2">
        <Button
          type="button"
          size="icon"
          disabled={isStreaming || !query.trim()}
          onClick={onSubmit}
          className={cn(
            "h-10 w-10 rounded-xl transition-all shadow-sm",
            query.trim() && !isStreaming ? "bg-black hover:bg-slate-800 text-white dark:bg-white dark:hover:bg-slate-200 dark:text-black" : ""
          )}
        >
          {isStreaming ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <ArrowUp className="h-5 w-5" />
          )}
          <span className="sr-only">Send</span>
        </Button>
      </div>
    </div>
  )
}
