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

        # Support both api_key (new) and openai_key (legacy) for backward compatibility
        api_key = configs.get("api_key") or configs.get("openai_key")
        if configs and api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            # litellm uses OPENAI_API_KEY for OpenAI-compatible endpoints

        # Support both api_endpoint (new) and openai_endpoint (legacy)
        api_endpoint = configs.get("api_endpoint") or configs.get("openai_endpoint")
        if configs and api_endpoint:
            os.environ["OPENAI_BASE_URL"] = api_endpoint
            # For OpenRouter, set additional environment variables
            if "openrouter.ai" in api_endpoint:
                os.environ["OPENROUTER_API_BASE"] = api_endpoint
                os.environ["OPENROUTER_API_KEY"] = api_key
except FileNotFoundError:
    configs = {}
except yaml.YAMLError:  # Add YAMLError handling
    configs = {}
