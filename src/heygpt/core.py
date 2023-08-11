import os

import requests
import openai
import google.generativeai as palm
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter

from heygpt.constant import configs
from heygpt.utils import log, notNone

console = Console()

openai.api_key = os.getenv("OPENAI_API_KEY", configs.get("openai_key"))
openai.organization = os.getenv("OPENAI_ORG", configs.get("openai_org"))

__openai_model__ = os.getenv("OPENAI_MODEL", configs.get("openai_model"))
if notNone(__openai_model__, str):
    openai_model = __openai_model__
else:
    openai_model = "gpt-3.5-turbo"


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
    system: str = "",
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

    if "gpt-" in model:
        completion = openai.ChatCompletion.create(
            model=model,
            stream=True,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": f"Output has to be in markdown supported format.\n{system}",
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
            if _print:
                console.print(c, end="", markup=True)

    return out


def completion_palm_text(text: str, command: str = "", _print=False):
    """
    ref: https://developers.generativeai.google/api/python/google/generativeai/generate_text
    """
    if os.environ.get("PALM_API_KEY") == None:
        if configs.get("palm_key"):
            os.environ["PALM_API_KEY"] = configs.get("palm_key")

    palm.configure(api_key=os.environ.get("PALM_API_KEY"))

    defaults = {
        "model": "models/text-bison-001",
        "temperature": 0.7,
        "candidate_count": 1,
        "top_k": 40,
        "top_p": 0.95,
        "max_output_tokens": 1024,
        "stop_sequences": [],
        "safety_settings": [
            # {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 1},
            # {"category": "HARM_CATEGORY_TOXICITY", "threshold": 1},
            # {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 2},
            # {"category": "HARM_CATEGORY_SEXUAL", "threshold": 2},
            # {"category": "HARM_CATEGORY_MEDICAL", "threshold": 2},
            # {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 2},
        ],
    }
    prompt = f"""{command}

    {text}"""
    response = palm.generate_text(**defaults, prompt=prompt)

    completer = response.result
    if _print:
        print(completer)
    return completer


def wisper(audio_file):
    with open(f"{audio_file}", "rb") as file:
        transcript = openai.Audio.transcribe("whisper-1", file)
    return transcript["text"]
