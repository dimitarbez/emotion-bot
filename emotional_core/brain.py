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

    def generate_base(self, user_text: str, emotion: str, context: str) -> str:
        # Prefer OpenAI if available
        if _HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            try:
                client = openai.OpenAI()
                sys = (
                    "You are an empathetic, emotionally-aware assistant. "
                    "Keep responses concise but human. Use the conversation context. "
                    f"Current emotion: {emotion}. Reflect it subtly in tone."
                )
                prompt = f"Context:\n{context}\n\nUser: {user_text}\nAssistant:"
                resp = client.chat.completions.create(
                    model=self.cfg.openai_model,
                    temperature=self.cfg.openai_temperature,
                    max_tokens=self.cfg.openai_max_tokens,
                    messages=[
                        {"role": "system", "content": sys},
                        {"role": "user", "content": prompt},
                    ],
                )
                return resp.choices[0].message.content.strip()
            except Exception:
                pass

        # Local fallback: simple intent templates + reflection
        return self._local_reply(user_text, emotion, context)

    def _local_reply(self, user_text: str, emotion: str, context: str) -> str:
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
