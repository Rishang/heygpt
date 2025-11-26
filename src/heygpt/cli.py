#!/usr/bin/env python3
import sys
from typing_extensions import Annotated
from typing import List, Optional
from pathlib import Path
import yaml

import uvicorn
import rich
from rich.prompt import Prompt
import typer

from heygpt.utils import log
from heygpt.constant import prompt_items_url
from litellm import completion
from heygpt.prompts import load_prompts, make_prompt, fmt_prompt
from heygpt.core import (
    model as _model,
    sh,
    wisper,
    print_md,
    ask_prompt_input,
)

app = typer.Typer(
    help="""
HeyGPT CLI\n\nA simple command line tool to generate text using LLM models (via litellm) based on ready-made templated prompts.
\n\n\nFor debug logs use: `export LOG_LEVEL=DEBUG` or `set LOG_LEVEL=DEBUG` on windows.""",
    pretty_exceptions_enable=False,
)


@app.command(help="Ask query or task to GPT using prompt templates")
def ask(
    no_prompt: bool = typer.Option(
        False, "--no-prompt", "-n", help="Ask without any prompt templates."
    ),
    text: str = typer.Option(
        str, help="Optional provide text query as an input argument."
    ),
    tag: Annotated[Optional[List[str]], typer.Option()] = [],
    save: str = typer.Option("", "--output", "-o", help="Save output to file."),
    model: str = typer.Option(
        _model,
        "--model",
        "-m",
        help=f"default {_model} | LLM model name (supports any model via litellm).",
    ),
    temperature: float = typer.Option(
        0.5,
        "--temperature",
        "-t",
        help="Temperature value for LLM, more temperature more randomness",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Print response in raw text format, default is rich markdown format",
    ),
):
    tags: str = " #".join(tag)
    command: list = []

    # print(tags)
    # return
    if not no_prompt:
        prompts = load_prompts(prompt_items_url)
        log.debug(prompts)
        prompts_title = [i.Title for i in prompts]
        try:
            act = sh('echo "' + "\n".join(prompts_title) + '" | fzf -e').strip()
            if act == "":
                raise Exception("maybe fzf not present on system")
        except Exception:
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
        text += f"\nFor: #{tags}"

    if not sys.stdin.isatty():
        text = sys.stdin.read()
    elif text == "":
        rich.print(f"[yellow]Selected:[/yellow] {command}") if not no_prompt else ...
        print()
        text = Prompt.ask("[blue]Enter text")

    # log.debug(text)
    # Build messages from command and text
    messages = fmt_prompt(command) if command else []

    if messages:
        messages[-1]["content"] += "\n\n" + text
    else:
        messages = [{"role": "user", "content": text}]

    # Determine streaming based on model
    stream_enabled = not model.startswith("o1")

    if stream_enabled:
        # Stream the response
        chat_completion = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
            drop_params=True,
        )

        content = ""
        for chunk in chat_completion:
            c = chunk.choices[0].delta.content or ""
            content += c
            if raw:
                print(c, end="", flush=True)
    else:
        # Non-streaming response
        chat_completion = completion(
            model=model,
            messages=messages,
            stream=False,
            drop_params=True,
        )
        content = chat_completion.choices[0].message.content

    if not raw:
        print_md(content)

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
    api_key: str = typer.Option(
        "", help="API key (supports OpenAI, Anthropic, etc. via litellm)."
    ),
    api_endpoint: str = typer.Option("", help="API endpoint URL."),
    openai_key: str = typer.Option(
        "", help="[Deprecated] Use --api-key instead. OpenAI API key."
    ),
    openai_endpoint: str = typer.Option(
        "", help="[Deprecated] Use --api-endpoint instead. OpenAI endpoint."
    ),
    openai_org: str = typer.Option("", help="[Deprecated] OpenAI organization id."),
    model: str = typer.Option("", help="LLM model name."),
):
    from heygpt.constant import config_path

    if not Path(config_path).parent.is_dir():
        Path(config_path).parent.mkdir(parents=True)

    # Load existing config (support YAML list format)
    loaded_yaml = []
    configs = {}

    if Path(config_path).is_file():
        with open(config_path, "r") as f:
            try:
                loaded_yaml = yaml.safe_load(f)
                if isinstance(loaded_yaml, list) and len(loaded_yaml) > 0:
                    configs = loaded_yaml[0] if isinstance(loaded_yaml[0], dict) else {}
                elif isinstance(loaded_yaml, dict):
                    configs = loaded_yaml
                    loaded_yaml = [configs]  # Convert to list format
                else:
                    loaded_yaml = []
            except yaml.YAMLError:
                loaded_yaml = []
    else:
        # Create new file with empty list
        with open(config_path, "w") as c:
            yaml.dump([], c)

    # Update configs with new values
    if prompt_file != "":
        configs["prompt_file"] = Path(prompt_file).absolute().as_posix()
    if prompt_url != "":
        configs["prompt_url"] = prompt_url
    # Support both new and deprecated options
    if api_key != "":
        configs["api_key"] = api_key
    elif openai_key != "":
        configs["api_key"] = openai_key
        configs["openai_key"] = openai_key  # Keep for backward compatibility
    if api_endpoint != "":
        configs["api_endpoint"] = api_endpoint
    elif openai_endpoint != "":
        configs["api_endpoint"] = openai_endpoint
        configs["openai_endpoint"] = openai_endpoint  # Keep for backward compatibility
    if openai_org != "":
        configs["openai_org"] = openai_org
    if model != "":
        configs["model"] = model

    # Write back as YAML list format
    output_data = [configs] if configs else []
    with open(config_path, "w") as f:
        print(yaml.dump(output_data))
        yaml.dump(output_data, f)


if __name__ == "__main__":
    app()
