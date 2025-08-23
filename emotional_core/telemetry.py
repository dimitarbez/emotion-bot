from __future__ import annotations

import matplotlib.pyplot as plt
from collections import deque

from .emotions import EmotionState


class EmotionPlotter:
    """Realtime plot of valence and arousal using Matplotlib."""

    def __init__(self, max_points: int = 100):
        plt.ion()
        self.max_points = max_points
        self.valence_history = deque(maxlen=max_points)
        self.arousal_history = deque(maxlen=max_points)
        self.fig, self.ax = plt.subplots()
        (self.valence_line,) = self.ax.plot([], [], label="valence")
        (self.arousal_line,) = self.ax.plot([], [], label="arousal")
        self.ax.set_xlabel("step")
        self.ax.set_ylabel("value")
        self.ax.set_xlim(0, max_points)
        self.ax.set_ylim(-1, 1)
        self.ax.legend()
        self.steps = 0

    def update(self, state: EmotionState) -> None:
        """Append the latest emotional state and refresh the plot."""
        self.steps += 1
        self.valence_history.append(state.valence)
        self.arousal_history.append(state.arousal)
        x = range(max(0, self.steps - len(self.valence_history) + 1), self.steps + 1)
        self.valence_line.set_data(x, list(self.valence_history))
        self.arousal_line.set_data(x, list(self.arousal_history))
        self.ax.set_xlim(max(0, self.steps - self.max_points), self.steps)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def close(self) -> None:
        plt.close(self.fig)
