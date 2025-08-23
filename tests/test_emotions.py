import os
import sys

import pytest

# Ensure the project root is on sys.path so emotional_core can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from emotional_core.emotions import EmotionState


def test_apply_delta_respects_inertia():
    st = EmotionState(valence=0.5, arousal=0.4)
    st.apply_delta(dv=0.2, da=0.1, inertia=0.75)
    assert st.valence == pytest.approx(0.5 + 0.2 * (1 - 0.75))
    assert st.arousal == pytest.approx(0.4 + 0.1 * (1 - 0.75))
