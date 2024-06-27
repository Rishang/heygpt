from heygpt.constant import prompt_items_url
from heygpt.prompts import load_prompts

prompts = load_prompts(prompt_items_url)
prompts_title = {i.Title: i.Command for i in prompts}
