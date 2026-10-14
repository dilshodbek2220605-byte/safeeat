/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class', '[data-theme="dark"]'],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Telegram theme variables (ThemeSync komponenti to'ldiradi)
        tg: {
          bg: 'var(--tg-bg)',
          secondary: 'var(--tg-secondary-bg)',
          text: 'var(--tg-text)',
          hint: 'var(--tg-hint)',
          link: 'var(--tg-link)',
          button: 'var(--tg-button)',
          buttonText: 'var(--tg-button-text)',
          destructive: 'var(--tg-destructive)',
          section: 'var(--tg-section-bg)',
          separator: 'var(--tg-separator)',
        },
        risk: {
          safe: '#22c55e',
          moderate: '#f59e0b',
          dangerous: '#ef4444',
        },
      },
      borderRadius: {
        card: '1rem',
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04)',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Inter',
          'system-ui',
          'sans-serif',
        ],
      },
      keyframes: {
        'slide-up': {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
      },
      animation: {
        'slide-up': 'slide-up .28s cubic-bezier(.16,1,.3,1)',
      },
    },
  },
  plugins: [],
}
