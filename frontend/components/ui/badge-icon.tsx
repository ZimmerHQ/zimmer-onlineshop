import * as React from "react"
import { cn } from "@/lib/utils"

interface BadgeIconProps {
  icon: React.ReactNode
  count?: number
  variant?: 'default' | 'primary' | 'accent' | 'success' | 'warning' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const BadgeIcon = React.forwardRef<HTMLDivElement, BadgeIconProps>(
  ({ icon, count, variant = 'default', size = 'md', className }, ref) => {
    const sizeClasses = {
      sm: 'w-6 h-6 text-xs',
      md: 'w-8 h-8 text-sm',
      lg: 'w-10 h-10 text-base'
    }

    const variantClasses = {
      default: 'bg-white border-gray-200 text-gray-900',
      primary: 'bg-primary-500 text-white',
      accent: 'bg-accent-500 text-bg',
      success: 'bg-success text-white',
      warning: 'bg-warning text-white',
      danger: 'bg-danger text-white'
    }

    return (
      <div
        ref={ref}
        className={cn(
          "relative inline-flex items-center justify-center rounded-lg border",
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
      >
        {icon}
        {count !== undefined && count > 0 && (
          <span className={cn(
            "absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-xs font-medium",
            variant === 'default' ? 'bg-primary-500 text-white' : 'bg-white text-bg'
          )}>
            {count > 99 ? '99+' : count}
          </span>
        )}
      </div>
    )
  }
)
BadgeIcon.displayName = "BadgeIcon"

export { BadgeIcon }
