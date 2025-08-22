
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List
import re

# Very small lexicon-based signals (no external deps)

POSITIVE = {
    "love", "like", "enjoy", "great", "awesome", "good", "happy", "glad",
    "thanks", "thank you", "appreciate", "cool", "nice", "beautiful", "amazing",
}
NEGATIVE = {
    "hate", "annoy", "angry", "mad", "upset", "bad", "sad", "terrible", "awful",
    "disgusting", "gross", "nasty", "horrible", "fear", "afraid", "scared",
    "worried", "anxious", "anxiety", "cry", "lonely", "tired",
}
INSULT = {
    "idiot", "stupid", "dumb", "moron", "useless", "trash",
}

JOY_TRIG = {"congrats", "congratulations", "yay", "party", "fun", "joke", "lol", "lmao"}
SAD_TRIG = {"loss", "lost", "broke", "breakup", "alone", "cry", "depressed"}
ANGER_TRIG = {"angry", "rage", "furious", "incompetent", "why you", "you never", "you always"}
FEAR_TRIG = {"scared", "fear", "worried", "panic", "danger", "unsafe"}
SURPRISE_TRIG = {"wow", "what?!", "no way", "unbelievable"}
DISGUST_TRIG = {"disgust", "gross", "eww", "nasty"}
AFFECTION_TRIG = {"love", "dear", "sweet", "hug", "kiss", "friend"}
CURIOUS_TRIG = {"why", "how", "what if", "tell me more", "explain", "?", "curious"}

INTENSIFIERS = {"very", "so", "extremely", "super", "really"}
NEGATORS = {"not", "never", "no", "n't"}

WORD_RE = re.compile(r"[\w']+")

@dataclass
class Appraisal:
    sentiment: float  # -1..1
    intensity: float  # 0..1
    discrete_hint: str | None

def _contains_any(text: str, vocab: set[str]) -> bool:
    t = text.lower()
    return any(w in t for w in vocab)

def _sentiment_score(tokens: List[str]) -> float:
    score = 0
    for w in tokens:
        lw = w.lower()
        if lw in POSITIVE: score += 1
        if lw in NEGATIVE: score -= 1
        if lw in INSULT:   score -= 1.5
    return 0 if len(tokens)==0 else max(-1.0, min(1.0, score / max(6, len(tokens))))

def _intensity_score(tokens: List[str], text: str) -> float:
    # heuristic: many !, ALL CAPS words, intensifiers
    exclam = text.count("!")
    caps = sum(1 for w in tokens if len(w) >= 2 and w.isupper())
    boost = 0.0
    boost += min(1.0, exclam * 0.15)
    boost += min(1.0, caps * 0.1)
    boost += min(1.0, sum(1 for w in tokens if w.lower() in INTENSIFIERS) * 0.12)
    return max(0.0, min(1.0, 0.2 + boost))

def _discrete_hint(text: str) -> str | None:
    t = text.lower()
    # Priority order: explicit triggers first
    if _contains_any(t, ANGER_TRIG) or _contains_any(t, INSULT): return "anger"
    if _contains_any(t, SAD_TRIG): return "sadness"
    if _contains_any(t, FEAR_TRIG): return "fear"
    if _contains_any(t, DISGUST_TRIG): return "disgust"
    if _contains_any(t, SURPRISE_TRIG): return "surprise"
    if _contains_any(t, JOY_TRIG): return "joy"
    if _contains_any(t, AFFECTION_TRIG): return "affection"
    if _contains_any(t, CURIOUS_TRIG): return "curiosity"
    return None

def appraise(user_text: str) -> Appraisal:
    tokens = WORD_RE.findall(user_text)
    sent = _sentiment_score(tokens)
    intensity = _intensity_score(tokens, user_text)
    hint = _discrete_hint(user_text)
    # Negation handling (simple): flip sentiment if negation near positive/negative words
    if any(n in user_text.lower() for n in NEGATORS) and abs(sent) > 0:
        sent *= -0.5  # partial flip
    return Appraisal(sentiment=sent, intensity=intensity, discrete_hint=hint)
