from __future__ import annotations

from collections import deque

try:  # pragma: no cover - graphical backend selection
    import matplotlib
    try:
        # Only use the Tk backend when the tkinter module is available
        import tkinter  # noqa: F401
        matplotlib.use("TkAgg")
    except Exception:
        matplotlib.use("Agg")

    import matplotlib.pyplot as plt
except Exception:  # matplotlib may not be installed in minimal environments
    plt = None  # type: ignore

from .emotions import EmotionState


class EmotionPlotter:
    """Realtime plot of valence, arousal and discrete emotion."""

    def __init__(self, max_points: int = 100):
        self.enabled = plt is not None
        if not self.enabled:
            return

        plt.ion()
        self.max_points = max_points
        self.valence_history = deque(maxlen=max_points)
        self.arousal_history = deque(maxlen=max_points)

        try:
            self.fig, self.ax = plt.subplots()
        except Exception:
            # Backend failed to initialize (e.g. missing Tk); disable plotting
            self.enabled = False
            return
        (self.valence_line,) = self.ax.plot([], [], label="valence")
        (self.arousal_line,) = self.ax.plot([], [], label="arousal")
        self.ax.set_xlabel("step")
        self.ax.set_ylabel("value")
        self.ax.set_xlim(0, max_points)
        self.ax.set_ylim(-1, 1)
        self.ax.legend()
        # text box for full state readout
        self.info_text = self.ax.text(
            0.02,
            0.95,
            "",
            transform=self.ax.transAxes,
            va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.6),
        )
        self.steps = 0

    def update(self, state: EmotionState) -> None:
        """Append the latest emotional state and refresh the plot."""
        if not self.enabled:
            return

        self.steps += 1
        self.valence_history.append(state.valence)
        self.arousal_history.append(state.arousal)
        x = range(max(0, self.steps - len(self.valence_history) + 1), self.steps + 1)
        self.valence_line.set_data(x, list(self.valence_history))
        self.arousal_line.set_data(x, list(self.arousal_history))
        self.ax.set_xlim(max(0, self.steps - self.max_points), self.steps)
        self.ax.set_title(f"emotion: {state.current_emotion}")
        info = state.as_dict()
        self.info_text.set_text("\n".join(f"{k}: {v}" for k, v in info.items()))
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def close(self) -> None:
        if self.enabled:
            plt.close(self.fig)
