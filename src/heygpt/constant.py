import os
import yaml  # type: ignore
from dotenv import load_dotenv

load_dotenv()

prompt_items_url = os.environ.get("GPT_PROMPT_URL", "")

genrtare_prompt_url = os.environ.get(
    "PROMPT_GENERATE_URL",
    "https://api-inference.huggingface.co/models/merve/chatgpt-prompt-generator-v12",
)


def get_config_path(app: str = "heygpt"):
    if os.name == "nt":  # Windows
        return os.path.expanduser(f"~\\AppData\\Roaming\\{app}\\config.yaml")
    elif os.name == "posix":  # Linux, macOS, etc.
        return os.path.expanduser(f"~/.config/{app}/config.yaml")
    else:
        raise OSError("Unsupported operating system")


config_path = get_config_path()

try:
    with open(config_path, "r") as f:
        loaded_yaml = yaml.safe_load(f)
        if isinstance(loaded_yaml, list) and len(loaded_yaml) > 0:
            configs = loaded_yaml[0]  # Use the first item in the list
        elif isinstance(loaded_yaml, dict):  # Keep support for old dict format for now
            configs = loaded_yaml
        else:
            configs = {}  # Default to empty dict if not a list or dict

        if configs and "openai_key" in configs:
            os.environ["OPENAI_API_KEY"] = configs["openai_key"]
        if configs and "openai_endpoint" in configs:
            os.environ["OPENAI_BASE_URL"] = configs.get(
                "openai_endpoint", "https://api.openai.com/v1"
            )
            if "https://openrouter.ai/api/v1" in configs.get("openai_endpoint", ""):
                os.environ["OPENROUTER_API_BASE"] = configs["openai_endpoint"]
                os.environ["OPENROUTER_API_KEY"] = configs["openai_key"]
except FileNotFoundError:
    configs = {}
except yaml.YAMLError:  # Add YAMLError handling
    configs = {}
