# EmotionBot AI Coding Guidelines

## Architecture Overview

EmotionBot implements Russell's Circumplex Model with a **5-stage pipeline** in `main.py:emotional_update()`:
1. **Decay** → baseline drift using exponential half-lives
2. **Appraisal** → NLP analysis (DistilBERT + GoEmotions) 
3. **Core Affect Update** → continuous valence/arousal with inertia dampening
4. **Discrete Mapping** → (valence, arousal) → closest emotion in `EMOTION_MAP`
5. **Stickiness Check** → minimum duration + force-switch logic

**Data Flow**: `user input` → `nlp.appraise()` → `EmotionState.apply_delta()` → `Brain.generate_base()` → `behavior.shape()` → `styled response`

## Key Design Patterns

### Graceful Degradation
- `nlp.py` returns neutral `Appraisal(0.0, 0.0, None)` when transformers unavailable
- `brain.py` falls back to local templates when OpenAI API missing
- Use try/except with `_HAS_OPENAI` pattern for optional dependencies

### Emotion State Management
- **Inertia dampening**: `apply_delta(dv, da, inertia=0.6)` prevents whiplash
- **Force switching**: High intensity (>0.7) or anger bypasses `min_emotion_duration`
- **Intensity scaling**: Emphatic inputs get `intensity_factor = 1 + a.intensity` multiplier

### Configuration Architecture
Centralized in `config.py` with dataclass hierarchy:
- `DecayConfig` → half-lives, duration thresholds
- `EmotionWeights` → impact scaling, inertia
- `BehaviorConfig` → response shaping parameters
- Access via `CONFIG.weights.inertia`, `CONFIG.decay.valence_half_life`

## Development Workflows

### Testing Emotion Logic
```bash
pytest tests/test_emotions.py -v
```
Focus on inertia mechanics and force-switch overrides. Emotion tests use `pytest.approx()` for float comparisons.

### Debug Emotional State
Use `:state` CLI command or check `EmotionState.as_dict()` for current (valence, arousal, emotion, duration).

### Adding New Emotions
1. Update `emotions.py:EMOTION_MAP` with (valence, arousal) coordinates
2. Add style preset in `behavior.py:STYLE_PRESETS`
3. Optional: Add emoji set in `behavior.py:EMOJIS`
4. Consider discrete hints in `main.py:emotional_update()` nudges

### NLP Model Integration
- Models are lazy-loaded with `@lru_cache()` decorators
- Map external labels via `nlp.py:_EMO_MAP` dictionary
- Return `Appraisal(sentiment, intensity, discrete_hint)` from `appraise()`

## Critical Implementation Details

### Behavioral Styling Chain
`behavior.shape()` applies emotion-specific transformations:
- Length scaling by `verbosity * arousal`
- Hedging injection based on `directness < 0.6`
- Emoji probability: `emoji_baseline * warmth * arousal * style.emoji_prob`
- Punctuation: `style.punctuation > 0.7` adds exclamation marks

### Memory Context Windows
`ConversationMemory.recent_context(limit=6)` provides conversation history to brain module.

### CLI Special Commands
- `:state` → emotional diagnostics
- `:quit`/`:q` → graceful exit
- Debug prints show transformer analysis results

When modifying emotional dynamics, always test with edge cases like high-intensity inputs and rapid emotion switches to ensure inertia and force-switch logic work correctly.
