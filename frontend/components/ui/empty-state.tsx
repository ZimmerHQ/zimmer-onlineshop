import * as React from "react"
import { cn } from "@/lib/utils"

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ icon, title, description, action, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex flex-col items-center justify-center py-12 px-6 text-center",
          className
        )}
      >
        {icon && (
          <div className="mb-4 p-4 bg-gray-100 rounded-full">
            {icon}
          </div>
        )}
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {title}
        </h3>
        {description && (
          <p className="text-gray-600 mb-6 max-w-md">
            {description}
          </p>
        )}
        {action && (
          <div className="flex justify-center">
            {action}
          </div>
        )}
      </div>
    )
  }
)
EmptyState.displayName = "EmptyState"

export { EmptyState }
