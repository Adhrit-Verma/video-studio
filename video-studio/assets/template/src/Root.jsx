import { Composition } from "remotion";
import cfg from "../video.json";
import { Video } from "./Video.jsx";

// Props come from out/props.json (gen_beat.py or master_audio.py): { music, bpm, offset, kicks, kickWeights, energy, bass }.
// Without music, render without --props: bpm comes from video.json (60 = 1 beat per second).
const meta = ({ props }) => ({ durationInFrames: Math.round((cfg.totalBeats * 60 * cfg.fps) / props.bpm) });
const DEFAULTS = { music: null, bpm: cfg.bpm, offset: 0, kicks: [], kickWeights: [], energy: [], bass: [] };
const frames = Math.round((cfg.totalBeats * 60 * cfg.fps) / cfg.bpm);
const FORMATS = [
  ["Film", 1920, 1080, "wide"],          // YouTube, site hero, presentations
  ["FilmTall", 1080, 1920, "tall"],      // Reels, TikTok, Shorts, Stories
  ["FilmSquare", 1080, 1080, "square"],  // feeds, LinkedIn
  ["FilmPortrait", 1080, 1350, "portrait"], // Instagram feed 4:5
];

export const Root = () => (
  <>
    {FORMATS.map(([id, width, height, format]) => (
      <Composition key={id} id={id} component={Video} fps={cfg.fps} width={width} height={height}
        durationInFrames={frames} defaultProps={{ ...DEFAULTS, format }} calculateMetadata={meta} />
    ))}
  </>
);
