from __future__ import annotations

import time
import threading
from queue import Empty, Queue

from emotional_core.config import CONFIG
from emotional_core.emotions import EmotionState
from emotional_core.nlp import appraise
from emotional_core.behavior import shape
from emotional_core.memory import ConversationMemory
from emotional_core.brain import Brain, BrainConfig
from emotional_core.telemetry import EmotionPlotter


def emotional_step(
    state: EmotionState, dt: float, user_text: str | None = None
) -> EmotionState:
    """Advance the emotional state by ``dt`` seconds.

    If ``user_text`` is provided, the appraisal of that text influences the
    resulting state. The function always performs decay and discrete emotion
    updates so it can be called on every loop iteration regardless of whether
    new input has arrived.
    """

    now = time.time()
    # 1) decay based on real time delta
    state.decay_toward_baseline(
        dt=dt,
        valence_half_life=CONFIG.decay.valence_half_life,
        arousal_half_life=CONFIG.decay.arousal_half_life,
    )

    force_switch = False
    if user_text is not None:
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
        # 4) high intensity or anger can force switch
        force_switch = a.discrete_hint == "anger" or a.intensity > 0.7

    # Discrete selection with stickiness
    state.maybe_switch_discrete(
        now, CONFIG.decay.min_emotion_duration, force=force_switch
    )
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

    # Queue for incoming user messages read on a background thread
    q: Queue[str] = Queue()
    stop = False

    def reader():
        nonlocal stop
        while not stop:
            try:
                msg = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                stop = True
                return
            q.put(msg)

    threading.Thread(target=reader, daemon=True).start()

    last = time.time()
    try:
        while not stop:
            now = time.time()
            dt = now - last
            last = now

            # Consume a message if available
            user = None
            try:
                user = q.get_nowait()
            except Empty:
                pass

            if user:
                if user.lower() in {":quit", ":q", "exit"}:
                    print("bot> take care!")
                    stop = True
                elif user.lower() == ":state":
                    state = emotional_step(state, dt)
                    print("bot>", state.as_dict())
                elif user != "":
                    state = emotional_step(state, dt, user)
                    mem.add("user", user)
                    context = mem.recent_context(limit=6)
                    raw = brain.generate_base(user, state.current_emotion, context)
                    styled = shape(
                        raw,
                        state.current_emotion,
                        state.arousal,
                        base_max_tokens=CONFIG.behavior.base_max_tokens,
                        emoji_baseline=CONFIG.behavior.emoji_baseline,
                    )
                    print("bot>", styled)
                    mem.add("bot", styled)
            else:
                state = emotional_step(state, dt)

            plotter.update(state)
            time.sleep(0.1)
    finally:
        stop = True
        plotter.close()


if __name__ == "__main__":
    run_cli()
