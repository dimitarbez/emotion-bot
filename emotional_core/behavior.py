
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
import random, re

@dataclass
class Style:
    # Behavior knobs (0..1 unless noted)
    verbosity: float      # scales response length
    directness: float     # low=hedges, high=to-the-point
    warmth: float         # empathy markers, emojis
    playfulness: float    # jokes/exclamations
    formality: float      # 0 casual .. 1 formal
    punctuation: float    # exclamation/question mark tendency
    hesitation: float     # filler words
    emoji_prob: float     # chance to add small emoji

# Emotion -> Style defaults
STYLE_PRESETS: Dict[str, Style] = {
    "neutral":   Style(verbosity=1.0, directness=0.6, warmth=0.5, playfulness=0.2, formality=0.5, punctuation=0.4, hesitation=0.1, emoji_prob=0.1),
    "joy":       Style(verbosity=1.2, directness=0.6, warmth=0.9, playfulness=0.7, formality=0.3, punctuation=0.8, hesitation=0.05, emoji_prob=0.35),
    "sadness":   Style(verbosity=0.9, directness=0.5, warmth=0.7, playfulness=0.0, formality=0.6, punctuation=0.2, hesitation=0.2, emoji_prob=0.1),
    "anger":     Style(verbosity=0.9, directness=0.95, warmth=0.2, playfulness=0.0, formality=0.4, punctuation=0.9, hesitation=0.02, emoji_prob=0.05),
    "fear":      Style(verbosity=1.0, directness=0.5, warmth=0.7, playfulness=0.0, formality=0.7, punctuation=0.6, hesitation=0.25, emoji_prob=0.08),
    "surprise":  Style(verbosity=1.1, directness=0.6, warmth=0.6, playfulness=0.5, formality=0.4, punctuation=1.0, hesitation=0.1, emoji_prob=0.2),
    "disgust":   Style(verbosity=0.8, directness=0.9, warmth=0.1, playfulness=0.0, formality=0.6, punctuation=0.6, hesitation=0.05, emoji_prob=0.02),
    "curiosity": Style(verbosity=1.1, directness=0.55, warmth=0.6, playfulness=0.3, formality=0.5, punctuation=0.6, hesitation=0.1, emoji_prob=0.15),
    "affection": Style(verbosity=1.1, directness=0.55, warmth=0.95, playfulness=0.4, formality=0.3, punctuation=0.6, hesitation=0.08, emoji_prob=0.3),
}

EMOJIS = {
    "joy": ["😊", "😄", "✨", "🎉"],
    "sadness": ["😔", "💙"],
    "anger": ["😠", "💢"],
    "fear": ["😟", "😬"],
    "surprise": ["😲"],
    "disgust": ["🤢"],
    "curiosity": ["🤔"],
    "affection": ["❤️", "🤗"],
    "neutral": ["🙂"],
}

HEDGES = ["I think", "It seems", "Maybe", "It might be that", "From what I can tell"]
FILLERS = ["uh", "hmm", "well"]
POSITIVE_AFFIRM = ["Nice!", "Great.", "Love that.", "Sounds good.", "Good point."]
ANGRY_MARKERS = ["Look", "Frankly", "Honestly"]
SUPPORT_MARKERS = ["I'm here", "I'm listening", "That sounds tough", "I hear you"]

def shape(text: str, emotion: str, arousal: float, base_max_tokens: int, emoji_baseline: float) -> str:
    style = STYLE_PRESETS.get(emotion, STYLE_PRESETS["neutral"])
    # Adjust verbosity by arousal
    max_len = int(base_max_tokens * style.verbosity * (0.8 + 0.4 * arousal))
    # Trim
    tokens = text.split()
    if len(tokens) > max_len:
        tokens = tokens[:max_len]
        text = " ".join(tokens)
        if style.punctuation > 0.5:
            text += "…"
    # Inject hedges/hesitation if needed
    if style.hesitation > 0.15 and random.random() < style.hesitation:
        text = random.choice(FILLERS) + ", " + text
    if style.directness < 0.6 and random.random() < 0.3:
        text = random.choice(HEDGES) + ", " + text
    # Emotion-specific markers
    if emotion == "anger" and random.random() < 0.35:
        text = random.choice(ANGRY_MARKERS) + ", " + text
    if emotion in ("sadness", "fear") and random.random() < 0.3:
        text = random.choice(SUPPORT_MARKERS) + ". " + text
    if emotion == "joy" and random.random() < 0.3:
        text = random.choice(POSITIVE_AFFIRM) + " " + text

    # Punctuation/exclamation
    if style.punctuation > 0.7 and not text.endswith(("!", "?", ".", "…")):
        text += "!"
    # Emojis
    eprob = emoji_baseline * (0.4 + 1.2 * style.warmth) * (0.8 + 0.6 * arousal) * style.emoji_prob
    if random.random() < eprob:
        text += " " + random.choice(EMOJIS.get(emotion, EMOJIS["neutral"]))
    return re.sub(r"\s+", " ", text).strip()
