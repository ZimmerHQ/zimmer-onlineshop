import * as React from "react"
import { cn } from "@/lib/utils"

interface StatusChipProps {
  status: 'paid' | 'pending' | 'cancelled' | 'awaiting' | 'draft' | 'approved' | 'sold'
  children?: React.ReactNode
  className?: string
}

const statusConfig = {
  paid: {
    label: 'پرداخت شده',
    className: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
  },
  pending: {
    label: 'در انتظار',
    className: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
  },
  cancelled: {
    label: 'لغو شده',
    className: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300'
  },
  awaiting: {
    label: 'در انتظار تأیید',
    className: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
  },
  draft: {
    label: 'پیش‌نویس',
    className: 'bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-300'
  },
  approved: {
    label: 'تأیید شده',
    className: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
  },
  sold: {
    label: 'فروخته شد',
    className: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
  }
}

const StatusChip = React.forwardRef<HTMLSpanElement, StatusChipProps>(
  ({ status, children, className }, ref) => {
    const config = statusConfig[status]
    
    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
          config.className,
          className
        )}
      >
        {children || config.label}
      </span>
    )
  }
)
StatusChip.displayName = "StatusChip"

export { StatusChip }
