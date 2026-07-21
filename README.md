# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify and YouTube predict what you'll enjoy next by combining two ideas: **collaborative filtering** ("people with taste like yours also liked this," learned from likes, skips, and watch time across millions of users) and **content-based filtering** ("this is similar to things you already liked," learned from the item's own attributes like tempo, mood, and genre). They retrieve a broad set of candidates cheaply, rank them precisely, learn from implicit feedback (did you keep listening past ~30 seconds, or skip?), and deliberately mix in some exploration so recommendations don't collapse into a rut. This simulation deliberately keeps only the **content-based** half — it has no crowd behavior to learn from — and prioritizes a simple, *explainable* scoring rule: match the user's stated taste (mood, genre) and find songs whose numeric feel (energy) is *closest* to what they want, then rank by that score and return the top `k`. Every recommendation comes with a plain-language "Because:" reason so the logic is transparent.

**Features the `Song` object uses in scoring:**

- `genre` — categorical; exact-match bonus (weight 0.20)
- `mood` — categorical; exact-match bonus (weight 0.30, weighted higher than genre because mood tracks *why* someone is listening)
- `energy` — numeric 0–1; scored by *closeness* to the user's target (`1 - |target - value|`)
- `acousticness` — numeric 0–1; bonus when the user prefers acoustic tracks
- `tempo_bpm` — numeric; normalized to 0–1 with fixed bounds (40–200 BPM), scored only when a tempo target is given

*(The `Song` also carries `id`, `title`, `artist`, `valence`, and `danceability`; these are stored but not currently used in the score — `valence` has too narrow a spread to help, and there's no danceability/artist preference in the profile yet.)*

**Information the `UserProfile` stores:**

- `favorite_genre` — the genre to reward
- `favorite_mood` — the mood to reward
- `target_energy` — the desired energy level (0–1) to match closeness against
- `likes_acoustic` — boolean flag that turns the acoustic bonus on or off

**How a score is computed:** `score_song()` measures one song against the profile — match bonuses for the categoricals (genre, mood) plus a closeness reward for the numeric features (energy, optional tempo) — and returns a score with human-readable reasons.

**How songs are chosen:** `recommend_songs()` scores every song, sorts by score (highest first), and returns the top `k` — the same score-then-rank split real platforms use.

### The Algorithm Recipe

The data flows in three stages — **Input → Process (judge each song) → Output (rank)**:

```
User Prefs ─┐
            ├─► score_song(prefs, song)  ─► (score, reasons)   [repeat for every song]
songs.csv ──┘                                     │
                                                  ▼
                              sort by score, desc ─► take top k ─► ranked recommendations
```

Each song is judged **independently** against the user (the loop), then all the scores are **ranked** together (the sort). Those two responsibilities stay separate.

**Scoring rule:** start every song at `0.0`, then *add* points for each way it matches the profile and *subtract* points for each clash. Two kinds of signal are scored differently:

- **Categorical** (`genre`, `mood`) — exact match earns a flat bonus; no partial credit.
- **Numeric** (`energy`, `tempo_bpm`) — scored by *closeness*, `weight × (1 - |target - value|)`, so a near-miss still earns partial points.

**Point budget (finalized weights):**

| Signal | Points | Type |
|--------|-------:|------|
| Mood match | +0.30 | flat bonus |
| Energy closeness | up to +0.30 | scaled |
| Genre match | +0.20 | flat bonus |
| Acoustic bonus (`likes_acoustic` + acousticness ≥ 0.5) | +0.20 | flat bonus |
| Tempo closeness (only if a tempo target is given) | up to +0.30 | scaled |
| Disliked-genre penalty | −0.30 | flat penalty |

Mood is weighted **above** genre (0.30 vs 0.20) on purpose: genre labels are fuzzy and overlapping (`pop`, `indie pop`, `synthwave`, `EDM` all describe similar music), while mood tracks *why* someone is listening (focus, workout, chill) — a cleaner, more reliable signal.

### Biases to expect

This scoring design bakes in some predictable blind spots:

- **The always-on numeric signals can quietly outweigh the categorical ones.** `energy` contributes to *every* song via closeness, while genre/mood bonuses only fire on an exact match — so across a full ranking, energy often moves the results more than intended, potentially burying a perfect mood-match that happens to sit at the wrong energy.
- **Genre is exact-match only, so it ignores near-neighbors.** A user who likes `pop` gets no credit for a great `indie pop` or `synthwave` track, even though they'd likely enjoy it. The system rewards the label, not the actual sound.
- **Popularity/diversity blind spot.** With no crowd data and no exploration step, the recommender always returns the same deterministic top-`k` for a given profile — it can trap a user in a narrow "taste rut" and never surprises them with something outside their stated preferences.
- **Cold-start and coverage.** A profile with only a `favorite_genre` and no energy target leans almost entirely on one flat bonus, making rankings coarse; and features that are stored but unscored (`valence`, `danceability`, `artist`) mean songs that match on *those* dimensions get no recognition at all.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Running `python -m src.main` with the profile `genre=pop, mood=happy, energy=0.8` produces:

```
============================================================
  MUSIC RECOMMENDER
============================================================
Profile: genre=pop | mood=happy | energy=0.8

Top 5 recommendations:

1. Sunrise City - Neon Echo                     score 0.79
      * matches a genre you like (pop) (+0.20)
      * fits a mood you like (happy) (+0.30)
      * energy level is close to what you want (+0.29)

2. Rooftop Lights - Indigo Parade               score 0.59
      * fits a mood you like (happy) (+0.30)
      * energy level is close to what you want (+0.29)

3. Gym Hero - Max Pulse                         score 0.46
      * matches a genre you like (pop) (+0.20)
      * energy level is close to what you want (+0.26)

4. Concrete Anthem - Rhyme Foundry              score 0.29
      * energy level is close to what you want (+0.29)

5. Night Drive Loop - Neon Echo                 score 0.28
      * energy level is close to what you want (+0.28)
```

Each recommendation shows the song title and artist, the final score, and the specific reasons (with the points each signal contributed) so the ranking is fully transparent.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



