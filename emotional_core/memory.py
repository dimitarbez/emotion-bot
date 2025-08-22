
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
import re, collections

@dataclass
class Utterance:
    speaker: str  # 'user' or 'bot'
    text: str

@dataclass
class ConversationMemory:
    history: List[Utterance] = field(default_factory=list)
    topic_counts: Dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))
    max_history: int = 30

    def add(self, speaker: str, text: str):
        self.history.append(Utterance(speaker, text))
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        for tok in re.findall(r"[\w']{4,}", text.lower()):
            self.topic_counts[tok] += 1

    def recent_context(self, limit: int = 6) -> str:
        return "\n".join(f"{u.speaker}: {u.text}" for u in self.history[-limit:])

    def top_topics(self, n: int = 5) -> List[str]:
        return [w for w, _ in sorted(self.topic_counts.items(), key=lambda kv: kv[1], reverse=True)[:n]]
