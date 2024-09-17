import os

import openai
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from litellm import completion
from heygpt.constant import configs
from heygpt.prompts import openai_fmt_prompt, Message
from heygpt.utils import log, notNone

console = Console()

openai.api_key = os.getenv("OPENAI_API_KEY", configs.get("openai_key"))
openai.organization = os.getenv("OPENAI_ORG", configs.get("openai_org"))

__model__ = os.getenv("MODEL", configs.get("model"))
if notNone(__model__, str):
    model = __model__
else:
    model = "gpt-3.5-turbo"


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
    text: str = "",
    command: list[Message] = [],
    system: str = "",
    model=model,
    _print=False,
    temperature=None,
    stream=True,
):
    """
    ref: https://docs.openai.com/api-reference/completions/create
    """
    out = ""
    log.debug(f"model: {model}")
    log.debug(f"command: {command}")
    log.debug(f"system: {system}")
    log.debug(f"text: {text}")
    if system == "":
        system = "Output has to be in markdown supported format.\n"

    if not text:
        raise Exception("No text found")

    messages = openai_fmt_prompt(command)

    if messages != []:
        messages[-1]["content"] += "\n\n" + text
    else:
        messages = [{"role": "user", "content": text}]

    if stream:
        chat_completion = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )

        for chunk in chat_completion:
            # Process each chunk as needed
            c = chunk.choices[0].delta.content or ""
            out += c
            if _print:
                console.print(c, end="", markup=True)

        return out
    else:
        chat_completion = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=False,
        )

        return chat_completion.choices[0].message.content


def wisper(audio_file):
    with open(f"{audio_file}", "rb") as file:
        transcript = openai.Audio.transcribe("whisper-1", file)
    return transcript["text"]
