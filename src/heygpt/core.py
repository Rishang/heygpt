import os

import requests
import openai
from bardapi import Bard
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter

from heygpt.constant import configs, genrtare_prompt_url, openai_model
from heygpt.utils import log

console = Console()

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


def completion_openai_gpt(
    text: str = None,
    command: str = "",
    model=openai_model,
    _print=False,
    temperature=0.7,
):
    """
    ref: https://docs.openai.com/api-reference/completions/create
    """
    out = ""
    log.debug(f"model: {model}")

    if not text:
        raise Exception("No text found")

    if command != "":
        _command = command + "\n\n" + text
    else:
        _command = text

    if "gpt-3" in model:
        completion = openai.ChatCompletion.create(
            model=model,
            stream=True,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": "Output has to be in markdown supported format",
                },
                {"role": "user", "content": _command},
            ],
            # stop="",
        )

        for chunk in completion:
            # Process each chunk as needed
            c = chunk["choices"][0]["delta"].get("content", "")
            out += c
            if _print:
                console.print(c, end="", markup=True)
    else:
        completion = openai.Completion.create(
            model=model,
            prompt=_command,
            temperature=temperature,
            max_tokens=1000,
            stream=True,
            top_p=1,
        )
        for chunk in completion:
            c = chunk["choices"][0]["text"]
            out += c
            console.print(c, end="", markup=True)

    return out


def completion_bard(text: str, command: str = "", _print=False):
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

    completer = Bard().get_answer(command + "\nTask: " + text)["content"]
    if _print:
        print_md(completer)
    return completer


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
