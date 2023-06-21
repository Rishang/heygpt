from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from heygpt.core import completion_openai_gpt, make_prompt

from heygpt.constant import PromptInput
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
async def gpt(msg: PromptInput, model: str = "gpt-3.5-turbo"):
    return completion_openai_gpt(
        command=msg.prompt.Command, text=f"""{msg.text}""", model=model
    )


@app.get("/prompt-items")
async def prompt_items():
    return prompts


@app.post("/create-prompt")
async def create_prompt(text: str):
    return make_prompt(text)
