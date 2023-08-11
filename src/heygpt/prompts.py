import csv
from dataclasses import dataclass, field

import requests
from pydantic import BaseModel

from heygpt.utils import log
from heygpt.constant import configs, genrtare_prompt_url


@dataclass
class Prompt:
    Title: str
    Command: str
    System: str = field(default_factory=str)
    Tags: list[str] = field(default_factory=list)


class PromptInput(BaseModel):
    prompt: Prompt
    text: str


class PromptResponse(BaseModel):
    message: str


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
