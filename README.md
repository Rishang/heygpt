# heygpt 🔮

[![Downloads](https://static.pepy.tech/personalized-badge/heygptcli?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/heygptcli)

A simple command line tool to generate text using OpenAI GPT-3 or Bard base on ready made templated promts.

## Purpose

- To provide a simple command line tool to generate text using GPT-3 or Bard based on ready made templated prompts, in both `cli` as well as `web-ui` interface.

- [CLI demo](./.github/images/demo.gif)

- [UI  demo](./.github/images/stream.png)

## Installation

- There is an optional dependency of `fzf` for interactive prompt selection. You can install it using your package manager.
- refer: [fzf README](https://github.com/junegunn/fzf#installation) for more info on step to install `fzf`.

```bash
pip install heygptcli
```

#### help page:

```bash
heygpt --help
```

For debug logs use: `export LOG_LEVEL=DEBUG` or `set LOG_LEVEL=DEBUG` on windows.

## Configuration

You will need openai api credentials to use `heygpt`. You can get them from [here](https://beta.openai.com/).


```bash
# gpt custom prompts (optional)
GPT_PROMPT_URL=<url-to-your-prompt-file>

# openai
OPENAI_API_KEY=<your-openai-api-key>

# bard (optional)
# ref: https://github.com/dsdanielpark/Bard-API
_BARD_API_KEY=<your-bard-api-key>
```

In order to configure them you can use `heygpt config` command:

```bash
❯ heygpt config --help
                                                                                                      
 Usage: heygpt config [OPTIONS]                                                                       
                                                                                                      
 Configure heygpt.                                                                                    
                                                                                                      
+─ Options ─────────────────────────────────────────────────+
│ --prompt-file        TEXT  Prompt file path.              │
│ --prompt-url         TEXT  Prompt file url.               │
│ --openai-key         TEXT  OpenAI API key <Required>.     │
│ --bard-key           TEXT  Bard API key.                  │
│ --help                     Show this message and exit.    │
+───────────────────────────────────────────────────────────+
```


```bash
heygpt config --openai-key <your-openai-api-key>
```
### Using local/remote prompts

Prompt csv formate
```csv
Title,Command
<Your title for promot>,<your command for promopt>
```

Here, `--prompt-url ` and `--prompt-file` is optional. If you want to use own custom 
prompts.


For providing a url of `csv` file containing your prompts.
  
```bash
# remote csv file
heygpt config --prompt-url <url-to-your-prompt-file.csv>
```

Note: This is the default csv used for prompts: [default-prompts.csv](./prompts.csv), for using your own prompts, you need to follow the same format as in this file.

For your own prompts by providing a url to a `csv` file containing your prompts. You can also use local `csv` file by providing a relative path to it.

```bash
# local csv file
heygpt config --prompt-file ~/path/to/prompts.csv
```

## Usage Examples

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


#### Using `heygpt` in Web-UI mode:

![](./.github/images/stream.png)

```bash
heygpt stream
```

This will start a `streamlit` server on `localhost`:


#### Using `heygpt` as a api:

```bash
heygpt api
```

This will start a `fastapi` server on `localhost`:
