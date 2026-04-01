/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0D0D12',
        primary: '#0D0D12', // Obsidian
        accent: '#C9A84C',  // Champagne
        ivory: '#FAF8F5',   // Marfim
        slate: '#2A2A35',   // Ardósia
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        drama: ['"Playfair Display"', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'magnetic': '0 8px 30px rgba(0,0,0,0.12)',
      }
    },
  },
  plugins: [],
}
