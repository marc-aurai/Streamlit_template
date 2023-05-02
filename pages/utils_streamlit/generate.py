import calendar
import datetime
import pytz

import streamlit as st
from streamlit_chat import message as st_message
from pages.utils_streamlit.chat import (
    GPT_3,
    GPT_chat_completion,
    GPT_chat_completion_streaming,
)
from pages.utils_streamlit.plot_winstreak import plot_winstreak


def get_datetime() -> str:
    """This function returns the current time (hour:minutes:seconds), 
    it is used to give the match summaries a timestamp in the Streamlit UI.

    Returns:
        str: A unique Timestamp
    """
    created_at = datetime.datetime.now(pytz.timezone("Europe/Amsterdam"))
    created_at_formatted = (
        str(calendar.month_name[created_at.month])
        + " "
        + str(created_at.day)
        + ": "
        + str(created_at.strftime("%H:%M:%S"))
    )
    return created_at_formatted


def generate_winstreak_plots(
    match_streak_home: str, home_team: str, match_streak_away: str, away_team: str
):
    """Creates two plots in the Streamlit UI with a indication for: win, lose and draw.

    Args:
        match_streak_home (str): The result of the last 6 matches. (Home team)
        home_team (str): Home team name
        match_streak_away (str): The result of the last 6 matches. (Away team)
        away_team (str): Away team name
    """
    plot_col1, plot_col2, plot_col3 = st.columns(3)
    # try:
    with plot_col1:
        st.pyplot(
            plot_winstreak(match_streak_home, title_plt=str(home_team) + "\n")
        )
    # except:
    #     with plot_col1:
    #         st.warning("Winstreak Home team not available.")
    try:
        with plot_col3:
            st.pyplot(
                plot_winstreak(match_streak_away, title_plt=str(away_team) + "\n")
            )
    except:
        with plot_col3:
            st.warning("Winstreak Away team not available.")


def generate_completion(
    openai_model: str,
    input_data: str,
    TOKENS: int,
    temperature_GPT: float,
    match_streak_home: str,
    home_team: str,
    match_streak_away: str,
    away_team: str,
):
    """This function will be called, when the button 'Genereer' has been pushed in the 
    Streamlit UI.

    Args:
        openai_model (str): Name of the model that the user selected.
        input_data (str): The prompt that has been created by OPTA data, soccer_pipeline and the
        creation of the user input.
        TOKENS (int): Amount of tokens that will be used to generate a summary.
        temperature_GPT (float): Creation of randomness (Higher value) or 
        make the model more focused (Lower value).
        match_streak_home (str): The result of the last 6 matches. (Home team)
        home_team (str): Home team name
        match_streak_away (str): The result of the last 6 matches. (Away team)
        away_team (str): Away team name
    """
    if str(openai_model) in ("gpt-3.5-turbo", "gpt-4"):
        generated_output = GPT_chat_completion_streaming(
            prompt=input_data,
            model_engine=openai_model,
            MAX_TOKENS=TOKENS,
            TEMP=temperature_GPT,
        )

        # generate_winstreak_plots(
        #     match_streak_home, home_team, match_streak_away, away_team
        # )

        chats = st.empty()
        completion_chunks = []
        _datetime = get_datetime()
        completion_chunks.append(str(_datetime) + "\n\n")
        for chunk in generated_output:
            try:
                completion_chunks.append(chunk.choices[0].delta.content)
            except:
                completion_chunks.append("")
            with chats.container():
                st.write("".join(completion_chunks).strip())

        st.session_state.message_history.append("".join(completion_chunks).strip())

    if str(openai_model) in (
        "curie:ft-southfields-2023-04-05-11-53-31",
        "davinci:ft-southfields-2023-04-07-18-26-14",
    ):
        generated_output = GPT_3(
            prompt=input_data,
            model_engine=openai_model,
            MAX_TOKENS=TOKENS,
            TEMP=temperature_GPT,
        )
        # generate_winstreak_plots(
        #     match_streak_home, home_team, match_streak_away, away_team
        # )
        
        chats = st.empty()
        completion_chunks = []
        _datetime = get_datetime()
        completion_chunks.append(str(_datetime) + "\n\n")
        for chunk in generated_output:
            try:
                completion_chunks.append(chunk.choices[0].text)
            except:
                completion_chunks.append("")
            with chats.container():
                st.write("".join(completion_chunks).strip())

        st.session_state.message_history.append("".join(completion_chunks).strip())

    for message_ in reversed(st.session_state.message_history):
        st_message(
            message_,
            avatar_style="bottts-neutral",
            seed="Aneka",
            is_user=False,
        )
    return "".join(completion_chunks).strip()