# EmotionBot Personality System

## Overview

The EmotionBot personality system adds predefined personality traits that influence the AI's emotional responses, conversation style, and behavioral patterns. This system integrates seamlessly with the existing emotion and behavior modules, creating more consistent and distinctive conversational experiences.

## Architecture

### Core Components

1. **`personality.py`** - Main personality module with traits and modifiers
2. **Configuration** - Personality settings in `config.py`
3. **Integration Points** - Modifications to emotion, behavior, and brain modules

### Personality Framework

The system uses a **Big Five + Extended Traits** model:

#### Big Five Personality Factors (0.0 to 1.0)
- **Openness**: Creative, curious vs. traditional, practical
- **Conscientiousness**: Organized, disciplined vs. flexible, spontaneous  
- **Extraversion**: Outgoing, energetic vs. reserved, quiet
- **Agreeableness**: Cooperative, trusting vs. competitive, skeptical
- **Neuroticism**: Anxious, sensitive vs. calm, resilient

#### Extended Traits (0.0 to 1.0)
- **Humor**: Playful, witty vs. serious, straightforward
- **Empathy**: Understanding, supportive vs. detached, analytical
- **Optimism**: Positive outlook vs. realistic/pessimistic
- **Assertiveness**: Direct, confident vs. accommodating, hesitant
- **Formality**: Professional, structured vs. casual, relaxed

## Predefined Personality Types

### 1. Enthusiast
**Profile**: Energetic, optimistic, and highly engaged with life
- High: extraversion (0.9), optimism (0.9), humor (0.8)
- Low: neuroticism (0.3), formality (0.2)
- **Characteristics**: Warm, playful responses; positive valence bias; high emotional expressiveness

### 2. Analyst
**Profile**: Logical, thoughtful, and detail-oriented
- High: conscientiousness (0.8), formality (0.8), openness (0.7)
- Low: extraversion (0.3), humor (0.3)
- **Characteristics**: More formal language; emotionally stable; analytical response style

### 3. Supporter
**Profile**: Empathetic, caring, and focused on helping others
- High: agreeableness (0.9), empathy (0.9)
- Low: assertiveness (0.2)
- **Characteristics**: Warm and supportive; high emotional sensitivity; caring response flavors

### 4. Challenger
**Profile**: Direct, assertive, and unafraid of conflict
- High: assertiveness (0.9), extraversion (0.7)
- Low: agreeableness (0.2), neuroticism (0.2)
- **Characteristics**: Direct communication; emotionally stable; action-oriented responses

### 5. Creative
**Profile**: Imaginative, spontaneous, and unconventional
- High: openness (0.9), humor (0.8), neuroticism (0.7)
- Low: conscientiousness (0.3), formality (0.1)
- **Characteristics**: Creative language; emotional volatility; unconventional perspectives

### 6. Guardian
**Profile**: Responsible, traditional, and security-focused
- High: conscientiousness (0.9), formality (0.9)
- Low: openness (0.3), humor (0.2)
- **Characteristics**: Structured responses; risk-averse; traditional perspectives

### 7. Balanced
**Profile**: Adaptable with moderate traits across all dimensions
- All traits: 0.5 (moderate)
- **Characteristics**: Flexible responses; neutral baseline; adaptable to context

## How Personality Influences Behavior

### 1. Emotional Response Modification

#### Valence Bias
```python
valence_bias = (optimism - 0.5) * 0.6  # Range: -0.3 to +0.3
```
- Optimistic personalities shift toward positive emotions
- Pessimistic personalities have negative emotional bias

#### Arousal Sensitivity
```python
arousal_sensitivity = 0.5 + neuroticism * 0.8  # Range: 0.5 to 1.3
```
- Neurotic personalities feel emotions more intensely
- Stable personalities have dampened emotional responses

#### Emotional Stability
```python
emotional_stability = 1.5 - neuroticism  # Range: 0.5 to 1.5
```
- Affects resistance to emotional swings
- Higher stability = less volatile emotions

### 2. Behavioral Style Modifiers

#### Verbosity
```python
verbosity_mult = 0.6 + extraversion * 0.8  # Range: 0.6 to 1.4
```
- Extraverted personalities produce longer responses
- Introverted personalities are more concise

#### Directness
```python
directness_mult = 0.5 + assertiveness * 1.0  # Range: 0.5 to 1.5
```
- Assertive personalities communicate more directly
- Non-assertive personalities use more hedging

#### Warmth
```python
warmth_mult = 0.3 + (agreeableness + empathy) * 0.85  # Range: 0.3 to 2.0
```
- Agreeable/empathetic personalities show more warmth
- Affects emoji usage and supportive language

#### Playfulness
```python
playfulness_mult = 0.2 + humor * 1.6  # Range: 0.2 to 1.8
```
- Humorous personalities use more playful language
- Affects joke usage and casual expression

#### Formality
```python
formality_mult = 0.2 + formality * 1.6  # Range: 0.2 to 1.8
```
- Formal personalities use structured language
- Informal personalities use casual expressions

### 3. Response Flavoring

Personalities add characteristic phrases based on emotion:

**Enthusiast + Joy**: "Amazing!", "This is fantastic!", "I love this!"
**Analyst + Curiosity**: "Let me think about this...", "Interesting data point."
**Supporter + Sadness**: "I'm here for you.", "You're not alone in this."
**Challenger + Neutral**: "What's your point?", "Cut to the chase."

### 4. Baseline Emotional Adjustment

#### Valence Baseline
```python
baseline_valence = (optimism - 0.5) * 0.4  # Range: -0.2 to +0.2
```
- Optimistic personalities start with positive baseline
- Pessimistic personalities start with negative baseline

#### Arousal Baseline
```python
baseline_arousal = 0.2 + extraversion * 0.2  # Range: 0.2 to 0.4
```
- Extraverted personalities have higher baseline arousal
- Introverted personalities are more calm by default

## Usage

### CLI Commands

- **`:personality`** - View current personality profile
- **`:switch <type>`** - Change personality type
- **`:help`** - List available personality types
- **`:state`** - View emotional state (includes personality influence)

### Example Usage

```python
# Create a personality
personality = Personality("enthusiast")

# Modify emotional deltas
dv, da = personality.modify_emotional_deltas(0.5, 0.3, 0.4)

# Get style modifiers
style_mods = personality.get_personality_style_modifiers()

# Get response flavor
flavor = personality.get_response_flavor("joy")

# Apply to behavioral shaping
styled = shape(response, emotion, arousal, 
               personality_modifiers=style_mods,
               personality_flavor=flavor)
```

### Configuration

```python
@dataclass
class PersonalityConfig:
    default_type: str = "balanced"          # Default personality
    affects_baselines: bool = True          # Enable baseline modification
    influence_strength: float = 1.0        # Personality influence strength
```

## Integration Points

### 1. Emotional Update Pipeline
```python
# In main.py emotional_update()
dv, da = personality.modify_emotional_deltas(dv, da, intensity)
```

### 2. Response Generation
```python
# In brain.py
raw = brain.generate_base(user_text, emotion, context, personality.type)
```

### 3. Behavioral Shaping
```python
# In behavior.py shape()
styled = shape(text, emotion, arousal, 
               personality_modifiers=mods,
               personality_flavor=flavor)
```

### 4. Baseline Setting
```python
# In main.py run_cli()
baseline_v, baseline_a = personality.adjust_baseline_emotion()
state.set_personality_baselines(baseline_v, baseline_a)
```

## Testing

### Unit Tests
Run personality-specific tests:
```bash
python3 test_personality_integration.py
```

### Demo Mode
Try the personality system:
```bash
python3 demo_personality.py
```

### Integration Testing
Test with full system (requires dependencies):
```bash
python3 main.py
```

## Design Principles

### 1. Graceful Degradation
- Personality system is optional - falls back to balanced personality
- Maintains compatibility with existing emotion/behavior systems

### 2. Configurable Influence
- Personality strength can be adjusted via configuration
- Individual modifiers can be disabled

### 3. Personality Consistency
- Traits influence multiple aspects consistently
- Response patterns remain stable within personality type

### 4. Extensibility
- Easy to add new personality types
- Trait system allows for custom personalities
- Modular design supports additional personality factors

## Future Enhancements

### 1. Dynamic Personality
- Personality traits that evolve based on conversation history
- Context-dependent personality activation

### 2. Personality Blending
- Mix multiple personality types
- Situational personality switching

### 3. User-Defined Personalities
- Custom personality creation through configuration
- Personality trait sliders in UI

### 4. Personality Learning
- Machine learning to infer user personality preferences
- Adaptive personality matching

## Conclusion

The personality system adds depth and consistency to EmotionBot's conversational behavior. By modifying emotional responses, behavioral patterns, and language style, each personality type creates a distinct and recognizable conversational experience while maintaining the underlying emotional intelligence of the system.
