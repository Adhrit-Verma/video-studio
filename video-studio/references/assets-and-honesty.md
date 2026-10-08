# Assets, privacy and honesty

## What goes on screen
0. **The product's real components and styles (when you can).** If the product is
   React (or plain HTML/CSS) and a component renders without its backend, copy it into
   the video project and render it in the scene with the product's own stylesheet, fonts
   and images, feeding it invented props instead of API data. Reuse beats re-creation:
   it looks exactly right. Strip network calls, auth and analytics first, and leave
   anything that needs a server to option 1.
1. **Native mock UI.** Rebuild the product's key panels as React components styled from
   the theme (and the product's real labels from discovery): sharp at any zoom,
   animatable text. The template's `MockWindow` is the pattern.
2. **Real screenshots on invented data.** If the product runs, point it at a throwaway
   data folder, load made-up records (fictional names, companies, documents), and
   screenshot its real UI. Keep a small script that rebuilds the fake dataset so shots
   can be retaken.
3. **Fictional backdrop pages** (a browser page, a document, a dashboard): write small
   HTML pages and render them to PNG with a headless browser, one page per process
   (batching several page loads in one Electron process failed on the second load), or
   render them as Remotion components directly.
4. **User-supplied media** (photos, logos, footage): use as given; ask before
   generating substitutes.
5. **Generated imagery** (AI images/video) only if the user wants it, and never to
   depict real people or the product doing things it can't.

## Privacy and secrets
- Never put a user's real data on screen: captures, emails, names, files, messages,
  faces. Real products often show them by default; build fake datasets instead, and say
  in the brief where you substituted fiction.
- Never put secrets on screen or in the caption: API keys, tokens, `.env` values,
  internal hostnames or URLs, private repo paths. Discovery doesn't read secret files
  (discovery.md §7); check mock UI and code snippets for them anyway.
- Check whether the destination (repo, account) is public before adding media.
- Keep the video project out of the product's git history unless asked
  (`.git/info/exclude` hides it locally without committing an ignore rule).

## Honesty
- Only show features that exist. An illustration (a calendar graphic for a date) is
  fine; UI that looks like a feature is a promise.
- Numbers on screen are true or clearly illustrative; testimonials are real and attributed.
- Don't imitate another company's brand, logo or UI; "feels like X" is a mood, not a copy.

## Rights
- Music: the user supplies tracks they have rights to; never download commercial
  music; `gen_beat.py` makes original music.
- Sound effects: the bundled library is CC0 (Kenney; keyboard by unicae_games).
- Images found in a product repo may be stock with their own licence: ask before using
  them in something the user will post.
- Fonts: Google Fonts are free to use; commercial fonts need the user's licence.
- Remotion: free for individuals and companies of up to 3 people; larger companies need
  a company licence (mention it when it applies).
