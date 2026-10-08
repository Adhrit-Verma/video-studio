// The look, decided in the brief (see references/styles.md). Every visual in the kit
// reads from here, so a new style is a new theme, not new scene code.
//
// Fonts: any family in @remotion/google-fonts works: change the import path
// ("@remotion/google-fonts/Inter" -> ".../SpaceGrotesk", ".../Fraunces", ".../DMSans" ...).
// For the product's own font file use @remotion/fonts' loadFont with a file in public/.
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont("normal", { weights: ["400", "500", "600", "700", "800"], subsets: ["latin"] });

export const theme = {
  font: fontFamily,
  bg: "#0b0b0f",                 // stage colour; light styles use e.g. "#f7f7f5"
  ink: "#f5f5f7",                // main text
  muted: "#8a8a93",              // secondary text
  accent: ["#7c3aed", "#06b6d4"], // gradient stops for highlights (one stop = solid colour)
  surface: {                     // the UI material: panels, cards, chips
    background: "rgba(22,22,27,0.92)",
    border: "rgba(255,255,255,0.10)",
    shadow: "0 40px 120px -30px rgba(0,0,0,0.8)",
    radius: 22,
    blur: 0,                     // >0 = frosted glass (backdrop blur; 2D scenes only, it flattens 3D)
  },
  headline: { weight: 700, tracking: "-0.04em", lineHeight: 1.02, transform: "none" },  // "uppercase" for bold kinetic styles
  motion: "expo",                // expo | snappy | bouncy | back | linear | smooth (see kit EASES)
  grain: 0,                      // 0..0.2 film grain for cinematic/retro styles
};
