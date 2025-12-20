/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        'bg-main': 'var(--bg-main)',
        'bg-sec': 'var(--bg-sec)',
        'text-main': 'var(--text-main)',
        'text-sec': 'var(--text-sec)',
        'border-custom': 'var(--border)', // 'border' is a reserved key sometimes, better safe
        'border-focus': 'var(--border-focus)',
        'card-hover': 'var(--card-hover)',
        'accent': 'var(--accent)',
        'accent-text': 'var(--accent-text)',
        'tri-state-bg': 'var(--tri-state-bg)',
        'tri-state-hover': 'var(--tri-state-hover)',
        'code-bg': 'var(--code-bg)',
      },
      fontFamily: {
        mono: ['"Space Mono"', 'monospace'],
      }
    }
  }
}
