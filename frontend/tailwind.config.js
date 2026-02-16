/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef2f4',
          100: '#fde6ea',
          200: '#fbc9d4',
          300: '#f79fb7',
          400: '#f26692',
          500: '#e6376e',
          600: '#B3224D',
          700: '#8d1a3c',
          800: '#6d1530',
          900: '#5a122a',
        },
      },
    },
  },
  plugins: [],
}
