import * as React from "react"
import { cn } from "@/lib/utils"
import { TrendingUp, TrendingDown } from "lucide-react"

interface KpiProps {
  label: string
  value: string | number
  caption?: string
  trend?: {
    value: number
    label: string
  }
  icon?: React.ReactNode
  className?: string
}

const Kpi = React.forwardRef<HTMLDivElement, KpiProps>(
  ({ label, value, caption, trend, icon, className }, ref) => {
    const isPositiveTrend = trend && trend.value > 0
    const isNegativeTrend = trend && trend.value < 0

    return (
      <div
        ref={ref}
        className={cn(
          "zimmer-card p-6 zimmer-hover-lift",
          className
        )}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3 space-x-reverse">
            {icon && (
              <div className="p-2 bg-primary-500/10 rounded-lg">
                {icon}
              </div>
            )}
            <div>
              <p className="text-sm font-medium text-gray-600">{label}</p>
              {caption && (
                <p className="text-xs text-gray-500">{caption}</p>
              )}
            </div>
          </div>
          {trend && (
            <div className={cn(
              "flex items-center space-x-1 space-x-reverse text-xs font-medium",
              isPositiveTrend && "text-success",
              isNegativeTrend && "text-danger",
              !isPositiveTrend && !isNegativeTrend && "text-gray-600"
            )}>
              {isPositiveTrend && <TrendingUp className="h-3 w-3" />}
              {isNegativeTrend && <TrendingDown className="h-3 w-3" />}
              <span>{trend.label}</span>
            </div>
          )}
        </div>
        <div className="text-2xl font-bold text-gray-900">
          {value}
        </div>
      </div>
    )
  }
)
Kpi.displayName = "Kpi"

export { Kpi }
