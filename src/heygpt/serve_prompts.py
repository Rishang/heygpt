from heygpt.constant import prompt_items_url
from heygpt.prompts import load_promps

prompts = load_promps(prompt_items_url)
prompts_title = {i.Title: i.Command for i in prompts}
