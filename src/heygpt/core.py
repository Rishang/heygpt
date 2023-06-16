import os

import requests
import openai
from dotenv import load_dotenv
from bardapi import Bard
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from rich import print as pprint

from heygpt.constant import configs, genrtare_prompt_url, openai_model

console = Console()

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY", configs.get("openai_key"))


def sh(command):
    return os.popen(command).read()


def print_md(markdown: str, **kwargs):
    md = Markdown(markdown)
    console.print(md, **kwargs)


def ask_prompt_input(items: list, title="Select item"):
    completer = FuzzyWordCompleter(items)
    text = prompt(f"{title}: ", completer=completer, complete_while_typing=True)
    return text


def completion_openai_gpt(text: str = None, command: str = "", _print=False):
    out = ""

    if not text:
        raise Exception("No text found")

    completion = openai.ChatCompletion.create(
        model=openai_model,
        stream=True,
        messages=[
            {"role": "user", "content": command + "\n" + text},
        ],
        # stop="",
    )

    for chunk in completion:
        # Process each chunk as needed
        c = chunk["choices"][0]["delta"].get("content", "")
        out += c
        if _print:
            pprint(c, end="")

    return out


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


def make_prompt(text: str):
    json_data = {
        "inputs": f"""{text}""",
    }

    response = requests.post(
        genrtare_prompt_url,
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
