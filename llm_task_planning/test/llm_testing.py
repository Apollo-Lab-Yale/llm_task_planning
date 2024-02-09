from llm_task_planning.llm.openai_interface import setup_openai, query_model, add_messages_to_conversation

setup_openai()
prompt = [f"In what room should I look for a dirty mug?"]

messages = add_messages_to_conversation(prompt, "user", [], mode="context_engine")

print(query_model(messages, N=15))
print(messages)