from fastapi import FastAPI, Request, HTTPException
from llama_cpp import Llama
import json

MODEL_PATH = "/app/models/phi-2.Q4_K_M.gguf"

llm = Llama(model_path=MODEL_PATH)

app = FastAPI()

@app.get("/")
def root():
    return {"status": "LLaMA is running"}

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        # Accept both "prompt" and "message" keys
        prompt = data.get("prompt") or data.get("message", "")
        if not prompt:
            return {"error": "No prompt or message provided"}
        
        output = llm(prompt, max_tokens=128)
        return {"response": output["choices"][0]["text"].strip()}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")