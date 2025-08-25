from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover - fallback when transformers missing
    pipeline = None  # type: ignore


@dataclass
class Appraisal:
    """Results of NLP analysis for a user utterance."""

    sentiment: float  # -1..1 negative..positive
    intensity: float  # 0..1 strength of the signal
    discrete_hint: str | None  # Optional emotion hint


# Map GoEmotions labels to bot's discrete emotion set
_EMO_MAP: Dict[str, str] = {
    # anger-like
    "anger": "anger",
    "annoyance": "anger",
    # sadness-like
    "sadness": "sadness",
    "grief": "sadness",
    "disappointment": "sadness",
    "remorse": "sadness",
    # fear-like
    "fear": "fear",
    "nervousness": "fear",
    # disgust-like
    "disgust": "disgust",
    "disapproval": "disgust",
    # surprise-like
    "surprise": "surprise",
    "realization": "surprise",
    # joy-like
    "joy": "joy",
    "amusement": "joy",
    "admiration": "joy",
    "approval": "joy",
    "excitement": "joy",
    "gratitude": "joy",
    "optimism": "joy",
    "pride": "joy",
    "relief": "joy",
    # curiosity
    "curiosity": "curiosity",
    # affection
    "love": "affection",
    "caring": "affection",
}


@lru_cache()
def _sentiment_analyzer():
    """Lazy-load the sentiment model."""
    if pipeline is None:  # pragma: no cover - dependency missing
        raise RuntimeError("transformers not installed")
    return pipeline("sentiment-analysis")


@lru_cache()
def _emotion_analyzer():
    """Lazy-load the emotion classifier (GoEmotions)."""
    if pipeline is None:  # pragma: no cover - dependency missing
        raise RuntimeError("transformers not installed")
    return pipeline(
        "text-classification",
        model="joeddav/distilbert-base-uncased-go-emotions-student",
    )


def appraise(user_text: str) -> Appraisal:
    """Infer sentiment, intensity and emotion from ``user_text``.

    Uses pretrained Transformer models rather than simple keyword lists.
    """

    if pipeline is None:  # pragma: no cover - fallback when transformers missing
        return Appraisal(sentiment=0.0, intensity=0.0, discrete_hint=None)

    s_res = _sentiment_analyzer()(user_text)[0]
    sentiment = s_res["score"] if "POS" in s_res["label"].upper() else -s_res["score"]
    print(f"Debug: sentiment analysis result: {s_res}")

    e_res = _emotion_analyzer()(user_text)[0]
    discrete_hint = _EMO_MAP.get(e_res["label"])
    print(f"Debug: emotion analysis result: {e_res}")

    intensity = float(max(s_res["score"], e_res["score"]))
    return Appraisal(sentiment=float(sentiment), intensity=intensity, discrete_hint=discrete_hint)
