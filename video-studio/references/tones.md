# Tones: how the video talks, paces and cuts

A **style** (styles.md) is how the video looks; a **tone** is how it talks. Tone sets the
copy voice, scene count and length, transitions, SFX density, the motion preset default
and the share caption. Pick one preset in the brief. Freeform direction ("fake Series A
launch from 2016", "museum exhibit", "overproduced mobile game ad") maps to the nearest
preset for pacing, but keep the user's words in `brief/brief.md` and follow them for copy.
Presets are defaults, not limits. (Adapted from latent-spaces/brag, MIT.)

| Tone | Energy | Scenes (in ~20 s) | Transitions | Motion preset | SFX density |
|---|---|---|---|---|---|
| `default` | Playful, clean, postable | 4-5, 3-5 s each | crossfade/dip, clean wipe | `snappy` | moderate: 3-5 cues |
| `polished` | Serious, elegant, restraint | 3-4, 4-6 s, long holds | slow dip/crossfade 0.6-0.8 s | `expo` | minimal: 2-3 soft cues |
| `yc-parody` | Deadpan startup launch, played straight | 4-5, one claim each | hard cut, ≤0.2 s fade | `snappy` | sparse: 2-3 dry cues |
| `chaotic` | FAST, LOUD, ALL CAPS | 6-8, some < 2 s, none > 4 s | hard cut, flash, zoom cut (1.2→1.0) | `back` | dense: on beats, stacked |
| `deadpan` | Calm, dry, nothing is a joke | 3-4, 4-7 s, big empty space | very slow fade 0.8-1 s, long holds | `smooth` | very sparse: 1-2 cues |
| `cinematic` | Trailer-scale, epic claims | 4-5, 3-5 s | dramatic wipe, fade + scale 0.95→1 | `expo`/`smooth` | 2-3 big hits |
| `app-store` | Clean feature cards | 4-6 | slide/wipe 0.35-0.45 s | `snappy` | a light, even layer |

Longer purposes (explainers, demos) keep the tone's voice and transitions and scale the
scene count with the length.

## Voice and copy per tone
**default**: first person plural, warm, direct. Hook: a question or observation that
sets up the reveal ("Dating apps were built for humans. / Obvious mistake."). Highlights:
one short punchy idea per scene. Outro: name, then a light tagline.

**polished**: third person or no voice; the product speaks. Mixed case, light-medium
weight, generous tracking. Hook: one strong image or the name at full scale. One feature
per scene, no lists ("Wing certification / upon completion."). Outro: name, tagline, silence.

**yc-parody**: serious and matter-of-fact, no winking. The absurdity comes from the
product. Sentence case; mono for data points. Hook: the problem stated completely
seriously ("Every day, taxis carry us. / But who carries the taxis?"). Highlights: a
feature or metric stated as fact. Outro: name, tagline, a URL that implies legitimacy.

**chaotic**: SHORT WORDS, CAPS, metric dumps; some words tilted or oversized. Hook:
something that shouldn't exist, at full volume ("TRANSPORTATION WAS TOO CALM."). One word
or number per beat. Outro: the name slams, the tagline hits, cut to black.

**deadpan**: minimal. One observation, then the product. Large type, lots of empty space,
one thought at a time ("I used to fear the sky."). Outro: the name, maybe a tiny tagline,
a long hold. Silence may be the joke, but only when the brief says so.

**cinematic**: short declarative sentences, each landing before the next. ALL CAPS or
heavy mixed case, full-bleed type. Capabilities stated like superpowers. Outro: the name
full-screen, the tagline, a music swell.

**app-store**: feature-benefit, third person, present tense, title case. Feature card
structure: name plus one line of detail. Outro: a CTA ("Available now.").

## Share caption per tone (out/share-copy.txt)
1-3 sentences, postable as-is on X, LinkedIn or Discord, specific to the project. Never
"excited to share".
- **default**: "Made [Name]. It's [what it does, in its own terms]. [Best line from the product.]"
- **polished**: "Introducing [Name]: [clean one-liner from the site]. Built with [stack, if notable]."
- **yc-parody**: "We built [Name] to solve [problem, stated completely seriously]. [Deadpan stat.]"
- **chaotic**: "[ALL CAPS CLAIM]. [Name] is [wildly overstated description]. Link below."
- **deadpan**: "I made [Name]. It [what it does]."
- **cinematic**: "[Name]. [Tagline, verbatim or lightly adapted.]"
- **app-store**: "[Name] is now live. [Feature 1], [Feature 2] and [Feature 3], all in one place."
Put any per-platform variants in `out/share-copy-variants.md`, not in the main file.
