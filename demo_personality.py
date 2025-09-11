#!/usr/bin/env python3
"""
Minimal EmotionBot demo with personality system
This version works without external dependencies (OpenAI, transformers, etc.)
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from emotional_core.config import CONFIG
from emotional_core.emotions import EmotionState
from emotional_core.behavior import shape
from emotional_core.memory import ConversationMemory
from emotional_core.personality import Personality, get_available_personalities

# Simple mock NLP analysis (replaces the transformer-based one)
class MockAppraisal:
    def __init__(self, sentiment, intensity, discrete_hint=None):
        self.sentiment = sentiment
        self.intensity = intensity
        self.discrete_hint = discrete_hint

def mock_appraise(text):
    """Simple mock NLP analysis based on keywords."""
    text_lower = text.lower()
    
    # Sentiment analysis
    positive_words = ["good", "great", "awesome", "love", "happy", "excellent", "wonderful", "amazing"]
    negative_words = ["bad", "terrible", "hate", "sad", "awful", "horrible", "disappointing", "angry"]
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        sentiment = min(0.8, pos_count * 0.3)
    elif neg_count > pos_count:
        sentiment = max(-0.8, -neg_count * 0.3)
    else:
        sentiment = 0.0
    
    # Intensity analysis
    intensity_markers = ["!", "?", "very", "really", "extremely", "totally", "absolutely"]
    intensity = min(0.8, sum(0.2 for marker in intensity_markers if marker in text_lower))
    
    # Discrete emotion hints
    discrete_hint = None
    if any(word in text_lower for word in ["angry", "mad", "furious"]):
        discrete_hint = "anger"
    elif any(word in text_lower for word in ["sad", "depressed", "down"]):
        discrete_hint = "sadness"
    elif any(word in text_lower for word in ["scared", "afraid", "worried"]):
        discrete_hint = "fear"
    elif any(word in text_lower for word in ["happy", "joy", "excited"]):
        discrete_hint = "joy"
    elif any(word in text_lower for word in ["curious", "wonder", "interesting"]):
        discrete_hint = "curiosity"
    
    return MockAppraisal(sentiment, intensity, discrete_hint)

def emotional_update(state: EmotionState, user_text: str, personality: Personality) -> EmotionState:
    """Update emotional state based on user input and personality."""
    now = time.time()
    
    # 1) decay
    state.decay_toward_baseline(
        dt=1.0,  # assume ~1s between steps in CLI
        valence_half_life=CONFIG.decay.valence_half_life,
        arousal_half_life=CONFIG.decay.arousal_half_life,
    )
    
    # 2) appraisal (using mock NLP)
    a = mock_appraise(user_text)
    
    # Scale deltas by input intensity
    intensity_factor = 1 + a.intensity
    dv = a.sentiment * CONFIG.weights.sentiment_to_valence * intensity_factor
    da = a.intensity * CONFIG.weights.intensity_to_arousal
    
    # Apply personality modifications to emotional deltas
    dv, da = personality.modify_emotional_deltas(dv, da, a.intensity)
    
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
    elif a.discrete_hint == "joy":
        dv += 0.3 * mult
        da += 0.05 * mult
    elif a.discrete_hint == "curiosity":
        da += 0.1 * mult
    
    # 3) inertia-blended delta
    state.apply_delta(dv, da, inertia=CONFIG.weights.inertia)
    
    # 4) discrete selection with stickiness
    force_switch = a.discrete_hint == "anger" or a.intensity > 0.7
    state.maybe_switch_discrete(now, CONFIG.decay.min_emotion_duration, force=force_switch)
    
    return state

def generate_simple_response(user_text: str, emotion: str, personality_type: str) -> str:
    """Generate a simple response without OpenAI."""
    responses = {
        "enthusiast": {
            "joy": ["That's absolutely amazing!", "I'm so excited about this!", "This is fantastic!"],
            "neutral": ["Interesting!", "Tell me more!", "That's cool!"],
            "sadness": ["I'm here for you!", "That sounds tough, but we'll get through it!", "Sending positive vibes!"],
        },
        "analyst": {
            "joy": ["That's a positive development.", "Interesting data point.", "I see the benefits."],
            "neutral": ["I understand.", "Let me process this.", "That makes logical sense."],
            "sadness": ["I see the challenges here.", "Let's analyze the situation.", "Data suggests this is temporary."],
        },
        "supporter": {
            "joy": ["I'm so happy for you!", "You deserve this happiness!", "That's wonderful news!"],
            "neutral": ["I'm listening.", "Tell me how you feel.", "I'm here to support you."],
            "sadness": ["I'm here for you.", "You're not alone in this.", "That sounds really hard."],
        },
        "challenger": {
            "joy": ["Great! Now what's next?", "Time to build on this!", "Let's keep pushing forward!"],
            "neutral": ["What's your point?", "Cut to the chase.", "Let's be direct here."],
            "sadness": ["Time to take action.", "We need to address this.", "No giving up!"],
        },
        "creative": {
            "joy": ["This sparks so many ideas!", "The possibilities are endless!", "What if we explored this further?"],
            "neutral": ["There's a story here...", "This reminds me of something...", "What patterns do you see?"],
            "sadness": ["Every ending is a new beginning.", "Let's reimagine this situation.", "What's the hidden opportunity?"],
        },
        "guardian": {
            "joy": ["That's good progress.", "Following the right path.", "Steady as she goes."],
            "neutral": ["Let's stick to what works.", "Following protocol here.", "Tried and true approach."],
            "sadness": ["We'll get through this together.", "Let's focus on stability.", "One step at a time."],
        }
    }
    
    personality_responses = responses.get(personality_type, responses["analyst"])
    emotion_responses = personality_responses.get(emotion, personality_responses["neutral"])
    
    import random
    return random.choice(emotion_responses)

def run_demo():
    """Run the personality demo."""
    print("🤖 EmotionBot Personality Demo")
    print("=" * 50)
    print("This is a simplified demo showcasing the personality system.")
    print("Type ':state' to view emotional state")
    print("Type ':personality' to view personality details")
    print("Type ':switch <type>' to change personality")
    print("Type ':help' for available personalities")
    print("Type ':quit' to exit\n")
    
    # Initialize personality system
    personality = Personality(CONFIG.personality.default_type)
    print(f"🎭 Current personality: {personality.type}")
    available_personalities = get_available_personalities()
    
    # Initialize emotion state with personality-influenced baselines
    state = EmotionState()
    if CONFIG.personality.affects_baselines:
        baseline_v, baseline_a = personality.adjust_baseline_emotion()
        state.set_personality_baselines(baseline_v, baseline_a)
        state.valence = baseline_v
        state.arousal = baseline_a
    
    memory = ConversationMemory()
    
    try:
        while True:
            try:
                user = input("\nyou> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break
                
            if user == "":
                continue
                
            if user.lower() in {":quit", ":q", "exit"}:
                print("bot> Take care! 👋")
                break
                
            if user.lower() == ":state":
                state_info = state.as_dict()
                print(f"bot> 🧠 Emotional State: {state_info}")
                continue
                
            if user.lower() == ":personality":
                personality_info = personality.as_dict()
                print("bot> 🎭 Personality Profile:")
                print(f"  Type: {personality_info['type']}")
                print(f"  Key Traits: {personality_info['traits']}")
                print(f"  Modifiers: {personality_info['modifiers']}")
                continue
                
            if user.lower() == ":help":
                print(f"bot> 📚 Available personalities: {', '.join(available_personalities)}")
                print("  • enthusiast: energetic and optimistic")
                print("  • analyst: logical and detail-oriented") 
                print("  • supporter: empathetic and caring")
                print("  • challenger: direct and assertive")
                print("  • creative: imaginative and unconventional")
                print("  • guardian: responsible and traditional")
                print("  • balanced: moderate across all traits")
                continue
                
            if user.lower().startswith(":switch "):
                new_personality = user[8:].strip()
                if new_personality in available_personalities:
                    personality = Personality(new_personality)
                    print(f"bot> 🔄 Switched to {new_personality} personality!")
                    
                    # Update baselines if enabled
                    if CONFIG.personality.affects_baselines:
                        baseline_v, baseline_a = personality.adjust_baseline_emotion()
                        state.set_personality_baselines(baseline_v, baseline_a)
                else:
                    print(f"bot> ❌ Unknown personality. Available: {', '.join(available_personalities)}")
                continue
            
            # Update emotion with personality influence
            print("💭 Processing with personality influence...")
            state = emotional_update(state, user, personality)
            
            # Generate response
            memory.add("user", user)
            raw_response = generate_simple_response(user, state.current_emotion, personality.type)
            
            # Get personality-based style modifiers and flavor
            style_modifiers = personality.get_personality_style_modifiers()
            personality_flavor = personality.get_response_flavor(state.current_emotion)
            
            # Style shaping with personality
            styled_response = shape(
                raw_response,
                state.current_emotion,
                state.arousal,
                base_max_tokens=CONFIG.behavior.base_max_tokens,
                emoji_baseline=CONFIG.behavior.emoji_baseline,
                personality_modifiers=style_modifiers,
                personality_flavor=personality_flavor,
            )
            
            print(f"bot> [{state.current_emotion}] {styled_response}")
            memory.add("bot", styled_response)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_demo()
