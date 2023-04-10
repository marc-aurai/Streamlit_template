import openai
import streamlit as st

openai.api_key = st.secrets['OPENAI_KEY']

def GPT_3(prompt, model_engine, MAX_TOKENS, TEMP):
    """
    max_tokens = Maximum of characters/tokens in the output (1000 tokens is about 750 words)
    n = amount of answers
    stop = Because we are define no stopping rules.
    temperature = internal parameter for the language model we use.

    Args:
        prompt (str): Your question to the language model

    Returns:
        str: The response of GPT 3
    """
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=MAX_TOKENS, 
        n=1,
        stop=None,
        temperature=TEMP
    )
    return completion.choices[0].text

def GPT_chat_completion(user_prompt, model_engine, MAX_TOKENS, TEMP):
    """_summary_

    Args:
        prompt (_type_): _description_
        model_engine (_type_): _description_
    """
    prompt = {
        "role": "user",
        "content": user_prompt
    }
    completion = openai.ChatCompletion.create(
        model=model_engine,
        messages=[prompt],
        max_tokens=MAX_TOKENS, 
        temperature=TEMP
    )
    return completion.choices[0].message.content
