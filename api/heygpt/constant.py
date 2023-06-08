import os

prompt_items_url = os.environ.get(
    "GPT_PROMPT_URL",
    "https://raw.githubusercontent.com/kk-rishang/gpt-prompts/main/demo.csv",
)


def get_config_path(app: str = "heygpt"):
    if os.name == "nt":  # Windows
        return os.path.expanduser(f"~\\AppData\\Roaming\\{app}\\config.json")
    elif os.name == "posix":  # Linux, macOS, etc.
        return os.path.expanduser(f"~/.config/{app}/config.json")
    else:
        raise OSError("Unsupported operating system")


config_path = get_config_path()
