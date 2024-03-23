import openai
from openai import OpenAI
import time
import base64
import numpy as np
import cv2

def set_api_key(api_key):
    """
        Initializes the OpenAI API with the provided API key.
        :param api_key: The API key for OpenAI.
    """
    openai.api_key = api_key

def get_openai_key():
    file_path = "/usr/config/llm_task_planning.txt"
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline()
            return first_line.strip()
    except:
        raise "failed to find api key."

def setup_openai():
    file_path = "/usr/config/llm_task_planning.txt"
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline()
            set_api_key(first_line.strip())
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except IOError as e:
        print(f"An error occurred while reading the file: {str(e)}")

def query_model(messages, model_name="gpt-3.5-turbo", image=None, N = 1, logProbs = False):
    """
    Queries an OpenAI model.
    :param prompt: The input prompt for the model.
    :param model_name: The name of the model to query. Default is 'text-davinci-002'.
    :param max_tokens: Maximum number of tokens in the model's response.
    :return: Model's response as a string.
    """
    if image is not None:
        from io import BytesIO
        image = np.array(image)
        retval, buffer = cv2.imencode('.png', image)
        base64_image = base64.b64encode(buffer.tobytes()).decode('utf-8')

        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "This is my current view."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        })
    # print(messages)
    if logProbs:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            timeout = 2,
            max_tokens=1000,
            logprobs=logProbs,
            top_logprobs=N)
    else:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            timeout=0.5,
            max_tokens=1000,
            logprobs=logProbs,
            temperature=0.5)
    return response

def add_messages_to_conversation(messages, speaker, conversation, mode= "action_selection"):
    total_message_size = 0
    for message in messages:
        conversation.append({
            "role": speaker,
            "content": str(message)
        })
    total_message_size = sum(len(message["content"]) for message in conversation)
    if total_message_size > 15000:
        conversation = conversation[len(conversation)//2:]
    if mode =="action_selection":
        conversation.insert(0, {
            "role": 'system',
            "content": "You are helping me select my next action, take your time and verify that the action you select is part of the list I provide. Take your time and go step by step."
        })
    elif mode == "context_engine":
        conversation.insert(0, {
            "role": 'system',
            "content": "Please answer the following question in as few tokens as possible."
        })
    return conversation

class OpenAIInterface:
    def __init__(self):
        self.client = OpenAI(api_key = get_openai_key(), timeout=10)

    def query_model(self, messages, model_name="gpt-4-1106-preview", image=None, N=1, logProbs=False):
            """
            Queries an OpenAI model.
            :param prompt: The input prompt for the model.
            :param model_name: The name of the model to query. Default is 'text-davinci-002'.
            :param max_tokens: Maximum number of tokens in the model's response.
            :return: Model's response as a string.
            """
            if image is not None:
                from io import BytesIO
                image = np.array(image)
                retval, buffer = cv2.imencode('.png', image)
                base64_image = base64.b64encode(buffer.tobytes()).decode('utf-8')

                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is my current view."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                })
            # print(messages)
            try:
                if logProbs:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        timeout=10,
                        max_tokens=1000,
                        logprobs=logProbs,
                        top_logprobs=N)
                else:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        timeout=10,
                        max_tokens=1000,
                        logprobs=logProbs,
                        temperature = 1)
            except openai.APITimeoutError as e:
                response = None
                print("Api timed out")
            return response