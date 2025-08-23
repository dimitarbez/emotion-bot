import os
import sys
import time

import pytest

# Ensure the project root is on sys.path so emotional_core can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from emotional_core.emotions import EmotionState


def test_apply_delta_respects_inertia():
    st = EmotionState(valence=0.5, arousal=0.4)
    st.apply_delta(dv=0.2, da=0.1, inertia=0.75)
    assert st.valence == pytest.approx(0.5 + 0.2 * (1 - 0.75))
    assert st.arousal == pytest.approx(0.4 + 0.1 * (1 - 0.75))


def test_force_switch_overrides_min_duration():
    st = EmotionState()
    # Set affect near anger so compute_discrete_emotion picks it
    st.valence = -0.6
    st.arousal = 0.8
    st.current_emotion = "neutral"
    st.last_switch_time = time.time()
    # Without force the switch should be blocked
    st.maybe_switch_discrete(now=st.last_switch_time + 1, min_duration=100)
    assert st.current_emotion == "neutral"
    # Forcing switch should override the duration gate
    st.maybe_switch_discrete(now=st.last_switch_time + 1, min_duration=100, force=True)
    assert st.current_emotion == "anger"
