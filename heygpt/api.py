from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from litellm import completion
from heygpt.core import model
from heygpt.prompts import make_prompt, PromptInput, fmt_prompt

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
    # Build messages from command and text
    messages = fmt_prompt(msg.prompt.Command) if msg.prompt.Command else []

    if messages:
        messages[-1]["content"] += f"\n\n{msg.text}"
    else:
        messages = [{"role": "user", "content": msg.text}]

    # Use litellm completion directly
    response = completion(
        model=model,
        messages=messages,
        stream=False,
        drop_params=True,
    )

    return response.choices[0].message.content


@app.get("/prompt-items")
async def prompt_items():
    return prompts


@app.post("/create-prompt")
async def create_prompt(text: str):
    return make_prompt(text)
