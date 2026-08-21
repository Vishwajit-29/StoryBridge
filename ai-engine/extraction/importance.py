from __future__ import annotations
from schemas.canonical import StoryEvent, Entity


class ImportanceCalculator:
    """
    Computes composite importance scores according to SRS Section 11:
    Importance = Plot Relevance + Character Relevance + Causal Relevance +
                 Emotional Relevance + Future Dependency / Mystery
    Normalized to 0.0 - 1.0 range.
    """

    DEFAULT_WEIGHTS = {
        "plot": 0.30,
        "causal": 0.25,
        "character": 0.20,
        "emotional": 0.15,
        "mystery": 0.10,
    }

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        # Normalize weights so sum is 1.0
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def score_event(self, event: StoryEvent) -> float:
        raw_score = (
            event.plot_relevance * self.weights.get("plot", 0.3)
            + event.causal_relevance * self.weights.get("causal", 0.25)
            + event.character_relevance * self.weights.get("character", 0.2)
            + event.emotional_relevance * self.weights.get("emotional", 0.15)
            + event.mystery_relevance * self.weights.get("mystery", 0.1)
        )
        # Cap between 0.0 and 1.0
        score = max(0.0, min(1.0, round(raw_score, 3)))
        event.importance_score = score
        # Events with >= 0.75 or explicit plot criticality are marked crucial
        if score >= 0.75 or event.plot_relevance >= 0.85 or event.causal_relevance >= 0.85:
            event.is_crucial = True
        return score
