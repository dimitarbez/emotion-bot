
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
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

def shape(text: str, emotion: str, arousal: float, base_max_tokens: int, emoji_baseline: float, 
          personality_modifiers: Optional[Dict[str, float]] = None, 
          personality_flavor: Optional[str] = None,
          personality_type: str = "balanced",
          randomness_engine=None) -> str:
    """Shape response text based on emotion, arousal, personality traits, and randomness."""
    style = STYLE_PRESETS.get(emotion, STYLE_PRESETS["neutral"])
    
    # Apply personality modifiers if provided
    if personality_modifiers:
        style = Style(
            verbosity=style.verbosity * personality_modifiers.get("verbosity", 1.0),
            directness=style.directness * personality_modifiers.get("directness", 1.0),
            warmth=style.warmth * personality_modifiers.get("warmth", 1.0),
            playfulness=style.playfulness * personality_modifiers.get("playfulness", 1.0),
            formality=style.formality * personality_modifiers.get("formality", 1.0),
            punctuation=style.punctuation,
            hesitation=style.hesitation,
            emoji_prob=style.emoji_prob,
        )
    
    # Convert style to dict for randomness processing
    style_dict = {
        "verbosity": style.verbosity,
        "directness": style.directness,
        "warmth": style.warmth,
        "playfulness": style.playfulness,
        "formality": style.formality,
        "punctuation": style.punctuation,
        "hesitation": style.hesitation,
        "emoji_prob": style.emoji_prob,
    }
    
    # Apply randomness if engine provided
    modified_text = text
    response_delay = 0.0
    
    if randomness_engine:
        modified_text, style_dict, response_delay = randomness_engine.apply_all_randomness(
            text, style_dict, emotion, personality_type
        )
        
        # Apply mood swing to arousal if applicable
        mood_dv, mood_da = randomness_engine.get_mood_swing_delta()
        if mood_da != 0.0:
            arousal = max(0.0, min(1.0, arousal + mood_da))
    
    # Reconstruct style from modified dict
    style = Style(
        verbosity=style_dict["verbosity"],
        directness=style_dict["directness"],
        warmth=style_dict["warmth"],
        playfulness=style_dict["playfulness"],
        formality=style_dict["formality"],
        punctuation=style_dict["punctuation"],
        hesitation=style_dict["hesitation"],
        emoji_prob=style_dict["emoji_prob"],
    )
    
    # Add personality flavor at the beginning if provided
    if personality_flavor and random.random() < 0.6:  # 60% chance to use flavor
        modified_text = personality_flavor + " " + modified_text
    
    # Adjust verbosity by arousal
    max_len = int(base_max_tokens * style.verbosity * (0.8 + 0.4 * arousal))
    
    # Trim text if too long
    tokens = modified_text.split()
    if len(tokens) > max_len:
        tokens = tokens[:max_len]
        modified_text = " ".join(tokens)
        if style.punctuation > 0.5:
            modified_text += "…"
    
    # Inject hedges/hesitation if needed
    if style.hesitation > 0.15 and random.random() < style.hesitation:
        modified_text = random.choice(FILLERS) + ", " + modified_text
    if style.directness < 0.6 and random.random() < 0.3:
        modified_text = random.choice(HEDGES) + ", " + modified_text
    
    # Emotion-specific markers
    if emotion == "anger" and random.random() < 0.35:
        modified_text = random.choice(ANGRY_MARKERS) + ", " + modified_text
    if emotion in ("sadness", "fear") and random.random() < 0.3:
        modified_text = random.choice(SUPPORT_MARKERS) + ". " + modified_text
    if emotion == "joy" and random.random() < 0.3:
        modified_text = random.choice(POSITIVE_AFFIRM) + " " + modified_text

    # Punctuation/exclamation (enhanced with randomness)
    if style.punctuation > 0.7 and not modified_text.endswith(("!", "?", ".", "…")):
        if style.playfulness > 0.6 and random.random() < 0.3:
            # Multiple exclamation marks for high playfulness
            modified_text += "!" * random.randint(1, 3)
        else:
            modified_text += "!"
    
    # Emojis (enhanced probability calculation)
    eprob = emoji_baseline * (0.4 + 1.2 * style.warmth) * (0.8 + 0.6 * arousal) * style.emoji_prob
    if random.random() < eprob:
        emoji_pool = EMOJIS.get(emotion, EMOJIS["neutral"])
        # Sometimes add multiple emojis for high playfulness
        if style.playfulness > 0.8 and random.random() < 0.2:
            emoji_count = random.randint(1, 2)
            emojis = [random.choice(emoji_pool) for _ in range(emoji_count)]
            modified_text += " " + " ".join(emojis)
        else:
            modified_text += " " + random.choice(emoji_pool)
    
    # Clean up spacing
    final_text = re.sub(r"\s+", " ", modified_text).strip()
    
    # Return with delay information (could be used by caller)
    if hasattr(shape, '_last_delay'):
        shape._last_delay = response_delay
    
    return final_text
