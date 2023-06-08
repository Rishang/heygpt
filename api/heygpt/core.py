import os
import csv
import json
from dataclasses import dataclass, field

import requests
import openai
from dotenv import load_dotenv
from pydantic import BaseModel
from bardapi import Bard
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter


from heygpt.constant import config_path

console = Console()

load_dotenv()

try:
    with open(config_path, "r") as f:
        configs = json.loads(f.read())
except FileNotFoundError:
    configs = {}

openai.api_key = os.getenv("OPENAI_API_KEY", configs.get("openai_key"))


@dataclass
class Prompt:
    Title: str
    Command: str
    ExtraCommands: str = field(default_factory=str)
    Tags: list[str] = field(default_factory=list)


class PromptInput(BaseModel):
    prompt: Prompt
    text: str


class PromptResponse(BaseModel):
    message: str


def ask_prompt_input(items: list, title="Select item"):
    completer = FuzzyWordCompleter(items)
    text = prompt(f"{title}: ", completer=completer, complete_while_typing=True)
    return text


def completion_openai_gpt(text: str = None, command: str = ""):
    if not text:
        raise Exception("No text found")

    # payload = f"{command} ```{text}```"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": command + "\n" + text},
            # {"role": "user", "content": text},
        ],
        # stop="",
    )

    return completion


def completion_bard(text: str, command: str = ""):
    """
    ref: https://github.com/dsdanielpark/Bard-API
    Bard is a GPT-3 model trained on 38 million lines of fantasy text.

    This function requires "_BARD_API_KEY" which can get from below steps:
    Go to https://bard.google.com/
        : Go to Application → Cookies → __Secure-1PSID. Copy the value of that cookie.
    """
    if os.environ.get("_BARD_API_KEY") == None:
        if configs.get("bard_key"):
            os.environ["_BARD_API_KEY"] = configs.get("bard_key")

    return Bard().get_answer(command + "\n" + text)["content"]


def load_promps(url: str = ""):
    _all_renders = []
    if isinstance(configs.get("prompt_url"), str):
        r = requests.get(configs.get("prompt_url"))
        reader = csv.DictReader(r.text.splitlines())
        _all_renders.extend(list(reader))

    if isinstance(configs.get("prompt_file"), str):
        with open(f"{configs.get('prompt_file')}", "r") as f:
            reader = csv.DictReader(f)
            _all_renders.extend(list(reader))

    if isinstance(url, str) and url.endswith(".csv"):
        r = requests.get(url)
        reader = csv.DictReader(r.text.splitlines())
        _all_renders.extend(list(reader))
    else:
        raise Exception("Invalid url")

    prompts = [Prompt(**i) for i in _all_renders]  # type: ignore
    return prompts


def make_prompt(text: str):
    json_data = {
        "inputs": f"""{text}""",
    }

    response = requests.post(
        "https://api-inference.huggingface.co/models/merve/chatgpt-prompt-generator-v12",
        json=json_data,
    )

    if response.status_code != 200:
        raise Exception(
            f"Request failed with code {response.status_code}: {response.text}"
        )
    res = response.json()
    return res[0]


def wisper(audio_file):
    with open(f"{audio_file}", "rb") as file:
        transcript = openai.Audio.transcribe("whisper-1", file)
    return transcript["text"]


def sh(command):
    return os.popen(command).read()


def print_md(markdown: str):
    md = Markdown(markdown)
    console.print(md)
