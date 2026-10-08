// README art for the repo, rendered as stills with the skill's own kit:
//   npx remotion still src/banner.jsx Banner ../../docs/banner.png
import { AbsoluteFill, Composition, registerRoot } from "remotion";
import { Check, Clapperboard, Gauge, Images, Music2, ScanEye, Sparkles } from "lucide-react";
import { theme } from "./theme.js";

const F = theme.font;
const UI = '"Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif';
const panel = { background: "rgba(14,14,16,0.92)", borderRadius: 22, fontFamily: UI, color: "#f5f5f5",
  boxShadow: "0 0 0 1.5px rgba(255,255,255,0.10), 0 40px 120px -30px rgba(0,0,0,0.9)" };
const grad = { backgroundImage: "linear-gradient(95deg, #7dd3fc, #a78bfa 60%, #f0abfc)", WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" };
const chip = (c, t, Icon) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 10, fontFamily: UI, fontSize: 24, color: c, background: `${c}1c`,
    boxShadow: `0 0 0 1.5px ${c}50`, borderRadius: 999, padding: "9px 20px", whiteSpace: "nowrap" }}>{Icon && <Icon size={22} />}{t}</span>
);

const Wave = ({ w = 640, h = 96 }) => {
  const bars = 72;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      {Array.from({ length: bars }, (_, i) => {
        const beat = i % 6 === 0;
        const v = beat ? 0.95 : 0.25 + 0.45 * Math.abs(Math.sin(i * 1.7) * Math.cos(i * 0.37));
        const x = (i / bars) * w + 3;
        return <rect key={i} x={x} y={(h - v * h) / 2} width={4.5} height={v * h} rx={2.2} fill={beat ? "#34d399" : "rgba(255,255,255,0.28)"} />;
      })}
    </svg>
  );
};

const Banner = () => (
  <AbsoluteFill style={{ background: "#000", fontFamily: F, overflow: "hidden" }}>
    <AbsoluteFill style={{ background: "radial-gradient(ellipse 50% 70% at 78% 55%, rgba(56,189,248,0.20), rgba(167,139,250,0.10) 45%, transparent 75%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse 35% 50% at 10% 0%, rgba(52,211,153,0.10), transparent 70%)" }} />
    {/* left: the name */}
    <div style={{ position: "absolute", left: 110, top: 110, width: 980 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, fontFamily: UI, fontSize: 26, color: "#a3a3a3", letterSpacing: "0.16em" }}>
        <span style={{ width: 16, height: 16, borderRadius: 99, background: "#34d399", boxShadow: "0 0 24px #34d399" }} /> A SKILL FOR CLAUDE CODE
      </div>
      <div style={{ fontSize: 168, fontWeight: 600, letterSpacing: "-0.055em", lineHeight: 1, color: "#f5f5f7", marginTop: 26 }}>
        Video <span style={grad}>Studio</span>
      </div>
      <div style={{ fontSize: 46, fontWeight: 500, letterSpacing: "-0.025em", color: "#e5e5ea", marginTop: 34, lineHeight: 1.22 }}>
        Launch films, made in code.<br /><span style={{ color: "#86868b" }}>From your repo to a finished, beat‑synced cut.</span>
      </div>
      <div style={{ display: "flex", gap: 14, marginTop: 46, flexWrap: "wrap" }}>
        {chip("#7dd3fc", "Remotion · React")}{chip("#a78bfa", "Beat-synced to your song")}{chip("#34d399", "16:9 · 9:16 · 1:1 · 4:5")}
      </div>
    </div>
    {/* right: the studio, as floating UI */}
    <div style={{ position: "absolute", right: 110, top: 70, width: 760, perspective: 1800 }}>
      <div style={{ transform: "rotateY(-14deg) rotateX(6deg)", transformStyle: "preserve-3d" }}>
        <div style={{ ...panel, padding: "26px 30px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 21, color: "#a3a3a3", letterSpacing: "0.08em" }}>
            <Music2 size={22} color="#34d399" /> RAYA (SLOWED) · 97.998 BPM
            <span style={{ marginLeft: "auto", color: "#6ee7b7" }}>IN SYNC · +17 ms</span>
          </div>
          <div style={{ marginTop: 18 }}><Wave w={700} /></div>
          <div style={{ display: "flex", gap: 6, marginTop: 16 }}>
            {["Hook", "Tease", "Reveal", "Ask", "Proof", "Screen", "Timeline", "End"].map((s, i) => (
              <span key={s} style={{ flex: 1, textAlign: "center", fontSize: 17, padding: "8px 0", borderRadius: 8,
                background: i === 2 ? "rgba(52,211,153,0.18)" : "rgba(255,255,255,0.06)", color: i === 2 ? "#a7f3d0" : "#a3a3a3" }}>{s}</span>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", gap: 22, marginTop: 24, transform: "translateZ(60px)" }}>
          <div style={{ ...panel, flex: 1.25, height: 250, overflow: "hidden", position: "relative", background: "#050506" }}>
            <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 70% 60% at 50% 60%, rgba(56,189,248,0.22), transparent 75%)" }} />
            <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <span style={{ width: 18, height: 18, borderRadius: 99, background: "#34d399", boxShadow: "0 0 26px #34d399" }} />
                <span style={{ fontFamily: F, fontSize: 54, fontWeight: 600, letterSpacing: "-0.04em", color: "#f5f5f7", whiteSpace: "nowrap" }}>Coming soon.</span>
              </div>
            </div>
            <div style={{ position: "absolute", left: 16, bottom: 12, fontSize: 16, color: "#737373" }}>frame 1735 · 1920×1080</div>
          </div>
          <div style={{ ...panel, flex: 1, padding: "22px 24px", display: "flex", flexDirection: "column", gap: 14, fontSize: 21 }}>
            {[["#6ee7b7", "−14.0 LUFS · −1 dBTP"], ["#7dd3fc", "Layout check clean"], ["#c4b5fd", "Every line readable"], ["#fde68a", "Poster = frame 0"]].map(([c, t]) => (
              <span key={t} style={{ display: "flex", alignItems: "center", gap: 10, color: "#e5e5e5" }}>
                <span style={{ width: 26, height: 26, borderRadius: 8, background: `${c}22`, color: c, display: "grid", placeItems: "center" }}><Check size={17} /></span>{t}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  </AbsoluteFill>
);

const STEPS = [
  [ScanEye, "Discover", "reads your repo, README, UI", "#7dd3fc"],
  [Sparkles, "Brief", "purpose, style, camera, tone", "#a78bfa"],
  [Music2, "Sound", "measures your song's beats", "#34d399"],
  [Clapperboard, "Build", "real UI, 3D type, motion", "#f0abfc"],
  [Images, "Review", "stills + layout check", "#fde68a"],
  [Gauge, "Verify", "sync · loudness · poster", "#6ee7b7"],
];
const Pipeline = () => (
  <AbsoluteFill style={{ background: "#000", fontFamily: F, alignItems: "center", justifyContent: "center" }}>
    <AbsoluteFill style={{ background: "radial-gradient(ellipse 60% 70% at 50% 60%, rgba(167,139,250,0.12), transparent 75%)" }} />
    <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
      {STEPS.map(([Icon, name, sub, c], i) => (
        <div key={name} style={{ display: "flex", alignItems: "center" }}>
          <div style={{ ...panel, width: 240, height: 250, padding: "26px 24px", boxSizing: "border-box",
            background: `radial-gradient(120% 90% at 0% 0%, ${c}22, transparent 55%), linear-gradient(180deg, #141416, #0c0c0d)` }}>
            <div style={{ fontSize: 18, color: "#737373", letterSpacing: "0.1em" }}>0{i + 1}</div>
            <span style={{ marginTop: 14, width: 58, height: 58, borderRadius: 16, background: `${c}24`, color: c, display: "grid", placeItems: "center" }}><Icon size={30} /></span>
            <div style={{ fontFamily: F, fontSize: 36, fontWeight: 600, letterSpacing: "-0.03em", marginTop: 18 }}>{name}</div>
            <div style={{ fontSize: 19, color: "#a3a3a3", marginTop: 8, lineHeight: 1.35 }}>{sub}</div>
          </div>
          {i < STEPS.length - 1 && <div style={{ width: 44, height: 2, background: `linear-gradient(90deg, ${c}, ${STEPS[i + 1][3]})`, opacity: 0.7 }} />}
        </div>
      ))}
    </div>
  </AbsoluteFill>
);

registerRoot(() => (
  <>
    <Composition id="Banner" component={Banner} width={2400} height={820} fps={30} durationInFrames={1} />
    <Composition id="Pipeline" component={Pipeline} width={1960} height={420} fps={30} durationInFrames={1} />
  </>
));
