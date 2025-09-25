# EmotionBot AI Coding Guidelines

BE SHORT AND CONCSISE. This is a reference for contributors and AI assistants (like GitHub Copilot) working on the EmotionBot project.

## Purpose
This document gives succinct, practical guidance for contributors and automated assistants (like GitHub Copilot) working on EmotionBot. It highlights key architecture, integration points, testing guidance, and safe defaults for optional dependencies.

## Architecture Overview

EmotionBot implements Russell's Circumplex Model with a 5-stage emotional processing pipeline located in `main.py:emotional_update()`:

1. Decay — exponential decay toward personality-influenced baselines (`EmotionState.decay_toward_baseline`) using configurable half-lives.
2. Appraisal — NLP analysis via `nlp.appraise()` (DistilBERT sentiment + GoEmotions discrete hints) with neutral fallback when models are unavailable.
3. Core Affect Update — compute valence/arousal deltas, apply personality modifiers, randomness nudges, discrete-emotion-specific nudges, then apply with inertia via `state.apply_delta()`.
4. Discrete Mapping — map continuous valence/arousal to one of 9 discrete emotions in `EMOTION_MAP` using Euclidean distance.
5. Stickiness & Force Switch — `maybe_switch_discrete()` enforces a minimum duration and allows force-switch on high intensity or anger.

Data flow: user input → nlp.appraise() → EmotionState.apply_delta() → Brain.generate_base() → behavior.shape() → styled response

## Core Modules (high level)
- `main.py` — CLI orchestration, `emotional_update()`, initialization of personality, randomness, memory, brain, and telemetry.
- `nlp.py` — lazy-loaded transformer pipelines for sentiment and GoEmotions classification; returns `Appraisal(sentiment, intensity, discrete_hint)` and gracefully falls back to neutral output.
- `emotions.py` — `EmotionState` dataclass, `EMOTION_MAP`, decay, inertia, discrete selection, and personality baselines.
- `personality.py` — seven personality presets, trait-driven modifiers for emotional deltas and response style, baseline adjustment helpers.
- `randomness.py` — human-like variability engine (mood swings, style drift, delays, typos, tangents) with `RandomnessConfig` and methods like `get_mood_swing_delta()` and `get_response_delay()`.
- `brain.py` — dual-path response generation (OpenAI primary, local template fallback), emotion-aware prompts and context integration.
- `behavior.py` — post-processing style shaping (verbosity, directness, warmth, punctuation, emoji insertion).
- `memory.py` — conversation context windowing and topic tracking.
- `telemetry.py` — live matplotlib plotting via `EmotionPlotter`.
- `config.py` — centralized dataclass configuration (decay, weights, behavior, openai, personality, randomness).

### Expanded per-system details

Below are concise, copy-paste friendly contracts and tips for each core module so maintainers and assistants can make safe, testable changes.

`main.py` (CLI & pipeline)
- Contract: `emotional_update(state: EmotionState, user_text: str, personality: Personality, randomness_engine: RandomnessEngine|None) -> EmotionState`.
- Key responsibilities: orchestrate decay → appraisal → core-affect update → discrete selection; initialize systems (personality, randomness, memory, brain, telemetry) and provide CLI commands (`:state`, `:personality`, `:randomness`, `:switch`).
- Important config keys: `CONFIG.decay.*`, `CONFIG.weights.*`, `CONFIG.personality.affects_baselines`, `CONFIG.openai.*`.
- Edge cases: empty input (ignore), very high intensity (force-switch), and unavailable randomness/openai (use fallbacks).
- Tests: integration test that simulates multiple inputs and asserts discrete selection stickiness and inertia behavior (use short half-lives in test fixture).

`nlp.py` (Appraisal)
- Contract: `appraise(text: str) -> Appraisal(sentiment: float, intensity: float, discrete_hint: Optional[str])`.
- Key functions: lazy-loaded sentiment and GoEmotions pipelines, mapping `_EMO_MAP` from GoEmotions labels to discrete emotions.
- Behavior: return neutral appraisal `(0.0, 0.0, None)` when model invocation fails or packages are missing.
- Config: model selection and device defaults live in `CONFIG` (if present).
- Edge cases: very short / non-text input — return neutral; model timeouts — fallback to neutral with logged warning.
- Tests: unit tests that patch the pipelines to return deterministic values and assert intensity scaling and discrete_hint mapping.

`emotions.py` (Core affect & discrete mapping)
- Contract: `EmotionState` exposes `.valence: float`, `.arousal: float`, `.current_emotion: str`, `.last_switched: float`, and methods `decay_toward_baseline(dt, valence_half_life, arousal_half_life)`, `apply_delta(dv, da, inertia)`, `maybe_switch_discrete(now, min_duration, force=False)`.
- Key constants: `EMOTION_MAP` (9 emotions → (v,a) coords).
- Algorithms: exponential decay using k = ln(2)/half_life; inertia blending `new = old + delta * (1 - inertia)`; discrete selection via Euclidean nearest neighbor.
- Edge cases: keep valence in [-1,1], arousal in [0,1]; clamp values after updates; handle NaN/None defensively.
- Tests: floating-point comparisons with `pytest.approx()`; tests for decay math, inertia blending, boundary clamping, and forced switches.

`personality.py` (Presets & modifiers)
- Contract: `Personality(type: str)` and methods `modify_emotional_deltas(dv, da, intensity) -> (dv2, da2)`, `get_personality_style_modifiers() -> dict`, `adjust_baseline_emotion() -> (baseline_v, baseline_a)`.
- Key behavior: apply valence bias, arousal sensitivity, and emotional stability modifiers. Also supply style multipliers used by `behavior.shape()`.
- Config: `CONFIG.personality.default_type`, `CONFIG.personality.affects_baselines`.
- Edge cases: unknown personality type — default to `balanced`; extremely large modifier multipliers should be clamped.
- Tests: deterministic checks for each preset; seed randomness where personality uses stochastic elements.

`randomness.py` (Human variability)
- Contract: `RandomnessConfig(...)` and `RandomnessEngine(config)` with methods `get_mood_swing_delta() -> (dv, da)`, `get_response_delay() -> float`, `as_dict()`.
- Behavior: probabilistic, but tests should be able to inject a seeded RNG or mock the engine for deterministic results.
- Config keys: `CONFIG.randomness.*` (probabilities and intensities for mood swings, style drift, typos, etc.).
- Edge cases: avoid large instantaneous jumps; cap mood swing deltas and ensure resulting valence/arousal stay in valid ranges.
- Tests: provide deterministic RNG or patch `random.random()`/`random.gauss()` to validate outputs.

`brain.py` (Response generation)
- Contract: `Brain(BrainConfig).generate_base(user_text, discrete_emotion, context, personality_type) -> str`.
- Behavior: prefer OpenAI when `_HAS_OPENAI` and `OPENAI_API_KEY` present; otherwise use localized template fallback.
- Important config: `CONFIG.openai.model`, `CONFIG.openai.temperature`, `CONFIG.openai.max_tokens`.
- Edge cases: API failures → return local fallback; context too long → truncate to `ConversationMemory.recent_context(limit=...)`.
- Tests: mock OpenAI client to return canned completions; test fallback generation separately.

`behavior.py` (Styling/post-processing)
- Contract: `shape(raw_text, discrete_emotion, arousal, base_max_tokens, emoji_baseline, personality_modifiers, personality_flavor, randomness_engine) -> str`.
- Behavior: applies multi-layer style transformation: base emotion style → personality multipliers → randomness variations → final content transformations (length, hedging, punctuation, emoji).
- Config keys: `CONFIG.behavior.base_max_tokens`, `CONFIG.behavior.emoji_baseline`.
- Edge cases: avoid harmful transformations (do not inject offensive content); when randomness_engine introduces typos, ensure lifetime or reversibility for tests.
- Tests: small fixtures showing mapping from `raw_text` to styled output under a few style modifier sets.

`memory.py` (Conversation memory)
- Contract: `ConversationMemory.add(speaker, text)` and `recent_context(limit=6) -> list[dict]`.
- Behavior: sliding window with `max_history` from config; topic tracking via basic token frequency.
- Edge cases: very long utterances should be truncated when placed into context; ensure timestamps are monotonic.
- Tests: assert formatting of `recent_context()` and that `add()` increases history and discards oldest items when at capacity.

`telemetry.py` (Visualization)
- Contract: `EmotionPlotter()` with `update(state: EmotionState)` and `close()` methods.
- Behavior: draw valence/arousal lines with annotations. In headless CI (no display) the plotter should degrade to a no-op implementation or save images to a temp dir.
- Edge cases: calling `update()` frequently should not leak memory — use a sliding buffer of points.
- Tests: integration smoke test that calls `update()` repeatedly with synthetic states; in CI, use headless backend (e.g., Agg) or patch `EmotionPlotter` to a no-op.

`config.py` (Centralized configuration)
- Contract: `CONFIG` dataclass with nested sections: `decay`, `weights`, `behavior`, `openai`, `personality`, `randomness`.
- Behavior: all runtime tuning should be done here; prefer adding flags and defaults here instead of scattering magic numbers.
- Edge cases: invalid config values should be validated on load (e.g., half-life > 0, inertia in [0,1]).
- Tests: validate config defaults and example overrides.

## Key Design Patterns

Graceful degradation
- Transformers and OpenAI are optional: code must fall back to deterministic/local behavior when external services or models are unavailable. Use explicit feature flags (e.g. `_HAS_OPENAI`) and try/except patterns.

Emotion dynamics
- Inertia dampening: `apply_delta(dv, da, inertia)` prevents whiplash. Default inertia is configured in `CONFIG.weights.inertia`.
- Intensity scaling: deltas are scaled by `1 + appraisal.intensity` so emalphatic inputs have larger impact.
- Stickiness: discrete emotions have a minimum duration (`CONFIG.decay.min_emotion_duration`) to avoid flicker; force-switches are allowed for high intensity or anger.

Personality & randomness
- Personality presets affect baseline valence/arousal, valence bias, arousal sensitivity, and style modifiers.
- Randomness engine introduces subtle, configurable variability (mood swings, style drift, response delays, typos). Use `RandomnessConfig` to tune behavior.

Configuration
- Single source of truth: `CONFIG` in `config.py`. Prefer adding new parameters there and wiring defaults via dataclasses.

## Development & Testing Guidance

Quick test commands
```bash
pytest tests/test_emotions.py -q
pytest tests/test_personality.py -q
```

Testing focus
- Unit tests should cover inertia blending, decay math, discrete mapping, and force-switch behavior. Use `pytest.approx()` for float comparisons.
- Add small deterministic tests for personality modifiers and randomness hooks (seed randomness where appropriate).
- Integration tests exist in the repo for personality and randomness; run them after changes that affect those modules.

Debugging tools
- Use the CLI commands `:state`, `:personality`, and `:randomness` to dump runtime state during manual testing.
- `EmotionState.as_dict()` and `Personality.as_dict()` are helpful for logging and assertions in tests.

## Contribution Notes (for Copilot-style assistants)

- When adding features, prefer small, focused changes and update `config.py` with new parameters and sensible defaults.
- Respect graceful degradation: do not add hard failures when optional external services are absent.
- Keep public module APIs stable where possible (e.g., `apply_delta`, `maybe_switch_discrete`, `appraise`, `generate_base`, `shape`).
- When modifying emotional dynamics, include unit tests for edge cases: high-intensity bursts, rapid succession inputs, and near-boundary valence/arousal values.

## Quick Start (developer)

1. Create a venv and install requirements from `requirements.txt`.
2. (Optional) export `OPENAI_API_KEY` to enable GPT responses.
3. Run `python main.py` to start the CLI and visualizer.

## Small checklist when editing behavior or emotion code

- Update or add config options in `config.py`.
- Add/adjust unit tests in `tests/` for the changed behavior.
- Run the CLI and use `:state` to validate runtime behavior under manual inputs.

---

If you need a shorter summary for a specific file or function, open that file and request a focused edit.
