
# EmoBot — Emotionally-Driven Chatbot (Python)

EmoBot is a self-contained Python chatbot that maintains *emotional state* (valence/arousal + discrete mood), 
updates that state from user input, and lets emotions influence its behavior, tone, and response decisions.

## Highlights
- Core Affect model: **valence [-1..1]** and **arousal [0..1]**
- Discrete emotions mapped from core affect: `neutral, joy, sadness, anger, fear, surprise, disgust, curiosity, affection`
- **Decay + stickiness**: emotions fade over time with configurable half-lives and minimum durations
- **Appraisal** of user input via lexicon-based sentiment + emotion triggers (no external APIs)
- Behavior control: wording, punctuation, emoji use, length, directness — all based on emotion
- Pluggable "brain": simple local generator + optional OpenAI integration via `OPENAI_API_KEY` (if installed)
- Conversation memory with topic tracking
- CLI chat loop
- Realtime telemetry plot of valence and arousal (Matplotlib)

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install matplotlib
# Optional if you want OpenAI responses:
# pip install openai>=1.0.0
python main.py
```

If you set `OPENAI_API_KEY` in your environment and have `openai` installed, the bot will use the LLM for base replies. 
Otherwise it falls back to the local generator.

## Files
- `config.py` — tunable parameters
- `emotions.py` — core affect, discrete emotion mapping, decay, stickiness
- `nlp.py` — sentiment/emotion keyword appraisal
- `behavior.py` — style shaping from emotions
- `memory.py` — conversation memory & topic tracking
- `brain.py` — base reply generator (local + optional OpenAI)
- `main.py` — CLI runner

## Example
Run `python main.py` and chat. A Matplotlib window will chart valence and arousal over time.
Type `:state` to peek at the current emotional state; `:quit` to exit.

## License
MIT
