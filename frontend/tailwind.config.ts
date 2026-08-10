import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: { "2xl": "1600px" },
    },
    extend: {
      colors: {
        border: "#1E293B",
        input: "#1E293B",
        ring: "#22D3EE",
        background: "#060A12",
        surface: "#0D1624",
        surface2: "#111C2D",
        surface3: "#090F1A",
        foreground: "#F8FAFC",
        muted: { DEFAULT: "#94A3B8", foreground: "#64748B" },
        accent: { DEFAULT: "#22D3EE", foreground: "#04121A", muted: "#0E7490" },
        emerald: { DEFAULT: "#22C55E", foreground: "#022C22" },
        success: "#22C55E",
        critical: "#EF4444",
        high: "#F97316",
        medium: "#F59E0B",
        low: "#3B82F6",
        info: "#64748B",
        mono: "#7DD3FC",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(34,211,238,0.15), 0 0 24px -8px rgba(34,211,238,0.25)",
        panel: "0 1px 0 rgba(255,255,255,0.03) inset, 0 8px 24px -16px rgba(0,0,0,0.8)",
      },
      keyframes: {
        "pulse-dot": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
        "fade-slide-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "radar-sweep": {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
      },
      animation: {
        "pulse-dot": "pulse-dot 2s ease-in-out infinite",
        "fade-slide-in": "fade-slide-in 0.3s ease-out",
        "radar-sweep": "radar-sweep 6s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
