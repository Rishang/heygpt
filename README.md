# heygpt 🔮

A simple command line tool to generate text using OpenAI GPT-3 or Bard base on ready made templated promts.

## Purpose

- To provide a simple command line tool to generate text using GPT-3 or Bard based on ready made templated prompts, in both `cli` as well as `web-ui` interface.


## Installation

- There is a dependency of `fzf` for interactive prompt selection. You can install it using your package manager.
- refer: [fzf README](https://github.com/junegunn/fzf#installation) for more info on step to install `fzf`.

```bash
pip install heygpt
```

## Configuration

You will need openai api credentials to use `heygpt`. You can get them from [here](https://beta.openai.com/).

provide it in `.env` file as following format.

```bash
# gpt custom prompts (optional)
GPT_PROMPT_URL=<url-to-your-prompt-file>

# openai
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_ORGANIZATION=<your-openai-organization>

# bard (optional)
# ref: https://github.com/dsdanielpark/Bard-API
_BARD_API_KEY=<your-bard-api-key>
```

Here, `GPT_PROMPT_URL` is optional. If you want to use own custom prompts, you can provide a url to a `csv` file containing your prompts.
  
Note: This is the default csv used for prompts: [default-prompts.csv](https://github.com/kk-rishang/gpt-prompts/blob/main/demo.csv), for using your own prompts, you need to follow the same format as in this file.

## Usage

```bash
heygpt --help
```

## Examples

#### Asking `heygpt` to perform a cretain task based on prompt template:

```bash
heygpt ask
```

- `heygpt` will ask you to choose a prompt from a list of available templates.
- After that it will ask you to enter your query/task and will provide you with the result based on type of prompt you selected.

- If you want to see output from bard instead of openai gpt-3, you can pass `--bard` flag to `ask` command.

```bash
heygpt ask --bard
```

- For asking queries without any prompt templates you can use `--no-prompt` flag.

```bash
heygpt ask --no-prompt
```

#### Convert audio to text using `heygpt`:

```bash
heygpt wisper ../path/to/audio.mp3
```

- You can provide standard output as well to `heygpt ask`
  
  ```bash
  echo "why sky is blue" | heygpt ask --no-prompt
  ```

  An other way to use it can be providing `wisper` audio 2 text, output to `heygpt ask`:

  ```bash
  heygpt wisper ../path/to/audio.mp3 | heygpt ask
  ```

#### Using `heygpt` as a api:

```bash
heygpt serve
```

This will start a `fastapi` server on `localhost`:
