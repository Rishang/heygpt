import os

import requests
import openai
import google.generativeai as palm
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
