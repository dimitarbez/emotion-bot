
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Dict
import math, time

# Mapping discrete emotions to typical (valence, arousal) centers
EMOTION_MAP: Dict[str, Tuple[float, float]] = {
    "neutral":   (0.0, 0.2),
    "joy":       (0.7, 0.6),
    "sadness":   (-0.7, 0.3),
    "anger":     (-0.6, 0.8),
    "fear":      (-0.8, 0.7),
    "surprise":  (0.2, 0.9),
    "disgust":   (-0.6, 0.5),
    "curiosity": (0.2, 0.5),
    "affection": (0.6, 0.4),
}

def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

@dataclass
class EmotionState:
    # Core affect
    valence: float = 0.0   # -1..1 (negative..positive)
    arousal: float = 0.2   # 0..1 (calm..excited)

    # Discrete
    current_emotion: str = "neutral"
    last_switch_time: float = field(default_factory=time.time)

    # Baselines
    baseline_valence: float = 0.0
    baseline_arousal: float = 0.2

    def decay_toward_baseline(self, dt: float, valence_half_life: float, arousal_half_life: float):
        # exponential decay toward baseline
        if valence_half_life > 0:
            k_v = math.log(2) / valence_half_life
            self.valence = self.baseline_valence + (self.valence - self.baseline_valence) * math.exp(-k_v * dt)
        if arousal_half_life > 0:
            k_a = math.log(2) / arousal_half_life
            self.arousal = self.baseline_arousal + (self.arousal - self.baseline_arousal) * math.exp(-k_a * dt)
        self.valence = _clip(self.valence, -1.0, 1.0)
        self.arousal = _clip(self.arousal, 0.0, 1.0)

    def apply_delta(self, dv: float, da: float, inertia: float = 0.75):
        # Inertia: blend previous state to avoid jerk
        self.valence = _clip(self.valence * inertia + dv * (1.0 - inertia), -1.0, 1.0)
        self.arousal = _clip(self.arousal * inertia + da * (1.0 - inertia), 0.0, 1.0)

    def compute_discrete_emotion(self) -> str:
        # Choose the emotion whose center is closest in (v,a) Euclidean distance
        best = None
        best_d = 1e9
        for name, (v0, a0) in EMOTION_MAP.items():
            d = (self.valence - v0)**2 + (self.arousal - a0)**2
            if d < best_d:
                best_d = d
                best = name
        return best or "neutral"

    def maybe_switch_discrete(self, now: float, min_duration: float):
        candidate = self.compute_discrete_emotion()
        if candidate != self.current_emotion:
            if now - self.last_switch_time >= min_duration:
                self.current_emotion = candidate
                self.last_switch_time = now

    def as_dict(self):
        return {
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "emotion": self.current_emotion,
            "since": round(time.time() - self.last_switch_time, 1),
        }
