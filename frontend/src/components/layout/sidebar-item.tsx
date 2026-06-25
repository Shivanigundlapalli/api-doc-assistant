import * as React from "react"
import { cn } from "@/lib/utils"
import { MoreHorizontal, Pin, Pencil, Trash2, type LucideIcon } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

interface SidebarItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: LucideIcon
  title: string
  isActive?: boolean
  hasMenu?: boolean
}

export function SidebarItem({
  icon: Icon,
  title,
  isActive,
  hasMenu,
  className,
  ...props
}: SidebarItemProps) {
  return (
    <div className={cn("group flex items-center relative rounded-md", className)}>
      <button
        className={cn(
          "flex-1 flex items-center gap-2.5 px-2.5 py-1.5 text-sm rounded-md transition-colors text-muted-foreground hover:bg-accent hover:text-accent-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring",
          isActive && "bg-accent/50 text-foreground font-medium"
        )}
        {...props}
      >
        {Icon && <Icon className="h-4 w-4 shrink-0 opacity-70" />}
        <span className="truncate text-left">{title}</span>
      </button>

      {hasMenu && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity data-[state=open]:opacity-100"
            >
              <MoreHorizontal className="h-4 w-4" />
              <span className="sr-only">More options</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem>
              <Pencil className="mr-2 h-4 w-4" />
              <span>Rename</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Pin className="mr-2 h-4 w-4" />
              <span>Pin</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive focus:text-destructive">
              <Trash2 className="mr-2 h-4 w-4" />
              <span>Delete</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  )
}
