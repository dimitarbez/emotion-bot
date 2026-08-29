import os

from emotional_core.engine import EmotionEngine
from emotional_core.emotions import EMOTION_MAP


def test_deterministic_text_produces_joy_without_external_services(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = EmotionEngine(seed=7).process("I am thrilled and joyful!")
    assert result.emotion == "joy"
    assert result.source == "deterministic"
    assert -1.0 <= result.valence <= 1.0
    assert 0.0 <= result.arousal <= 1.0
    assert result.response


def test_all_nine_deterministic_events_use_real_emotion_state():
    engine = EmotionEngine(seed=3)
    for emotion, (valence, arousal) in EMOTION_MAP.items():
        result = engine.process("event:%s" % emotion)
        assert result.emotion == emotion
        assert result.valence == valence
        assert result.arousal == arousal
        assert result.source == "event"


def test_seeded_sessions_are_repeatable():
    text = "I am furious and angry!"
    first = EmotionEngine(seed=123).process(text)
    second = EmotionEngine(seed=123).process(text)
    assert first == second


def test_invalid_event_is_rejected():
    engine = EmotionEngine()
    try:
        engine.process("event:confused")
    except ValueError as exc:
        assert "unknown emotion" in str(exc)
    else:
        raise AssertionError("invalid event was accepted")
