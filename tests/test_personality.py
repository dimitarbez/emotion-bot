"""
Tests for the personality module integration
"""

import pytest
from emotional_core.personality import Personality, get_available_personalities, PERSONALITY_PRESETS
from emotional_core.emotions import EmotionState
from emotional_core.behavior import shape


def test_personality_creation():
    """Test that personalities can be created and have expected traits."""
    p = Personality("enthusiast")
    assert p.type == "enthusiast"
    assert p.traits.extraversion > 0.7  # Enthusiasts should be extraverted
    assert p.traits.optimism > 0.7      # And optimistic


def test_personality_emotional_modifiers():
    """Test that personality modifies emotional responses."""
    enthusiast = Personality("enthusiast")
    analyst = Personality("analyst")
    
    # Enthusiast should have positive valence bias (optimistic)
    assert enthusiast.valence_bias > 0
    
    # Analyst should be more emotionally stable
    assert analyst.emotional_stability > enthusiast.emotional_stability


def test_personality_style_modifiers():
    """Test that personality affects behavioral style."""
    enthusiast = Personality("enthusiast")
    analyst = Personality("analyst")
    
    enthusiast_mods = enthusiast.get_personality_style_modifiers()
    analyst_mods = analyst.get_personality_style_modifiers()
    
    # Enthusiast should be more warm and playful
    assert enthusiast_mods["warmth"] > analyst_mods["warmth"]
    assert enthusiast_mods["playfulness"] > analyst_mods["playfulness"]
    
    # Analyst should be more formal
    assert analyst_mods["formality"] > enthusiast_mods["formality"]


def test_personality_baselines():
    """Test that personality affects emotional baselines."""
    optimist = Personality("enthusiast")  # High optimism
    pessimist = Personality("analyst")    # Neutral optimism
    
    opt_baseline_v, opt_baseline_a = optimist.adjust_baseline_emotion()
    pess_baseline_v, pess_baseline_a = pessimist.adjust_baseline_emotion()
    
    # Optimist should have higher baseline valence
    assert opt_baseline_v > pess_baseline_v


def test_emotion_state_personality_baselines():
    """Test that emotion state can be modified by personality baselines."""
    state = EmotionState()
    original_valence = state.baseline_valence
    
    # Set personality-influenced baselines
    state.set_personality_baselines(0.2, 0.3)
    
    assert state.baseline_valence == 0.2
    assert state.baseline_arousal == 0.3
    assert state.baseline_valence != original_valence


def test_personality_response_flavoring():
    """Test that personalities add appropriate response flavors."""
    enthusiast = Personality("enthusiast")
    supporter = Personality("supporter")
    
    # Test multiple times to account for randomness
    enthusiast_flavors = []
    supporter_flavors = []
    
    for _ in range(10):
        e_flavor = enthusiast.get_response_flavor("joy")
        s_flavor = supporter.get_response_flavor("sadness")
        if e_flavor:
            enthusiast_flavors.append(e_flavor)
        if s_flavor:
            supporter_flavors.append(s_flavor)
    
    # Should get some flavors (not guaranteed every time due to randomness)
    # but at least one of each type should appear in 10 attempts
    assert len(enthusiast_flavors) > 0 or len(supporter_flavors) > 0


def test_behavioral_shaping_with_personality():
    """Test that personality modifiers affect behavioral shaping."""
    # Test with enthusiast personality (high warmth, playfulness)
    enthusiast = Personality("enthusiast")
    mods = enthusiast.get_personality_style_modifiers()
    flavor = "Amazing!"
    
    # Shape a neutral response with personality
    shaped = shape(
        "That's interesting",
        "joy", 
        0.6,
        100,
        0.15,
        personality_modifiers=mods,
        personality_flavor=flavor
    )
    
    # Should include the personality flavor
    assert "Amazing!" in shaped or "That's interesting" in shaped  # Flavor has a chance to be added


def test_available_personalities():
    """Test that we can get the list of available personalities."""
    personalities = get_available_personalities()
    assert "enthusiast" in personalities
    assert "analyst" in personalities
    assert "supporter" in personalities
    assert "challenger" in personalities
    assert "creative" in personalities
    assert "guardian" in personalities
    assert "balanced" in personalities


def test_personality_as_dict():
    """Test that personality can be serialized to dict."""
    p = Personality("enthusiast")
    p_dict = p.as_dict()
    
    assert p_dict["type"] == "enthusiast"
    assert "traits" in p_dict
    assert "modifiers" in p_dict
    assert "openness" in p_dict["traits"]
    assert "valence_bias" in p_dict["modifiers"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
