#!/usr/bin/env python3
import sys
from typing_extensions import Annotated
from typing import List, Optional
from pathlib import Path
import json

import uvicorn
import rich
from rich.prompt import Prompt
import typer

from heygpt.utils import log
from heygpt.constant import load_promps, prompt_items_url
from heygpt.core import (
    sh,
    completion_openai_gpt,
    completion_bard,
    make_prompt,
    wisper,
    print_md,
    ask_prompt_input,
)

app = typer.Typer(
    help="""
HeyGPT CLI\n\nA simple command line tool to generate text using OpenAI GPT-3 or Bard base on ready made templated promts.
\n\n\nFor debug logs use: `export LOG_LEVEL=DEBUG` or `set LOG_LEVEL=DEBUG` on windows."""
)


@app.command(help="Ask query or task to gpt using prompt templates")
def ask(
    bard: bool = typer.Option(False, "--bard", "-b", help="Use bard instead of gpt-3."),
    no_prompt: bool = typer.Option(
        False, "--no-prompt", "-n", help="Ask without anyprompt templates."
    ),
    text: str = typer.Option(
        str, help="Optional provide text query as an input argument."
    ),
    tag: Annotated[Optional[List[str]], typer.Option()] = [],
    save: str = typer.Option(
        "", "--output", "-o", help="save output to file availabe formats: md"
    ),
):
    tags: str = " #".join(tag)
    command: str = ""

    # print(tags)
    # return
    if not no_prompt:
        prompts = load_promps(prompt_items_url)
        log.debug(prompts)
        prompts_title = [i.Title for i in prompts]
        try:
            act = sh('echo "' + "\n".join(prompts_title) + '" | fzf -e').strip()
            if act == "":
                raise Exception("maybe fzf not present on system")
        except Exception as e:
            act = ask_prompt_input(items=prompts_title)

        if not act:
            return

        act = act.strip()
        _found_prompt = False

        for i in prompts:
            if i.Title == act:
                command = i.Command
                log.debug(command)
                _found_prompt = True
                break
        if not _found_prompt:
            rich.print(f"No prompt '{act}' found")
            return

    if tags.strip() != "":
        command += f"\nFor: #{tags}"

    if not sys.stdin.isatty():
        text = sys.stdin.read()
    elif text == "":
        rich.print(f"Selected: {command}") if not no_prompt else ...
        print()
        text = Prompt.ask("[blue]Enter text")

    # log.debug(text)
    if bard:
        content = completion_bard(command=command, text=text, _print=True)
    else:
        completion = completion_openai_gpt(command=command, text=text, _print=True)
        content = completion

    # typer.echo("\n---------- output ----------\n")

    if save != "":
        with open(f"{save}", "w") as f:
            f.write(content)
        rich.print(f"\n\nINFO: Output saved to: {save}")


@app.command(help="Generate new prompts.")
def create_prompt(text):
    data = make_prompt(text)

    rich.print(data["generated_text"])


@app.command(name="wisper", help="Generate text form audio.")
def audio2txt(audo_file: str):
    _audo_file = Path(audo_file).resolve().as_posix()
    log.debug(f"file: {_audo_file}")

    text = wisper(_audo_file)
    print()
    rich.print(text)


@app.command(help="Use heygpt as api server.")
def api():
    uvicorn.run(
        "heygpt.api:app", port=5000, host="0.0.0.0", reload=True, log_level="info"
    )


@app.command(help="Use heygpt as UI.")
def stream():
    # run streamlit app
    path = str(Path(__file__).parent) + "/serve.py"
    print(path)
    sh(f"streamlit run {path}")


@app.command(help="Configure heygpt.")
def config(
    prompt_file: str = typer.Option("", help="Prompt file path."),
    prompt_url: str = typer.Option("", help="Prompt file url."),
    openai_key: str = typer.Option("", help="OpenAI API key."),
    bard_key: str = typer.Option("", help="Bard API key."),
):
    from heygpt.constant import config_path

    if not Path(config_path).parent.is_dir():
        Path(config_path).parent.mkdir(parents=True)
    if not Path(config_path).is_file():
        with open(config_path, "w") as c:
            c.write("{}")

    with open(config_path, "r") as f:
        configs = json.loads(f.read())

    with open(config_path, "w") as f:
        new_configs = {}

        if prompt_file != "":
            configs["prompt_file"] = Path(prompt_file).absolute().as_posix()
        if prompt_url != "":
            configs["prompt_url"] = prompt_url
        if openai_key != "":
            configs["openai_key"] = openai_key
        if bard_key != "":
            configs["bard_key"] = bard_key

        new_configs = configs
        print(json.dumps(new_configs))
        f.write(json.dumps(new_configs))


if __name__ == "__main__":
    app()
