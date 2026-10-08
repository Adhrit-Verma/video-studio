# Discovery: understand the subject before asking anything

The video must be about what the product *actually is*, in its own visual language.
Ten minutes of reading saves the user from answering questions you could have answered.

## 1. Decide what the input is
| Input | Recognize it by | Material comes from |
|---|---|---|
| Project | no input, or a local folder that is a project | the code (`discover.py <dir>`) |
| Website | an `http(s)://` URL or a bare domain | the live site (`discover.py <url>`, then a browser) |
| Repo URL | a GitHub/GitLab link | clone it shallow into the scratchpad, then treat it as a project |
| Other | a doc, deck, changelog, idea in chat | the material itself; ask for 2-3 references if the look is unclear |
If nothing matches, ask what the video is about.

## 2. Run the scan
```bash
python <skill>/scripts/discover.py <project-dir-or-url> --out brief
```
For a folder it prints and saves (`brief/discovery.json`): name and pitch, stack, README
sections and feature bullets, screens/routes/CLI commands, brand colours (named variables
first, then most-used hex), fonts, and visual assets. It skips secrets (see §7).
For a URL it fetches the page and reads the title, meta description, social-preview tags,
headings, calls to action, CSS colour variables, loaded fonts and image URLs.

## 3. Read what the scan points at
- **The README**, top to bottom: the pitch, who it's for, the core flow, numbers worth
  showing (speed, limits, prices, users), what the authors are proud of.
- **The main UI**: the 2-5 screens users spend time in (`screens`/`routes`). Read the
  components to learn the real labels, empty states and flows. Mock UI in the video uses
  the product's actual wording.
- **The product in use**: beyond the marketing page, find the 2-3 beats of *using* it:
  **entry → key action → result** (upload → processing → 3 clips ready; type a message →
  the assistant answers → "mark resolved"). Look at routes, feature components, stores and
  step components, "how it works"/usage sections, and example or demo folders. This is
  usually the strongest material a video has.
- **Brand**: `tailwind.config.*`, CSS custom properties (`:root { --primary ... }`),
  theme files, Google Fonts `<link>`s and `@import`s, logo SVGs. Note the background,
  text, primary/accent colours (exact values), any gradient, the display and body fonts,
  corner radius, and whether it's a light or dark product.
- **Existing media**: screenshots, a site, a previous video, docs images.
- **Build-only repos**: if a repo ships only a production build, check for `*.js.map`
  source maps. Their `sourcesContent` holds the original components (labels, routes, API
  calls) and is worth recovering into the scratchpad.

## 4. Websites
Many sites render with JavaScript, so a plain fetch can come back as an empty shell. If
`discover.py <url>` finds little, load the page in a browser (the browser tools, or
headless Chrome). Dismiss cookie banners and overlays, and scroll section by section,
because content that animates in on scroll stays blank in a single full-page capture.
- **Copy**: headline, tagline, section headings, feature names, CTAs, testimonials, plus
  the title, meta description and og:/twitter: tags.
- **Identity**: exact colours from the site's CSS and the fonts it loads.
- **Visuals**: the logo, product screenshots, hero images, demo videos. Download the ones
  you'll use into the video's `public/`.
- **Screenshots**: capture at the video's aspect ratio to understand the layout. In the
  video, rebuild or reuse the real markup/CSS/assets and animate those rather than panning
  over flat screenshots.

## 5. Answer the planning rubric (write it into the product brief)
1. **What is it?** One plain sentence.
2. **Who is it for, and what does it do for them?** What sets it apart?
3. **The most impressive (or funniest) claim.** The one line that earns a reaction.
4. **The visual hook.** The strongest visual: a palette moment, a UI element, a diagram.
5. **The flow worth showing.** Entry → key action → result, or "none (landing page only)".
6. **What real UI/copy must appear** on screen.
7. **The tone that fits** (tones.md): a preset plus a short freeform direction.
8. **The sound** it wants: music bed, SFX posture, voiceover, silence (sound.md).
9. **The share caption**: one sentence (becomes `out/share-copy.txt`).

## 6. Write the product brief (show it to the user)
Keep it to a screen; it anchors every later question.
```
Product: <name> - <one-line pitch in plain words>
For: <audience>, who get <benefit>
Flow worth showing: <entry → key action → result>
Features (ranked by how visual/impressive they are): 1. ... 2. ... 3. ...
Proof points: <numbers, limits, privacy, speed, pricing>, true and sourced
Brand: bg <light/dark #...>, text <#...>, primary <#...>, accent <#...>, fonts <display/body>, radius <...>, logo <path>
Visual assets available: <screenshots, logo, none>
Suggested tone: <preset> - <direction>
Draft caption: <one sentence>
Gaps: <what I couldn't find and need from you>
```
Then run the brief questions (`references/brief.md`) with this as context: the focus
question lists the features you found, not generic ones.

## 7. Privacy and secrets while discovering
Anything read here can end up on screen in a video the user posts publicly.
- **Don't read**: `.env`/`.env.*`, `*.pem`/`*.key`/`id_rsa*`, service-account or
  credential JSON, anything under `secrets/` or `credentials/`, local config that holds
  tokens, build output, lock files, tests, `.git/`.
- **Never carry into the brief, the video or the caption**: secrets, API keys, tokens,
  internal hostnames or URLs, real customer or user names, emails, or other personal data.
  Real products often show them by default. Plan mock UI or synthetic data from the start,
  and say in the brief where you substituted fiction (`references/assets-and-honesty.md`).
