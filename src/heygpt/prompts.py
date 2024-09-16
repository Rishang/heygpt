import csv
import yaml
from dataclasses import dataclass, field
from typing import List
import requests
from pydantic import BaseModel

from heygpt.utils import log
from heygpt.constant import configs, genrtare_prompt_url


@dataclass
class Message:
    role: str
    content: str

    def __post_init__(self):
        valid_roles = ["user", "assistant", "system"]
        if self.role not in valid_roles:
            raise ValueError(f"role must be either of {valid_roles}")


@dataclass
class Prompt:
    Title: str
    Command: List[Message]
    Tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.Command = [Message(**i) for i in self.Command]  # type: ignore


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
        if prompt_url.endswith(".yaml") or prompt_url.endswith(".yml"):
            r = requests.get(prompt_url)
            _all_renders.extend(load_yaml(r.text))

    if isinstance(configs.get("prompt_file"), str):
        prompt_file = configs.get("prompt_file")
        with open(prompt_file, "r") as f:
            if prompt_file.endswith(".yaml") or prompt_file.endswith(".yml"):
                _all_renders.extend(load_yaml(f.read()))

    if isinstance(url, str):
        if url.endswith(".yaml") or url.endswith(".yml"):
            r = requests.get(url)
            _all_renders.extend(load_yaml(r.text))
    else:
        raise Exception("Invalid url")

    prompts = [Prompt(**i) for i in _all_renders]  # type: ignore

    # Sort the prompts by Title
    prompts.sort(key=lambda p: p.Title.lower())

    return prompts


def openai_fmt_prompt(messages: List[Message]):
    return [{"role": message.role, "content": message.content} for message in messages]


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
