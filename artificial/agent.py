from fastapi import FastAPI, Request
import requests

app = FastAPI()

# Ollama 本地 API 地址
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:4b"

# 全局对话上下文，简单保存历史
conversation_history = []


@app.get("/")
def home():
    return {"message": "Ollama 智能体已启动！"}


@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    prompt = data.get("prompt", "").strip()

    # 简单决策逻辑
    if prompt.lower() in ["hello", "hi", "你好"]:
        reply = "你好！我是你的智能体助手，有什么可以帮你？"
    elif prompt.lower().startswith("记住"):
        # 存入上下文
        note = prompt[2:].strip()
        conversation_history.append(note)
        reply = f"已记住: {note}"
    elif prompt.lower() == "告诉我记忆":
        if conversation_history:
            reply = "我记得这些信息: " + "; ".join(conversation_history)
        else:
            reply = "我还没有记住任何东西。"
    else:
        # 调用 Ollama 模型
        payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_API, json=payload)
        reply = response.json().get("response", "抱歉，我没有理解你的意思。")

    return {"reply": reply}

