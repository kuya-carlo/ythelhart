"""
This module manages the local leaderboard, including loading and saving high scores.
"""

import json
from pathlib import Path

LEADERBOARD_FILE = Path("leaderboard.json")
MAX_SCORES = 10


def load_scores() -> list[dict]:
    """
    Loads the high scores from the leaderboard file.

    Returns
    -------
    list[dict]
        A list of score dictionaries, e.g., [{"name": "Kaoru", "wave": 10}].
    """
    if not LEADERBOARD_FILE.exists() or LEADERBOARD_FILE.stat().st_size == 0:
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            scores = json.load(f)

        # Backward compatibility: convert old format (list of ints) to new format (list of dicts)
        if scores and isinstance(scores[0], int):
            scores = [{"name": "Anonymous", "wave": score} for score in scores]

        # Sort scores by wave in descending order
        scores.sort(key=lambda s: s.get("wave", 0), reverse=True)
        return scores
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_score(name: str, wave: int):
    """
    Saves a new score to the leaderboard.

    Parameters
    ----------
    name : str
        The player's name.
    wave : int
        The wave number to save.
    """
    scores = load_scores()
    scores.append({"name": name, "wave": wave})
    # Sort scores and keep only the top MAX_SCORES
    scores.sort(key=lambda s: s.get("wave", 0), reverse=True)
    updated_scores = scores[:MAX_SCORES]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(updated_scores, f, indent=4)
