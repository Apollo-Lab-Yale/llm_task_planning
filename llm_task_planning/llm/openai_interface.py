import openai
import time

def set_api_key(api_key):
    """
        Initializes the OpenAI API with the provided API key.
        :param api_key: The API key for OpenAI.
    """
    openai.api_key = api_key

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

def query_model(prompts, model_name="gpt-3.5-turbo", max_tokens=150):
    """
    Queries an OpenAI model.
    :param prompt: The input prompt for the model.
    :param model_name: The name of the model to query. Default is 'text-davinci-002'.
    :param max_tokens: Maximum number of tokens in the model's response.
    :return: Model's response as a string.
    """
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt} for prompt in prompts
        ],
        max_tokens=max_tokens
    )
    return response


