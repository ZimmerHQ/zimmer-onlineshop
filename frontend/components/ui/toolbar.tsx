import * as React from "react"
import { cn } from "@/lib/utils"

interface ToolbarProps {
  children: React.ReactNode
  className?: string
}

const Toolbar = React.forwardRef<HTMLDivElement, ToolbarProps>(
  ({ children, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex items-center justify-between p-4 bg-gray-50 border-b border-gray-200",
          className
        )}
      >
        {children}
      </div>
    )
  }
)
Toolbar.displayName = "Toolbar"

const ToolbarLeft = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("flex items-center space-x-4 space-x-reverse", className)}
        {...props}
      />
    )
  }
)
ToolbarLeft.displayName = "ToolbarLeft"

const ToolbarRight = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("flex items-center space-x-4 space-x-reverse", className)}
        {...props}
      />
    )
  }
)
ToolbarRight.displayName = "ToolbarRight"

export { Toolbar, ToolbarLeft, ToolbarRight }
