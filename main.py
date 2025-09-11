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
from emotional_core.personality import Personality, get_available_personalities
from emotional_core.randomness import RandomnessEngine, RandomnessConfig


def emotional_update(state: EmotionState, user_text: str, personality: Personality, randomness_engine: RandomnessEngine = None) -> EmotionState:
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
    
    # Apply personality modifications to emotional deltas
    dv, da = personality.modify_emotional_deltas(dv, da, a.intensity)
    
    # Apply randomness mood swings if engine provided
    if randomness_engine:
        mood_dv, mood_da = randomness_engine.get_mood_swing_delta()
        dv += mood_dv
        da += mood_da
    
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
        "EmoBot — emotionally-driven chatbot with personality and randomness\nType ':state' to view state, ':personality' to view personality, ':randomness' to view randomness, ':switch <type>' to change personality, ':quit' to exit.\n"
    )
    
    # Initialize personality system
    personality = Personality(CONFIG.personality.default_type)
    print(f"Personality: {personality.type}")
    available_personalities = get_available_personalities()
    print(f"Available personalities: {', '.join(available_personalities)}")
    
    # Initialize randomness system
    randomness_config = RandomnessConfig(
        intensity=CONFIG.randomness.intensity,
        style_drift_prob=CONFIG.randomness.style_drift_prob,
        mood_swing_prob=CONFIG.randomness.mood_swing_prob,
        memory_quirk_prob=CONFIG.randomness.memory_quirk_prob,
        topic_tangent_prob=CONFIG.randomness.topic_tangent_prob,
        response_delay_prob=CONFIG.randomness.response_delay_prob,
        typo_slip_prob=CONFIG.randomness.typo_slip_prob,
        enthusiasm_burst_prob=CONFIG.randomness.enthusiasm_burst_prob,
        distraction_prob=CONFIG.randomness.distraction_prob,
    )
    randomness_engine = RandomnessEngine(randomness_config)
    print(f"Randomness intensity: {randomness_config.intensity}\n")
    
    # Initialize emotion state with personality-influenced baselines
    state = EmotionState()
    if CONFIG.personality.affects_baselines:
        baseline_v, baseline_a = personality.adjust_baseline_emotion()
        state.set_personality_baselines(baseline_v, baseline_a)
        # Set initial values to baselines
        state.valence = baseline_v
        state.arousal = baseline_a
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
            if user.lower() == ":personality":
                print("bot>", personality.as_dict())
                continue
            if user.lower() == ":randomness":
                print("bot>", randomness_engine.as_dict())
                continue
            if user.lower().startswith(":switch "):
                new_personality = user[8:].strip()
                if new_personality in available_personalities:
                    personality = Personality(new_personality)
                    print(f"bot> Switched to {new_personality} personality!")
                    # Update baselines if enabled
                    if CONFIG.personality.affects_baselines:
                        baseline_v, baseline_a = personality.adjust_baseline_emotion()
                        state.set_personality_baselines(baseline_v, baseline_a)
                else:
                    print(f"bot> Unknown personality. Available: {', '.join(available_personalities)}")
                continue

            # Apply response delay from randomness (simulate thinking)
            response_delay = randomness_engine.get_response_delay()
            if response_delay > 0:
                print("💭 thinking...")
                time.sleep(response_delay)

            # Update emotion with randomness
            print("Updating emotion...")
            state = emotional_update(state, user, personality, randomness_engine)
            plotter.update(state)

            # Build context & generate base reply
            mem.add("user", user)
            context = mem.recent_context(limit=6)
            raw = brain.generate_base(user, state.current_emotion, context, personality.type)

            # Get personality-based style modifiers and flavor
            style_modifiers = personality.get_personality_style_modifiers()
            personality_flavor = personality.get_response_flavor(state.current_emotion)

            # Style shaping with personality and randomness
            styled = shape(
                raw,
                state.current_emotion,
                state.arousal,
                base_max_tokens=CONFIG.behavior.base_max_tokens,
                emoji_baseline=CONFIG.behavior.emoji_baseline,
                personality_modifiers=style_modifiers,
                personality_flavor=personality_flavor,
                randomness_engine=randomness_engine,
            )
            print("bot>", styled)
            mem.add("bot", styled)
    finally:
        plotter.close()


if __name__ == "__main__":
    run_cli()
