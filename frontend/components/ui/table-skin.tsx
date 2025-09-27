import * as React from "react"
import { cn } from "@/lib/utils"

interface TableSkinProps {
  children: React.ReactNode
  className?: string
}

const TableSkin = React.forwardRef<HTMLDivElement, TableSkinProps>(
  ({ children, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "zimmer-card overflow-hidden",
          className
        )}
      >
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            {children}
          </table>
        </div>
      </div>
    )
  }
)
TableSkin.displayName = "TableSkin"

const TableHeader = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => {
    return (
      <thead
        ref={ref}
        className={cn("bg-gray-50 sticky top-0 z-10", className)}
        {...props}
      />
    )
  }
)
TableHeader.displayName = "TableHeader"

const TableBody = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => {
    return (
      <tbody
        ref={ref}
        className={cn("bg-white divide-y divide-gray-200", className)}
        {...props}
      />
    )
  }
)
TableBody.displayName = "TableBody"

const TableRow = React.forwardRef<HTMLTableRowElement, React.HTMLAttributes<HTMLTableRowElement>>(
  ({ className, ...props }, ref) => {
    return (
      <tr
        ref={ref}
        className={cn(
          "hover:bg-gray-50 transition-colors duration-200",
          className
        )}
        {...props}
      />
    )
  }
)
TableRow.displayName = "TableRow"

const TableHead = React.forwardRef<HTMLTableCellElement, React.ThHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => {
    return (
      <th
        ref={ref}
        className={cn(
          "px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider",
          className
        )}
        scope="col"
        {...props}
      />
    )
  }
)
TableHead.displayName = "TableHead"

const TableCell = React.forwardRef<HTMLTableCellElement, React.TdHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => {
    return (
      <td
        ref={ref}
        className={cn(
          "px-6 py-4 whitespace-nowrap text-sm text-gray-900",
          className
        )}
        {...props}
      />
    )
  }
)
TableCell.displayName = "TableCell"

export { TableSkin, TableHeader, TableBody, TableRow, TableHead, TableCell }
