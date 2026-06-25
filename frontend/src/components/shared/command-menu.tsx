"use client"

import * as React from "react"
import { MessageSquare, FileText, Folder, Settings, Search } from "lucide-react"

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"

export function CommandMenu() {
  const [open, setOpen] = React.useState(false)

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Recent Chats">
          <CommandItem>
            <MessageSquare className="mr-2 h-4 w-4 text-muted-foreground" />
            <span>Stripe API Integration</span>
          </CommandItem>
          <CommandItem>
            <MessageSquare className="mr-2 h-4 w-4 text-muted-foreground" />
            <span>Authentication flow</span>
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Documents">
          <CommandItem>
            <FileText className="mr-2 h-4 w-4 text-muted-foreground" />
            <span>OAuth2 Setup Guide</span>
          </CommandItem>
          <CommandItem>
            <FileText className="mr-2 h-4 w-4 text-muted-foreground" />
            <span>Rate limits and errors</span>
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Collections">
          <CommandItem>
            <Folder className="mr-2 h-4 w-4 text-muted-foreground" />
            <span>Core API V2</span>
          </CommandItem>
          <CommandItem>
            <Folder className="mr-2 h-4 w-4 text-muted-foreground" />
            <span>Admin Dashboard</span>
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Settings">
          <CommandItem>
            <Settings className="mr-2 h-4 w-4 text-muted-foreground" />
            <span>Preferences</span>
            <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
              <span className="text-xs">⌘</span>S
            </kbd>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
