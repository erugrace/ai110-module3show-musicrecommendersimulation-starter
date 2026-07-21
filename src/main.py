"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

# Works whether you run `python -m src.main` (package) or `python main.py` (from src/).
try:
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from recommender import load_songs, recommend_songs


def print_recommendations(user_prefs: dict, recommendations: list) -> None:
    """Render the ranked recommendations as a clean terminal report."""
    width = 60
    profile = " | ".join(f"{key}={value}" for key, value in user_prefs.items())

    print("=" * width)
    print("  MUSIC RECOMMENDER".ljust(width))
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


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(user_prefs, recommendations)


if __name__ == "__main__":
    main()
