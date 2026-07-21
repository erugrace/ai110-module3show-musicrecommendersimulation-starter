"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys

# Works whether you run `python -m src.main` (package) or `python main.py` (from src/).
try:
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from recommender import load_songs, recommend_songs


# A few distinct taste profiles to demo how the recommender responds to
# different users. Each is a plain dict that score_song() understands.
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
}

# --- Adversarial / edge-case profiles ------------------------------------
# Each one is built to stress a specific seam in score_song(). Run them and
# read the top 5 + explanations to see whether the logic behaves as intended
# or produces something surprising.
ADVERSARIAL_PROFILES = {
    # 1. CONFLICTING SIGNALS: a low-energy mood label paired with a high energy
    #    target. mood and energy are scored independently and never reconciled,
    #    so watch whether a "sad" song or a "hype" song ends up on top.
    "Conflicted: Sad but Hyped": {"mood": "melancholic", "energy": 0.9},

    # 2. GHOST PREFERENCE: "sad" is not a mood that exists in the dataset, so the
    #    mood term silently contributes nothing. Ranking quietly collapses onto
    #    genre + energy. Reveals no warning on an unknown category (e.g. a typo).
    "Ghost Preference (unknown mood)": {"genre": "pop", "mood": "sad", "energy": 0.5},

    # 3. CASE TRAP: the intent clearly matches, but matching is case-sensitive
    #    string equality, so "Pop"/"Happy" never match the lowercase data.
    #    The genre and mood bonuses silently never fire.
    "Case Trap": {"genre": "Pop", "mood": "Happy", "energy": 0.8},

    # 4. SELF-CONTRADICTION: the same genre is both liked and disliked. Both the
    #    +genre bonus and the -dislike penalty fire, netting a contradictory
    #    explanation ("matches a genre you like" AND "is a genre you dislike").
    "Self-Contradiction": {"genres": ["rock"], "disliked_genres": ["rock"], "energy": 0.5},

    # 5. OUT-OF-RANGE + WEIGHT ABUSE: energy target is outside [0,1] and the
    #    per-user weight is inflated. No validation clamps either, so scores go
    #    negative and the ranking is driven by an unintended side effect.
    "Weight Hacker (out of range)": {"energy": 5.0, "weights": {"energy": 2.0}},

    # 6. BLANK SLATE: no signal at all. Every song scores 0.0, so the sort is a
    #    tie and you just get the first 5 songs in file order — a silent, non-
    #    obvious fallback. Reveals what "no information" degrades to.
    "Blank Slate": {},
}


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Render one profile's ranked recommendations as a clean terminal report."""
    width = 60
    profile = " | ".join(f"{key}={value}" for key, value in user_prefs.items())

    print("=" * width)
    print(f"  {name.upper()}".ljust(width))
    print("=" * width)
    print(f"Profile: {profile}")
    print(f"\nTop {len(recommendations)} recommendations:\n")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        header = f"{rank}. {song['title']} - {song['artist']}"
        print(f"{header:<48}score {score:.2f}")
        # explanation is a "; "-joined list of reasons; show each on its own line.
        for reason in explanation.split("; "):
            print(f"      * {reason}")
        print()


def run_profiles(profiles: dict, songs: list) -> None:
    """Run the recommender for each profile and print its top 5."""
    for name, user_prefs in profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Pick which set to run:
    #   python -m src.main               -> the normal demo profiles
    #   python -m src.main adversarial   -> only the edge-case profiles
    #   python -m src.main all           -> both sets
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "demo"

    if mode == "adversarial":
        run_profiles(ADVERSARIAL_PROFILES, songs)
    elif mode == "all":
        run_profiles(PROFILES, songs)
        run_profiles(ADVERSARIAL_PROFILES, songs)
    else:
        run_profiles(PROFILES, songs)


if __name__ == "__main__":
    main()
