# EmotionBot — Emotionally-Driven Chatbot

EmotionBot is an emotionally-aware conversational AI that maintains a dynamic emotional state and lets that state influence every response. Built as a modular, self-contained system, it demonstrates how a small set of components can work together to create natural, emotionally intelligent conversations.

## ✨ Features

- **Real-time Emotion Tracking**: Tracks continuous valence (-1 to 1) and arousal (0 to 1) values
- **9 Discrete Emotions**: neutral, joy, sadness, anger, fear, surprise, disgust, curiosity, affection  
- **🎭 Personality System**: 7 distinct personality types that influence emotional responses and conversation style
- **Intelligent Appraisal**: Uses transformer models (sentiment analysis + GoEmotions) with graceful fallbacks
- **Adaptive Response Generation**: OpenAI GPT integration with local fallback system
- **Dynamic Style Adaptation**: Adjusts verbosity, directness, warmth, punctuation, and emoji usage
- **Live Visualization**: Real-time matplotlib plotting of emotional state evolution
- **Conversation Memory**: Maintains context and tracks discussion topics
- **Robust Configuration**: Easily tunable emotional dynamics and behavior parameters

---

## 🧠 How It Works

1. **Input Appraisal**: Transformer models (DistilBERT + GoEmotions) analyze user text for sentiment and discrete emotions, with neutral fallbacks when models are unavailable.

2. **Core Affect Update**: The system maintains continuous valence (negative↔positive) and arousal (calm↔excited) values. New inputs create deltas that are:
   - Scaled by input intensity for stronger impact from emphatic messages  
   - Dampened by configurable inertia to prevent emotional whiplash
   - Subject to exponential decay back toward baseline over time

3. **Discrete Emotion Selection**: Maps current (valence, arousal) coordinates to the nearest emotion in EMOTION_MAP using Euclidean distance, with minimum duration requirements to prevent flickering and force-switch capability for high-intensity inputs.

4. **Response Generation**: A "brain" module creates base responses using either:
   - **OpenAI GPT**: Emotion-aware system prompts with GPT-4o-mini (when `OPENAI_API_KEY` available)
   - **Local Heuristics**: Deterministic templates with emotion-specific response patterns

5. **Behavioral Styling**: The behavior module post-processes responses by adjusting:
   - Length based on verbosity and arousal levels
   - Directness (hedging vs. assertiveness) 
   - Warmth markers and emoji probability
   - Punctuation patterns and hesitation markers

The conversation history is stored in `ConversationMemory` which provides context windows to the brain module and tracks discussion topics over time.

---

## 🏗️ Architecture

EmotionBot follows a clean, modular architecture where the CLI orchestrates specialized components:

```
user input
     │
     ▼
 appraise() ────────────────┐
     │ sentiment/intensity  │
     ▼                     │
EmotionState ← decay ──────┘
     │ current emotion
     ▼
Brain.generate_base() ── Memory.recent_context()
     │ base reply
     ▼
behavior.shape()
     │
 styled reply
```

### 📦 Core Modules

- **`main.py`**: CLI orchestration and the `emotional_update()` pipeline. Handles decay, appraisal integration, core affect updates, and discrete emotion selection.

- **`emotions.py`**: Defines `EmotionState` dataclass with exponential decay, inertia-dampened updates, and the `EMOTION_MAP` for discrete emotion selection based on (valence, arousal) coordinates.

- **`personality.py`**: 🎭 **NEW** Personality system with 7 distinct types (enthusiast, analyst, supporter, challenger, creative, guardian, balanced). Modifies emotional responses, behavioral patterns, and conversation style.

- **`nlp.py`**: NLP processing with transformer models. Wraps DistilBERT sentiment analysis and GoEmotions classification, returning `Appraisal` objects with graceful fallbacks when models are missing.

- **`memory.py`**: Conversation storage and context management. Maintains transcript history, provides context windows for response generation, and tracks topic frequency.

- **`brain.py`**: Response generation engine. Integrates OpenAI Chat Completions with sophisticated emotion-aware prompting, falling back to template-based local generation when needed.

- **`behavior.py`**: Post-processing for emotional styling. Applies emotion-specific adjustments to length, hedging, punctuation, emoji usage, and conversational markers.

- **`telemetry.py`**: Real-time visualization with matplotlib. Plots valence/arousal evolution over time with discrete emotion annotations.

- **`config.py`**: Centralized configuration for decay constants, emotion weights, OpenAI settings, and behavioral parameters.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

```bash
# Clone the repository (if applicable)
cd emotion-bot

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Optional: Enable OpenAI responses
# Set your API key: set OPENAI_API_KEY=your_key_here (Windows)
# Or: export OPENAI_API_KEY=your_key_here (macOS/Linux)
```

### Running the Bot

```bash
python main.py
```

The bot will start with a matplotlib window showing real-time emotional state visualization.

---

## 💬 Using the CLI

### Basic Interaction
Simply type messages and press Enter to chat with the bot. The emotional state will evolve based on the conversation.

### Special Commands
- **`:state`** - Display current valence, arousal, and discrete emotion
- **`:personality`** - 🎭 View current personality profile and traits
- **`:switch <type>`** - 🎭 Change personality (enthusiast, analyst, supporter, challenger, creative, guardian, balanced)
- **`:quit`** or **`:q`** - Exit the conversation gracefully
- **`Ctrl+C`** - Force quit

### Visualization
A matplotlib window displays:
- **Blue line**: Valence over time (-1 to 1)
- **Orange line**: Arousal over time (0 to 1)
- **Title**: Current discrete emotion
- **Info box**: Detailed emotional state metrics

### 🎭 Personality Types

Choose from 7 distinct personality types that influence conversation style:

- **Enthusiast**: Energetic, optimistic, and highly expressive
- **Analyst**: Logical, formal, and detail-oriented  
- **Supporter**: Empathetic, caring, and emotionally supportive
- **Challenger**: Direct, assertive, and action-oriented
- **Creative**: Imaginative, playful, and unconventional
- **Guardian**: Responsible, traditional, and security-focused
- **Balanced**: Moderate traits across all dimensions (default)

Each personality affects emotional sensitivity, response style, baseline mood, and conversation patterns.

---

## ⚙️ Configuration

All settings are centralized in `emotional_core/config.py` and organized into logical groups:

### DecayConfig
- **`valence_half_life`** (900s): How quickly positive/negative feelings fade
- **`arousal_half_life`** (600s): How quickly excitement/calm states decay  
- **`min_emotion_duration`** (45s): Minimum time before switching discrete emotions

### EmotionWeights
- **`sentiment_to_valence`** (0.8): Impact strength of sentiment analysis
- **`intensity_to_arousal`** (0.9): Impact strength of input intensity
- **`inertia`** (0.6): Resistance to sudden emotional changes (0-1)

### BehaviorConfig
- **`base_max_tokens`** (140): Base response length before emotional scaling
- **`emoji_baseline`** (0.15): Base probability of emoji usage

### OpenAIConfig  
- **`model`** (gpt-4o-mini): OpenAI model for response generation
- **`temperature`** (0.7): Creativity/randomness of responses
- **`max_tokens`** (220): Maximum response length

### PersonalityConfig 🎭
- **`default_type`** (balanced): Default personality on startup
- **`affects_baselines`** (True): Whether personality influences emotional baselines
- **`influence_strength`** (1.0): Overall strength of personality effects (0.0-1.0)

---

## 🧪 Development & Testing

### Running Tests
The project includes test suites for both emotion and personality systems:

```bash
# Test personality system integration (no dependencies required)
python3 test_personality_integration.py

# Demo the personality system
python3 demo_personality.py

# Install pytest for full test suite
pip install pytest

# Run tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_emotions.py
```

### Test Coverage
Current tests focus on:
- Inertia-dampened emotion updates
- Force-switch override mechanics for high-intensity inputs
- Discrete emotion selection logic

### Development Setup
The modular architecture makes it easy to extend or modify components:

1. **Adding new emotions**: Update `EMOTION_MAP` in `emotions.py` and `STYLE_PRESETS` in `behavior.py`
2. **Customizing NLP**: Modify model selection or add new transformers in `nlp.py`  
3. **Extending behaviors**: Add new style parameters and processing logic in `behavior.py`
4. **New response modes**: Extend the `Brain` class with additional generation strategies

---

## 📈 Emotional Model Details

### Core Affect Theory
EmotionBot implements a computational model based on Russell's Circumplex Model of Affect:
- **Valence**: Pleasant ↔ Unpleasant dimension (-1 to 1)
- **Arousal**: Low ↔ High activation dimension (0 to 1)

### Discrete Emotions Mapping
Each emotion maps to typical (valence, arousal) coordinates:

| Emotion   | Valence | Arousal | Characteristics |
|-----------|---------|---------|-----------------|
| joy       | +0.7    | 0.6     | Happy, enthusiastic |
| sadness   | -0.7    | 0.3     | Melancholic, subdued |
| anger     | -0.6    | 0.8     | Hostile, energetic |
| fear      | -0.8    | 0.7     | Anxious, vigilant |
| surprise  | +0.2    | 0.9     | Startled, alert |
| disgust   | -0.6    | 0.5     | Repulsed, withdrawn |
| curiosity | +0.2    | 0.5     | Inquisitive, engaged |
| affection | +0.6    | 0.4     | Warm, caring |
| neutral   | 0.0     | 0.2     | Baseline, calm |

### Dynamic Behavior
- **Exponential Decay**: Emotions naturally return to baseline over time
- **Inertia Dampening**: Prevents unrealistic emotional whiplash
- **Intensity Scaling**: Stronger inputs create proportionally larger changes
- **Force Switching**: High-intensity or anger inputs can immediately override minimum duration rules

---

## 🔧 Troubleshooting

### Common Issues

**Q: The bot responses are generic/not emotional**
- Ensure transformer models are properly installed: `pip install transformers torch`
- Check if OPENAI_API_KEY is set for more sophisticated responses
- Verify emotional state is changing with `:state` command

**Q: Matplotlib window doesn't appear**
- Install GUI backend: `pip install PyQt5` or similar
- On headless systems, the bot will still work without visualization

**Q: Import errors with transformers**
- Ensure all requirements are installed: `pip install -r requirements.txt`
- The system gracefully degrades to neutral appraisals if transformers is missing

**Q: OpenAI responses not working**
- Verify `OPENAI_API_KEY` environment variable is set
- Check API key has sufficient credits
- The system falls back to local responses automatically

---

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

This is a reference implementation designed to demonstrate emotionally-aware conversational AI concepts. While primarily educational, contributions that improve the core emotion modeling, add new behavioral patterns, or enhance the visualization are welcome.

### Areas for Enhancement
- Additional discrete emotions and behavioral patterns
- More sophisticated NLP processing pipelines  
- Enhanced memory and context management
- Alternative visualization modes
- Performance optimizations for real-time applications
