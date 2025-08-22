# -*- coding: utf-8 -*-
from emotional_core.core import EmotionalChatCore

bot = EmotionalChatCore()  # pass llm_fn=your_fn later if you want


from emotional_core.core import EmotionalChatCore
from emotional_core.state_machine import EmotionEngine, EngineConfig


# Make the robot more reactive and remove calming:
cfg = EngineConfig(
    decay=0.95,  # keep mood longer
    user_influence=0.90,  # user affect strongly moves the bot
    self_regulation=0.02,
    empathy_gain=0.00,  # don't auto-cheer up when user is negative
    anger_dampening=0.00,  # don't reduce arousal on user anger
    dominance_floor=0.30,
)
bot.engine = EmotionEngine(cfg=cfg)


print("Type something. Ctrl+C to exit.\n")
while True:
    try:
        user = input("You: ").strip()
        if not user:
            continue
        out = bot.process(user_text=user)
        msg = out["bot_message"]
        mood = out["emotion_state"]["label"]
        sig = out["signals"]
        print(f"Bot ({mood}): {msg}")
        print(f"Signals: {sig}\n")
    except KeyboardInterrupt:
        print("\nBye!")
        break
