# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0** — it matches songs to the "vibe" a listener asks for.

---

## 2. Intended Use  

**Goal / task.** VibeMatch takes a short taste profile (a favorite genre, a mood,
and how much energy you want) and suggests the top 5 songs that fit it. For every
pick, it also prints a plain-English reason so you can see *why* it was chosen.

**Who it's for.** This is a classroom learning project. It is meant to show how a
simple recommender turns preferences into ranked results — not to power a real
music app.

**What it should NOT be used for.** Do not use it for real listeners or real
product decisions. It only knows 18 songs, has no idea what is actually popular,
and never learns from what you play or skip. It should not be treated as a fair
or complete picture of anyone's music taste.

---

## 3. How the Model Works  

Think of it like a scorecard. Every song starts at zero points. Then the system
checks it against what you asked for and adds points:

- **Genre** — if the song's genre is the one you like, it earns some points.
- **Mood** — if the song's mood matches your mood, it earns a few more points
  (mood is worth a little more than genre).
- **Energy** — you pick how energetic you want music to be, from calm to intense.
  The closer a song's energy is to your target, the more points it gets.
- **Acoustic bonus** — if you say you like acoustic music, softer/acoustic songs
  get a small boost.

The system adds up the points for every song, sorts them from highest to lowest,
and shows you the top 5. That's it — no hidden AI, just a transparent scorecard.

---

## 4. Data  

- **Size:** a tiny catalog of **18 songs**.
- **Features per song:** title, artist, genre, mood, energy, tempo, valence,
  danceability, and acousticness. The scorecard mainly uses **genre, mood, and
  energy** (plus acoustic feel), and ignores the rest for now.
- **Variety:** **15 different genres** and many moods (happy, chill, intense,
  melancholic, and more).
- **Limits:** the catalog is very small and unbalanced. Most genres show up only
  once, and the songs are either quite calm or quite energetic with very little
  in the middle. It also has no lyrics, no language info, and no popularity data.

---

## 5. Strengths  

- **Clear favorites work great.** If someone wants calm, acoustic lofi, the top
  picks are exactly that — the results match plain intuition.
- **Every pick is explained.** You always see the reasons ("matches a genre you
  like", "energy is close to what you want"), so nothing feels like a black box.
- **It respects the energy dial.** Turn energy up and loud songs rise; turn it
  down and quiet songs rise. Opposite tastes get clearly different lists.
- **It's consistent.** The same profile always gives the same result, which makes
  it easy to test and easy to trust.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

**The "energy gap" blind spot (discovered during testing).** The catalog's
energy values are bimodal, not evenly spread: of the 18 songs, 8 cluster at low
energy (0.24–0.42) and 8 at high energy (0.75–0.95), leaving only two tracks
(0.54 and 0.58) in the middle and an outright gap between 0.58 and 0.75 where no
song exists. Because energy is scored as pure closeness (`1 − |target − value|`),
a listener who wants high or low energy can always find a near-perfect match
(closeness ≈ 0.99), while a listener who wants moderate energy (~0.65) has no song
near their target and can never earn a strong energy score. The system therefore
serves "hyped" and "chill" users well but quietly ignores anyone in between — a
filter bubble created by the dataset, not the user's taste. This is compounded by
genre sparsity: 13 of the 15 genres appear only once, so a fan of jazz, metal,
reggae, or country gets exactly one on-genre song and four energy-driven
strangers, whereas lofi (3 songs) and pop (2) fans get a genre-coherent list.

Other prompts to consider:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

**Profiles I tested.** Three everyday listeners — **High-Energy Pop**
(happy, upbeat), **Chill Lofi** (calm, acoustic), and **Deep Intense Rock**
(loud, hard-hitting) — plus a few "trick" profiles meant to confuse the system
(like asking for a *sad* mood but *high* energy at the same time).

**What surprised me.** The system gives a song points for three separate things
— genre, mood, and energy — and adds them up. A song can win by matching just two
of the three, even if it clearly misses the "vibe" the user asked for. In one
trick test, the *calmest* song in the whole list came out #1 for someone who
asked for high-energy music, simply because it matched their mood.

**Why "Gym Hero" keeps showing up for a "Happy Pop" fan.** *Gym Hero* is a pop
song with very high energy — but its mood is *intense*, not *happy*. The Happy
Pop listener still gives it points for being pop and for being high-energy (two
boxes ticked out of three), so it lands near the top even though it's really a
workout track, not a feel-good one. The system rewards "close enough on genre and
energy" and only quietly misses on mood.

### Comparing the profiles two at a time

- **Happy Pop vs. Chill Lofi:** These are near opposites and their lists barely
  overlap. Pop pulls bright, high-energy songs to the top (*Sunrise City*); Lofi
  pulls quiet, acoustic songs (*Library Rain*). This makes sense — one wants the
  energy dial turned up, the other turned down.

- **Happy Pop vs. Deep Intense Rock:** Both want *high* energy, so they actually
  **share** songs — *Gym Hero* and *Storm Runner* appear on both lists. The
  difference is who wins the top spot: Pop puts the *happy* song first, Rock puts
  the *intense* song first. Same energy level, but mood breaks the tie.

- **Chill Lofi vs. Deep Intense Rock:** Complete opposites — soft and acoustic
  vs. loud and aggressive — so their top 5 lists have nothing in common. This is
  the clearest sign the energy setting is doing its job.

I also kept the automated tests passing (`2 passed`) as a math check, and tried
turning the mood rule off entirely; that mostly *changed* the results rather than
*improving* them, which told me mood and genre often agree in this small catalog.

---

## 8. Future Work  

If I kept building this, I would:

1. **Add more songs, more evenly spread.** A bigger catalog with some
   medium-energy songs would fix the "energy gap" that leaves moderate listeners
   with no good match.
2. **Make matching smarter, not exact.** Right now "Pop" and "pop" don't match,
   and pop fans get no credit for indie pop. I'd clean up the text and treat
   similar genres as close cousins.
3. **Reward mood and energy together.** I'd stop a "sad" song from winning when
   someone asked for high energy, so the results feel more like a real vibe.

---

## 9. Personal Reflection  

**Biggest learning moment.** Seeing that a recommender is really just simple math
adding up points — no magic. Once I could read the score breakdown, I understood
exactly why each song was picked.

**How AI tools helped, and when I double-checked.** AI tools helped me design
tricky test profiles, explain the scoring math, and write these sections faster.

**What surprised me.** Even with no real "intelligence," the picks *felt* like
recommendations. Adding up a few points and showing a plain reason was enough to
make it seem thoughtful — until a workout song kept showing up for a "happy pop"
fan and reminded me how easily simple rules can miss the vibe.

**What I'd try next.** A bigger, more balanced song list, smarter genre matching
(so "pop" and "indie pop" count as close), and a way to blend mood and energy so
the results feel more like a true vibe.
