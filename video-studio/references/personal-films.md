# Personal films: love, apologies, birthdays, anniversaries, friends

Two people matter here. The **sender** (the user) owns the message. The **recipient** (the
person it's for) decides whether it worked. The recipient's taste decides the look, not
ours, and the sender's words decide what it says. A beautifully made film with neither is
a template, and recipients spot templates instantly.

Learned the hard way: an apology film built from the girlfriend's own photos and clips, set to
her favourite song, cut fast with glitch and flash transitions and the song's lyrics written
on screen, got "yeh kya faltu video banaye ho" ("what is this rubbish video you've made").
It had none of his words, nothing only he would know, and a hype mood on an apology.

## 1. The story interview (before any style or build)
Ask with the structured question tool where it fits; leave room for free text. Required:
1. **Occasion and the one feeling:** what should they feel at the end? (laugh, melt,
   forgive, nostalgic, proud)
2. **The recipient's taste:** 1-3 reels or videos they loved (links or screenshots), the
   aesthetic they like (cute and pastel · soft "aesthetic" · filmy/Bollywood · funny/meme ·
   minimal), and what they'd find **cringe**.
3. **3-6 specific memories:** what, when, where, and which photo or clip shows each one.
4. **Inside jokes, nicknames, phrases** they say, and their language mix (Hinglish, Hindi, English…).
5. **The message in the sender's own words:** at least 2-3 sentences, or a voice note.
   Offer to tidy grammar, never to replace their voice. For an apology, also ask, gently,
   what happened in a line or two, so the words can name it.
6. **Music:** their song and what it means to them. Lyrics come from the user; the skill
   never types copyrighted lyrics itself.
7. **Boundaries:** photos or clips that must not be used. Media sent privately ("she
   sent these because she trusts me") is handled with care: nothing she'd feel exposed by.
8. **Where it's watched:** WhatsApp or DMs → 9:16, 30-90 s.

Without items 3 and 5, don't build a message film. Say why, briefly: the specifics are
what make it land. Offer to start with the parts that don't need them (the look, the
shot log) while the user thinks.

## 2. Message structures
- **Apology** (45-90 s, mood: cute → romantic → sincere, `moods.md`):
  1. a moment that's unmistakably "you two" (3-5 s: her laugh, the inside joke);
  2. "I know I hurt you when…": specific, owned, no "if", no "but";
  3. what she means: three specific memories, each with its clip;
  4. what will change: concrete;
  5. an invitation or question, not a demand ("can we talk tonight?"), held on the "us" shot.
  Text in his handwriting or plain lowercase; the song low and instrumental, or silence under
  the words. If the situation is serious, say kindly that a film can open the door but the
  real conversation does the repairing, and keep the film modest.
- **Birthday / "a year of you":** hook (her best laugh) → chapters by month or place with date
  stamps → the funny ones → the tender ones → the wish in the sender's words → candles.
- **Anniversary:** then vs now match cuts → a day counter → the "us" peak → the message.
- **Proposal or confession:** memories building → the question as the last card, held.
- **"Things I love about you":** a numbered list. Each item is one specific trait plus the
  clip that proves it ("4. you narrate your food like a reviewer").
- **Friendship / farewell:** inside jokes and meme timing, group shots, one tender hold at the end.

## 3. What lands, what fails
**Fails:**
- the template feel (the same effect on every cut, clips assigned by rotation);
- effects with no feeling behind them (glitch on romance);
- someone's own selfies shown back to them as filler;
- song lyrics standing in for the message;
- nothing only the sender would know;
- a 3-minute montage with no story;
- overused "aesthetic" defaults (glowing Great Vibes script, rose-gold everything).

**Lands:**
- specificity (details only the two of them share);
- the sender's voice (handwriting, a voice note, their words);
- recognition ("he noticed *that*?");
- humour where they share it;
- flattering choices and restraint;
- a clear, gentle ask at the end.

## 4. Making it feel handmade (effort is the gift)
- **Their handwriting:** ask the sender to write the lines on paper and photograph them in
  good light. Threshold the photo to ink-on-transparent (Pillow: grayscale → levels → alpha)
  and reveal it with a wipe that follows the writing direction. Their real handwriting beats any font.
- **Their voice:** a 20-40 s voice note under the sincere section, with the music ducked
  (`mix_voice.py`). Never TTS for a personal message.
- **Doodles and stickers** (`Doodle`, `StickerText`), drawn on twos (`useStepFrame(2)`).
- **Real dates and places** (`Camcorder` date stamp, polaroid captions).
- **Imperfection on purpose:** slight wobble, tape, paper texture. It reads as made by hand.

## 5. Respect
- Private media stays private: nothing intimate, nothing the person would be embarrassed by,
  and no public posting of someone else's photos without their consent.
- No guilt-tripping or pressure framing ("if you leave me…"). Steer toward honest,
  warm words; the film should give the recipient room, not corner them.
- Don't invent memories or quotes. Placeholders stay visibly placeholders until the sender
  fills them in.
