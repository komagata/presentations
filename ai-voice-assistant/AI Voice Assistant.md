---
title: AI Voice Assistant
theme: tokyo-night
---

# AI Voice Assistant

@komagata

---

What AI agents look like today

---

Grok bot, dots, OpenClaw

![span](slide3-official-mascots.png)

---

Cute

---

That is not the AI I imagined

---

HAL 9000 by 2001: A Space Odyssey (1968)


![span](<HAL9000.webp>)

---

MU/TH/UR by Alien (1979)

![span](<MUTHUR.webp>)

---

TARS from Interstellar (2014)

![span](<TARS.webp>)

---

Not cute

---

So I built the AI voice assistant I imagined

---

![span](<Hey OMA - What are you - What can you do - Thank you bye.mp4>)

---

It can speak many languages

---

![span](<ヘイ、オーマあなたは何ですか.mp4>)

---

# How it works

---

OMA is composed of the following:
　
- UI
- STT (speech-to-text), TTS (text-to-speech)
- Hyprland's window recognition
- Long-term memory
- OMA Skill

---

OMA provides a GUI and voice interface to AI agents

---

![span](oma-agent-interface-layer-filled-neon-glow-en-v2.png)

---

About listening and speaking

---

Default

---

![span](<listen-speak-think.svg>)
<!--
By default: GPT Live + Codex CLI
-->

---

Each part can use a different model

---

![span](listen-speak-think-whisper-qwen3-claude.svg)
<!--
You can swap out each part. I have not yet found local models that run well on many PCs,
support languages including Japanese, and meet my quality bar. We may be close.
-->

---

I am still looking for local models that run on most PCs and work well in Japanese and other languages. We may be close.

---

UI

---

![](<annotated-ui.webp>)

---

# Long-term memory

OMA has its own long-term memory, separate from the AI agent's memory

---

# OMA Skill

Most OMA-specific behavior is defined in the OMA Skill

---

# What's next

- Find speech recognition and synthesis models that work well in most languages, and make them the default.
- Make small tasks possible without looking at the screen or using the keyboard.

---

# Try it and tell me what you think

- If you are interested, please try OMA and share your feedback.
- If your first language is not Japanese, I would especially like to know how the voice sounds to you.
