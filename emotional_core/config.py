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
    sentiment_to_valence: float = 0.8
    intensity_to_arousal: float = 0.9
    # Dampens sudden swings
    inertia: float = 0.6  # 0..1 (closer to 1 = more inertia)


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
class PersonalityConfig:
    # Default personality type - can be changed at runtime
    default_type: str = "balanced"
    # Whether personality affects emotional baselines
    affects_baselines: bool = True
    # Strength of personality influence (0.0 to 1.0)
    influence_strength: float = 1.0


@dataclass
class RandomnessConfig:
    # Overall randomness intensity (0.0 = deterministic, 1.0 = very random)
    intensity: float = 0.3
    
    # Individual randomness type probabilities (0.0 to 1.0)
    style_drift_prob: float = 0.2        # Gradual style changes
    mood_swing_prob: float = 0.1         # Sudden emotional shifts  
    memory_quirk_prob: float = 0.15      # Memory-related quirks
    topic_tangent_prob: float = 0.08     # Spontaneous topic shifts
    response_delay_prob: float = 0.25    # Thinking pauses
    typo_slip_prob: float = 0.05         # Occasional typos
    enthusiasm_burst_prob: float = 0.12  # Random excitement
    distraction_prob: float = 0.1        # Getting distracted
    
    # Timing parameters
    min_delay: float = 0.5               # Minimum thinking delay (seconds)
    max_delay: float = 3.0               # Maximum thinking delay (seconds)
    
    # Style drift parameters
    drift_magnitude: float = 0.2         # How much styles can drift
    drift_persistence: float = 0.8       # How long drifts last


@dataclass
class AppConfig:
    decay: DecayConfig = field(default_factory=DecayConfig)
    weights: EmotionWeights = field(default_factory=EmotionWeights)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    personality: PersonalityConfig = field(default_factory=PersonalityConfig)
    randomness: RandomnessConfig = field(default_factory=RandomnessConfig)


CONFIG = AppConfig()
