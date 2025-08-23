from __future__ import annotations
import time, os
from dataclasses import dataclass
from typing import Tuple

from emotional_core.config import CONFIG
from emotional_core.emotions import EmotionState
from emotional_core.nlp import appraise
from emotional_core.behavior import shape
from emotional_core.memory import ConversationMemory
from emotional_core.brain import Brain, BrainConfig
from emotional_core.telemetry import EmotionPlotter


def emotional_update(state: EmotionState, user_text: str) -> EmotionState:
    now = time.time()
    # 1) decay
    state.decay_toward_baseline(
        dt=1.0,  # assume ~1s between steps in CLI; real apps: use real dt
        valence_half_life=CONFIG.decay.valence_half_life,
        arousal_half_life=CONFIG.decay.arousal_half_life,
    )
    # 2) appraisal
    a = appraise(user_text)
    # Scale deltas by input intensity so emphatic messages have bigger impact
    intensity_factor = 1 + a.intensity
    dv = a.sentiment * CONFIG.weights.sentiment_to_valence * intensity_factor
    da = a.intensity * CONFIG.weights.intensity_to_arousal
    # emotion-specific nudges (also scaled by intensity)
    mult = intensity_factor
    if a.discrete_hint == "anger":
        dv -= 0.2 * mult
        da += 0.15 * mult
    elif a.discrete_hint == "sadness":
        dv -= 0.25 * mult
        da -= 0.05 * mult
    elif a.discrete_hint == "fear":
        dv -= 0.25 * mult
        da += 0.05 * mult
    elif a.discrete_hint == "disgust":
        dv -= 0.2 * mult
        da += 0.05 * mult
    elif a.discrete_hint == "joy":
        dv += 0.3 * mult
        da += 0.05 * mult
    elif a.discrete_hint == "surprise":
        da += 0.2 * mult
    elif a.discrete_hint == "curiosity":
        da += 0.1 * mult
    elif a.discrete_hint == "affection":
        dv += 0.25 * mult
        da -= 0.05 * mult

    # 3) inertia-blended delta
    state.apply_delta(dv, da, inertia=CONFIG.weights.inertia)
    # 4) discrete selection with stickiness; high intensity or anger can force switch
    force_switch = a.discrete_hint == "anger" or a.intensity > 0.7
    state.maybe_switch_discrete(now, CONFIG.decay.min_emotion_duration, force=force_switch)
    return state


def run_cli():
    print(
        "EmoBot — emotionally-driven chatbot\nType ':state' to view state, ':quit' to exit.\n"
    )
    state = EmotionState()
    mem = ConversationMemory()
    brain = Brain(
        BrainConfig(
            openai_model=CONFIG.openai.model,
            openai_temperature=CONFIG.openai.temperature,
            openai_max_tokens=CONFIG.openai.max_tokens,
        )
    )
    plotter = EmotionPlotter()
    try:
        while True:
            try:
                user = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye!")
                break
            if user == "":
                continue
            if user.lower() in {":quit", ":q", "exit"}:
                print("bot> take care!")
                break
            if user.lower() == ":state":
                print("bot>", state.as_dict())
                continue

            # Update emotion
            state = emotional_update(state, user)
            plotter.update(state)

            # Build context & generate base reply
            mem.add("user", user)
            context = mem.recent_context(limit=6)
            raw = brain.generate_base(user, state.current_emotion, context)

            # Style shaping
            styled = shape(
                raw,
                state.current_emotion,
                state.arousal,
                base_max_tokens=CONFIG.behavior.base_max_tokens,
                emoji_baseline=CONFIG.behavior.emoji_baseline,
            )
            print("bot>", styled)
            mem.add("bot", styled)
    finally:
        plotter.close()


if __name__ == "__main__":
    run_cli()
