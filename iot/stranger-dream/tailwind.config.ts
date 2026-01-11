import type { Config } from 'tailwindcss'

export default <Config>{
  content: [],
  theme: {
    extend: {
      colors: {
        'stranger-rose': '#FF00CF',
        'stranger-blue': '#150059',
        'stranger-yellow': '#FFFF00',
        'stranger-green': '#00FFC4',
      },
      fontFamily: {
        stranger: ['Montserrat', 'sans-serif'],
        display: ['Cinzel', 'serif'], // Cinematic/Dreamy feel
        cartoon: ['"Fredoka One"', 'cursive'],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        }
      }
    }
  }
}
