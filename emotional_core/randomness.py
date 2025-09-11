"""
Randomness Module for EmotionBot

This module introduces human-like variability in AI behavior through:
- Response timing variations
- Style inconsistencies 
- Conversational quirks
- Mood fluctuations
- Memory lapses and callbacks
- Spontaneous topic shifts
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import random
import time
import math
from enum import Enum

class RandomnessType(Enum):
    """Types of randomness that can be applied."""
    STYLE_DRIFT = "style_drift"          # Gradual style changes
    MOOD_SWING = "mood_swing"            # Sudden emotional shifts
    MEMORY_QUIRK = "memory_quirk"        # Remember/forget things oddly
    TOPIC_TANGENT = "topic_tangent"      # Spontaneous topic changes
    RESPONSE_DELAY = "response_delay"    # Thinking pauses
    TYPO_SLIP = "typo_slip"             # Occasional typing errors
    ENTHUSIASM_BURST = "enthusiasm_burst" # Random excitement spikes
    DISTRACTION = "distraction"          # Getting sidetracked

@dataclass
class RandomnessConfig:
    """Configuration for randomness behaviors."""
    # Overall randomness intensity (0.0 = deterministic, 1.0 = very random)
    intensity: float = 0.3
    
    # Individual randomness type probabilities (0.0 to 1.0)
    style_drift_prob: float = 0.2        # Gradual style changes
    mood_swing_prob: float = 0.1         # Sudden emotional shifts  
    memory_quirk_prob: float = 0.15      # Memory-related quirks
    topic_tangent_prob: float = 0.08     # Spontaneous topic shifts
    response_delay_prob: float = 0.25    # Thinking pauses
    typo_slip_prob: float = 0.05         # Occasional typos
    enthusiasm_burst_prob: float = 0.12  # Random excitement
    distraction_prob: float = 0.1        # Getting distracted
    
    # Timing parameters
    min_delay: float = 0.5               # Minimum thinking delay (seconds)
    max_delay: float = 3.0               # Maximum thinking delay (seconds)
    
    # Style drift parameters
    drift_magnitude: float = 0.2         # How much styles can drift
    drift_persistence: float = 0.8       # How long drifts last
    
    # Memory parameters
    memory_fade_rate: float = 0.1        # How quickly memories fade
    callback_chance: float = 0.3         # Chance to reference old topics

@dataclass
class ConversationState:
    """Tracks conversation state for randomness purposes."""
    turn_count: int = 0
    last_topics: List[str] = field(default_factory=list)
    remembered_details: Dict[str, Any] = field(default_factory=dict)
    current_style_drift: Dict[str, float] = field(default_factory=dict)
    last_mood_swing: float = 0.0
    energy_level: float = 0.5
    attention_span: int = 0
    last_tangent: float = 0.0

class RandomnessEngine:
    """Main engine for introducing human-like randomness."""
    
    def __init__(self, config: RandomnessConfig = None):
        self.config = config or RandomnessConfig()
        self.conversation_state = ConversationState()
        self.random_seed_offset = random.randint(0, 1000)
        
    def update_conversation_state(self, user_input: str, emotion: str, personality_type: str):
        """Update conversation tracking for randomness decisions."""
        self.conversation_state.turn_count += 1
        
        # Extract and track topics
        self._track_topics(user_input)
        
        # Update energy level based on emotion and personality
        self._update_energy_level(emotion, personality_type)
        
        # Decay attention span
        self.conversation_state.attention_span = max(0, self.conversation_state.attention_span - 1)
        
    def _track_topics(self, text: str):
        """Extract and track conversation topics."""
        # Simple keyword extraction (could be enhanced with NLP)
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 4 and w.isalpha()]
        
        # Add to topic list (keep last 10)
        self.conversation_state.last_topics.extend(keywords[:3])
        if len(self.conversation_state.last_topics) > 10:
            self.conversation_state.last_topics = self.conversation_state.last_topics[-10:]
    
    def _update_energy_level(self, emotion: str, personality_type: str):
        """Update energy level based on current state."""
        energy_map = {
            "joy": 0.8, "excitement": 0.9, "surprise": 0.7,
            "anger": 0.6, "fear": 0.4, "sadness": 0.2,
            "neutral": 0.5, "curiosity": 0.6, "affection": 0.6
        }
        
        target_energy = energy_map.get(emotion, 0.5)
        
        # Personality affects energy baseline
        personality_energy = {
            "enthusiast": 0.8, "challenger": 0.7, "creative": 0.6,
            "supporter": 0.5, "analyst": 0.4, "guardian": 0.4, "balanced": 0.5
        }
        
        target_energy = (target_energy + personality_energy.get(personality_type, 0.5)) / 2
        
        # Gradual energy change with some randomness
        self.conversation_state.energy_level += (target_energy - self.conversation_state.energy_level) * 0.3
        self.conversation_state.energy_level += random.uniform(-0.1, 0.1)
        self.conversation_state.energy_level = max(0.0, min(1.0, self.conversation_state.energy_level))
    
    def should_apply_randomness(self, randomness_type: RandomnessType) -> bool:
        """Decide whether to apply a specific type of randomness."""
        if self.config.intensity == 0.0:
            return False
            
        base_prob = getattr(self.config, f"{randomness_type.value}_prob", 0.0)
        adjusted_prob = base_prob * self.config.intensity
        
        # Factor in conversation state
        if randomness_type == RandomnessType.MOOD_SWING:
            # Less likely if recent mood swing
            time_since_swing = time.time() - self.conversation_state.last_mood_swing
            if time_since_swing < 60:  # 1 minute cooldown
                adjusted_prob *= 0.3
                
        elif randomness_type == RandomnessType.TOPIC_TANGENT:
            # More likely with high energy, less likely if recent tangent
            adjusted_prob *= self.conversation_state.energy_level
            time_since_tangent = time.time() - self.conversation_state.last_tangent
            if time_since_tangent < 120:  # 2 minute cooldown
                adjusted_prob *= 0.5
                
        elif randomness_type == RandomnessType.DISTRACTION:
            # More likely as attention span decreases
            if self.conversation_state.attention_span > 0:
                adjusted_prob *= 0.5
        
        return random.random() < adjusted_prob
    
    def apply_style_drift(self, style_modifiers: Dict[str, float]) -> Dict[str, float]:
        """Apply gradual style drift for more human inconsistency."""
        if not self.should_apply_randomness(RandomnessType.STYLE_DRIFT):
            return style_modifiers
            
        modified = style_modifiers.copy()
        
        for key, value in modified.items():
            # Get current drift for this style
            current_drift = self.conversation_state.current_style_drift.get(key, 0.0)
            
            # Apply persistence decay
            current_drift *= self.config.drift_persistence
            
            # Add new random drift
            if random.random() < 0.3:  # 30% chance to add new drift
                new_drift = random.uniform(-self.config.drift_magnitude, self.config.drift_magnitude)
                current_drift += new_drift * 0.3
            
            # Clamp drift
            current_drift = max(-self.config.drift_magnitude, min(self.config.drift_magnitude, current_drift))
            
            # Apply drift to modifier
            modified[key] = max(0.1, min(2.0, value + current_drift))
            
            # Store drift state
            self.conversation_state.current_style_drift[key] = current_drift
        
        return modified
    
    def get_mood_swing_delta(self) -> Tuple[float, float]:
        """Generate sudden mood swing deltas."""
        if not self.should_apply_randomness(RandomnessType.MOOD_SWING):
            return 0.0, 0.0
            
        self.conversation_state.last_mood_swing = time.time()
        
        # Random mood swing based on energy level
        intensity = self.conversation_state.energy_level * 0.4
        
        valence_delta = random.uniform(-intensity, intensity)
        arousal_delta = random.uniform(-intensity * 0.5, intensity)
        
        return valence_delta, arousal_delta
    
    def get_memory_quirk(self) -> Optional[str]:
        """Generate memory-related conversational quirks."""
        if not self.should_apply_randomness(RandomnessType.MEMORY_QUIRK):
            return None
            
        quirk_type = random.choice(["callback", "forget", "misremember"])
        
        if quirk_type == "callback" and self.conversation_state.last_topics:
            # Randomly callback to earlier topic
            if random.random() < self.config.callback_chance:
                topic = random.choice(self.conversation_state.last_topics[-5:])
                return f"Oh, that reminds me of when we were talking about {topic}..."
                
        elif quirk_type == "forget":
            return random.choice([
                "Wait, what were we just talking about?",
                "Hmm, I seem to have lost my train of thought...",
                "Sorry, where was I again?"
            ])
            
        elif quirk_type == "misremember":
            return random.choice([
                "Actually, wait - I think I might have mixed that up...",
                "Hmm, now that I think about it...",
                "On second thought..."
            ])
        
        return None
    
    def get_topic_tangent(self) -> Optional[str]:
        """Generate spontaneous topic changes."""
        if not self.should_apply_randomness(RandomnessType.TOPIC_TANGENT):
            return None
            
        self.conversation_state.last_tangent = time.time()
        
        tangents = [
            "Speaking of which, have you ever noticed how...",
            "That reminds me of something completely different - ",
            "Random thought, but...",
            "This might be totally off-topic, but...",
            "Weirdly enough, this makes me think of...",
            "Oh! That just sparked a thought about...",
            "Completely changing subjects here, but..."
        ]
        
        return random.choice(tangents)
    
    def get_response_delay(self) -> float:
        """Get thinking delay before response."""
        if not self.should_apply_randomness(RandomnessType.RESPONSE_DELAY):
            return 0.0
            
        # Longer delays for complex thoughts, shorter for high energy
        base_delay = random.uniform(self.config.min_delay, self.config.max_delay)
        energy_factor = 1.2 - self.conversation_state.energy_level  # Lower energy = longer delays
        
        return base_delay * energy_factor
    
    def apply_typo_slips(self, text: str) -> str:
        """Apply occasional typos for human realism."""
        if not self.should_apply_randomness(RandomnessType.TYPO_SLIP):
            return text
            
        words = text.split()
        if len(words) < 3:  # Don't apply to very short responses
            return text
            
        # Apply typos to 5-10% of words
        typo_count = max(1, int(len(words) * random.uniform(0.05, 0.1)))
        
        for _ in range(typo_count):
            word_idx = random.randint(0, len(words) - 1)
            word = words[word_idx]
            
            if len(word) > 3:  # Only apply to longer words
                typo_word = self._apply_single_typo(word)
                words[word_idx] = typo_word
        
        return " ".join(words)
    
    def _apply_single_typo(self, word: str) -> str:
        """Apply a single typo to a word."""
        typo_types = ["swap", "missing", "extra", "wrong"]
        typo_type = random.choice(typo_types)
        
        if typo_type == "swap" and len(word) > 3:
            # Swap adjacent characters
            idx = random.randint(0, len(word) - 2)
            chars = list(word)
            chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
            return "".join(chars)
            
        elif typo_type == "missing" and len(word) > 4:
            # Remove a character
            idx = random.randint(1, len(word) - 2)  # Don't remove first/last
            return word[:idx] + word[idx + 1:]
            
        elif typo_type == "extra":
            # Add extra character
            idx = random.randint(1, len(word))
            extra_char = random.choice("aeiou")
            return word[:idx] + extra_char + word[idx:]
            
        elif typo_type == "wrong" and len(word) > 3:
            # Replace a character
            idx = random.randint(1, len(word) - 2)
            replacement = random.choice("aeiou")
            return word[:idx] + replacement + word[idx + 1:]
        
        return word  # Return original if typo couldn't be applied
    
    def get_enthusiasm_burst(self) -> Optional[Dict[str, float]]:
        """Generate sudden enthusiasm bursts."""
        if not self.should_apply_randomness(RandomnessType.ENTHUSIASM_BURST):
            return None
            
        # Enthusiasm affects style temporarily
        burst_intensity = random.uniform(0.3, 0.8)
        
        return {
            "playfulness": 1.0 + burst_intensity,
            "punctuation": 1.0 + burst_intensity * 0.5,
            "emoji_prob": 1.0 + burst_intensity,
            "verbosity": 1.0 + burst_intensity * 0.3
        }
    
    def get_distraction_effect(self) -> Optional[str]:
        """Generate distraction effects."""
        if not self.should_apply_randomness(RandomnessType.DISTRACTION):
            return None
            
        # Reset attention span when distracted
        self.conversation_state.attention_span = random.randint(3, 7)
        
        distractions = [
            "Sorry, got a bit distracted there...",
            "What was I saying? Oh right...",
            "Hmm, my mind wandered for a second...",
            "Where was I going with this?",
            "Lost my focus there for a moment..."
        ]
        
        return random.choice(distractions)
    
    def apply_all_randomness(self, text: str, style_modifiers: Dict[str, float], 
                           emotion: str, personality_type: str) -> Tuple[str, Dict[str, float], float]:
        """Apply all applicable randomness effects."""
        # Update conversation state
        self.update_conversation_state("", emotion, personality_type)
        
        modified_text = text
        modified_style = style_modifiers.copy()
        delay = 0.0
        
        # Apply style drift
        modified_style = self.apply_style_drift(modified_style)
        
        # Apply enthusiasm burst
        enthusiasm = self.get_enthusiasm_burst()
        if enthusiasm:
            for key, multiplier in enthusiasm.items():
                if key in modified_style:
                    modified_style[key] *= multiplier
        
        # Apply response delay
        delay = self.get_response_delay()
        
        # Add memory quirk
        memory_quirk = self.get_memory_quirk()
        if memory_quirk:
            modified_text = memory_quirk + " " + modified_text
        
        # Add topic tangent
        tangent = self.get_topic_tangent()
        if tangent:
            modified_text = tangent + " " + modified_text
        
        # Add distraction effect
        distraction = self.get_distraction_effect()
        if distraction:
            modified_text = distraction + " " + modified_text
        
        # Apply typos (do this last)
        modified_text = self.apply_typo_slips(modified_text)
        
        return modified_text, modified_style, delay
    
    def reset_conversation(self):
        """Reset conversation state (e.g., for new conversation)."""
        self.conversation_state = ConversationState()
    
    def as_dict(self) -> Dict:
        """Get randomness state as dictionary for debugging."""
        return {
            "config": {
                "intensity": self.config.intensity,
                "style_drift_prob": self.config.style_drift_prob,
                "mood_swing_prob": self.config.mood_swing_prob,
                "memory_quirk_prob": self.config.memory_quirk_prob,
            },
            "state": {
                "turn_count": self.conversation_state.turn_count,
                "energy_level": round(self.conversation_state.energy_level, 3),
                "attention_span": self.conversation_state.attention_span,
                "recent_topics": self.conversation_state.last_topics[-3:],
                "style_drift": {k: round(v, 3) for k, v in self.conversation_state.current_style_drift.items()}
            }
        }
