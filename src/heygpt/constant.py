import os
import json
from dotenv import load_dotenv

load_dotenv()

prompt_items_url = os.environ.get("GPT_PROMPT_URL", "")

genrtare_prompt_url = os.environ.get(
    "PROMPT_GENERATE_URL",
    "https://api-inference.huggingface.co/models/merve/chatgpt-prompt-generator-v12",
)


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
        if "openai_key" in configs:
            os.environ["OPENAI_API_KEY"] = configs["openai_key"]
except FileNotFoundError:
    configs = {}
