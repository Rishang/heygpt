from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from heygpt.core import completion_openai_gpt, model
from heygpt.prompts import make_prompt, PromptInput

from heygpt.serve_prompts import prompts

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.post("/gpt")
async def gpt(msg: PromptInput, model: str = model):
    return completion_openai_gpt(
        command=msg.prompt.Command, text=f"""{msg.text}""", model=model
    )


@app.get("/prompt-items")
async def prompt_items():
    return prompts


@app.post("/create-prompt")
async def create_prompt(text: str):
    return make_prompt(text)
