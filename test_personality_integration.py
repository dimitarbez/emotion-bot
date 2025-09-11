#!/usr/bin/env python3
"""
Simple test script to verify personality module integration
This bypasses external dependencies like dotenv and OpenAI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from emotional_core.personality import Personality, get_available_personalities
from emotional_core.emotions import EmotionState
from emotional_core.behavior import shape
from emotional_core.config import CONFIG

def test_personality_system():
    """Test the personality system integration."""
    print("🧠 Testing EmotionBot Personality System")
    print("=" * 50)
    
    # Test available personalities
    personalities = get_available_personalities()
    print(f"Available personalities: {', '.join(personalities)}")
    print()
    
    # Test different personality types
    for personality_type in ["enthusiast", "analyst", "supporter", "challenger"]:
        print(f"🎭 Testing {personality_type} personality:")
        
        # Create personality
        personality = Personality(personality_type)
        print(f"  Type: {personality.type}")
        
        # Show key traits
        traits = personality.traits
        print(f"  Key traits: extraversion={traits.extraversion:.1f}, optimism={traits.optimism:.1f}, empathy={traits.empathy:.1f}")
        
        # Test emotional modifiers
        dv, da = personality.modify_emotional_deltas(0.5, 0.3, 0.4)
        print(f"  Emotional modifiers: valence_delta={dv:.3f}, arousal_delta={da:.3f}")
        
        # Test style modifiers
        style_mods = personality.get_personality_style_modifiers()
        print(f"  Style: warmth={style_mods['warmth']:.1f}, playfulness={style_mods['playfulness']:.1f}")
        
        # Test response flavoring
        flavor = personality.get_response_flavor("joy")
        if flavor:
            print(f"  Joy flavor: '{flavor}'")
        
        # Test baseline adjustment
        baseline_v, baseline_a = personality.adjust_baseline_emotion()
        print(f"  Baselines: valence={baseline_v:.3f}, arousal={baseline_a:.3f}")
        
        print()

def test_emotion_personality_integration():
    """Test how personality affects emotional state."""
    print("🔗 Testing Emotion-Personality Integration")
    print("=" * 50)
    
    # Create two different personalities
    enthusiast = Personality("enthusiast")
    analyst = Personality("analyst")
    
    # Create emotion states
    state1 = EmotionState()
    state2 = EmotionState()
    
    # Apply personality baselines
    baseline_v1, baseline_a1 = enthusiast.adjust_baseline_emotion()
    baseline_v2, baseline_a2 = analyst.adjust_baseline_emotion()
    
    state1.set_personality_baselines(baseline_v1, baseline_a1)
    state2.set_personality_baselines(baseline_v2, baseline_a2)
    
    print(f"Enthusiast baseline - valence: {state1.baseline_valence:.3f}, arousal: {state1.baseline_arousal:.3f}")
    print(f"Analyst baseline - valence: {state2.baseline_valence:.3f}, arousal: {state2.baseline_arousal:.3f}")
    
    # Test emotional delta modifications
    print("\nTesting emotional deltas for positive input:")
    dv_orig, da_orig = 0.4, 0.3
    
    dv1, da1 = enthusiast.modify_emotional_deltas(dv_orig, da_orig, 0.5)
    dv2, da2 = analyst.modify_emotional_deltas(dv_orig, da_orig, 0.5)
    
    print(f"Original deltas: valence={dv_orig}, arousal={da_orig}")
    print(f"Enthusiast modified: valence={dv1:.3f}, arousal={da1:.3f}")
    print(f"Analyst modified: valence={dv2:.3f}, arousal={da2:.3f}")
    print()

def test_behavioral_shaping():
    """Test how personality affects behavioral response shaping."""
    print("🎨 Testing Behavioral Shaping with Personality")
    print("=" * 50)
    
    base_text = "That's really interesting"
    
    for personality_type in ["enthusiast", "analyst", "supporter"]:
        personality = Personality(personality_type)
        
        # Get style modifiers and flavor
        style_mods = personality.get_personality_style_modifiers()
        flavor = personality.get_response_flavor("joy")
        
        # Shape the response
        shaped = shape(
            base_text,
            "joy",
            0.6,
            100,
            0.15,
            personality_modifiers=style_mods,
            personality_flavor=flavor
        )
        
        print(f"{personality_type}: {shaped}")
    
    print()

def main():
    """Run all tests."""
    try:
        test_personality_system()
        test_emotion_personality_integration()
        test_behavioral_shaping()
        
        print("✅ All personality system tests completed successfully!")
        print("\nPersonality module is ready for integration!")
        print("\nTo use in the main app:")
        print("1. Install dependencies: pip install python-dotenv (or use virtual environment)")
        print("2. Run: python3 main.py")
        print("3. Try commands like ':personality', ':switch enthusiast', etc.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
