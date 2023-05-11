import streamlit as st
from pages.utils_streamlit.AWS import get_secret

try:
    password_aws = get_secret(secret_name="dev/GPT_AI_TOOL", region="eu-central-1")
    AWS = True
except:
    AWS = False
    print("AWS password secret not found.")

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in password_aws
            and st.session_state["password"]
            == password_aws[st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Gebruikersnaam", key="username")
        st.text_input(
            "Wachtwoord", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Gebruikersnaam", on_change=password_entered, key="username")
        password_input = st.text_input(
            "Wachtwoord", type="password", on_change=password_entered, key="password"
        )
        if password_input:
            st.error("😕 Gebruiker niet herkend of wachtwoord incorrect")
            return False
    else:
        # Password correct.
        return True
