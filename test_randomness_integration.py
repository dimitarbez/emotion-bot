#!/usr/bin/env python3
"""
Test script for the randomness module integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from emotional_core.randomness import RandomnessEngine, RandomnessConfig, RandomnessType
from emotional_core.behavior import shape
from emotional_core.emotions import EmotionState
from emotional_core.personality import Personality

def test_randomness_engine():
    """Test the randomness engine functionality."""
    print("🎲 Testing EmotionBot Randomness System")
    print("=" * 50)
    
    # Test with high randomness for visible effects
    config = RandomnessConfig(
        intensity=0.8,
        style_drift_prob=0.5,
        mood_swing_prob=0.3,
        memory_quirk_prob=0.4,
        topic_tangent_prob=0.3,
        response_delay_prob=0.6,
        typo_slip_prob=0.3,
        enthusiasm_burst_prob=0.4,
        distraction_prob=0.3,
    )
    
    engine = RandomnessEngine(config)
    
    # Test individual randomness types
    print("Testing individual randomness types:")
    
    # Test style drift
    print("\n1. Style Drift:")
    original_style = {"verbosity": 1.0, "warmth": 0.5, "playfulness": 0.3}
    for i in range(5):
        modified_style = engine.apply_style_drift(original_style)
        print(f"  Iteration {i+1}: {modified_style}")
    
    # Test mood swings
    print("\n2. Mood Swings:")
    for i in range(5):
        dv, da = engine.get_mood_swing_delta()
        if dv != 0 or da != 0:
            print(f"  Mood swing {i+1}: valence_delta={dv:.3f}, arousal_delta={da:.3f}")
    
    # Test memory quirks
    print("\n3. Memory Quirks:")
    for i in range(5):
        quirk = engine.get_memory_quirk()
        if quirk:
            print(f"  Memory quirk {i+1}: '{quirk}'")
    
    # Test topic tangents
    print("\n4. Topic Tangents:")
    for i in range(5):
        tangent = engine.get_topic_tangent()
        if tangent:
            print(f"  Tangent {i+1}: '{tangent}'")
    
    # Test response delays
    print("\n5. Response Delays:")
    delays = []
    for i in range(10):
        delay = engine.get_response_delay()
        if delay > 0:
            delays.append(delay)
    if delays:
        avg_delay = sum(delays) / len(delays)
        print(f"  Generated {len(delays)} delays, average: {avg_delay:.2f}s")
    
    # Test typo slips
    print("\n6. Typo Slips:")
    test_texts = [
        "This is a perfectly normal sentence with several words.",
        "Another example of text that might get some typos applied.",
        "The randomness system should introduce human-like mistakes occasionally."
    ]
    
    for text in test_texts:
        modified = engine.apply_typo_slips(text)
        if modified != text:
            print(f"  Original: '{text}'")
            print(f"  Modified: '{modified}'")
    
    # Test enthusiasm bursts
    print("\n7. Enthusiasm Bursts:")
    for i in range(5):
        burst = engine.get_enthusiasm_burst()
        if burst:
            print(f"  Burst {i+1}: {burst}")
    
    # Test distraction effects
    print("\n8. Distraction Effects:")
    for i in range(5):
        distraction = engine.get_distraction_effect()
        if distraction:
            print(f"  Distraction {i+1}: '{distraction}'")

def test_randomness_integration():
    """Test randomness integration with personality and emotion systems."""
    print("\n🔗 Testing Randomness Integration")
    print("=" * 50)
    
    # Create components
    personality = Personality("enthusiast")
    engine = RandomnessEngine(RandomnessConfig(intensity=0.6))
    
    # Test integrated randomness application
    base_text = "That's really interesting and I'd love to hear more about it."
    style_mods = personality.get_personality_style_modifiers()
    
    print("Testing integrated randomness effects:")
    print(f"Original text: '{base_text}'")
    print(f"Original style mods: {style_mods}")
    
    for i in range(5):
        modified_text, modified_style, delay = engine.apply_all_randomness(
            base_text, style_mods, "joy", "enthusiast"
        )
        
        print(f"\nIteration {i+1}:")
        print(f"  Text: '{modified_text}'")
        if delay > 0:
            print(f"  Delay: {delay:.2f}s")
        
        # Show style changes
        style_changes = {}
        for key, orig_val in style_mods.items():
            new_val = modified_style.get(key, orig_val)
            if abs(new_val - orig_val) > 0.05:  # Significant change
                style_changes[key] = f"{orig_val:.2f} → {new_val:.2f}"
        
        if style_changes:
            print(f"  Style changes: {style_changes}")

def test_behavioral_shaping_with_randomness():
    """Test the enhanced behavioral shaping with randomness."""
    print("\n🎨 Testing Behavioral Shaping with Randomness")
    print("=" * 50)
    
    # Create components
    personality = Personality("creative")
    engine = RandomnessEngine(RandomnessConfig(intensity=0.7))
    
    base_text = "I think that's a fascinating perspective on the topic."
    
    print(f"Base text: '{base_text}'")
    print("Applying randomness through behavioral shaping:")
    
    for i in range(8):
        # Get style modifiers
        style_mods = personality.get_personality_style_modifiers()
        flavor = personality.get_response_flavor("curiosity")
        
        # Apply shaping with randomness
        shaped = shape(
            base_text,
            "curiosity",
            0.6,
            100,
            0.15,
            personality_modifiers=style_mods,
            personality_flavor=flavor,
            randomness_engine=engine
        )
        
        print(f"  {i+1}: '{shaped}'")

def test_conversation_state_tracking():
    """Test conversation state tracking for context-aware randomness."""
    print("\n💬 Testing Conversation State Tracking")
    print("=" * 50)
    
    engine = RandomnessEngine(RandomnessConfig(intensity=0.5))
    
    # Simulate a conversation
    conversation_turns = [
        ("Hello there!", "joy"),
        ("I'm working on a machine learning project", "neutral"),
        ("It's about natural language processing", "curiosity"),
        ("The algorithm is quite complex", "neutral"),
        ("I'm getting frustrated with debugging", "anger"),
        ("Maybe I should take a break", "sadness"),
    ]
    
    print("Simulating conversation with state tracking:")
    
    for turn_num, (user_input, emotion) in enumerate(conversation_turns):
        print(f"\nTurn {turn_num + 1}: User says '{user_input}' (emotion: {emotion})")
        
        # Update conversation state
        engine.update_conversation_state(user_input, emotion, "balanced")
        
        # Show state
        state = engine.as_dict()
        print(f"  Energy level: {state['state']['energy_level']}")
        print(f"  Recent topics: {state['state']['recent_topics']}")
        print(f"  Turn count: {state['state']['turn_count']}")
        
        # Test context-aware randomness
        if engine.should_apply_randomness(RandomnessType.TOPIC_TANGENT):
            tangent = engine.get_topic_tangent()
            if tangent:
                print(f"  Triggered tangent: '{tangent}'")
        
        if engine.should_apply_randomness(RandomnessType.MEMORY_QUIRK):
            quirk = engine.get_memory_quirk()
            if quirk:
                print(f"  Triggered memory quirk: '{quirk}'")

def test_randomness_configuration():
    """Test different randomness configurations."""
    print("\n⚙️ Testing Randomness Configurations")
    print("=" * 50)
    
    configs = [
        ("Minimal", RandomnessConfig(intensity=0.1)),
        ("Moderate", RandomnessConfig(intensity=0.5)),
        ("High", RandomnessConfig(intensity=0.9)),
        ("Style-focused", RandomnessConfig(
            intensity=0.6,
            style_drift_prob=0.8,
            typo_slip_prob=0.0,
            distraction_prob=0.0
        )),
        ("Memory-focused", RandomnessConfig(
            intensity=0.6,
            memory_quirk_prob=0.8,
            topic_tangent_prob=0.6,
            style_drift_prob=0.0
        ))
    ]
    
    test_text = "I really appreciate your help with this problem."
    
    for config_name, config in configs:
        print(f"\n{config_name} Configuration:")
        engine = RandomnessEngine(config)
        
        # Test a few applications
        for i in range(3):
            modified, _, delay = engine.apply_all_randomness(
                test_text, {"verbosity": 1.0, "warmth": 0.7}, "joy", "balanced"
            )
            if modified != test_text or delay > 0:
                print(f"  {i+1}: '{modified}'" + (f" (delay: {delay:.1f}s)" if delay > 0 else ""))

def main():
    """Run all randomness tests."""
    try:
        test_randomness_engine()
        test_randomness_integration()
        test_behavioral_shaping_with_randomness()
        test_conversation_state_tracking()
        test_randomness_configuration()
        
        print("\n✅ All randomness system tests completed!")
        print("\nThe randomness module adds human-like variability to:")
        print("• Response timing (thinking delays)")
        print("• Style inconsistencies (gradual drift)")
        print("• Mood fluctuations (sudden swings)")
        print("• Memory quirks (callbacks, forgetfulness)")
        print("• Topic tangents (spontaneous shifts)")
        print("• Typing errors (realistic mistakes)")
        print("• Enthusiasm bursts (excitement spikes)")
        print("• Attention spans (getting distracted)")
        
        print("\nTo see it in action:")
        print("python3 demo_personality.py")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
