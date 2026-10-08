// PLACEHOLDER scenes: each one only shows how to use a piece of the kit. Replace them
// with the storyboard agreed in the brief; the look comes from theme.js, not from here.
import { AbsoluteFill, interpolate } from "remotion";
import cfg from "../video.json";
import {
  ACCENT, Caption, Center, Count, Cover, Film, Glow, Layer, MUTED, Reveal, SURFACE, Scene, Stage, Stream, Words,
  accentFill, body, clamp, head, rise, useBeat, useFormat, useV,
} from "./kit.jsx";

const NAME = "Product";

// Mock UI built from divs: sharp at any zoom, text can animate. Real screenshots go through <Pic>.
const MockWindow = ({ w, h, children }) => (
  <div style={{ ...SURFACE, width: w, height: h, overflow: "hidden" }}>
    <div style={{ height: 44, display: "flex", alignItems: "center", gap: 8, padding: "0 16px", opacity: 0.9,
      borderBottom: "1px solid rgba(127,127,127,0.18)" }}>
      {[0, 1, 2].map((i) => <span key={i} style={{ width: 12, height: 12, borderRadius: 99, background: "rgba(127,127,127,0.35)" }} />)}
    </div>
    <div style={{ padding: 32 }}>{children}</div>
  </div>
);

// Pattern: type-led hook. Words land on the grid; one word carries the accent.
const Hook = () => (
  <Center>
    <Words text="Your hook line goes here." at={0} step={0.5} accent={[2]} out={7.4} style={head(useV() ? 96 : 110)} />
  </Center>
);

// Pattern: the product in 3D, the camera settling to frontal while content streams in.
const ProductMoment = () => {
  const b = useBeat();
  const v = useV();
  const k = rise(b, 0, 5);
  return (
    <>
      <Glow size={80} />
      <Stage rx={16 - 12 * k} ry={-20 + 16 * k} z={-200 + 160 * k}>
        <Layer><MockWindow w={v ? 880 : 1200} h={v ? 1200 : 660}>
          <div style={head(v ? 56 : 48)}>A feature, shown working</div>
          <div style={{ ...body(v ? 34 : 30), marginTop: 20, maxWidth: 900 }}>
            <Stream text="Content that streams in as if the product is answering right now." at={1.5} step={0.25} />
          </div>
        </MockWindow></Layer>
        <Layer x={v ? 0 : 520} y={v ? 360 : 250} z={140}>
          <div style={{ ...SURFACE, padding: "18px 26px", background: accentFill, color: "#fff", ...head(28, { color: "#fff" }),
            opacity: rise(b, 3, 0.8) }}>A floating detail</div>
        </Layer>
      </Stage>
      <Caption><Reveal at={5}><span style={head(44)}>One idea per scene. <span style={ACCENT}>Its payoff.</span></span></Reveal></Caption>
      <Cover at={0} dur={0.6} />
    </>
  );
};

// Pattern: proof as numbers.
const Proof = () => {
  const v = useV();
  const stats = [[12000, "people", (n) => `${Math.round(n / 1000)}k`], [49, "rating", (n) => (n / 10).toFixed(1)], [3, "clicks", String]];
  return (
    <Center style={{ flexDirection: v ? "column" : "row", gap: v ? 60 : 140 }}>
      {stats.map(([to, label, fmt], i) => (
        <Reveal key={label} at={i * 0.5} dur={1}>
          <div style={head(v ? 130 : 150, ACCENT)}><Count to={to} at={i * 0.5} dur={2.5} format={fmt} /></div>
          <div style={body(30)}>{label}</div>
        </Reveal>
      ))}
    </Center>
  );
};

// Pattern: end card with a call to action; fades over the last beats.
const End = () => {
  const b = useBeat();
  const p = rise(b, 0, 0.8);
  const fmt = useFormat();
  return (
    <AbsoluteFill style={{ opacity: interpolate(b, [6.4, 8], [1, 0], clamp) }}>
      <Glow size={70} />
      <Center style={{ flexDirection: "column" }}>
        <div style={head(fmt === "tall" ? 170 : 200, { ...ACCENT, paddingBottom: 14, opacity: p, transform: `scale(${1.06 - 0.06 * p})` })}>{NAME}.</div>
        <Reveal at={1}><div style={head(48, { color: MUTED, fontWeight: 600 })}>Your call to action.</div></Reveal>
      </Center>
    </AbsoluteFill>
  );
};

export const Video = (props) => (
  <Film fps={cfg.fps} punch={cfg.punch} totalBeats={cfg.totalBeats} {...props}>
    <Scene from={0} to={8}><Hook /></Scene>
    <Scene from={8} to={16}><ProductMoment /></Scene>
    <Scene from={16} to={24}><Proof /></Scene>
    <Scene from={24} to={32}><End /></Scene>
  </Film>
);
