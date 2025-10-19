from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from google import genai

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 初始化 Gemini 客户端，直接传入 API key
client = genai.Client(api_key="AIzaSyAJjK0XYvoitU0saAqb0useLbDed4nH3dQ")  # 替换为你的 Gemini API Key

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request, user_input: str = Form(...)):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_input
        )
        return JSONResponse({"response": response.text})
    except Exception as e:
        return JSONResponse({"error": str(e)})



