import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 zimmer-focus-ring disabled:pointer-events-none disabled:opacity-50 zimmer-button",
  {
        variants: {
          variant: {
            default: "bg-primary-500 text-white hover:bg-primary-600 shadow-sm hover:shadow-md",
            destructive:
              "bg-red-500 text-white hover:bg-red-600 shadow-sm hover:shadow-md",
            outline:
              "border border-gray-300 bg-white hover:bg-gray-50 text-gray-900 hover:text-gray-900",
            secondary:
              "bg-gray-100 text-gray-900 hover:bg-gray-200",
            ghost: "hover:bg-gray-100 text-gray-600 hover:text-gray-900",
            link: "text-primary-500 underline-offset-4 hover:underline",
            accent: "bg-accent-500 text-white hover:bg-accent-600 shadow-sm hover:shadow-md",
          },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-12 rounded-xl px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants } 