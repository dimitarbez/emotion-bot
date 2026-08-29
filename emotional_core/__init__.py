"""EmotionBot's reusable emotional core."""

from .engine import EmotionEngine, EngineResult
from .emotions import EMOTION_MAP, EmotionState

__all__ = ["EmotionEngine", "EngineResult", "EMOTION_MAP", "EmotionState"]
