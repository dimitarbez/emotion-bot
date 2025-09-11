# EmotionBot Personality System - Usage Examples

This document provides practical examples of how the personality system affects conversations.

## Quick Demo

To see the personality system in action:

```bash
# Run the demo (no dependencies required)
python3 demo_personality.py

# Or run the full system (requires dependencies)
python3 main.py
```

## Example Conversations

### Same Input, Different Personalities

**User Input**: "I'm really excited about this new project!"

#### Enthusiast Response:
```
💭 Processing with personality influence...
bot> [joy] Amazing! I'm so excited about this! This is fantastic! ✨
```

#### Analyst Response:
```
💭 Processing with personality influence...
bot> [joy] That's a positive development. I see the benefits in this approach.
```

#### Supporter Response:
```
💭 Processing with personality influence...
bot> [joy] I'm so happy for you! You deserve this happiness! That's wonderful news! ❤️
```

#### Challenger Response:
```
💭 Processing with personality influence...
bot> [joy] Great! Now what's next? Let's keep pushing forward!
```

### Personality-Influenced Emotional Responses

**User Input**: "I'm feeling really down today"

#### Supporter (High Empathy):
```
💭 Processing with personality influence...
bot> [sadness] I'm here for you. You're not alone in this. That sounds really hard.
```

#### Analyst (Lower Emotional Expression):
```
💭 Processing with personality influence...
bot> [sadness] I see the challenges here. Let's analyze the situation. Data suggests this is temporary.
```

#### Creative (Imaginative Perspective):
```
💭 Processing with personality influence...
bot> [sadness] Every ending is a new beginning. What's the hidden opportunity here?
```

## CLI Commands Demo

### Viewing Personality Details

```bash
you> :personality
bot> 🎭 Personality Profile:
  Type: enthusiast
  Key Traits: {'openness': 0.8, 'conscientiousness': 0.4, 'extraversion': 0.9, 'agreeableness': 0.7, 'neuroticism': 0.3, 'humor': 0.8, 'empathy': 0.7, 'optimism': 0.9, 'assertiveness': 0.7, 'formality': 0.2}
  Modifiers: {'valence_bias': 0.24, 'arousal_sensitivity': 0.74, 'emotional_stability': 1.2}
```

### Switching Personalities

```bash
you> :switch challenger
bot> 🔄 Switched to challenger personality!

you> :help
bot> 📚 Available personalities: enthusiast, analyst, supporter, challenger, creative, guardian, balanced
  • enthusiast: energetic and optimistic
  • analyst: logical and detail-oriented
  • supporter: empathetic and caring
  • challenger: direct and assertive
  • creative: imaginative and unconventional
  • guardian: responsible and traditional
  • balanced: moderate across all traits
```

### Emotional State with Personality Influence

```bash
you> :state
bot> 🧠 Emotional State: {'valence': 0.163, 'arousal': 0.381, 'emotion': 'joy', 'since': 12.4}
```

*Note: The enthusiast personality has positive valence bias (0.24) affecting the baseline emotion*

## Personality Trait Effects

### Extraversion Impact

**High Extraversion (Enthusiast)**: Longer, more expressive responses
```
you> How was your day?
bot> [neutral] Interesting! Tell me more! It's been quite the adventure - so many fascinating conversations and ideas bouncing around! ✨
```

**Low Extraversion (Analyst)**: Shorter, more reserved responses  
```
you> How was your day?
bot> [neutral] I understand. Let me process this.
```

### Optimism Bias

**High Optimism (Enthusiast)**: Positive emotional baseline
- Baseline valence: +0.16 (starts slightly positive)
- Responds more positively to neutral inputs

**Low Optimism (Challenger)**: Realistic/slightly negative baseline
- Baseline valence: -0.04 (starts slightly negative)  
- More skeptical responses

### Empathy Influence

**High Empathy (Supporter)**: Warmth multiplier of 1.8
```
you> I failed my exam
bot> [sadness] I'm here for you. That sounds really hard. You're stronger than you know. 💙
```

**Low Empathy (Challenger)**: Warmth multiplier of 0.7
```
you> I failed my exam  
bot> [neutral] Time to take action. What's your next move?
```

## Configuration Examples

### Adjusting Personality Influence

In `emotional_core/config.py`:

```python
@dataclass
class PersonalityConfig:
    default_type: str = "enthusiast"        # Start with enthusiast
    affects_baselines: bool = True          # Enable baseline modification
    influence_strength: float = 0.8        # Reduce personality influence to 80%
```

### Custom Personality Traits

```python
# In personality.py - add custom personality
PERSONALITY_PRESETS["custom"] = PersonalityTraits(
    openness=0.9,           # Very creative
    conscientiousness=0.8,  # Highly organized  
    extraversion=0.3,       # Introverted
    agreeableness=0.9,      # Very cooperative
    neuroticism=0.2,        # Emotionally stable
    humor=0.6,              # Moderate humor
    empathy=0.9,            # Highly empathetic
    optimism=0.7,           # Generally positive
    assertiveness=0.4,      # Somewhat passive
    formality=0.3           # Casual communication
)
```

## Technical Integration

### Emotional Delta Modification

```python
# Example: Enthusiast modifying emotional response
original_valence_delta = 0.5
original_arousal_delta = 0.3

modified_dv, modified_da = enthusiast.modify_emotional_deltas(
    original_valence_delta, 
    original_arousal_delta, 
    intensity=0.4
)

# Result: 
# modified_dv = 0.477 (boosted by positive valence bias)
# modified_da = 0.185 (dampened by emotional stability)
```

### Style Modification

```python
# Get personality style modifiers
modifiers = personality.get_personality_style_modifiers()
# {'warmth': 1.5, 'playfulness': 1.5, 'directness': 1.2, ...}

# Apply to behavioral shaping
styled_response = shape(
    "That's interesting",
    emotion="joy",
    arousal=0.6,
    base_max_tokens=100,
    emoji_baseline=0.15,
    personality_modifiers=modifiers,
    personality_flavor="Amazing!"
)
# Result: "Amazing! That's interesting! ✨"
```

## Best Practices

### 1. Choose Appropriate Personalities for Context
- **Enthusiast**: Social conversations, brainstorming, positive interactions
- **Analyst**: Technical discussions, problem-solving, data analysis
- **Supporter**: Emotional support, counseling, empathetic listening
- **Challenger**: Debates, motivation, decision-making
- **Creative**: Brainstorming, artistic discussions, innovation
- **Guardian**: Planning, risk assessment, structured tasks

### 2. Monitor Emotional State Changes
Use `:state` to see how personality affects emotional baselines and responses.

### 3. Experiment with Switching
Try the same conversation with different personalities to see the impact:
```bash
:switch enthusiast
# Have a conversation
:switch analyst  
# Continue the same conversation topic
```

### 4. Adjust Configuration
Fine-tune personality influence through configuration settings based on your use case.

## Troubleshooting

### Personality Not Switching
- Ensure the personality name is spelled correctly
- Use `:help` to see available personalities
- Check configuration settings

### Minimal Personality Effect
- Verify `influence_strength` is not set too low
- Check that `affects_baselines` is enabled
- Some effects are subtle and emerge over longer conversations

### Unexpected Responses
- Remember that personality works alongside emotion system
- Current emotional state affects personality expression
- Use `:state` and `:personality` to debug current system state
