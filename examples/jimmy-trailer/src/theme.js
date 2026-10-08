// Keynote-dark, Apple-style: true black stage, one clean sans, Jimmy's own accents
// (sky = listening, violet = focus, emerald = the live dot).
import { loadFont } from "@remotion/google-fonts/Inter";
import { loadFont as loadDeva } from "@remotion/google-fonts/NotoSansDevanagari";

const { fontFamily } = loadFont("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin"] });
export const { fontFamily: devaFamily } = loadDeva("normal", { weights: ["500", "600"], subsets: ["devanagari"] });

export const theme = {
  font: fontFamily,
  bg: "#000000",
  ink: "#f5f5f7",
  muted: "#86868b",
  accent: ["#7dd3fc", "#a78bfa"],
  surface: {
    background: "rgba(14,14,16,0.94)",
    border: "rgba(255,255,255,0.10)",
    shadow: "0 40px 120px -20px rgba(0,0,0,0.9)",
    radius: 22,
    blur: 0,
  },
  headline: { weight: 600, tracking: "-0.035em", lineHeight: 1.04, transform: "none" },
  motion: "expo",
  grain: 0,
};
