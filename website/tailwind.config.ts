/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"Space Mono"', 'monospace'],
        lineal: ['Lineal', 'sans-serif'],
      },
      colors: {
        bg: {
          main: 'var(--bg-main)',
          sec: 'var(--bg-sec)',
        },
        text: {
          main: 'var(--text-main)',
          sec: 'var(--text-sec)',
        },
        border: {
          DEFAULT: 'var(--border)',
          focus: 'var(--border-focus)',
        },
        accent: {
          DEFAULT: 'var(--accent)',
          text: 'var(--accent-text)',
        },
        success: 'var(--success)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
