import openai

def set_api_key(api_key):
    """
        Initializes the OpenAI API with the provided API key.
        :param api_key: The API key for OpenAI.
    """
    openai.api_key = api_key


def query_model(prompt, model_name="gpt-3.5-turbo", max_tokens=150):
    """
    Queries an OpenAI model.
    :param prompt: The input prompt for the model.
    :param model_name: The name of the model to query. Default is 'text-davinci-002'.
    :param max_tokens: Maximum number of tokens in the model's response.
    :return: Model's response as a string.
    """
    response = openai.Completion.create(
        model=model_name,
        prompt=prompt,
        max_tokens=max_tokens
    )
    return response.choices[0].text.strip()