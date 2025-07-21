import random


def simple_human_review_score(ad_text: str) -> float:
    """
    Simulates a human review score for an ad text.

    Args:
        ad_text (str): The ad content to review.

    Returns:
        float: A score between 0.0 and 1.0 representing review quality.
    """
    # For now, simulate scoring using randomness and ad length as a rough heuristic.
    length_factor = len(ad_text) / 200  # Normalized length component
    randomness = random.uniform(0.4, 1.0)  # Add variability to simulate human subjectivity

    score = min(1.0, length_factor * 0.5 + randomness * 0.5)
    return round(score, 3)
