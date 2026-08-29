"""Reusable, headless EmotionBot session.

This module deliberately has no CLI, plotting, microphone, ROS, model-download,
or API-key side effects.  It is the supported integration boundary for other
processes such as ROS adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import random
import re
import time

from .behavior import shape
from .brain import Brain, BrainConfig
from .config import CONFIG
from .emotions import EMOTION_MAP, EmotionState
from .memory import ConversationMemory
from .nlp import Appraisal, appraise
from .personality import PERSONALITY_PRESETS, Personality
from .randomness import RandomnessConfig, RandomnessEngine


@dataclass
class EngineResult:
    emotion: str
    valence: float
    arousal: float
    response: str
    source: str


def apply_appraisal(
    state: EmotionState,
    appraisal: Appraisal,
    personality: Personality,
    randomness_engine: Optional[RandomnessEngine] = None,
    now: Optional[float] = None,
    dt: float = 1.0,
) -> EmotionState:
    """Apply EmotionBot's appraisal/update rules to an existing state."""
    state.decay_toward_baseline(
        dt=dt,
        valence_half_life=CONFIG.decay.valence_half_life,
        arousal_half_life=CONFIG.decay.arousal_half_life,
    )
    intensity_factor = 1.0 + appraisal.intensity
    dv = appraisal.sentiment * CONFIG.weights.sentiment_to_valence * intensity_factor
    da = appraisal.intensity * CONFIG.weights.intensity_to_arousal
    dv, da = personality.modify_emotional_deltas(dv, da, appraisal.intensity)

    if randomness_engine is not None:
        mood_dv, mood_da = randomness_engine.get_mood_swing_delta()
        dv += mood_dv
        da += mood_da

    nudges = {
        "anger": (-0.2, 0.15),
        "sadness": (-0.25, -0.05),
        "fear": (-0.25, 0.05),
        "disgust": (-0.2, 0.05),
        "joy": (0.3, 0.05),
        "surprise": (0.0, 0.2),
        "curiosity": (0.0, 0.1),
        "affection": (0.25, -0.05),
    }
    if appraisal.discrete_hint in nudges:
        nudge_v, nudge_a = nudges[appraisal.discrete_hint]
        dv += nudge_v * intensity_factor
        da += nudge_a * intensity_factor

    state.apply_delta(dv, da, inertia=CONFIG.weights.inertia)
    force = appraisal.intensity > 0.7 or appraisal.discrete_hint == "anger"
    state.maybe_switch_discrete(
        now=time.time() if now is None else now,
        min_duration=CONFIG.decay.min_emotion_duration,
        force=force,
    )
    return state


class EmotionEngine:
    """Own one deterministic or optional-transformer EmotionBot session."""

    EVENT_RE = re.compile(r"^\s*(?:event|emotion)\s*:\s*([a-z]+)\s*$", re.IGNORECASE)

    def __init__(
        self,
        personality_type: str = "balanced",
        backend: str = "deterministic",
        seed: int = 0,
        randomness_enabled: bool = False,
    ):
        if personality_type not in PERSONALITY_PRESETS:
            raise ValueError("unknown personality: %s" % personality_type)
        if backend not in ("deterministic", "transformers"):
            raise ValueError("unsupported backend: %s" % backend)

        random.seed(seed)
        self.backend = backend
        self.seed = seed
        self.personality = Personality(personality_type)
        self.state = EmotionState()
        if CONFIG.personality.affects_baselines:
            baseline_v, baseline_a = self.personality.adjust_baseline_emotion()
            self.state.set_personality_baselines(baseline_v, baseline_a)
            self.state.valence = baseline_v
            self.state.arousal = baseline_a
        self.memory = ConversationMemory()
        self.randomness_engine = None
        if randomness_enabled:
            self.randomness_engine = RandomnessEngine(RandomnessConfig())
        self.brain = Brain(
            BrainConfig(
                openai_model=CONFIG.openai.model,
                openai_temperature=CONFIG.openai.temperature,
                openai_max_tokens=CONFIG.openai.max_tokens,
            )
        )

    def process(self, user_text: str, now: Optional[float] = None) -> EngineResult:
        text = user_text.strip()
        if not text:
            raise ValueError("input text must not be empty")

        source = self.backend
        event_match = self.EVENT_RE.match(text)
        if event_match:
            emotion = event_match.group(1).lower()
            if emotion not in EMOTION_MAP:
                raise ValueError("unknown emotion event: %s" % emotion)
            self.state.valence, self.state.arousal = EMOTION_MAP[emotion]
            self.state.current_emotion = emotion
            self.state.last_switch_time = time.time() if now is None else now
            source = "event"
        else:
            appraisal = appraise(text, backend=self.backend)
            apply_appraisal(
                self.state,
                appraisal,
                self.personality,
                randomness_engine=self.randomness_engine,
                now=now,
            )

        if self.randomness_engine is not None:
            self.randomness_engine.update_conversation_state(
                text, self.state.current_emotion, self.personality.type
            )

        self.memory.add("user", text)
        context = self.memory.recent_context(limit=6)
        raw = self.brain.generate_local(
            text, self.state.current_emotion, context, self.personality.type
        )
        styled = shape(
            raw,
            self.state.current_emotion,
            self.state.arousal,
            base_max_tokens=CONFIG.behavior.base_max_tokens,
            emoji_baseline=CONFIG.behavior.emoji_baseline,
            personality_modifiers=self.personality.get_personality_style_modifiers(),
            personality_flavor=self.personality.get_response_flavor(self.state.current_emotion),
            personality_type=self.personality.type,
            randomness_engine=self.randomness_engine,
        )
        self.memory.add("bot", styled)
        return EngineResult(
            emotion=self.state.current_emotion,
            valence=self.state.valence,
            arousal=self.state.arousal,
            response=styled,
            source=source,
        )

    def snapshot(self) -> EngineResult:
        return EngineResult(
            emotion=self.state.current_emotion,
            valence=self.state.valence,
            arousal=self.state.arousal,
            response="",
            source=self.backend,
        )
