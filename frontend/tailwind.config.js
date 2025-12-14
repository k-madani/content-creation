/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Instrument Serif', 'serif'],
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#072e57',  // Deep navy
          hover: '#0a3d75',     // Lighter navy
        },
        accent: {
          DEFAULT: '#1a4d7a',   // Rich blue for headings
          light: '#2563eb',     // Bright blue
        },
        background: {
          DEFAULT: '#f8fafc',   // Very light blue-gray
          alt: '#f1f5f9',       // Section background
        }
      },
    },
  },
  plugins: [],
}