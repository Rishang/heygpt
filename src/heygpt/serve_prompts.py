from heygpt.constant import load_promps, prompt_items_url

prompts = load_promps(prompt_items_url)
prompts_title = {i.Title: i.Command for i in prompts}
