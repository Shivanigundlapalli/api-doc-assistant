"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { 
  Plus, 
  MessageSquare, 
  Search, 
  Settings, 
  HelpCircle, 
  LogOut, 
  Moon, 
  Sun, 
  ChevronDown, 
  PanelLeftClose, 
  PanelLeftOpen,
  Library,
  Sparkles
} from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { SidebarItem } from "./sidebar-item"

interface SidebarProps {
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const { setTheme, theme } = useTheme()
  const [isCollectionsOpen, setIsCollectionsOpen] = React.useState(true)

  if (!isOpen) {
    return (
      <div className="flex flex-col h-screen border-r border-border bg-card w-16 items-center py-4 justify-between transition-all duration-300">
        <div className="flex flex-col items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setIsOpen(true)}>
            <PanelLeftOpen className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <Search className="h-5 w-5" />
          </Button>
          <Button variant="default" size="icon" className="rounded-full">
            <Plus className="h-5 w-5" />
          </Button>
        </div>
        <div className="flex flex-col items-center gap-4">
          <Avatar className="h-8 w-8 cursor-pointer">
            <AvatarImage src="" />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen border-r border-border bg-card w-[280px] shrink-0 transition-all duration-300">
      {/* Header */}
      <div className="p-4 flex items-center justify-between">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="w-full justify-start px-2 h-auto py-2 hover:bg-accent">
              <div className="flex items-center gap-3 w-full">
                <div className="h-8 w-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div className="flex flex-col items-start flex-1 text-left">
                  <span className="text-sm font-semibold leading-none">Workspace</span>
                  <span className="text-xs text-muted-foreground mt-1 line-clamp-1">Enterprise Documentation</span>
                </div>
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-[240px]">
            <DropdownMenuLabel>Workspaces</DropdownMenuLabel>
            <DropdownMenuItem>Engineering</DropdownMenuItem>
            <DropdownMenuItem>Product</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <Plus className="mr-2 h-4 w-4" />
              <span>Create Workspace</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button variant="ghost" size="icon" className="shrink-0 ml-1" onClick={() => setIsOpen(false)}>
          <PanelLeftClose className="h-5 w-5 text-muted-foreground" />
        </Button>
      </div>

      <div className="px-4 pb-2">
        <Button 
          variant="outline" 
          className="w-full justify-start text-muted-foreground bg-background hover:bg-accent hover:text-accent-foreground border-border"
        >
          <Search className="mr-2 h-4 w-4 shrink-0" />
          <span className="flex-1 text-left">Search...</span>
          <kbd className="hidden md:inline-flex h-5 items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
            <span className="text-xs">⌘</span>K
          </kbd>
        </Button>
      </div>

      <div className="px-4 py-2">
        <Button className="w-full justify-start font-medium" size="sm">
          <Plus className="mr-2 h-4 w-4 shrink-0" />
          New Chat
        </Button>
      </div>

      {/* Scrollable Content */}
      <ScrollArea className="flex-1 px-3">
        <div className="space-y-6 py-4">
          
          {/* Recent Chats */}
          <div>
            <h4 className="px-2 text-xs font-semibold text-muted-foreground mb-2 tracking-wider uppercase">Today</h4>
            <div className="space-y-[2px]">
              <SidebarItem icon={MessageSquare} title="Stripe API Integration" isActive hasMenu />
              <SidebarItem icon={MessageSquare} title="Authentication flow" hasMenu />
            </div>
          </div>

          <div>
            <h4 className="px-2 text-xs font-semibold text-muted-foreground mb-2 tracking-wider uppercase">Previous 7 Days</h4>
            <div className="space-y-[2px]">
              <SidebarItem icon={MessageSquare} title="Rate Limiting logic" hasMenu />
              <SidebarItem icon={MessageSquare} title="Database migration" hasMenu />
              <SidebarItem icon={MessageSquare} title="Caching strategy" hasMenu />
            </div>
          </div>

          {/* Collections */}
          <Collapsible
            open={isCollectionsOpen}
            onOpenChange={setIsCollectionsOpen}
            className="w-full space-y-2"
          >
            <div className="flex items-center justify-between px-2">
              <h4 className="text-xs font-semibold text-muted-foreground tracking-wider uppercase">Collections</h4>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 hover:bg-transparent">
                  <ChevronDown className={cn("h-4 w-4 text-muted-foreground transition-transform duration-200", isCollectionsOpen ? "" : "-rotate-90")} />
                  <span className="sr-only">Toggle</span>
                </Button>
              </CollapsibleTrigger>
            </div>
            <CollapsibleContent className="space-y-[2px]">
              <SidebarItem icon={Library} title="Authentication Docs" />
              <SidebarItem icon={Library} title="Rate Limits Docs" />
              <SidebarItem icon={Library} title="OpenAPI Spec" />
              <SidebarItem icon={Library} title="SDK Guides" />
            </CollapsibleContent>
          </Collapsible>

        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 mt-auto border-t border-border">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="w-full justify-start px-2 py-6 hover:bg-accent">
              <div className="flex items-center gap-3 w-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="" />
                  <AvatarFallback className="bg-primary/10 text-primary text-xs">U</AvatarFallback>
                </Avatar>
                <div className="flex flex-col items-start flex-1 text-left">
                  <span className="text-sm font-medium leading-none">User Name</span>
                  <span className="text-xs text-muted-foreground mt-1">user@example.com</span>
                </div>
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-[240px]">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              <span>Preferences</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
              {theme === "dark" ? <Sun className="mr-2 h-4 w-4" /> : <Moon className="mr-2 h-4 w-4" />}
              <span>Toggle Theme</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <HelpCircle className="mr-2 h-4 w-4" />
              <span>Help & Support</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive focus:text-destructive">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
