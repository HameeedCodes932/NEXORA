/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "sans-serif"]
      },
      colors: {
        graphite: {
          950: "#080a0d",
          900: "#0d1117",
          850: "#11161d",
          800: "#161b22",
          700: "#252c36"
        },
        signal: {
          400: "#35d0ba",
          500: "#20b8a6"
        }
      },
      boxShadow: {
        panel: "0 18px 60px rgba(0, 0, 0, 0.32)"
      }
    }
  },
  plugins: []
};
