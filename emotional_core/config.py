from dataclasses import dataclass, field


@dataclass
class DecayConfig:
    # Approximate half-lives (seconds). Emotions decay toward baseline over time.
    valence_half_life: float = 900.0  # 15 min
    arousal_half_life: float = 600.0  # 10 min

    # Minimum time (seconds) to keep a discrete emotion before switching (prevents flicker)
    min_emotion_duration: float = 45.0


@dataclass
class EmotionWeights:
    # How strongly different appraisals nudge core affect
    sentiment_to_valence: float = 0.5
    intensity_to_arousal: float = 0.6
    # Dampens sudden swings
    inertia: float = 0.75  # 0..1 (closer to 1 = more inertia)


@dataclass
class BehaviorConfig:
    # Max base response length; emotional scaling will adjust
    base_max_tokens: int = 140
    # Emoji policy (0..1)
    emoji_baseline: float = 0.15


@dataclass
class OpenAIConfig:
    model: str = "gpt-4o-mini"  # Used if openai is installed and OPENAI_API_KEY is set
    temperature: float = 0.7
    max_tokens: int = 220


@dataclass
class AppConfig:
    decay: DecayConfig = field(default_factory=DecayConfig)
    weights: EmotionWeights = field(default_factory=EmotionWeights)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)


CONFIG = AppConfig()
