// Render many stills from ONE bundle (the CLI re-bundles per still: minutes vs seconds).
//   node tools/stills.mjs --comp Film --frames 30,120,240 [--props out/props.json] [--outdir out/stills]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const arg = (name, dflt) => {
  const i = process.argv.indexOf(`--${name}`);
  return i > 0 ? process.argv[i + 1] : dflt;
};
const comp = arg("comp", "Film");
const frames = arg("frames", "0").split(",").map(Number);
const propsPath = arg("props", "");
const outdir = arg("outdir", "out/stills");
const inputProps = propsPath && fs.existsSync(propsPath) ? JSON.parse(fs.readFileSync(propsPath, "utf8")) : {};

fs.mkdirSync(outdir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.js") });
const composition = await selectComposition({ serveUrl, id: comp, inputProps });
for (const frame of frames) {
  const output = path.join(outdir, `${comp}_${String(frame).padStart(5, "0")}.png`);
  await renderStill({ composition, serveUrl, output, frame, inputProps,
    onBrowserLog: (log) => { if (/\[(layout|readability)\]/.test(log.text)) console.log(log.text); } });
  console.log(`frame ${frame} -> ${output}`);
}
