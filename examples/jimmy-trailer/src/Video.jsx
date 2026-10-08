// Jimmy — 60 s launch trailer, cut to an edit of "Raya (Slowed)" (97.99 BPM).
// Beats are film beats (0.6123 s). The song's drops land on 25.5 and 85.5 (each after a
// short gap), the breakdown runs 56-69.5, the re-entry is 69.5, the ending chord is 92.
// All on-screen data is the invented demo data Jimmy's own README uses (Northwind Fellowship).
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from "remotion";
import {
  AppWindow, Archive, Bell, CalendarClock, Check, Hand, MessageCircleQuestion, History, Languages, Lock, Mic, MonitorSmartphone, PenLine, RotateCcw, Search, Target, Timer, Trash2, Volume2,
} from "lucide-react";
import cfg from "../video.json";
import {
  ACCENT, BG, Caption, Center, Count, Cover, EASES, Stream, Film, Flash, Glow, INK, Layer, MUTED, Pic, Reveal, Scene, Stage,
  Vignette, Words, clamp, head, rise, useBeat, useEnergy, useSnap,
} from "./kit.jsx";
import { devaFamily } from "./theme.js";

// Jimmy's own UI font (Windows 11), so the mock overlay reads exactly like the product.
const UI = '"Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif';
const C = { emerald: "#34d399", sky: "#38bdf8", violet: "#a78bfa", amber: "#fbbf24", rose: "#fb7185", n400: "#a3a3a3", n500: "#737373" };
const panel = {
  background: "rgba(12,12,13,0.95)", borderRadius: 26, fontFamily: UI, color: "#f5f5f5",
  boxShadow: "0 0 0 1.5px rgba(255,255,255,0.10), 0 50px 140px -30px rgba(0,0,0,0.95)",
};
const lerp = (a, b, t) => a + (b - a) * t;
// An entrance that lands on the song's nearest real kick, with a hard attack.
const useKick = () => {
  const s = useSnap();
  return (b, at, dur = 0.5) => rise(b, s(at), dur, EASES.snappy);
};

// --- product pieces ----------------------------------------------------------------
const Eq = ({ color = C.sky, h = 22 }) => {
  const f = useCurrentFrame();
  return (
    <span style={{ display: "inline-flex", alignItems: "flex-end", gap: 3, height: h, width: 24 }}>
      {[0, 1, 2, 3].map((i) => (
        <span key={i} style={{ width: 3.5, borderRadius: 3, background: color,
          height: `${(0.35 + 0.65 * (0.5 + 0.5 * Math.sin(f * 0.21 + i * 1.9))) * 100}%` }} />
      ))}
    </span>
  );
};

const Shimmer = ({ children }) => {
  const f = useCurrentFrame();
  return (
    <span style={{ backgroundImage: "linear-gradient(90deg, #8a8a8a 0%, #f5f5f5 45%, #8a8a8a 90%)", backgroundSize: "200% 100%",
      backgroundPosition: `${200 - ((f * 3.6) % 300)}% 0`, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>
      {children}
    </span>
  );
};

// The pill: Jimmy's always-there presence at the top of the screen.
const Pill = ({ mode = "idle", text, size = 26, ping = 0 }) => {
  const dot = mode === "curtain" ? C.n500 : mode === "idle" ? C.emerald : C.sky;
  const status = mode === "curtain" ? <span style={{ color: "#d4d4d4" }}>Curtain down</span>
    : mode === "listening" ? <span style={{ color: "#bae6fd" }}>{text || "Listening… ask away"}</span>
      : mode === "thinking" ? <Shimmer>Thinking…</Shimmer>
        : mode === "done" ? <span style={{ color: "#fafafa", display: "inline-flex", alignItems: "center", gap: 8 }}>
          <Check size={size * 0.85} color="#6ee7b7" />{text}</span>
          : <span style={{ color: C.n400 }}>{text || "Listening"}</span>;
  return (
    <div style={{ ...panel, borderRadius: 999, display: "inline-flex", alignItems: "center", gap: size * 0.5,
      padding: `${size * 0.45}px ${size * 0.95}px`, fontSize: size, whiteSpace: "nowrap" }}>
      <span style={{ position: "relative", display: "inline-flex", width: size * 0.62, justifyContent: "center" }}>
        {mode === "listening" ? <Eq h={size * 0.8} /> : (
          <>
            <span style={{ position: "absolute", width: size * 0.36, height: size * 0.36, borderRadius: 99, background: dot,
              opacity: 0.6 * (1 - ping), transform: `scale(${1 + 2.2 * ping})` }} />
            <span style={{ width: size * 0.36, height: size * 0.36, borderRadius: 99, background: dot }} />
          </>
        )}
      </span>
      <span style={{ fontWeight: 600, color: "#fafafa" }}>Jimmy</span>
      {status}
    </div>
  );
};

const KINDS = {
  RESUME: [RotateCcw, "Welcome back", "rgba(56,189,248,0.15)", "#bae6fd"],
  RECALL: [History, "Recall", "rgba(255,255,255,0.06)", "#d4d4d4"],
  FOCUS: [Target, "Focus", "rgba(167,139,250,0.15)", "#ddd6fe"],
  DEADLINE: [CalendarClock, "Deadline", "rgba(251,113,133,0.15)", "#fecdd3"],
};
const Card = ({ kind, line, when, w = 720 }) => {
  const [Icon, label, bg, fg] = KINDS[kind];
  return (
    <div style={{ ...panel, width: w, padding: "26px 30px 30px", borderRadius: 30 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, fontSize: 20, color: C.n400 }}>
        <span style={{ width: 38, height: 38, borderRadius: 10, background: bg, color: fg, display: "grid", placeItems: "center" }}>
          <Icon size={22} />
        </span>
        <span style={{ textTransform: "uppercase", letterSpacing: "0.08em" }}>{label}</span>
        <span style={{ marginLeft: "auto", color: C.n500 }}>{when}</span>
      </div>
      <div style={{ marginTop: 16, fontSize: 31, fontWeight: 600, lineHeight: 1.25, color: "#fafafa" }}>{line}</div>
    </div>
  );
};

const Mark = ({ children }) => <span style={{ background: "rgba(52,211,153,0.22)", color: "#a7f3d0", borderRadius: 5, padding: "0 4px" }}>{children}</span>;

// The spoken request, shown as a subtitle with a mic (the words stream at speaking pace).
const Spoken = ({ text, at, step = 0.22, out, size = 64 }) => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 26 }}>
    <Reveal at={at - 0.3} dur={0.8} out={out} blur={8}>
      <span style={{ width: 74, height: 74, borderRadius: 99, display: "grid", placeItems: "center",
        background: "rgba(56,189,248,0.14)", boxShadow: "0 0 0 1.5px rgba(56,189,248,0.35)" }}><Mic size={36} color="#7dd3fc" /></span>
    </Reveal>
    <Words text={text} at={at} step={step} out={out} style={{ ...head(size, { fontWeight: 500 }), maxWidth: 1100, textAlign: "left" }} />
  </div>
);

// A page with Jimmy floating over it: a dimmed desktop backdrop.
const Desk = ({ src, dim = 0.32, w = 1640, h = 924 }) => (
  <Layer z={-260} w={w} h={h}><Pic src={src} width="100%" height="100%" dim={dim} radius={28} /></Layer>
);

// --- 1. Cold open --------------------------------------------------------------------
// --- 2. ...and forget them: a tunnel of everything you saw, fading as it passes ----------
const PANE_SRC = ["fellowship.jpg", "oauth.jpg", "plan.jpg", "timeline.jpg"];
const MiniPane = ({ seed }) => {
  const hue = Math.floor(random(seed) * 360);
  const lines = 5 + Math.floor(random(`${seed}l`) * 5);
  return (
    <div style={{ width: "100%", height: "100%", borderRadius: 18, background: "#f4f4f6", overflow: "hidden" }}>
      <div style={{ height: 34, background: "#e4e4e8", display: "flex", gap: 8, alignItems: "center", padding: "0 14px" }}>
        {[0, 1, 2].map((i) => <span key={i} style={{ width: 11, height: 11, borderRadius: 9, background: "#c9c9cf" }} />)}
      </div>
      <div style={{ padding: 26 }}>
        <div style={{ width: "55%", height: 22, borderRadius: 6, background: `hsl(${hue} 55% 55%)`, marginBottom: 18 }} />
        {Array.from({ length: lines }, (_, i) => (
          <div key={i} style={{ width: `${55 + random(`${seed}${i}`) * 40}%`, height: 11, borderRadius: 6, background: "#d4d4da", marginBottom: 13 }} />
        ))}
      </div>
    </div>
  );
};
const PANES = Array.from({ length: 22 }, (_, i) => {
  const a = random(`a${i}`) * Math.PI * 2;
  const r = 620 + random(`r${i}`) * 420;
  return { i, x: Math.cos(a) * r * 1.25, y: Math.sin(a) * r * 0.62, z: -400 - i * 260, ry: (random(`y${i}`) - 0.5) * 40, img: i % 3 !== 1 ? PANE_SRC[i % 4] : null };
});
const Forget = () => {
  const b = useBeat();
  const travel = interpolate(b, [0, 8], [0, 5200], clamp);
  const fade = rise(b, 3, 4.5, EASES.smooth);               // the forgetting
  return (
    <>
      <Stage z={travel} persp={1300}>
        {PANES.map((p) => {
          const zz = p.z + travel;
          const vis = interpolate(zz, [-6000, -3400, 150, 550], [0, 1, 1, 0], clamp);
          const forgot = Math.min(1, fade * (0.6 + random(`f${p.i}`) * 0.8));
          return (
            <Layer key={p.i} x={p.x} y={p.y} z={p.z} ry={p.ry} w={560} h={330}>
              <div style={{ width: "100%", height: "100%", opacity: vis * (1 - 0.85 * forgot),
                filter: `blur(${forgot * 14}px) grayscale(${forgot}) brightness(${0.75 - 0.3 * forgot})` }}>
                {p.img ? <Pic src={p.img} width="100%" height="100%" radius={18} /> : <MiniPane seed={`p${p.i}`} />}
              </div>
            </Layer>
          );
        })}
      </Stage>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 46% 34% at 50% 50%, rgba(0,0,0,0.92), rgba(0,0,0,0) 100%)" }} />
      <Center>
        <Words text="And forget almost all of them." at={1} step={0.5} accent={[1]} out={7.6} style={{ ...head(96), maxWidth: 1600 }} />
      </Center>
      <Cover at={0} dur={0.5} />
    </>
  );
};

// --- 3. The question, then the hush (the song's gap before the drop) ---------------------
// --- 4. Reveal on the drop --------------------------------------------------------------
const Wordmark = ({ b, at = 0, size = 260 }) => {
  const p = rise(b, at, 0.7, EASES.snappy);
  const sweep = interpolate(b, [at, at + 2.6], [-30, 130], clamp);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: size * 0.16, opacity: p,
      transform: `scale(${1.18 - 0.18 * p})`, filter: `blur(${(1 - p) * 24}px)` }}>
      <span style={{ width: size * 0.17, height: size * 0.17, borderRadius: 99, background: C.emerald,
        boxShadow: `0 0 ${size * 0.25}px rgba(52,211,153,0.7)`, marginTop: size * 0.08 }} />
      <span style={{ ...head(size, { fontWeight: 600, letterSpacing: "-0.05em", paddingBottom: size * 0.06 }),
        backgroundImage: `linear-gradient(100deg, #e9e9ee 0%, #e9e9ee ${sweep - 14}%, #ffffff ${sweep}%, #c5d9ff ${sweep + 4}%, #e9e9ee ${sweep + 16}%, #e9e9ee 100%)`,
        WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>Jimmy</span>
    </div>
  );
};
const Reveal4 = () => {
  const b = useBeat();
  const { energy } = useEnergy();
  return (
    <>
      <AbsoluteFill style={{ opacity: rise(b, 0, 1.5) * (0.8 + 0.3 * energy),
        background: "radial-gradient(ellipse 60% 45% at 50% 62%, rgba(56,189,248,0.20), rgba(167,139,250,0.10) 45%, transparent 75%)" }} />
      <Flash at={0} dur={0.45} peak={0.55} />
      <Center style={{ flexDirection: "column", gap: 34 }}>
        <Reveal at={1} dur={1.2} y={-20} blur={10}><Pill ping={(b * 0.8) % 1} /></Reveal>
        <Wordmark b={b} />
        <div style={{ textAlign: "center", marginTop: 6 }}>
          <Reveal at={2} dur={1.2}><div style={head(50, { color: INK, fontWeight: 500 })}>Remembers what you saw.</div></Reveal>
          <Reveal at={2.75} dur={1.2}><div style={head(50, { ...ACCENT, fontWeight: 500, paddingBottom: 6 })}>Answers when you ask.</div></Reveal>
        </div>
      </Center>
      <Vignette strength={0.6} />
    </>
  );
};

// --- 5. Ask: the hero flow --------------------------------------------------------------
const Evidence = ({ b }) => (
  <div style={{ ...panel, width: 560, padding: 18 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 17, color: C.n400, padding: "4px 6px 14px" }}>
      <Search size={18} /> <span style={{ letterSpacing: "0.08em" }}>EVIDENCE</span>
      <span style={{ marginLeft: "auto", color: C.n500 }}>2 moments · Tue 22 Sep</span>
    </div>
    <div style={{ borderRadius: 18, padding: 14, background: "rgba(16,185,129,0.07)", boxShadow: "0 0 0 1.5px rgba(52,211,153,0.35)" }}>
      <Pic src="fellowship.jpg" width="100%" height={286} radius={12} />
      <div style={{ display: "flex", alignItems: "center", marginTop: 14, fontSize: 18, color: C.n400 }}>
        Tue 22 Sep · 14:02 · Chrome
        <span style={{ marginLeft: "auto", fontSize: 17, color: "#6ee7b7", background: "rgba(52,211,153,0.14)", borderRadius: 8, padding: "3px 10px",
          opacity: rise(b, 2, 0.6), transform: `scale(${0.8 + 0.2 * rise(b, 2, 0.6, EASES.bouncy)})` }}>best match</span>
      </div>
      <div style={{ fontSize: 22, fontWeight: 600, marginTop: 6 }}>Northwind Fellowship · Apply</div>
      <div style={{ fontSize: 18.5, color: "#d4d4d4", marginTop: 6, lineHeight: 1.45 }}>
        2027 <Mark>Fellowship</Mark> <Mark>application</Mark> · Applications close on Monday, 12 October at 11:59 pm.
      </div>
    </div>
    <div style={{ padding: "16px 14px 6px", fontSize: 18.5, color: "#d4d4d4" }}>
      <div style={{ color: C.n400, display: "flex", alignItems: "center", gap: 8 }}><Mic size={16} /> Tue 22 Sep · 14:11</div>
      <div style={{ marginTop: 6 }}>“I really need to finish that <Mark>fellowship</Mark> essay before the deadline”</div>
    </div>
  </div>
);
const ANSWER = "It was the Northwind Fellowship application: a 12-week remote programme for early-career builders. Applications close on Monday, 12 October at 11:59 pm.";
const AnswerPanel = ({ b, at }) => {
  const words = ANSWER.split(" ");
  const n = Math.max(0, Math.min(words.length, Math.floor((b - at) / 0.14) + 1));
  return (
    <div style={{ ...panel, width: 660 }}>
      <div style={{ padding: "26px 30px 0", display: "flex", gap: 16 }}>
        <span style={{ width: 40, height: 40, borderRadius: 10, background: "rgba(255,255,255,0.08)", display: "grid", placeItems: "center" }}><Mic size={20} color="#d4d4d4" /></span>
        <div>
          <div style={{ fontSize: 16, color: C.n500, letterSpacing: "0.08em" }}>YOU ASKED</div>
          <div style={{ fontSize: 22, color: "#e5e5e5", marginTop: 2 }}>what was that fellowship application I saw on Tuesday</div>
        </div>
      </div>
      <div style={{ padding: "22px 30px 26px", fontSize: 29, lineHeight: 1.5, minHeight: 300, color: "#fafafa" }}>
        {b < at ? <Shimmer>Thinking…</Shimmer> : words.slice(0, n).map((w, i) => (
          <span key={i} style={i >= 16 ? { color: "#a7f3d0" } : undefined}>{w}{" "}</span>
        ))}
      </div>
      <div style={{ borderTop: "1.5px solid rgba(255,255,255,0.07)", padding: "16px 30px", display: "flex", fontSize: 18, color: C.n500 }}>
        Based on 2 moments on the left
        <span style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}><Volume2 size={18} /> Stop voice</span>
      </div>
    </div>
  );
};
const Ask = () => {
  const b = useBeat();
  const kick = useKick();
  const panels = kick(b, 4.6, 0.9);
  const ans = kick(b, 5.2, 0.9);
  const cam = rise(b, 0, 12, EASES.smooth);
  const quote = b < 5.2;
  return (
    <>
      <Glow color="rgba(56,189,248,0.16)" size={75} y={40} />
      <Stage ry={lerp(-13, 5, cam)} rx={lerp(7, 2, cam)} z={lerp(-140, 10, cam)}>
        <Desk src="plan.jpg" dim={quote ? 0.22 : 0.3} />
        <Layer y={-405} z={170}>
          <Pill mode={b < 4.4 ? "listening" : b < 6.2 ? "thinking" : "idle"} text={b < 4.4 ? "Listening… ask away" : "Answering"} />
        </Layer>
        <Layer x={lerp(-1200, -470, panels)} y={50} z={lerp(-300, 70, panels)} ry={lerp(30, 8, panels)}><div style={{ opacity: rise(b, 4.6, 0.8) }}><Evidence b={b - 4.6} /></div></Layer>
        <Layer x={lerp(1200, 410, ans)} y={10} z={lerp(-300, 120, ans)} ry={lerp(-30, -6, ans)}>
          <div style={{ opacity: rise(b, 5.2, 0.8) }}><AnswerPanel b={b} at={6.2} /></div>
        </Layer>
      </Stage>
      {quote && (
        <AbsoluteFill style={{ background: `rgba(0,0,0,${0.55 * (1 - rise(b, 4.6, 0.6))})` }}>
          <Center><Spoken text="“Jimmy, what was that fellowship application I saw on Tuesday?”" at={0.4} step={0.3} out={4.6} size={58} /></Center>
        </AbsoluteFill>
      )}
      <Caption bottom={34}>
        <Reveal at={9.5} dur={1}><span style={head(46, { fontWeight: 600 })}>Just ask. <span style={ACCENT}>Out loud.</span></span></Reveal>
      </Caption>
      <Cover at={0} dur={0.4} />
    </>
  );
};

// --- 6. It shows its work: macro push into the evidence ----------------------------------
const ShowsWork = () => {
  const b = useBeat();
  const k = rise(b, 0, 6.5, EASES.smooth);
  const kick = useKick();
  const draw = kick(b, 1, 0.6);
  const badge = kick(b, 2, 0.4);
  return (
    <>
      <Stage z={lerp(-260, 330, k)} y={lerp(0, 150, k)} ry={lerp(-9, 3, k)} rx={lerp(5, 0, k)}>
        <Layer w={1600} h={901}><Pic src="fellowship.jpg" width="100%" height="100%" radius={26} /></Layer>
        {/* the deadline line Jimmy answered from: an outline that draws itself */}
        <Layer x={0} y={-67} z={2} w={862} h={98}>
          <div style={{ position: "absolute", inset: 0, borderRadius: 14, boxShadow: `0 0 50px rgba(52,211,153,${0.55 * draw})` }} />
          <div style={{ position: "absolute", inset: 0, borderRadius: 14, border: `5px solid ${C.emerald}`, boxSizing: "border-box",
            clipPath: `inset(0 ${100 - 100 * draw}% 0 0)` }} />
        </Layer>
        <Layer x={-210} y={-184} z={2} w={474} h={52}>
          <div style={{ width: "100%", height: "100%", borderRadius: 10, background: "rgba(52,211,153,0.28)", opacity: rise(b, 0.5, 0.8),
            transform: `scaleX(${rise(b, 0.5, 0.8)})`, transformOrigin: "0 50%" }} />
        </Layer>
        <Layer x={300} y={-262} z={30}>
          <div style={{ fontFamily: UI, fontSize: 24, fontWeight: 600, color: "#052e22", background: C.emerald, padding: "6px 16px", borderRadius: 10,
            opacity: badge, transform: `scale(${0.7 + 0.3 * badge})` }}>best match · Tue 14:02</div>
        </Layer>
      </Stage>
      <AbsoluteFill style={{ background: "linear-gradient(0deg, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.6) 30%, rgba(0,0,0,0) 55%)" }} />
      <div style={{ position: "absolute", left: 120, bottom: 96 }}>
        <Reveal at={0.75} dur={1}><div style={head(96)}>It shows its work.</div></Reveal>
        <Reveal at={1.5} dur={1}><div style={head(44, { color: "#b4b4bb", fontWeight: 500, marginTop: 14 })}>Every answer comes with proof.</div></Reveal>
      </div>
      <Cover at={0} dur={0.3} />
    </>
  );
};

// --- 7. Cards, rarely ---------------------------------------------------------------------
const CARDS = [
  ["RESUME", "Left off: Fellowship essay · draft 2", "09:12"],
  ["RECALL", "Same Northwind Fellowship as Tue 15:02", "13:31"],
  ["FOCUS", "Back to: the fellowship essay", "15:30"],
  ["DEADLINE", "Tomorrow: Northwind Fellowship", "17:00"],
];
const Cards = () => {
  const b = useBeat();
  const hush = rise(b, 2.7, 2.2, EASES.smooth);
  const kick = useKick();
  return (
    <>
      <Glow color="rgba(167,139,250,0.14)" size={60} x={70} y={50} />
      <Stage ry={lerp(-18, -8, rise(b, 0, 7.5, EASES.smooth))} rx={6} x={330}>
        {CARDS.map(([kind, line, when], i) => {
          const p = kick(b, 0.3 + i * 0.6, 0.5);
          const keep = i === 2;                      // after the hush, only the one that matters stays bright
          return (
            <Layer key={kind} y={-330 + i * 215} z={lerp(-700, keep ? 60 * hush : -40 * hush, p)} rx={lerp(35, 0, p)}>
              <div style={{ opacity: p * (keep ? 1 : 1 - 0.75 * hush), filter: `blur(${(1 - p) * 10 + (keep ? 0 : hush * 3)}px)` }}>
                <Card kind={kind} line={line} when={when} />
              </div>
            </Layer>
          );
        })}
      </Stage>
      <div style={{ position: "absolute", left: 120, top: 0, bottom: 0, display: "flex", flexDirection: "column", justifyContent: "center", width: 760 }}>
        <Reveal at={0.3} dur={0.8} out={2.2}><div style={head(30, { color: MUTED, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 26 })}>A day with Jimmy</div></Reveal>
        <Reveal at={2.5} dur={1.2}><div style={head(92)}>It knows when to <span style={ACCENT}>stay quiet.</span></div></Reveal>
        <Reveal at={3.5} dur={1.2}><div style={head(42, { color: MUTED, fontWeight: 500, marginTop: 26 })}>Four cards an hour, max.</div></Reveal>
      </div>
      <Cover at={0} dur={0.3} />
    </>
  );
};

// --- 8. Private by construction (the breakdown) ------------------------------------------
const Face = ({ blur }) => (
  <svg viewBox="0 0 640 480" width="100%" height="100%" style={{ display: "block", filter: `blur(${blur}px)` }}>
    <defs>
      <linearGradient id="room" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#2b3442" /><stop offset="1" stopColor="#141820" /></linearGradient>
      <radialGradient id="skin" cx="0.45" cy="0.4" r="0.7"><stop offset="0" stopColor="#d9a47c" /><stop offset="1" stopColor="#8e5f43" /></radialGradient>
    </defs>
    <rect width="640" height="480" fill="url(#room)" />
    <rect x="430" y="40" width="160" height="210" rx="8" fill="#3a4658" />
    <path d="M150 480 C170 380 240 350 320 350 C400 350 470 380 490 480 Z" fill="#33475f" />
    <rect x="292" y="300" width="56" height="70" rx="20" fill="#a8734f" />
    <ellipse cx="320" cy="225" rx="92" ry="112" fill="url(#skin)" />
    <path d="M228 210 C230 130 290 105 330 108 C390 110 420 160 412 215 C400 170 360 150 320 152 C280 152 245 175 228 210 Z" fill="#2a1d17" />
  </svg>
);
const Privacy = () => {
  const b = useBeat();
  const blur = rise(b, 1.6, 1.2);
  const box = rise(b, 0.6, 0.6) * (1 - rise(b, 2.4, 0.6));
  const partB = b >= 4.3;
  const curtain = rise(b, 4.6, 1.6, EASES.smooth);
  return (
    <>
      {!partB && (
        <>
          <Stage ry={lerp(12, 4, rise(b, 0, 4.3, EASES.smooth))} x={380}>
            <Layer w={760} h={570}>
              <div style={{ width: "100%", height: "100%", borderRadius: 30, overflow: "hidden", boxShadow: "0 0 0 1.5px rgba(255,255,255,0.12), 0 50px 120px -30px #000" }}>
                <Face blur={blur * 26} />
              </div>
            </Layer>
            <Layer y={-50} z={20} w={250} h={300}>
              <div style={{ width: "100%", height: "100%", borderRadius: 24, border: `4px solid ${C.emerald}`, opacity: box, boxShadow: "0 0 30px rgba(52,211,153,0.5)" }} />
            </Layer>
            <Layer y={240} z={40}>
              <div style={{ fontFamily: UI, fontSize: 24, color: "#d1fae5", background: "rgba(6,78,59,0.85)", borderRadius: 999, padding: "8px 20px",
                opacity: rise(b, 2.2, 0.6), display: "flex", gap: 10, alignItems: "center" }}><Lock size={22} /> blurred before it touches disk</div>
            </Layer>
          </Stage>
          <div style={{ position: "absolute", left: 120, top: 0, bottom: 0, display: "flex", flexDirection: "column", justifyContent: "center", width: 700 }}>
            <Words text="Every face, blurred." at={0.3} step={0.4} accent={[2]} out={4.1} outDur={0.3} style={head(96)} />
            <Reveal at={1.6} dur={0.8} out={4.1} outDur={0.3}><div style={head(30, { color: MUTED, fontWeight: 500, marginTop: 34 })}>Never captured:</div></Reveal>
            <div style={{ display: "flex", gap: 12, marginTop: 14, flexWrap: "wrap" }}>
              {["Banking", "Password managers", "Incognito"].map((t, i) => (
                <Reveal key={t} inline at={2 + i * 0.5} dur={0.6} out={4.1} outDur={0.3} y={14} blur={6}>
                  <span style={{ fontFamily: UI, fontSize: 26, color: "#e5e5e5", background: "rgba(255,255,255,0.07)", boxShadow: "0 0 0 1.5px rgba(255,255,255,0.12)",
                    borderRadius: 999, padding: "8px 20px", display: "inline-flex", alignItems: "center", gap: 10 }}><Lock size={20} color={C.emerald} />{t}</span>
                </Reveal>
              ))}
            </div>
          </div>
        </>
      )}
      {partB && (
        <>
          <Stage rx={4} z={lerp(-120, -40, rise(b, 4.3, 4, EASES.smooth))}>
            <Desk src="oauth.jpg" dim={0.75} />
            <Layer z={-250} w={1640} h={924}>
              <div style={{ width: "100%", height: `${curtain * 100}%`, borderRadius: 28, background: "linear-gradient(180deg, rgba(20,20,22,0.97), rgba(10,10,11,0.99))",
                boxShadow: "0 20px 60px rgba(0,0,0,0.6)", borderBottom: "1.5px solid rgba(255,255,255,0.10)" }} />
            </Layer>
            <Layer y={-60} z={60}>
              <div style={{ opacity: rise(b, 5.6, 0.8), transform: `scale(${0.9 + 0.1 * rise(b, 5.6, 1)})` }}><Pill mode="curtain" size={34} /></div>
            </Layer>
          </Stage>
          <Center style={{ top: 140 }}>
            <Words text="Step away. Curtain down." at={4.8} step={0.25} accent={[2, 3]} style={head(80)} />
          </Center>
          <Cover at={4.3} dur={0.4} />
        </>
      )}
      <Cover at={0} dur={0.5} />
    </>
  );
};

// --- 9. How was my day? (re-entry) --------------------------------------------------------
const APPS = [["VS Code", "#10b981", 209, "3h 29m"], ["Notion", "#16a34a", 179, "2h 59m"], ["Chrome", "#3b82f6", 157, "2h 37m"],
  ["Discord", "#8b5cf6", 45, "45m"], ["Spotify", "#ef4444", 22, "22m"], ["Other", "#737373", 30, "30m"]];
const RIBBON = ["#3b82f6", "#10b981", "#10b981", "#3b82f6", "#8b5cf6", null, "#3b82f6", "#ef4444", "#16a34a", "#16a34a", "#3b82f6", "#ef4444",
  "#10b981", "#10b981", "#3b82f6", null, "#3b82f6", "#16a34a", "#8b5cf6", "#3b82f6"];
const DayPanel = ({ b }) => (
  <div style={{ ...panel, width: 780, padding: "30px 36px", background: "rgba(8,8,9,0.96)" }}>
    <div style={{ fontSize: 19, color: C.n400, letterSpacing: "0.08em" }}>YOUR TIME · TODAY</div>
    <div style={{ fontSize: 86, fontWeight: 700, marginTop: 4, fontVariantNumeric: "tabular-nums", letterSpacing: "-0.02em" }}>
      <Count to={642} at={0.3} dur={2.4} format={(n) => `${Math.floor(n / 60)}h ${String(n % 60).padStart(2, "0")}m`} />
    </div>
    <div style={{ fontSize: 21, color: C.n500, marginTop: -4 }}>on screen</div>
    <div style={{ display: "flex", gap: 4, marginTop: 26, height: 22 }}>
      {RIBBON.map((c, i) => (
        <span key={i} style={{ flex: 1, borderRadius: 5, background: c || "transparent", opacity: rise(b, 0.4 + i * 0.07, 0.5),
          transform: `scaleY(${rise(b, 0.4 + i * 0.07, 0.6, EASES.bouncy)})` }} />
      ))}
    </div>
    <div style={{ marginTop: 26 }}>
      {APPS.map(([name, color, mins, label], i) => (
        <div key={name} style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 24, padding: "8px 0", opacity: rise(b, 0.8 + i * 0.3, 0.6) }}>
          <span style={{ width: 12, height: 12, borderRadius: 9, background: color }} />
          <span style={{ width: 150 }}>{name}</span>
          <span style={{ flex: 1, height: 12, borderRadius: 9, background: "rgba(255,255,255,0.06)" }}>
            <span style={{ display: "block", height: "100%", borderRadius: 9, background: color, width: `${(mins / 209) * 100 * rise(b, 1 + i * 0.3, 1.6)}%` }} />
          </span>
          <span style={{ width: 92, textAlign: "right", color: "#d4d4d4", fontVariantNumeric: "tabular-nums" }}>{label}</span>
        </div>
      ))}
    </div>
  </div>
);
const DAY_LINE = "10 hours 42 minutes on screen today. Most on VS Code (3 hours 29 minutes), then Notion.";
const Day = () => {
  const b = useBeat();
  const words = DAY_LINE.split(" ");
  const n = Math.max(0, Math.min(words.length, Math.floor((b - 2.6) / 0.16) + 1));
  const cam = rise(b, 0, 8, EASES.smooth);
  const kick = useKick();
  return (
    <>
      <Glow color="rgba(16,185,129,0.13)" size={70} x={35} />
      <Stage ry={lerp(14, 2, cam)} rx={lerp(8, 3, cam)} z={lerp(-200, -40, cam)} y={40}>
        <Layer x={-400} z={lerp(-200, 40, kick(b, 0, 0.6))}><div style={{ opacity: kick(b, 0, 0.4) }}><DayPanel b={b} /></div></Layer>
        <Layer x={500} y={-120} z={lerp(-200, 110, kick(b, 2, 0.6))} ry={-6}>
          <div style={{ ...panel, width: 640, opacity: kick(b, 2, 0.4) }}>
            <div style={{ padding: "24px 30px 0", fontSize: 16, color: C.n500, letterSpacing: "0.08em" }}>YOUR TIME</div>
            <div style={{ padding: "2px 30px 0", fontSize: 24, color: "#e5e5e5" }}>how was my day?</div>
            <div style={{ padding: "18px 30px 28px", fontSize: 30, lineHeight: 1.45, minHeight: 170 }}>{words.slice(0, n).join(" ")}</div>
          </div>
        </Layer>
      </Stage>
      <div style={{ position: "absolute", top: 70, width: "100%", textAlign: "center" }}>
        <Reveal at={0.2} dur={1} out={6.6}><span style={head(54, { fontWeight: 500 })}>“Jimmy, how was my day?”</span></Reveal>
      </div>
      <Caption bottom={46}>
        <Reveal at={4.4} dur={1}><span style={head(44, { color: MUTED, fontWeight: 500 })}>Instant. <span style={{ color: INK }}>From your own data.</span></span></Reveal>
      </Caption>
    </>
  );
};

// --- 10. Hands: it proposes, you approve ---------------------------------------------------
const BTN = { x: 640, y: -360 };   // the "Sign in" button, in stage px from the centre
const Hands = () => {
  const b = useBeat();
  const cam = rise(b, 0, 8, EASES.smooth);
  const kick = useKick();
  const plan = kick(b, 2, 0.5);
  const yes = kick(b, 3, 0.25);
  const go = rise(b, 3.3, 1.1, EASES.smooth);
  const click = b >= 4.4;
  const ripple = rise(b, 4.4, 0.9);
  const cx = lerp(-80, BTN.x - 20, go);
  const cy = lerp(160, BTN.y + 10, go) - Math.sin(go * Math.PI) * 120;
  return (
    <>
      <Stage ry={lerp(-10, -3, cam)} rx={lerp(6, 2, cam)} z={lerp(-150, -60, cam)}>
        <Layer z={-200} w={1640} h={924}>
          <div style={{ width: "100%", height: "100%", borderRadius: 28, overflow: "hidden", background: "#f5f6f8", fontFamily: UI, color: "#111" }}>
            <div style={{ height: 64, background: "#e3e5ea", display: "flex", alignItems: "center", gap: 14, padding: "0 26px", fontSize: 21 }}>
              <span style={{ width: 16, height: 16, borderRadius: 4, background: "#4f46e5" }} /> Northwind Fellowship
              <span style={{ marginLeft: 40, background: "#fff", borderRadius: 99, padding: "8px 22px", color: "#555", flex: 1 }}>northwind-fellowship.org</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", padding: "26px 60px" }}>
              <span style={{ fontWeight: 700, fontSize: 28, color: "#1e3a8a" }}>NORTHWIND FELLOWSHIP</span>
              <span style={{ marginLeft: "auto", fontSize: 26, fontWeight: 600, color: "#fff", padding: "14px 34px", borderRadius: 14,
                background: click ? "#1e40af" : "#2563eb", transform: `scale(${click ? 0.96 + 0.04 * ripple : 1})` }}>
                {b >= 5 ? "Signed in ✓" : "Sign in"}</span>
            </div>
            <div style={{ padding: "60px 60px" }}>
              <div style={{ fontSize: 76, fontWeight: 700, letterSpacing: "-0.02em" }}>2027 Fellowship</div>
              <div style={{ fontSize: 30, color: "#555", marginTop: 16 }}>A 12-week programme for early-career builders.</div>
              {[70, 84, 62, 78].map((w, i) => <div key={i} style={{ width: `${w}%`, height: 18, borderRadius: 9, background: "#e2e4ea", marginTop: i ? 20 : 54 }} />)}
            </div>
          </div>
        </Layer>
        {/* click ripple */}
        <Layer x={BTN.x} y={BTN.y + 45} z={-190} w={10} h={10}>
          <div style={{ width: 10, height: 10, borderRadius: 99, border: `3px solid ${C.sky}`, opacity: click ? 1 - ripple : 0, transform: `scale(${1 + 18 * ripple})` }} />
        </Layer>
        {/* Jimmy's own cursor (never yours) */}
        <Layer x={cx} y={cy + 45} z={-120}>
          <div style={{ opacity: rise(b, 3.2, 0.4) * (1 - rise(b, 6.4, 0.5)), display: "flex", alignItems: "flex-start", gap: 4,
            transform: `translate(26px, 22px) scale(${click ? 0.92 + 0.08 * ripple : 1})` }}>
            <svg width="44" height="50" viewBox="0 0 22 25"><path d="M2 2 L2 20 L7 15.5 L10.5 23 L13.5 21.6 L10.2 14.3 L17 14 Z" fill={C.sky} stroke="#fff" strokeWidth="1.6" strokeLinejoin="round" /></svg>
            <span style={{ marginTop: 34, fontFamily: UI, fontSize: 20, fontWeight: 600, color: "#04263a", background: C.sky, padding: "3px 12px", borderRadius: 8 }}>Jimmy</span>
          </div>
        </Layer>
        <Layer y={-250} x={-140} z={180}>
          <div style={{ opacity: plan * (1 - rise(b, 4.3, 0.5)), transform: `translateY(${(1 - plan) * -30}px)` }}>
            <div style={{ ...panel, width: 560, padding: "22px 26px" }}>
              <div style={{ fontSize: 17, color: C.n400, letterSpacing: "0.08em" }}>PLAN · 1 STEP</div>
              <div style={{ fontSize: 30, fontWeight: 600, marginTop: 6 }}>Click “Sign in”</div>
              <div style={{ display: "flex", gap: 12, marginTop: 18, fontSize: 22 }}>
                <span style={{ padding: "8px 22px", borderRadius: 10, background: yes > 0 ? `rgba(52,211,153,${0.2 + 0.6 * yes})` : "rgba(255,255,255,0.12)",
                  color: yes > 0.5 ? "#052e22" : "#fafafa", transform: `scale(${1 - 0.06 * Math.sin(yes * Math.PI)})` }}>Yes</span>
                <span style={{ padding: "8px 22px", borderRadius: 10, background: "rgba(255,255,255,0.06)", color: C.n400 }}>Not now</span>
              </div>
            </div>
          </div>
        </Layer>
        <Layer y={-455} z={200}>
          <div style={{ opacity: rise(b, 0, 0.6) }}>
            {b >= 5 ? <Pill mode="done" text="Clicked “Sign in”" /> : b < 2 ? <Pill mode="listening" /> : <Pill text="Waiting for your yes" />}
          </div>
        </Layer>
      </Stage>
      <Caption bottom={40}>
        <div style={{ position: "relative", height: 70 }}>
          <div style={{ position: "absolute", width: "100%" }}>
            <Reveal at={0.2} dur={0.9} out={3.2}><span style={head(54, { fontWeight: 500 })}>“Jimmy, click Sign in.”</span></Reveal>
          </div>
          <div style={{ position: "absolute", width: "100%" }}>
            <Reveal at={5} dur={1}><span style={head(54)}>It proposes. <span style={ACCENT}>You approve.</span></span></Reveal>
          </div>
        </div>
      </Caption>
      <Cover at={0} dur={0.3} />
    </>
  );
};

// --- 11. Everything else, one per beat ----------------------------------------------------
// --- Skill shots: one skill each, its own UI alone on black --------------------------------
// The camera is one smooth drift per shot; only the elements land on the song's kicks.
const SkillShot = ({ icon: Icon, color, name, quote, len, children, ry = [-7, 5], uiY = 70 }) => {
  const b = useBeat();
  const cam = rise(b, 0, len, EASES.smooth);
  return (
    <>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 55% 45% at 50% 62%, ${color}26, transparent 72%)` }} />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 96 }}>
        <Reveal at={0} dur={0.5} y={12} blur={6}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 12, fontFamily: UI, fontSize: 24, fontWeight: 600, color,
            background: `${color}1f`, boxShadow: `0 0 0 1.5px ${color}55`, borderRadius: 999, padding: "8px 20px", letterSpacing: "0.04em" }}>
            <Icon size={22} /> {name}</span>
        </Reveal>
        <Words text={quote} at={0.2} step={0.12} y={22} blur={10} style={{ ...head(70), marginTop: 26, textAlign: "center", whiteSpace: "nowrap" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ perspective: 1800 }}>
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingTop: uiY * 2,
          transform: `rotateY(${lerp(ry[0], ry[1], cam)}deg) rotateX(${lerp(4, 1, cam)}deg) scale(${lerp(0.97, 1.03, cam)})` }}>
          {children}
        </AbsoluteFill>
      </AbsoluteFill>
    </>
  );
};
// An element that lands on the nearest kick: rises, sharpens, settles.
const Land = ({ at, from = [0, 50], dur = 0.45, children, style }) => {
  const b = useBeat();
  const p = useKick()(b, at, dur);
  return <div style={{ opacity: p, transform: `translate(${from[0] * (1 - p)}px, ${from[1] * (1 - p)}px) scale(${0.94 + 0.06 * p})`,
    filter: p < 1 ? `blur(${(1 - p) * 12}px)` : undefined, ...style }}>{children}</div>;
};
const StreamText = ({ text, at, step = 0.11, hi = 999, size = 32 }) => {
  const b = useBeat();
  const at2 = useSnap()(at);
  const w = text.split(" ");
  const n = Math.max(0, Math.min(w.length, Math.floor((b - at2) / step) + 1));
  return <div style={{ fontFamily: UI, fontSize: size, lineHeight: 1.45, color: "#fafafa" }}>
    {b < at2 ? <Shimmer>Thinking…</Shimmer> : w.slice(0, n).map((x, i) => <span key={i} style={i >= hi ? { color: "#6ee7b7" } : undefined}>{x} </span>)}
  </div>;
};

const AskShot = () => (
  <SkillShot icon={Mic} color={C.sky} name="Ask" quote="“Jimmy, what was that fellowship on Tuesday?”" len={6}>
    <div style={{ display: "flex", gap: 34, alignItems: "center" }}>
      <Land at={1.5} from={[-80, 0]}>
        <div style={{ ...panel, width: 430, padding: 16 }}>
          <Pic src="fellowship.jpg" width="100%" height={240} radius={14} />
          <div style={{ display: "flex", alignItems: "center", marginTop: 14, fontSize: 19, color: C.n400 }}>Tue 22 Sep · 14:02
            <span style={{ marginLeft: "auto", fontSize: 17, color: "#6ee7b7", background: "rgba(52,211,153,0.14)", borderRadius: 8, padding: "3px 10px" }}>best match</span></div>
        </div>
      </Land>
      <Land at={2} from={[80, 0]}>
        <div style={{ ...panel, width: 780, padding: "30px 36px", minHeight: 250 }}>
          <div style={{ fontSize: 17, color: C.n500, letterSpacing: "0.08em", marginBottom: 12 }}>JIMMY · ANSWERED IN ~1 S</div>
          <StreamText at={2.5} hi={7} text="The Northwind Fellowship, seen Tuesday at 14:02. Applications close Monday, 12 October at 11:59 pm." />
        </div>
      </Land>
    </div>
  </SkillShot>
);

const ProofShot = () => {
  const b = useBeat();
  const kick = useKick();
  const draw = kick(b, 1, 0.5);
  const badge = kick(b, 1.6, 0.4);
  return (
    <SkillShot icon={Search} color={C.emerald} name="Proof" quote="It shows its work." len={4} ry={[6, -4]}>
      <Land at={0.4} from={[0, 70]}>
        <div style={{ position: "relative", width: 1100, height: 619 }}>
          <Pic src="fellowship.jpg" width={1100} height={619} radius={24} />
          <div style={{ position: "absolute", left: 258, top: 232, width: 584, height: 62, borderRadius: 12, boxShadow: `0 0 50px rgba(52,211,153,${0.6 * draw})` }} />
          <div style={{ position: "absolute", left: 258, top: 232, width: 584, height: 62, borderRadius: 12, border: `5px solid ${C.emerald}`, boxSizing: "border-box",
            clipPath: `inset(0 ${100 - 100 * draw}% 0 0)` }} />
          <div style={{ position: "absolute", left: 600, top: 128, fontFamily: UI, fontSize: 24, fontWeight: 600, color: "#052e22", background: C.emerald,
            padding: "6px 16px", borderRadius: 10, opacity: badge, transform: `scale(${0.7 + 0.3 * badge})` }}>best match · Tue 14:02</div>
        </div>
      </Land>
    </SkillShot>
  );
};

const ScreenShot = () => {
  const b = useBeat();
  const s0 = useSnap()(0.6);
  const scan = interpolate(b, [s0, s0 + 1], [0, 100], { ...clamp, easing: EASES.smooth });
  return (
    <SkillShot icon={MonitorSmartphone} color={C.violet} name="Screen" quote="“What's on my screen?”" len={4}>
      <div style={{ display: "flex", gap: 34, alignItems: "center" }}>
        <Land at={0.4} from={[-60, 0]}>
          <div style={{ position: "relative", width: 640, height: 360, borderRadius: 18, overflow: "hidden" }}>
            <Pic src="oauth.jpg" width={640} height={360} radius={18} />
            <div style={{ position: "absolute", left: 0, right: 0, top: `${scan}%`, height: 4, background: C.violet, boxShadow: `0 0 30px 8px ${C.violet}`,
              opacity: scan > 0 && scan < 100 ? 1 : 0 }} />
            <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: `${scan}%`, background: "rgba(167,139,250,0.10)" }} />
          </div>
        </Land>
        <Land at={1.5} from={[60, 0]}>
          <div style={{ ...panel, width: 700, padding: "30px 36px", minHeight: 210 }}>
            <div style={{ fontSize: 17, color: C.n500, letterSpacing: "0.08em", marginBottom: 12 }}>ON YOUR SCREEN · CHROME</div>
            <StreamText at={1.8} step={0.1} text="“OAuth 2.0, explained simply”: how apps sign you in without ever seeing your password." />
          </div>
        </Land>
      </div>
    </SkillShot>
  );
};

const STRIP = [["plan.jpg", "09:40"], ["oauth.jpg", "11:05"], ["timeline.jpg", "12:20"], ["fellowship.jpg", "14:02"], ["plan.jpg", "15:30"], ["oauth.jpg", "17:12"], ["timeline.jpg", "18:45"]];
const TimelineShot = () => {
  const b = useBeat();
  const hit = useKick()(b, 2, 0.4);
  const slide = rise(b, 0, 4, EASES.smooth);
  const typeAt = useSnap()(0.6);
  return (
    <SkillShot icon={History} color={C.sky} name="Timeline" quote="Search your day by meaning." len={4}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 40 }}>
        <Land at={0.3} from={[0, 30]}>
          <div style={{ ...panel, borderRadius: 999, width: 820, padding: "18px 30px", display: "flex", alignItems: "center", gap: 18, fontSize: 32 }}>
            <Search size={30} color={C.n400} /><Stream text="fellowship deadline" at={typeAt} step={0.3} />
          </div>
        </Land>
        <Land at={0.8} from={[0, 40]} style={{ width: 1700, overflow: "hidden", padding: "40px 0", maskImage: "linear-gradient(90deg, transparent, #000 14%, #000 86%, transparent)", WebkitMaskImage: "linear-gradient(90deg, transparent, #000 14%, #000 86%, transparent)", display: "flex", justifyContent: "center" }}>
          <div style={{ display: "flex", gap: 20, transform: `translateX(${lerp(140, -140, slide)}px)` }}>
            {STRIP.map(([src, t], i) => {
              const m = i === 3;
              return (
                <div key={i} style={{ width: 280, flexShrink: 0, transform: `scale(${m ? 1 + 0.12 * hit : 1 - 0.04 * hit})`, opacity: m ? 1 : 1 - 0.55 * hit }}>
                  <div style={{ borderRadius: 14, overflow: "hidden", boxShadow: m ? `0 0 0 ${4 * hit}px ${C.emerald}, 0 0 ${50 * hit}px rgba(52,211,153,0.5)` : "0 0 0 1.5px rgba(255,255,255,0.1)" }}>
                    <Pic src={src} width={280} height={158} radius={0} style={{ filter: m ? undefined : "blur(1.5px)" }} />
                  </div>
                  <div style={{ fontFamily: UI, fontSize: 21, color: m ? "#6ee7b7" : C.n500, marginTop: 10, textAlign: "center" }}>{m ? "Tue 14:02 · match" : t}</div>
                </div>
              );
            })}
          </div>
        </Land>
      </div>
    </SkillShot>
  );
};

const RemindShot = () => {
  const b = useBeat();
  const at = useSnap()(1.6);
  const ring = b > at ? Math.sin((b - at) * 22) * 18 * Math.exp(-(b - at) * 2.2) : 0;
  return (
    <SkillShot icon={Bell} color={C.amber} name="Reminders" quote="“Remind me at 5 to call Sam.”" len={4}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 34 }}>
        <Land at={0.9} from={[0, -30]}><Pill mode="done" text="Reminder set · 17:00" size={30} /></Land>
        <Land at={1.6} from={[0, -90]}>
          <div style={{ ...panel, width: 760, padding: "30px 36px 36px", borderRadius: 32 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 22, color: C.n400 }}>
              <span style={{ width: 46, height: 46, borderRadius: 12, background: "rgba(251,191,36,0.15)", color: "#fde68a", display: "grid", placeItems: "center",
                transform: `rotate(${ring}deg)` }}><Bell size={26} /></span>
              <span style={{ textTransform: "uppercase", letterSpacing: "0.08em" }}>Reminder</span>
              <span style={{ marginLeft: "auto", color: "#fde68a", fontSize: 26, fontWeight: 600 }}>17:00</span>
            </div>
            <div style={{ marginTop: 18, fontSize: 52, fontWeight: 600, color: "#fafafa" }}>Call Sam</div>
          </div>
        </Land>
      </div>
    </SkillShot>
  );
};

const DayShot = () => {
  const b = useBeat();
  return (
    <SkillShot icon={Target} color={C.emerald} name="Your time" quote="“How was my day?”" len={4} uiY={60}>
      <Land at={0.3} from={[0, 60]}><div style={{ transform: "scale(0.92)" }}><DayPanel b={b - 0.3} /></div></Land>
    </SkillShot>
  );
};

const TimerShot = () => {
  const b = useBeat();
  const start = useSnap()(1);
  const sec = Math.max(0, (b - start) * 0.6123);
  const left = Math.max(0, 600 - Math.floor(sec));
  const frac = sec - Math.floor(sec);
  const roll = b > start ? rise(frac, 0, 0.3, EASES.snappy) : 1;   // the last digit rolls in each second
  const mm = String(Math.floor(left / 60)).padStart(2, "0");
  const ss = String(left % 60).padStart(2, "0");
  const size = 230;
  const cell = (v) => <span style={{ display: "inline-block", width: size * 0.62, textAlign: "center" }}>{v}</span>;
  return (
    <SkillShot icon={Timer} color="#fb923c" name="Timers" quote="“Set a timer for 10 minutes.”" len={4}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
        <Land at={0.5} from={[0, -30]}>
          <div style={{ ...panel, borderRadius: 999, display: "inline-flex", alignItems: "center", gap: 16, padding: "12px 26px", fontSize: 28 }}>
            <span style={{ width: 11, height: 11, borderRadius: 9, background: C.emerald }} /><span style={{ fontWeight: 600 }}>Jimmy</span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(251,191,36,0.15)", color: "#fde68a", borderRadius: 999, padding: "4px 14px",
              fontVariantNumeric: "tabular-nums" }}><Timer size={22} /> {mm}:{ss}</span>
          </div>
        </Land>
        <Land at={1} from={[0, 60]}>
          <div style={{ ...head(size, { fontWeight: 600, letterSpacing: "-0.02em" }), display: "flex", color: "#fff7ed" }}>
            {cell(mm[0])}{cell(mm[1])}<span style={{ opacity: 0.5 }}>:</span>{cell(ss[0])}
            <span style={{ display: "inline-block", width: size * 0.62, textAlign: "center", overflow: "hidden", height: size * 1.08 }}>
              <span style={{ display: "inline-block", transform: `translateY(${(1 - roll) * 60}%)`, opacity: roll }}>{ss[1]}</span>
            </span>
          </div>
        </Land>
      </div>
    </SkillShot>
  );
};

// --- Fragments of a day: they pop in on the kicks around the opening line, then Jimmy
// pulls them into its dot right before the drop. Kept out of the text band (|y| >= 200).
const FRAGS = [
  ["Northwind Fellowship · Apply", "#3b82f6", -560, -330],
  ["OAuth 2.0, explained simply", "#8b5cf6", 520, -300],
  ["Sam: call me at 5?", "#22c55e", -640, 250],
  ["Standup moved to 11", "#f59e0b", 600, 290],
  ["Applications close 12 Oct", "#f43f5e", -60, -420],
  ["Weekly plan", "#10b981", 80, 400],
  ["Discord · 3 new messages", "#6366f1", 600, -440],
  ["Fellowship essay · draft 2", "#a3a3a3", -600, 430],
];
const FRAG_AT = [2.4, 3.25, 4.1, 4.65, 5.1, 6, 6.3, 7];
const Frag = ({ text, color }) => (
  <div style={{ ...panel, borderRadius: 999, display: "inline-flex", alignItems: "center", gap: 12, padding: "12px 22px", fontSize: 24, whiteSpace: "nowrap",
    color: "#e5e5e5" }}>
    <span style={{ width: 12, height: 12, borderRadius: 4, background: color }} />{text}
  </div>
);
const at0 = (x, y, extra) => ({ position: "absolute", left: "50%", top: "50%", transform: `translate(-50%, -50%) translate(${x}px, ${y}px) ${extra || ""}` });

const ColdOpen = () => {
  const b = useBeat();
  const kick = useKick();
  const drift = rise(b, 0, 9.5, EASES.smooth);
  return (
    <AbsoluteFill style={{ transform: `scale(${1 + 0.035 * drift})` }}>
      <Glow color="rgba(125,211,252,0.10)" size={70} at={1} />
      {FRAGS.map(([t, c, x, y], i) => {
        const p = kick(b, FRAG_AT[i], 0.45);
        return (
          <div key={t} style={{ ...at0(x + (x > 0 ? 30 : -30) * drift, y + (y > 0 ? 14 : -14) * drift, `scale(${0.85 + 0.15 * p})`),
            opacity: p * 0.85, filter: p < 1 ? `blur(${(1 - p) * 10}px)` : undefined }}><Frag text={t} color={c} /></div>
        );
      })}
      <Center>
        <Words text="Every day, you see thousands of things." at={1.5} step={0.5} accent={[4]} out={9}
          style={{ ...head(84), whiteSpace: "nowrap" }} />
      </Center>
    </AbsoluteFill>
  );
};

const DOT_Y = 170;
const WhatIf = () => {
  const b = useBeat();
  const dotIn = rise(b, 4.2, 0.5);
  const toCenter = rise(b, 7.1, 0.4, EASES.smooth);
  const beatPulse = Math.exp(-Math.max(0, b - 7.4) * 2.2);
  const landed = FRAGS.filter((_, i) => b > 5.0 + i * 0.22 + 1.1).length;
  const dy = lerp(DOT_Y, 0, toCenter);
  return (
    <>
      {FRAGS.map(([t, c, x, y], i) => {
        const show = rise(b, 0.4 + i * 0.1, 0.8);
        const pull = interpolate(b, [5.0 + i * 0.22, 6.1 + i * 0.22], [0, 1], { ...clamp, easing: Easing.bezier(0.7, 0, 0.84, 0) });
        return (
          <div key={t} style={{ ...at0(lerp(x, 0, pull), lerp(y, DOT_Y, pull), `scale(${1 - 0.85 * pull})`),
            opacity: show * 0.7 * (1 - pull), filter: `blur(${pull * 6}px)` }}><Frag text={t} color={c} /></div>
        );
      })}
      <AbsoluteFill style={{ transform: "translateY(-150px)" }}>
        <Center>
          <Words text="What if your PC remembered for you?" at={0.25} step={0.4} accent={[4, 5, 6]} out={7.1} outDur={0.35}
            style={{ ...head(88), whiteSpace: "nowrap" }} />
        </Center>
      </AbsoluteFill>
      <div style={{ ...at0(0, dy), width: 22, height: 22, borderRadius: 99, background: C.emerald, opacity: dotIn,
        transform: `translate(-50%, -50%) translate(0px, ${dy}px) scale(${0.6 + 0.4 * dotIn + 0.08 * landed + 0.35 * beatPulse * toCenter})`,
        boxShadow: `0 0 ${30 + 8 * landed + 60 * beatPulse * toCenter}px ${C.emerald}` }} />
    </>
  );
};

// --- 11. And everything in between: a clean grid, each tile with a tiny live detail ---------
const TILES = [
  [Target, "Focus", "“focus on the essay”", C.violet, "focus"],
  [PenLine, "Drafts", "“draft a reply to this”", C.sky, "draft"],
  [CalendarClock, "Calendar", "“add this to my calendar”", C.rose, "cal"],
  [Archive, "Compacts itself", "Frees space while you're away", C.amber, "compact"],
  [Languages, "हिन्दी + English", "Ask in either language", C.emerald, "hindi"],
  [Lock, "Private", "Capture stays on your laptop", "#94a3b8", "lock"],
  [MessageCircleQuestion, "Asks back", "“what's this?”", "#38bdf8", "askback"],
  [AppWindow, "Your windows", "“switch to Chrome”", "#a3e635", "windows"],
  [Hand, "Hands-free", "“scroll down” · “next”", "#f472b6", "handsfree"],
];
const TILE_AT = [0.2, 0.6, 1, 1.6, 2, 2.5, 3, 3.5, 4];
const chip = (color, children) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 8, fontFamily: UI, fontSize: 21, color, background: `${color}1c`,
    boxShadow: `0 0 0 1px ${color}40`, borderRadius: 999, padding: "6px 14px", whiteSpace: "nowrap" }}>{children}</span>
);
const Detail = ({ kind, color, t }) => {
  if (kind === "focus") return chip(color, <><Target size={16} /> finish the essay · {Math.round(52 - 2 * t)}m</>);
  if (kind === "draft") return chip(color, <><Check size={16} /> Draft copied to clipboard</>);
  if (kind === "cal") return chip(color, <><CalendarClock size={16} /> Mon 12 Oct · 23:59</>);
  if (kind === "hindi") return <span style={{ fontFamily: `${devaFamily}, ${UI}`, fontSize: 22, color: "#a7f3d0" }}>“आज मेरा दिन कैसा था?”</span>;
  if (kind === "lock") return chip(color, <><Lock size={16} /> On this laptop only</>);
  if (kind === "askback") return <span style={{ display: "flex", gap: 8 }}>{chip(color, "Now")}{chip("#a3a3a3", "Earlier")}</span>;
  if (kind === "windows") return chip(color, <><AppWindow size={16} /> Chrome · VS Code · Notion</>);
  if (kind === "handsfree") return chip(color, <><Hand size={16} /> No wake word for 45 s</>);
  // compact: a storage bar that shrinks as Jimmy cleans up
  const k = rise(t, 0.3, 1.6, EASES.smooth);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, width: "100%" }}>
      <span style={{ flex: 1, height: 10, borderRadius: 9, background: "rgba(255,255,255,0.07)", overflow: "hidden" }}>
        <span style={{ display: "block", height: "100%", width: `${lerp(86, 38, k)}%`, borderRadius: 9, background: `linear-gradient(90deg, ${color}, #fde68a)` }} />
      </span>
      <span style={{ fontFamily: UI, fontSize: 20, color: "#fde68a", whiteSpace: "nowrap" }}>{k > 0.95 ? "Space freed" : "Compacting…"}</span>
    </div>
  );
};
const Montage = () => {
  const b = useBeat();
  const kick = useKick();
  const drift = rise(b, 0, 6.5, EASES.smooth);
  return (
    <>
      <Glow color="rgba(125,211,252,0.10)" size={80} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", transform: `scale(${1.04 - 0.04 * drift}) translateY(${10 - 20 * drift}px)` }}>
        <Reveal at={0} dur={0.6} y={16}><div style={head(56, { textAlign: "center", marginBottom: 34 })}>And everything <span style={ACCENT}>in between.</span></div></Reveal>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 520px)", gap: 22 }}>
          {TILES.map(([Icon, word, say, color, kind], i) => {
            const p = kick(b, TILE_AT[i], 0.45);
            const flash = 1 - rise(b, TILE_AT[i], 1.2);
            const deva = word.startsWith("हि");
            return (
              <div key={word} style={{ position: "relative", height: 206, borderRadius: 28, padding: "22px 30px", boxSizing: "border-box", fontFamily: UI, color: "#fafafa",
                background: `radial-gradient(120% 90% at 0% 0%, ${color}22, transparent 55%), linear-gradient(180deg, #141416, #0c0c0d)`,
                boxShadow: `inset 0 1px 0 rgba(255,255,255,0.08), 0 0 0 1.5px ${p > 0.5 ? color : "#ffffff"}${p > 0.5 ? Math.round(40 + 120 * flash).toString(16).padStart(2, "0") : "1f"}, 0 0 ${60 * flash}px ${color}55, 0 40px 90px -30px #000`,
                opacity: p, transform: `translateY(${(1 - p) * 40}px) scale(${0.94 + 0.06 * p})`, filter: p < 1 ? `blur(${(1 - p) * 10}px)` : undefined,
                display: "flex", flexDirection: "column" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
                  <span style={{ width: 56, height: 56, borderRadius: 16, background: `${color}24`, color, display: "grid", placeItems: "center", flexShrink: 0,
                    boxShadow: `0 0 ${24 * flash}px ${color}` }}><Icon size={28} /></span>
                  <span style={{ ...head(40), fontFamily: deva ? `${devaFamily}, ${head(1).fontFamily}` : head(1).fontFamily, letterSpacing: deva ? 0 : "-0.03em", whiteSpace: "nowrap" }}>{word}</span>
                </div>
                <div style={{ fontSize: 23, color: "#a3a3a3", marginTop: 12, whiteSpace: "nowrap" }}>{say}</div>
                <div style={{ marginTop: "auto", display: "flex" }}><Detail kind={kind} color={color} t={b - TILE_AT[i]} /></div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </>
  );
};

// --- 12. End card on the song's last chord -------------------------------------------------
const End = () => {
  const b = useBeat();
  const p = rise(b, 0.5, 0.8, EASES.snappy);
  const sweep = interpolate(b, [0.5, 3.2], [-30, 130], clamp);
  return (
    <AbsoluteFill style={{ opacity: interpolate(b, [5.3, 6], [1, 0], clamp) }}>
      <AbsoluteFill style={{ opacity: rise(b, 0, 2), background: "radial-gradient(ellipse 55% 40% at 50% 58%, rgba(56,189,248,0.14), rgba(167,139,250,0.08) 50%, transparent 78%)" }} />
      <Center style={{ flexDirection: "column", gap: 26 }}>
        <Reveal at={0} dur={0.6} y={-16} blur={8}><Pill ping={(b * 0.8) % 1} size={30} /></Reveal>
        <div style={{ ...head(190, { fontWeight: 600, letterSpacing: "-0.05em", paddingBottom: 16 }), opacity: p,
          transform: `scale(${1.12 - 0.12 * p})`, filter: `blur(${(1 - p) * 22}px)`,
          backgroundImage: `linear-gradient(100deg, #e9e9ee 0%, #e9e9ee ${sweep - 14}%, #ffffff ${sweep}%, #c5d9ff ${sweep + 4}%, #e9e9ee ${sweep + 16}%, #e9e9ee 100%)`,
          WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>Coming soon.</div>
        <Reveal at={1.4} dur={1}><div style={head(50, { fontWeight: 500 })}>It remembers. <span style={ACCENT}>So you don’t have to.</span></div></Reveal>
        <Reveal at={2.2} dur={1}><div style={{ ...head(28, { color: MUTED, fontWeight: 500, letterSpacing: "0.14em", textTransform: "uppercase" }), marginTop: 14 }}>For Windows 11</div></Reveal>
      </Center>
    </AbsoluteFill>
  );
};

export const Video = (props) => (
  <Film fps={cfg.fps} punch={cfg.punch} totalBeats={cfg.totalBeats} {...props}>
    <Scene from={0} to={9.5} exit="soft"><ColdOpen /></Scene>
    <Scene from={9.5} to={17.5} enter="soft" exit="hard"><Forget /></Scene>
    <Scene from={17.5} to={25.5} enter="hard"><WhatIf /></Scene>
    <Scene from={25.5} to={31.5} enter="hard" exit="hard"><Reveal4 /></Scene>
    <Scene from={31.5} to={37.5} enter="hard" exit="hard"><AskShot /></Scene>
    <Scene from={37.5} to={41.5} enter="hard" exit="hard"><ProofShot /></Scene>
    <Scene from={41.5} to={45.5} enter="hard" exit="hard"><ScreenShot /></Scene>
    <Scene from={45.5} to={49.5} enter="hard" exit="hard"><TimelineShot /></Scene>
    <Scene from={49.5} to={53.5} enter="hard" exit="hard"><RemindShot /></Scene>
    <Scene from={53.5} to={61} enter="hard" exit="soft"><Cards /></Scene>
    <Scene from={61} to={69.5} enter="soft" exit="hard"><Privacy /></Scene>
    <Scene from={69.5} to={73.5} enter="hard" exit="hard"><DayShot /></Scene>
    <Scene from={73.5} to={77.5} enter="hard" exit="hard"><TimerShot /></Scene>
    <Scene from={77.5} to={85.5} enter="hard" exit="hard"><Hands /></Scene>
    <Scene from={85.5} to={92} enter="hard" exit="hard"><Montage /></Scene>
    <Scene from={92} to={98} enter="hard"><End /></Scene>
  </Film>
);
