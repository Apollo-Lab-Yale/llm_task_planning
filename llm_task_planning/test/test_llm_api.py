from openai import OpenAI
from llm_task_planning.llm.openai_interface import OpenAIInterface, add_messages_to_conversation

interface = OpenAIInterface()

conversation = add_messages_to_conversation(["I am testing a new interface"],  "user", [])
print(interface.query_model(conversation))