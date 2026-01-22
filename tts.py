import ollama
import edge_tts
import asyncio
import sounddevice as sd
import numpy as np
from reachy_mini import ReachyMini

# ---------- 参数 ----------
MODEL = "qwen3:0.6b"
VOICE = "zh-CN-XiaoxiaoNeural" # 中文女声，可换
SAMPLE = 22050
REACHY_IP = "127.0.0.1" # 换成实际 IP 或 None（USB）

# ---------- 初始化 ----------
reachy = ReachyMini(host=REACHY_IP) if REACHY_IP else ReachyMini()

async def speak(text: str):
    """Edge-TTS 播放"""
    communicate = edge_tts.Communicate(text, VOICE)
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    audio = np.frombuffer(audio, dtype=np.int16)
    sd.play(audio, samplerate=SAMPLE)
    sd.wait()

def emote(level: float):
    """简单表情：嘴角 + 眼皮随 level 动"""
    reachy.head.r_antenna.goal_position = level
    reachy.head.l_antenna.goal_position = level
    reachy.head.r_eye.goal_position = 1 - level
    reachy.head.l_eye.goal_position = 1 - level

def chat_once():
    user = input("你：")
    if not user.strip():
        return False
    # 调用 Ollama
    resp = ollama.chat(model=MODEL, messages=[{"role": "user", "content": user}])
    reply = resp["message"]["content"]
    print(f"Reachy：{reply}")
    # 情感值简单映射
    emote(min(len(reply) / 200, 1.0))
    asyncio.run(speak(reply))
    return True

if __name__ == "__main__":
    print("Reachy-Mini 文字聊天启动，直接输入文字即可，Ctrl-C 退出")
    try:
        while chat_once():
            pass
    except KeyboardInterrupt:
        print(" 拜拜~")
