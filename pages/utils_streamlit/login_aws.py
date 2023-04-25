import streamlit as st
import boto3
import json

client = boto3.client('secretsmanager')
response = client.get_secret_value(
    SecretId='dev/GPT_AI_TOOL'
)

secretDictAWS = json.loads(response['SecretString'])

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in secretDictAWS["password"]
            and st.session_state["password"]
            == secretDictAWS["password"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Gebruiker niet herkend of wachtwoord incorrect")
        return False
    else:
        # Password correct.
        return True
