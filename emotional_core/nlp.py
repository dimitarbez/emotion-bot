from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional
import re


@dataclass
class Appraisal:
    """Results of NLP analysis for a user utterance."""

    sentiment: float  # -1..1 negative..positive
    intensity: float  # 0..1 strength of the signal
    discrete_hint: Optional[str]  # Optional emotion hint


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

# A small, dependency-free appraisal backend for headless integrations and
# repeatable tests.  Transformer appraisal remains available as an explicit
# opt-in and is imported only when it is actually requested.
_DETERMINISTIC_TERMS = {
    "joy": (0.9, ("joy", "joyful", "happy", "thrilled", "delighted", "excited", "wonderful")),
    "sadness": (-0.9, ("sad", "sadness", "grief", "heartbroken", "miserable", "unhappy")),
    "anger": (-0.9, ("angry", "anger", "furious", "rage", "outraged", "frustrated")),
    "fear": (-0.85, ("afraid", "fear", "fearful", "scared", "terrified", "worried")),
    "surprise": (0.2, ("surprised", "surprise", "astonished", "unexpected", "shocked", "whoa")),
    "disgust": (-0.8, ("disgust", "disgusted", "gross", "revolting", "repulsive", "yuck")),
    "curiosity": (0.25, ("curious", "curiosity", "wonder", "why", "how", "investigate")),
    "affection": (0.85, ("affection", "adore", "cherish", "love", "caring", "dear")),
}


def appraise_deterministic(user_text: str) -> Appraisal:
    """Appraise text without models, downloads, network access, or secrets."""
    words = set(re.findall(r"[a-z']+", user_text.lower()))
    best_emotion = None
    best_count = 0
    sentiment = 0.0
    for emotion, (candidate_sentiment, terms) in _DETERMINISTIC_TERMS.items():
        count = len(words.intersection(terms))
        if count > best_count:
            best_emotion = emotion
            best_count = count
            sentiment = candidate_sentiment

    if best_emotion is None:
        return Appraisal(sentiment=0.0, intensity=0.15 if words else 0.0, discrete_hint=None)

    punctuation_boost = min(0.1, user_text.count("!") * 0.025)
    intensity = min(1.0, 0.85 + 0.05 * (best_count - 1) + punctuation_boost)
    return Appraisal(sentiment=sentiment, intensity=intensity, discrete_hint=best_emotion)


def _transformers_pipeline():
    try:
        from transformers import pipeline  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("transformers backend is unavailable") from exc
    return pipeline


@lru_cache()
def _sentiment_analyzer():
    """Lazy-load the sentiment model."""
    return _transformers_pipeline()("sentiment-analysis")


@lru_cache()
def _emotion_analyzer():
    """Lazy-load the emotion classifier (GoEmotions)."""
    return _transformers_pipeline()(
        "text-classification",
        model="joeddav/distilbert-base-uncased-go-emotions-student",
    )


def appraise(user_text: str, backend: str = "deterministic") -> Appraisal:
    """Infer sentiment, intensity and emotion from ``user_text``.

    The deterministic backend is the safe default.  ``transformers`` is an
    explicit opt-in because it may download large models.
    """
    if backend == "deterministic":
        return appraise_deterministic(user_text)
    if backend != "transformers":
        raise ValueError("unsupported appraisal backend: %s" % backend)

    s_res = _sentiment_analyzer()(user_text)[0]
    sentiment = s_res["score"] if "POS" in s_res["label"].upper() else -s_res["score"]
    print(f"Debug: sentiment analysis result: {s_res}")

    e_res = _emotion_analyzer()(user_text)[0]
    discrete_hint = _EMO_MAP.get(e_res["label"])
    print(f"Debug: emotion analysis result: {e_res}")

    intensity = float(max(s_res["score"], e_res["score"]))
    return Appraisal(sentiment=float(sentiment), intensity=intensity, discrete_hint=discrete_hint)
