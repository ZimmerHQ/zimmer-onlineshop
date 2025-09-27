/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Zimmer Theme Colors
        primary: {
          50: '#f0f0ff',
          100: '#e6e6ff',
          200: '#d1d1ff',
          300: '#b3b3ff',
          400: '#8a8aff',
          500: '#6C63FF', // Main primary
          600: '#5B54F6', // Darker primary
          700: '#4c46d9',
          800: '#3f3ab3',
          900: '#363192',
          DEFAULT: '#6C63FF',
          foreground: '#ffffff',
        },
        accent: {
          50: '#f7ffe6',
          100: '#edffcc',
          200: '#dbff99',
          300: '#c2ff66',
          400: '#a6ff33',
          500: '#B6FF5C', // Main accent
          600: '#a6e64d',
          700: '#8fcc3d',
          800: '#78b333',
          900: '#66992a',
          DEFAULT: '#B6FF5C',
          foreground: '#0F1116',
        },
        bg: {
          DEFAULT: '#FFFFFF', // Light background
          soft: '#F8F9FA', // Very light gray
        },
        card: {
          DEFAULT: '#FFFFFF', // White cards
          contrast: '#000000',
        },
        text: {
          strong: '#1F2937', // Dark text
          muted: '#6B7280', // Muted gray
        },
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
        info: '#38BDF8',
        
        // Legacy shadcn colors (keep for compatibility)
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius-lg, 12px)",
        xl: "var(--radius-xl, 16px)",
        pill: "var(--radius-pill, 9999px)",
        md: "calc(var(--radius-lg, 12px) - 2px)",
        sm: "calc(var(--radius-lg, 12px) - 4px)",
      },
      boxShadow: {
        card: "var(--shadow-card, 0 10px 30px rgba(0,0,0,.18))",
      },
      fontFamily: {
        sans: ['Vazirmatn', 'system-ui', 'sans-serif'],
      },
      fontFeatureSettings: {
        'ss01': '"ss01"',
        'cv01': '"cv01"',
      },
      transitionProperty: {
        'all': 'all',
      },
      transitionDuration: {
        '200': '200ms',
      },
    },
  },
  plugins: [],
} 