# EmotionBot contributor guide

This repository owns emotional-domain logic. ROS contracts, Gazebo behavior, and robot actuation belong in the sibling maintained Lite3 fork, not here.

## Supported integration API

- `emotional_core.engine.EmotionEngine` is the supported headless integration boundary. It must import without a GUI, microphone, API key, model download, ROS installation, or network access.
- `EmotionEngine` owns one session's appraisal, state, personality, memory, local response shaping, and optional seeded randomness.
- Keep valence within `[-1, 1]`, arousal within `[0, 1]`, and categorical output to the nine keys in `EMOTION_MAP`.
- The deterministic backend and exact `event:<emotion>` inputs are test and ROS integration contracts. Preserve their repeatability and explicit error behavior.
- `main.py` remains the interactive CLI/plotting application. Do not make downstream integrations automate it through stdin, and do not move plotting or startup key checks into the headless engine.

## Architecture and changes

- Shared reusable code lives under `emotional_core/`; keep imports free of heavyweight runtime side effects.
- `engine.py` orchestrates the reusable path. When changing appraisal/update behavior, test rapid category replacement, neutral handling, force switching, bounds, seeded repeatability, and all nine exact events.
- `nlp.py` must lazy-load optional transformer models and degrade explicitly to deterministic or neutral behavior. Tests must patch models/network rather than download them.
- `brain.py` may use OpenAI for the standalone CLI, but API failures must retain a local fallback. The ROS integration's live OpenAI sidecar is intentionally outside this repository.
- `config.py` owns standalone defaults. Avoid scattered tuning constants when an existing configuration group fits.
- Preserve public APIs used by the ROS adapter: `EmotionEngine`, `EngineResult`, `EmotionState`, and `EMOTION_MAP`.
- Do not add ROS, Gazebo, controller, UDP, or physical-robot dependencies to this repository.
- Physical hardware consumes the same versioned emotional result through the outer ROS adapter and validated uplink. Do not encode robot choreography, contact logic, commissioning state, or actuator fallbacks in the emotional engine.

## Dependencies and secrets

- `requirements.txt` is the full standalone runtime and is newer than ROS Noetic's Python 3.8 environment. Do not install it wholesale into the ROS image.
- Development-only test dependencies belong in `requirements-dev.txt`.
- Never commit `.env`, API keys, model caches, generated plots, virtual environments, or downloaded weights.
- Tests must not require a paid API call, secret, GUI, microphone, physical robot, or internet access.

## Documentation

- `README.md` is the English user guide and `README.mkd` is its Macedonian counterpart. Keep shared behavior, setup, commands, configuration, and architecture changes aligned across both.
- `PERSONALITY_SYSTEM.md` and `PERSONALITY_EXAMPLES.md` own detailed personality documentation.
- `.github/copilot-instructions.md` is older contributor context. Checked-out code and this file take precedence where it still describes the pre-headless `main.py` path as the sole integration flow.
- Preserve the GPL-3.0 license and attribution. Review compatibility before code is copied or vendored elsewhere.

## Verification

For focused domain changes, run the smallest affected tests and then the full local suite when dependencies are available:

```bash
python3 -m pytest -q
```

From the parent workspace, the compatible integration path is:

```bash
make -C lite3-noetic emotion-unit-tests
```

That wrapper target exercises the EmotionBot tests against the ROS package without installing the full standalone dependency set into Noetic. Report which environment and command were actually used.
