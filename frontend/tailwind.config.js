/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: { DEFAULT: '#101722', soft: '#3A4657', muted: '#6B7789' },
        canvas: '#F4F6F9',
        line: '#E2E7EE',
        brand: { DEFAULT: '#0B6B62', dark: '#085048', light: '#E6F2F0' },
        approved: { DEFAULT: '#0E7A4E', light: '#E7F4EE' },
        review: { DEFAULT: '#B26A00', light: '#FCF2E2' },
        blocked: { DEFAULT: '#B32B2B', light: '#FBECEC' },
      },
      fontFamily: {
        sans: ['Figtree', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(16,23,34,0.04), 0 4px 12px rgba(16,23,34,0.05)',
      },
      borderRadius: { card: '10px' },
    },
  },
  plugins: [],
}
