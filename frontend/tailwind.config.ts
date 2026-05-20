import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // domain palette
        fintech:     { DEFAULT: '#3B82F6', light: '#DBEAFE', dark: '#1D4ED8' },
        retail:      { DEFAULT: '#F59E0B', light: '#FEF3C7', dark: '#B45309' },
        healthcare:  { DEFAULT: '#14B8A6', light: '#CCFBF1', dark: '#0F766E' },
        // priority / severity
        critical:    '#EF4444',
        high:        '#F97316',
        medium:      '#EAB308',
        low:         '#22C55E',
      },
    },
  },
  plugins: [],
} satisfies Config
