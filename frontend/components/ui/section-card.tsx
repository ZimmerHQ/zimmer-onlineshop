import * as React from "react"
import { cn } from "@/lib/utils"

interface SectionCardProps {
  title: string
  children: React.ReactNode
  action?: React.ReactNode
  className?: string
}

const SectionCard = React.forwardRef<HTMLDivElement, SectionCardProps>(
  ({ title, children, action, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-xl border border-black/5 bg-white shadow-sm dark:bg-neutral-900 dark:border-white/5",
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 md:p-5 pb-2 mb-3 border-b border-black/5">
          <h3 className="text-lg md:text-xl font-semibold">{title}</h3>
          {action && (
            <div className="flex items-center">
              {action}
            </div>
          )}
        </div>
        
        {/* Body */}
        <div className="p-4 md:p-5 pt-0">
          {children}
        </div>
      </div>
    )
  }
)
SectionCard.displayName = "SectionCard"

export { SectionCard }
