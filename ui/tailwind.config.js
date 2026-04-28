/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', "system-ui", "sans-serif"],
        display: ['"Instrument Serif"', "Georgia", "serif"],
        mono: ['"JetBrains Mono"', '"Menlo"', '"Consolas"', "monospace"],
      },
      colors: {
        canvas: "#F8F5F1",
        ink: "#191919",
        terracotta: "#D4542C",
        mineral: "#2F7F73",
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
          "0%, 100%": { opacity: "1", boxShadow: "0 0 0 0 rgba(212,84,44,0.45)" },
          "50%": { opacity: "0.75", boxShadow: "0 0 0 5px rgba(212,84,44,0)" },
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
          primary: "#D4542C",
          "primary-content": "#FFFBF8",
          secondary: "#2F7F73",
          "secondary-content": "#F4FBFA",
          accent: "#2F7F73",
          "accent-content": "#F4FBFA",
          neutral: "#E5DFD6",
          "neutral-content": "#191919",
          "base-100": "#F8F5F1",
          "base-200": "#F0EBE4",
          "base-300": "#E5DFD6",
          "base-content": "#191919",
          info: "#3d7a9e",
          "info-content": "#F8F5F1",
          success: "#2F7F73",
          "success-content": "#F4FBFA",
          warning: "#b8860b",
          "warning-content": "#1a1408",
          error: "#b91c1c",
          "error-content": "#fff5f5",
        },
      },
    ],
    darkTheme: "minerva",
  },
};
