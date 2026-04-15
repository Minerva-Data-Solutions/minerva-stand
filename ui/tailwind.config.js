/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Fraunces"', '"Georgia"', "serif"],
        mono: ['"JetBrains Mono"', '"Menlo"', '"Consolas"', "monospace"],
      },
      colors: {
        minerva: "#E24D27",
      },
      keyframes: {
        slideUp: {
          from: { opacity: "0", transform: "translateY(14px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        dotPulse: {
          "0%, 80%, 100%": { transform: "scale(0.6)", opacity: "0.25" },
          "40%": { transform: "scale(1)", opacity: "1" },
        },
        statusGlow: {
          "0%, 100%": { opacity: "1", boxShadow: "0 0 0 0 rgba(226,77,39,0.5)" },
          "50%": { opacity: "0.7", boxShadow: "0 0 0 4px rgba(226,77,39,0)" },
        },
      },
      animation: {
        "slide-up": "slideUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) both",
        "fade-in": "fadeIn 0.3s ease-out both",
        "dot-1": "dotPulse 1.4s ease-in-out infinite 0ms",
        "dot-2": "dotPulse 1.4s ease-in-out infinite 200ms",
        "dot-3": "dotPulse 1.4s ease-in-out infinite 400ms",
        "status-glow": "statusGlow 2.5s ease-in-out infinite",
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        minerva: {
          primary: "#E24D27",
          "primary-content": "#fff8f6",
          secondary: "#64748b",
          "secondary-content": "#f8fafc",
          accent: "#ff6b47",
          "accent-content": "#fff8f6",
          neutral: "#1e1e2e",
          "neutral-content": "#e8e8f8",
          "base-100": "#1c1c28",
          "base-200": "#13131e",
          "base-300": "#0d0d17",
          "base-content": "#eeeef8",
          info: "#7dd3fc",
          "info-content": "#0c1a24",
          success: "#86efac",
          "success-content": "#0c1a0c",
          warning: "#fde68a",
          "warning-content": "#1a140c",
          error: "#fca5a5",
          "error-content": "#1a0c0c",
        },
      },
    ],
    darkTheme: "minerva",
  },
};
