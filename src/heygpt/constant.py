import os
import csv
import json
from dataclasses import dataclass, field

from dotenv import load_dotenv
import requests
from pydantic import BaseModel
from heygpt.utils import log

load_dotenv()


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


prompt_items_url = os.environ.get(
    "GPT_PROMPT_URL",
    "https://raw.githubusercontent.com/Rishang/heygpt/main/prompts.csv",
)

genrtare_prompt_url = os.environ.get(
    "PROMPT_GENERATE_URL",
    "https://api-inference.huggingface.co/models/merve/chatgpt-prompt-generator-v12",
)

openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def get_config_path(app: str = "heygpt"):
    if os.name == "nt":  # Windows
        return os.path.expanduser(f"~\\AppData\\Roaming\\{app}\\config.json")
    elif os.name == "posix":  # Linux, macOS, etc.
        return os.path.expanduser(f"~/.config/{app}/config.json")
    else:
        raise OSError("Unsupported operating system")


config_path = get_config_path()


try:
    with open(config_path, "r") as f:
        configs = json.loads(f.read())
except FileNotFoundError:
    configs = {}


def load_promps(url: str = ""):
    log.debug("Loading prompts...")
    _all_renders = []
    if isinstance(configs.get("prompt_url"), str) and configs.get(
        "prompt_url"
    ).endswith(".csv"):
        r = requests.get(configs.get("prompt_url"))
        reader = csv.DictReader(r.text.splitlines())
        _all_renders.extend(list(reader))

    if isinstance(configs.get("prompt_file"), str) and configs.get(
        "prompt_file"
    ).endswith(".csv"):
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
