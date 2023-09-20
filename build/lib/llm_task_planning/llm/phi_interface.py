from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

input_text = "I want a pddl domain for the blocksworld problem "
input_ids = tokenizer(input_text, return_tensors="pt", max_length=500, truncation=False).input_ids

outputs = model.generate(input_ids)
print([tokenizer.decode(output) for output in outputs])
