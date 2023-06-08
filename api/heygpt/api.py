from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from heygpt.core import completion_openai_gpt, PromptInput, load_promps, make_prompt
from heygpt.constant import prompt_items_url

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.post("/gpt")
async def gpt(msg: PromptInput):
    return completion_openai_gpt(command=msg.prompt.Command, text=f"""{msg.text}""")


@app.get("/prompt-items")
async def prompt_items():
    return load_promps(prompt_items_url)


@app.post("/create-prompt")
async def create_prompt(text: str):
    return make_prompt(text)
