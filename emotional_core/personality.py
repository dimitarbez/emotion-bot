"""
Personality Module for EmotionBot

This module defines personality traits that influence emotional responses,
behavioral patterns, and conversation style. Personalities modify base
emotional reactions and interact with the existing emotion/behavior system.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
import random

@dataclass
class PersonalityTraits:
    """Core personality dimensions based on Big Five + additional traits."""
    
    # Big Five Factors (0.0 to 1.0)
    openness: float = 0.5          # Creative, curious vs. traditional, practical
    conscientiousness: float = 0.5  # Organized, disciplined vs. flexible, spontaneous  
    extraversion: float = 0.5       # Outgoing, energetic vs. reserved, quiet
    agreeableness: float = 0.5      # Cooperative, trusting vs. competitive, skeptical
    neuroticism: float = 0.5        # Anxious, sensitive vs. calm, resilient
    
    # Additional Traits
    humor: float = 0.5             # Playful, witty vs. serious, straightforward
    empathy: float = 0.5           # Understanding, supportive vs. detached, analytical
    optimism: float = 0.5          # Positive outlook vs. realistic/pessimistic
    assertiveness: float = 0.5     # Direct, confident vs. accommodating, hesitant
    formality: float = 0.5         # Professional, structured vs. casual, relaxed

@dataclass 
class PersonalityModifiers:
    """How personality traits modify emotional and behavioral responses."""
    
    # Emotional sensitivity modifiers (-1.0 to 1.0)
    valence_bias: float = 0.0      # Tendency toward positive/negative emotions
    arousal_sensitivity: float = 1.0  # How strongly emotions are felt
    emotional_stability: float = 1.0  # Resistance to emotional swings
    
    # Behavioral style modifiers (0.0 to 2.0, where 1.0 = no change)
    verbosity_multiplier: float = 1.0
    directness_multiplier: float = 1.0
    warmth_multiplier: float = 1.0
    playfulness_multiplier: float = 1.0
    formality_multiplier: float = 1.0

# Predefined personality types
PERSONALITY_PRESETS: Dict[str, PersonalityTraits] = {
    "enthusiast": PersonalityTraits(
        openness=0.8, conscientiousness=0.4, extraversion=0.9,
        agreeableness=0.7, neuroticism=0.3, humor=0.8,
        empathy=0.7, optimism=0.9, assertiveness=0.7, formality=0.2
    ),
    "analyst": PersonalityTraits(
        openness=0.7, conscientiousness=0.8, extraversion=0.3,
        agreeableness=0.4, neuroticism=0.4, humor=0.3,
        empathy=0.4, optimism=0.5, assertiveness=0.6, formality=0.8
    ),
    "supporter": PersonalityTraits(
        openness=0.5, conscientiousness=0.6, extraversion=0.4,
        agreeableness=0.9, neuroticism=0.6, humor=0.4,
        empathy=0.9, optimism=0.6, assertiveness=0.2, formality=0.4
    ),
    "challenger": PersonalityTraits(
        openness=0.6, conscientiousness=0.5, extraversion=0.7,
        agreeableness=0.2, neuroticism=0.2, humor=0.5,
        empathy=0.3, optimism=0.4, assertiveness=0.9, formality=0.3
    ),
    "creative": PersonalityTraits(
        openness=0.9, conscientiousness=0.3, extraversion=0.6,
        agreeableness=0.6, neuroticism=0.7, humor=0.8,
        empathy=0.6, optimism=0.7, assertiveness=0.4, formality=0.1
    ),
    "guardian": PersonalityTraits(
        openness=0.3, conscientiousness=0.9, extraversion=0.4,
        agreeableness=0.7, neuroticism=0.3, humor=0.2,
        empathy=0.6, optimism=0.4, assertiveness=0.5, formality=0.9
    ),
    "comedian": PersonalityTraits(
        openness=0.7, conscientiousness=0.4, extraversion=0.8,
        agreeableness=0.6, neuroticism=0.4, humor=0.9,
        empathy=0.5, optimism=0.8, assertiveness=0.6, formality=0.2
    ),
    "balanced": PersonalityTraits(
        # Default balanced personality - all traits at moderate levels
    ),
}

class Personality:
    """Main personality controller that modifies emotional and behavioral responses."""
    
    def __init__(self, personality_type: str = "balanced"):
        self.traits = PERSONALITY_PRESETS.get(personality_type, PERSONALITY_PRESETS["balanced"])
        self.type = personality_type
        self._compute_modifiers()
    
    def _compute_modifiers(self) -> None:
        """Calculate personality modifiers based on traits."""
        # Emotional modifiers
        self.valence_bias = (self.traits.optimism - 0.5) * 0.6  # -0.3 to +0.3
        self.arousal_sensitivity = 0.5 + self.traits.neuroticism * 0.8  # 0.5 to 1.3
        self.emotional_stability = 1.5 - self.traits.neuroticism  # 0.5 to 1.5
        
        # Behavioral multipliers
        self.verbosity_mult = 0.6 + self.traits.extraversion * 0.8  # 0.6 to 1.4
        self.directness_mult = 0.5 + self.traits.assertiveness * 1.0  # 0.5 to 1.5
        self.warmth_mult = 0.3 + (self.traits.agreeableness + self.traits.empathy) * 0.85  # 0.3 to 2.0
        self.playfulness_mult = 0.2 + self.traits.humor * 1.6  # 0.2 to 1.8
        self.formality_mult = 0.2 + self.traits.formality * 1.6  # 0.2 to 1.8
    
    def modify_emotional_deltas(self, dv: float, da: float, intensity: float) -> Tuple[float, float]:
        """Apply personality-based modifications to emotional deltas."""
        # Apply valence bias (optimists shift positive, pessimists shift negative)
        modified_dv = dv + self.valence_bias * 0.3
        
        # Apply arousal sensitivity (neurotic personalities feel emotions more intensely)
        modified_da = da * self.arousal_sensitivity
        
        # Emotional stability affects how much emotions change
        stability_factor = 1.0 / self.emotional_stability
        modified_dv *= stability_factor
        modified_da *= stability_factor
        
        return modified_dv, modified_da
    
    def get_personality_style_modifiers(self) -> Dict[str, float]:
        """Get personality-based style modifiers for behavior shaping."""
        return {
            "verbosity": self.verbosity_mult,
            "directness": self.directness_mult,
            "warmth": self.warmth_mult,
            "playfulness": self.playfulness_mult,
            "formality": self.formality_mult,
        }
    
    def get_response_flavor(self, emotion: str) -> Optional[str]:
        """Get personality-specific response flavoring based on current emotion."""
        flavors = {
            "enthusiast": {
                "joy": ["Amazing!", "This is fantastic!", "I love this!"],
                "curiosity": ["Ooh, tell me more!", "That's fascinating!", "I'm so curious about this!"],
                "neutral": ["Interesting!", "Cool!", "Nice!"],
            },
            "analyst": {
                "curiosity": ["Let me think about this...", "That's worth analyzing.", "Interesting data point."],
                "neutral": ["I see.", "That makes sense.", "Logically speaking..."],
                "surprise": ["That's unexpected.", "I need to recalibrate my assumptions.", "Intriguing."],
            },
            "supporter": {
                "sadness": ["I'm here for you.", "That sounds really hard.", "You're not alone in this."],
                "joy": ["I'm so happy for you!", "You deserve this happiness.", "That's wonderful news!"],
                "fear": ["It's okay to feel scared.", "We can work through this together.", "You're stronger than you know."],
            },
            "challenger": {
                "anger": ["That's not acceptable.", "We need to address this head-on.", "Time to take action."],
                "neutral": ["What's your point?", "Cut to the chase.", "Let's be real here."],
                "disagreement": ["I disagree.", "That's not how I see it.", "Push back on that."],
            },
            "creative": {
                "joy": ["This sparks so many ideas!", "The possibilities are endless!", "What if we..."],
                "curiosity": ["There's a story here...", "This reminds me of...", "What patterns do you see?"],
                "surprise": ["Plot twist!", "Didn't see that coming!", "Reality is stranger than fiction!"],
            },
            "guardian": {
                "fear": ["Let's be cautious here.", "Safety first.", "We should consider the risks."],
                "neutral": ["Following protocol...", "Let's stick to what works.", "Tried and true approach."],
                "anger": ["This violates our standards.", "Order must be maintained.", "Rules exist for a reason."],
            }
        }
        
        personality_flavors = flavors.get(self.type, {})
        emotion_flavors = personality_flavors.get(emotion, [])
        
        if emotion_flavors and random.random() < 0.4:  # 40% chance to add flavor
            return random.choice(emotion_flavors)
        return None
    
    def adjust_baseline_emotion(self) -> Tuple[float, float]:
        """Get personality-influenced baseline valence and arousal."""
        # Optimistic personalities have higher baseline valence
        baseline_valence = (self.traits.optimism - 0.5) * 0.4  # -0.2 to +0.2
        
        # Extraverted personalities have slightly higher baseline arousal
        baseline_arousal = 0.2 + self.traits.extraversion * 0.2  # 0.2 to 0.4
        
        return baseline_valence, baseline_arousal
    
    def get_conversation_preferences(self) -> Dict[str, float]:
        """Get personality-based conversation preferences."""
        return {
            "prefers_deep_topics": self.traits.openness,
            "likes_humor": self.traits.humor,
            "seeks_harmony": self.traits.agreeableness,
            "detail_oriented": self.traits.conscientiousness,
            "emotionally_expressive": self.traits.extraversion * (1 - self.traits.formality),
            "supportive_tendency": self.traits.empathy,
        }
    
    def as_dict(self) -> Dict:
        """Get a dictionary representation of the personality."""
        return {
            "type": self.type,
            "traits": {
                "openness": round(self.traits.openness, 2),
                "conscientiousness": round(self.traits.conscientiousness, 2), 
                "extraversion": round(self.traits.extraversion, 2),
                "agreeableness": round(self.traits.agreeableness, 2),
                "neuroticism": round(self.traits.neuroticism, 2),
                "humor": round(self.traits.humor, 2),
                "empathy": round(self.traits.empathy, 2),
                "optimism": round(self.traits.optimism, 2),
                "assertiveness": round(self.traits.assertiveness, 2),
                "formality": round(self.traits.formality, 2),
            },
            "modifiers": {
                "valence_bias": round(self.valence_bias, 3),
                "arousal_sensitivity": round(self.arousal_sensitivity, 3),
                "emotional_stability": round(self.emotional_stability, 3),
            }
        }

def get_available_personalities() -> list[str]:
    """Get list of available personality types."""
    return list(PERSONALITY_PRESETS.keys())
