import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("OpenAssistant/llama2-13b-orca-8k-3319", use_fast=False)
model = AutoModelForCausalLM.from_pretrained("OpenAssistant/llama2-13b-orca-8k-3319", torch_dtype=torch.float16, low_cpu_mem_usage=True, device_map="auto")

system_message = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
user_prompt = "Write me a poem please"
prompt = f"""<|system|>{system_message}</s><|prompter|>{user_prompt}</s><|assistant|>"""
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
output = model.generate(**inputs, do_sample=True, top_p=0.95, top_k=0, max_new_tokens=256)
print(tokenizer.decode(output[0], skip_special_tokens=True))

