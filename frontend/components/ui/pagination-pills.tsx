import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface PaginationPillsProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
}

const PaginationPills = React.forwardRef<HTMLDivElement, PaginationPillsProps>(
  ({ currentPage, totalPages, onPageChange, className }, ref) => {
    const getVisiblePages = () => {
      const delta = 2
      const range = []
      const rangeWithDots = []

      for (
        let i = Math.max(2, currentPage - delta);
        i <= Math.min(totalPages - 1, currentPage + delta);
        i++
      ) {
        range.push(i)
      }

      if (currentPage - delta > 2) {
        rangeWithDots.push(1, '...')
      } else {
        rangeWithDots.push(1)
      }

      rangeWithDots.push(...range)

      if (currentPage + delta < totalPages - 1) {
        rangeWithDots.push('...', totalPages)
      } else if (totalPages > 1) {
        rangeWithDots.push(totalPages)
      }

      return rangeWithDots
    }

    const visiblePages = getVisiblePages()

    return (
      <div
        ref={ref}
        className={cn(
          "flex items-center justify-center space-x-2 space-x-reverse",
          className
        )}
      >
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className={cn(
            "flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "hover:bg-gray-100 text-gray-600 hover:text-gray-900",
            "zimmer-focus-ring"
          )}
          aria-label="صفحه قبلی"
        >
          <ChevronRight className="h-4 w-4" />
          <span className="mr-1">قبلی</span>
        </button>

        {visiblePages.map((page, index) => (
          <React.Fragment key={index}>
            {page === '...' ? (
              <span className="px-3 py-2 text-sm text-gray-600">...</span>
            ) : (
              <button
                onClick={() => onPageChange(page as number)}
                className={cn(
                  "px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200",
                  "zimmer-focus-ring",
                  currentPage === page
                    ? "bg-primary-500 text-white"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                )}
              >
                {page}
              </button>
            )}
          </React.Fragment>
        ))}

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={cn(
            "flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "hover:bg-gray-100 text-gray-600 hover:text-gray-900",
            "zimmer-focus-ring"
          )}
          aria-label="صفحه بعدی"
        >
          <span className="ml-1">بعدی</span>
          <ChevronLeft className="h-4 w-4" />
        </button>
      </div>
    )
  }
)
PaginationPills.displayName = "PaginationPills"

export { PaginationPills }
