import csv
import yaml
from dataclasses import dataclass, field
from typing import List, Union

import requests
from pydantic import BaseModel

from heygpt.utils import log
from heygpt.constant import configs, genrtare_prompt_url


@dataclass
class Prompt:
    Title: str
    Command: str
    System: str = field(default_factory=str)
    Tags: List[str] = field(default_factory=list)


class PromptInput(BaseModel):
    prompt: Prompt
    text: str


class PromptResponse(BaseModel):
    message: str


def load_prompts(url: str = ""):
    log.debug("Loading prompts...")
    _all_renders = []

    def load_csv(data: str):
        reader = csv.DictReader(data.splitlines())
        return list(reader)

    def load_yaml(data: str):
        return yaml.safe_load(data)

    if isinstance(configs.get("prompt_url"), str):
        prompt_url = configs.get("prompt_url")
        if prompt_url.endswith(".csv"):
            r = requests.get(prompt_url)
            _all_renders.extend(load_csv(r.text))
        elif prompt_url.endswith(".yaml") or prompt_url.endswith(".yml"):
            r = requests.get(prompt_url)
            _all_renders.extend(load_yaml(r.text))

    if isinstance(configs.get("prompt_file"), str):
        prompt_file = configs.get("prompt_file")
        with open(prompt_file, "r") as f:
            if prompt_file.endswith(".csv"):
                _all_renders.extend(load_csv(f.read()))
            elif prompt_file.endswith(".yaml") or prompt_file.endswith(".yml"):
                _all_renders.extend(load_yaml(f.read()))

    if isinstance(url, str):
        if url.endswith(".csv"):
            r = requests.get(url)
            _all_renders.extend(load_csv(r.text))
        elif url.endswith(".yaml") or url.endswith(".yml"):
            r = requests.get(url)
            _all_renders.extend(load_yaml(r.text))
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
