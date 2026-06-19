/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        ink: "#172033",
        graphite: "#2f3848",
        signal: "#0f766e",
        harvest: "#b45309",
        coral: "#be123c",
      },
      boxShadow: {
        panel: "0 18px 45px rgba(47, 56, 72, 0.08)",
      },
    },
  },
  plugins: [],
};

