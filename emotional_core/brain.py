from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import os, random

from dotenv import load_dotenv

load_dotenv()  # take variables from .env

from .memory import ConversationMemory
from .nlp import Appraisal
from .behavior import shape

try:
    import openai  # type: ignore

    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False


@dataclass
class BrainConfig:
    openai_model: str
    openai_temperature: float
    openai_max_tokens: int


class Brain:
    def __init__(self, cfg: BrainConfig):
        self.cfg = cfg

    def generate_base(self, user_text: str, emotion: str, context: str, personality_type: str = "balanced") -> str:
        if not (_HAS_OPENAI and os.getenv("OPENAI_API_KEY")):
            raise RuntimeError("OpenAI API is required but not available. Set OPENAI_API_KEY and install openai.")

        try:
                client = openai.OpenAI()

                # Improved system prompt with clearer structure and guidance
                personality_descriptions = {
                    "enthusiast": "energetic, optimistic, and highly engaged with life",
                    "analyst": "logical, thoughtful, and detail-oriented",
                    "supporter": "empathetic, caring, and focused on helping others", 
                    "challenger": "direct, assertive, and unafraid of conflict",
                    "creative": "imaginative, spontaneous, and unconventional",
                    "guardian": "responsible, traditional, and security-focused",
                    "balanced": "adaptable with moderate traits across all dimensions"
                }
                
                personality_desc = personality_descriptions.get(personality_type, "balanced and adaptable")
                
                sys = (
                    "You are a human having a natural conversation. Never mention being an AI.\n\n"
                    f"PERSONALITY TYPE: {personality_type}\n"
                    f"You are {personality_desc}. Let this personality come through naturally in your responses.\n\n"
                    "EMOTIONAL STATE AND EXPRESSION:\n"
                    f"Current emotion: {emotion}\n"
                    "- Let this emotion permeate your entire response\n"
                    "- Adjust your tone, word choice, sentence structure, and punctuation accordingly\n"
                    "- Show the emotion through your language, don't just state it\n"
                    "- Use appropriate intensity - subtle for mild emotions, vivid for strong ones\n\n"
                    "RESPONSE STYLE:\n"
                    "- Be authentic, candid, and naturally expressive\n"
                    "- Keep responses concise but impactful (aim for 1-3 sentences typically)\n"
                    "- Have strong, clear opinions - don't hedge unnecessarily\n"
                    "- Use natural human speech patterns and colloquialisms when appropriate\n"
                    "- Match the conversational energy and formality level of the user\n\n"
                    "CONTEXTUAL AWARENESS:\n"
                    "- Pay close attention to the provided context\n"
                    "- Reference relevant details naturally without over-explaining\n"
                    "- Build on the conversational flow established in context\n"
                )

                # Improved user prompt with clearer structure
                prompt = (
                    f"CONVERSATION CONTEXT:\n{context}\n\n"
                    f"USER MESSAGE:\n{user_text}\n\n"
                    f"Respond as a {personality_desc} human in the {emotion} emotional state, being natural and engaging:"
                )

                resp = client.chat.completions.create(
                    model=self.cfg.openai_model,
                    temperature=max(0.9, getattr(self.cfg, "openai_temperature", 0.7)),
                    presence_penalty=0.8,
                    frequency_penalty=0.4,
                    max_tokens=self.cfg.openai_max_tokens,
                    messages=[
                        {"role": "system", "content": sys},
                        {"role": "user", "content": prompt},
                    ],
                )
                return resp.choices[0].message.content.strip()
        except Exception as e:
            # Surface OpenAI errors to caller
            raise RuntimeError(f"OpenAI generation failed: {e}")

    def _local_reply(self, user_text: str, emotion: str, context: str, personality_type: str = "balanced") -> str:
        ut = user_text.strip()
        is_question = ut.endswith("?") or any(
            w in ut.lower() for w in ["why", "how", "what", "when", "where"]
        )
        # Very small reflection pool
        starters = {
            "joy": ["That’s exciting", "I’m glad to hear that", "Love it"],
            "sadness": [
                "I’m sorry you’re going through that",
                "That sounds heavy",
                "I hear you",
            ],
            "anger": [
                "I get why that’s frustrating",
                "That’s rough",
                "I can see why you’re upset",
            ],
            "fear": [
                "It’s understandable to feel uncertain",
                "That sounds worrying",
                "I get the concern",
            ],
            "surprise": ["Whoa", "That’s unexpected", "Didn’t see that coming"],
            "disgust": ["Yikes", "That’s off-putting", "I’m not a fan of that either"],
            "curiosity": ["Interesting", "I’m curious too", "Let’s unpack it"],
            "affection": ["I appreciate you", "That’s sweet", "Thanks for sharing"],
            "neutral": ["Got it", "Understood", "Okay"],
        }
        s = random.choice(starters.get(emotion, starters["neutral"]))
        if is_question:
            return f"{s}. Here’s my take: {self._answer_like(ut)}"
        else:
            return f"{s}. {self._respond_like(ut)}"

    def _answer_like(self, q: str) -> str:
        # Rudimentary Q/A
        if "why" in q.lower():
            return "Because of a mix of context, goals, and constraints. What part matters most to you right now?"
        if "how" in q.lower():
            return "We can break it down into small steps and iterate. What step would you like to tackle first?"
        if "what" in q.lower():
            return "It depends on your priorities—speed, quality, or learning. Which one should we optimize for?"
        if "when" in q.lower():
            return (
                "As soon as we gather the needed info. Do you have a deadline in mind?"
            )
        if "where" in q.lower():
            return "Wherever it helps you stay focused and comfortable. What do you prefer?"
        return "Let’s think it through together. What outcome would you like?"

    def _respond_like(self, s: str) -> str:
        # Paraphrase-like acknowledgement
        return "Tell me more about that—what led up to it, and what would feel like progress?"
