import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# --- Scoring configuration -------------------------------------------------
# Fixed musical tempo bounds (Option B): stable regardless of which songs are
# loaded, so a new/out-of-range track never rescales everyone else.
MIN_BPM, MAX_BPM = 40.0, 200.0

# Default feature weights (kept simple and interpretable). A profile can
# override any of these per-user via a "weights" dict.
# Mood is weighted higher than genre: it tracks *why* a user is listening
# (focus, workout, chill) better than fuzzy, overlapping genre labels.
GENRE_MATCH_BONUS = 0.20
MOOD_MATCH_BONUS = 0.30
ENERGY_WEIGHT = 0.30
ACOUSTIC_BONUS = 0.20
DANCEABILITY_WEIGHT = 0.15
ACOUSTICNESS_WEIGHT = 0.15
DISLIKE_PENALTY = 0.30

# CSV columns that must be parsed as numbers when loading songs.
_FLOAT_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")


def normalize_tempo(bpm: float) -> float:
    """Min-max scale a BPM value into [0, 1] using fixed bounds (Option B).

    Clamped so out-of-range songs still land inside [0, 1].
    """
    norm = (bpm - MIN_BPM) / (MAX_BPM - MIN_BPM)
    return max(0.0, min(1.0, norm))

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _prefs(self, user: UserProfile) -> Dict:
        """Translate a UserProfile into the dict shape score_song expects."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by their score against the user's profile."""
        prefs = self._prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda s: score_song(prefs, asdict(s))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable, "; "-joined explanation of why a song was recommended."""
        _, reasons = score_song(self._prefs(user), asdict(song))
        return "; ".join(reasons) if reasons else "No strong matches, but worth a listen."

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file, parsing numeric columns as numbers.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for field in _FLOAT_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against a taste profile (content-based).

    The profile is a dict. Every key is optional, so both the minimal shape
    ({"genre", "mood", "energy"}) and the richer shape below work:
      - "genre" (single) and/or "genres" (list)  -> match bonus
      - "mood"  (single) and/or "moods"  (list)  -> match bonus
      - "disliked_genres" (list)                 -> penalty
      - "energy"/"target_energy", "target_danceability",
        "target_acousticness"                    -> closeness reward
      - "likes_acoustic" (bool)                  -> acoustic bonus
      - "tempo_bpm"                              -> tempo closeness
      - "weights" (dict)                         -> per-user weight overrides
    Returns (score, reasons).
    """
    score = 0.0
    reasons: List[str] = []
    weights = user_prefs.get("weights", {})

    def weight(key: str, default: float) -> float:
        return weights.get(key, default)

    # --- Genre: match against a set of liked genres (single or list) ---
    liked_genres = set(user_prefs.get("genres", []))
    if user_prefs.get("genre"):
        liked_genres.add(user_prefs["genre"])
    if song["genre"] in liked_genres:
        awarded = weight("genre", GENRE_MATCH_BONUS)
        score += awarded
        reasons.append(f"matches a genre you like ({song['genre']}) (+{awarded:.2f})")

    # --- Disliked genres: negative signal ---
    if song["genre"] in set(user_prefs.get("disliked_genres", [])):
        awarded = weight("dislike", DISLIKE_PENALTY)
        score -= awarded
        reasons.append(f"{song['genre']} is a genre you dislike (-{awarded:.2f})")

    # --- Mood: match against a set of liked moods (single or list) ---
    # mood is a category, so we compare labels rather than using distance math.
    liked_moods = set(user_prefs.get("moods", []))
    if user_prefs.get("mood"):
        liked_moods.add(user_prefs["mood"])
    if song["mood"] in liked_moods:
        awarded = weight("mood", MOOD_MATCH_BONUS)
        score += awarded
        reasons.append(f"fits a mood you like ({song['mood']}) (+{awarded:.2f})")

    # --- Energy: reward closeness to the target (both already 0-1) ---
    # accepts "target_energy" (richer profile) or "energy" (minimal profile).
    energy_target = user_prefs.get("target_energy", user_prefs.get("energy"))
    if energy_target is not None:
        closeness = 1.0 - abs(energy_target - song["energy"])
        awarded = weight("energy", ENERGY_WEIGHT) * closeness
        score += awarded
        if closeness >= 0.85:
            reasons.append(f"energy level is close to what you want (+{awarded:.2f})")

    # --- Danceability: closeness to target ---
    if user_prefs.get("target_danceability") is not None:
        closeness = 1.0 - abs(user_prefs["target_danceability"] - song["danceability"])
        awarded = weight("danceability", DANCEABILITY_WEIGHT) * closeness
        score += awarded
        if closeness >= 0.85:
            reasons.append(f"danceability matches your taste (+{awarded:.2f})")

    # --- Acousticness: closeness to target ---
    if user_prefs.get("target_acousticness") is not None:
        closeness = 1.0 - abs(user_prefs["target_acousticness"] - song["acousticness"])
        awarded = weight("acousticness", ACOUSTICNESS_WEIGHT) * closeness
        score += awarded
        if closeness >= 0.85:
            reasons.append(f"acoustic level matches your taste (+{awarded:.2f})")

    # --- Acoustic preference (simple boolean flag) ---
    if user_prefs.get("likes_acoustic") and song["acousticness"] >= 0.5:
        awarded = weight("acoustic_bonus", ACOUSTIC_BONUS)
        score += awarded
        reasons.append(f"acoustic sound you enjoy (+{awarded:.2f})")

    # --- Tempo: only scored when the profile names a target tempo ---
    # Normalized with fixed bounds (Option B) so it shares the 0-1 scale.
    if user_prefs.get("tempo_bpm") is not None:
        target = normalize_tempo(user_prefs["tempo_bpm"])
        actual = normalize_tempo(song["tempo_bpm"])
        awarded = weight("tempo", ENERGY_WEIGHT) * (1.0 - abs(target - actual))
        score += awarded
        reasons.append(f"tempo is close to what you want (+{awarded:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "a general match for your taste"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]

def build_profile_from_history(liked_songs: List[Dict]) -> Dict:
    """
    Derive a taste profile from songs the user liked/played, instead of
    typing it in by hand. This is content-based filtering building the
    profile automatically: average the numeric features and collect the
    genres/moods that appear.
    """
    if not liked_songs:
        return {}

    n = len(liked_songs)
    return {
        "genres": sorted({s["genre"] for s in liked_songs}),
        "moods": sorted({s["mood"] for s in liked_songs}),
        "target_energy": sum(s["energy"] for s in liked_songs) / n,
        "target_danceability": sum(s["danceability"] for s in liked_songs) / n,
        "target_acousticness": sum(s["acousticness"] for s in liked_songs) / n,
    }
