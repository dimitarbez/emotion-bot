
# EmoBot — Emotionally‑Driven Chatbot (Python)

EmoBot is a self‑contained chatbot that keeps track of an evolving emotional
state and lets that state influence every reply.  It is primarily meant as a
reference implementation showing how a small set of modules can work together
to create an emotion‑aware conversational agent.

---

## How It Works

1. **User input is appraised.**  Transformer models infer sentiment and a
   coarse discrete emotion from the text.  When the `transformers` library is
   unavailable the appraisal gracefully falls back to neutral values.
2. **Core affect is updated.**  The bot tracks *valence* (‑1..1) and *arousal*
   (0..1).  Appraisal results nudge these numbers, while inertia dampens sudden
   swings and exponential decay slowly drifts the values back to a baseline.
3. **Discrete emotion is chosen.**  The closest match in `EMOTION_MAP` is
   selected, subject to a minimum duration to avoid flicker.  Intense or angry
   messages can force an immediate switch.
4. **Response is generated.**  A small “brain” module produces a base reply –
   either using OpenAI (if `openai` and `OPENAI_API_KEY` are available) or a
   lightweight local heuristic.
5. **Style shaping.**  The `behavior` module tweaks length, punctuation,
   hedging, and emoji usage so the final reply reflects the current emotion.

The conversation history is stored in `ConversationMemory`.  It provides short
context windows to the brain module and tracks rough topics discussed so far.

---

## Architecture

EmoBot is intentionally modular. The CLI orchestrates a handful of small
components housed in the `emotional_core` package:

```
user text
   │
   ▼
appraise() ─────────────┐
   │ sentiment/intensity │
   ▼                    │
EmotionState <─ decay ──┘
   │ current emotion
   ▼
Brain.generate_base() ── Memory.recent_context()
   │ base reply
   ▼
behavior.shape()
   │
styled reply
```

* `main.py` hosts the CLI loop and the `emotional_update` helper. For every user
  utterance it decays the previous state, calls `appraise`, nudges valence and
  arousal, chooses a discrete emotion and then feeds the result into the other
  modules.
* **`emotions.py`** – defines the `EmotionState` dataclass, exponential decay,
  inertia‑blended updates and the `EMOTION_MAP` used to select discrete
  categories.
* **`nlp.py`** – wraps transformer sentiment and GoEmotions classifiers. It
  returns an `Appraisal` object with sentiment, intensity and an optional emotion
  hint, falling back to neutral scores if models are missing.
* **`memory.py`** – stores the running transcript, provides short context windows
  for the brain and tracks rough topic frequency.
* **`brain.py`** – generates a base reply. It can call OpenAI Chat Completions or
  fall back to a deterministic template system depending on availability.
* **`behavior.py`** – adjusts length, hedging, punctuation and emoji usage so the
  final output mirrors the current emotion and arousal level.
* **`telemetry.py`** – renders a Matplotlib plot of valence, arousal and the
  active emotion as the conversation progresses.
* **`config.py`** – central location for decay constants, OpenAI settings and
  behavior parameters.

---

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install matplotlib transformers torch
# Optional: enable OpenAI responses
# pip install openai>=1.0.0
python main.py
```

Set `OPENAI_API_KEY` in your environment to enable LLM‑based replies.  Without
it the deterministic local generator is used instead.

---

## Using the CLI

Run `python main.py` and chat.  Special commands:

* `:state` – show the current valence, arousal and discrete emotion.
* `:quit` or `:q` – exit the conversation.

A Matplotlib window plots valence and arousal over time and annotates the
current emotion.  The plot updates in realtime as you converse with the bot.

---

## Configuration

All adjustable knobs live in `emotional_core/config.py` and are loaded into the
`CONFIG` object.  Notable groups:

* **DecayConfig** – half‑lives for valence/arousal and the minimum duration to
  keep a discrete emotion.
* **EmotionWeights** – how strongly sentiment and intensity affect core affect
  plus the inertia factor.
* **BehaviorConfig** – response length and emoji baseline used by the styler.
* **OpenAIConfig** – model, temperature and token limit for OpenAI replies.

---

## Development

The repository includes a small test suite for the emotion logic:

```bash
pytest
```

---

## License

MIT
