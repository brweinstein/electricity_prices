import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0F1412",
        surface: "#171D1A",
        hairline: "#2A322E",
        ink: "#E8ECE9",
        muted: "#8A948F",
        cheap: "#4FD1AE",
        expensive: "#F2A93B",
      },
      fontFamily: {
        mono: ["var(--font-plex-mono)", "monospace"],
        sans: ["var(--font-plex-sans)", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;