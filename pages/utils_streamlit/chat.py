import openai
import streamlit as st


openai.api_key = st.secrets['OPENAI_KEY']

def GPT_3(prompt, model_engine, MAX_TOKENS, TEMP):
    """This function interacts with th OpenAI  API through HTTP request. 
    The model will respond with a completion.

    Args:
        prompt (str): The prompt that has been created by OPTA data, soccer_pipeline and the
        creation of the user input.
        model_engine (str): Name of the model that the user selected.
        MAX_TOKENS (int): Maximum of characters/tokens in the output (1000 tokens is about 750 words)
        TEMP (float) = internal parameter for the language model we use.
        Creation of randomness (Higher value) or make the model more focused (Lower value).

    Returns:
        str: The response of GPT 3
    """
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=MAX_TOKENS, 
        n=1,
        stop=None,
        temperature=TEMP,
        stream=True
    )
    return completion

def GPT_chat_completion(prompt, model_engine, MAX_TOKENS, TEMP):
    """This function interacts with th OpenAI  API through HTTP request. 
    The model will respond with a completion.

    Args:
        prompt (str): The prompt that has been created by OPTA data, soccer_pipeline and the
        creation of the user input.
        model_engine (str): Name of the model that the user selected.
    """
    user_prompt = {
        "role": "user",
        "content": prompt
    }
    completion = openai.ChatCompletion.create(
        model=model_engine,
        messages=[user_prompt],
        max_tokens=MAX_TOKENS, 
        temperature=TEMP
    )
    return "\n" + str(completion.choices[0].message.content)


def GPT_chat_completion_streaming(prompt, model_engine, MAX_TOKENS, TEMP):
    """This function interacts with th OpenAI  API through HTTP request. 
    The model will respond with a completion.

    Args:
        prompt (str): The prompt that has been created by OPTA data, soccer_pipeline and the
        creation of the user input.
        model_engine (str): Name of the model that the user selected.
    """
    user_prompt = {
        "role": "user",
        "content": prompt
    }
    completion = openai.ChatCompletion.create(
        model=model_engine,
        messages=[user_prompt],
        max_tokens=MAX_TOKENS, 
        temperature=TEMP,
        stream=True
    )
    return completion