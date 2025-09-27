import * as React from "react"
import { cn } from "@/lib/utils"

interface StatsCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  deltaLabel?: string
  delta?: number
  hint?: string
  className?: string
}

const StatsCard = React.forwardRef<HTMLDivElement, StatsCardProps>(
  ({ icon, label, value, deltaLabel, delta, hint, className }, ref) => {
    const isPositiveDelta = delta && delta > 0
    const isNegativeDelta = delta && delta < 0

    return (
      <div
        ref={ref}
        className={cn(
          "rounded-xl border border-black/5 bg-white shadow-sm dark:bg-neutral-900 dark:border-white/5 p-4 md:p-5 transition-transform hover:-translate-y-0.5",
          className
        )}
      >
        {/* Delta pill at top-left */}
        {delta !== undefined && deltaLabel && (
          <div className={cn(
            "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium mb-3",
            isPositiveDelta && "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
            isNegativeDelta && "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300",
            !isPositiveDelta && !isNegativeDelta && "bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-300"
          )}>
            {deltaLabel}
          </div>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 space-x-reverse">
            <div className="p-2 bg-primary-500/10 rounded-lg">
              {icon}
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{label}</p>
              {hint && (
                <p className="text-xs text-muted-foreground/70">{hint}</p>
              )}
            </div>
          </div>
        </div>
        
        <div className="mt-3">
          <div className="text-2xl font-bold tracking-tight">
            {typeof value === 'number' ? (
              <span dir="ltr" className="font-mono tabular-nums">
                {value.toLocaleString('fa-IR')}
              </span>
            ) : (
              <span dir="ltr" className="font-mono tabular-nums">
                {value}
              </span>
            )}
          </div>
        </div>
      </div>
    )
  }
)
StatsCard.displayName = "StatsCard"

export { StatsCard }
