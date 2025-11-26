import os

from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from litellm import completion, transcription
from heygpt.constant import configs
from heygpt.utils import notNone

console = Console()

# Set API key for litellm (litellm uses OPENAI_API_KEY by default for OpenAI-compatible endpoints)
api_key = (
    os.getenv("OPENAI_API_KEY") or configs.get("api_key") or configs.get("openai_key")
)
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

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


# Export litellm completion and other utilities for direct use
__all__ = ["completion", "model", "print_md", "wisper", "sh", "ask_prompt_input"]


def wisper(audio_file):
    """
    Transcribe audio file using litellm (supports whisper models).
    """
    with open(f"{audio_file}", "rb") as file:
        # litellm supports transcription via the transcription function
        # Use whisper-1 model for transcription
        response = transcription(
            model="whisper-1",
            file=file,
        )
    return response["text"]
