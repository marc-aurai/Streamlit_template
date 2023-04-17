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
    match_streak_home, home_team, match_streak_away, away_team
):
    plot_col1, plot_col2, plot_col3 = st.columns(3)
    try:
        with plot_col1:
            st.pyplot(
                plot_winstreak(match_streak_home, title_plt=str(home_team) + "\n")
            )
    except:
        with plot_col1:
            st.warning("Winstreak Home team not available.")
    try:
        with plot_col3:
            st.pyplot(
                plot_winstreak(match_streak_away, title_plt=str(away_team) + "\n")
            )
    except:
        with plot_col3:
            st.warning("Winstreak Away team not available.")


def generate_completion(
    openai_model,
    input_data,
    TOKENS,
    temperature_GPT,
    match_streak_home,
    home_team,
    match_streak_away,
    away_team,
):
    if str(openai_model) in ("gpt-3.5-turbo", "gpt-4"):
        generated_output = GPT_chat_completion_streaming(
            prompt=input_data,
            model_engine=openai_model,
            MAX_TOKENS=TOKENS,
            TEMP=temperature_GPT,
        )

        generate_winstreak_plots(
            match_streak_home, home_team, match_streak_away, away_team
        )

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
        generate_winstreak_plots(
            match_streak_home, home_team, match_streak_away, away_team
        )
        
        chats = st.empty()
        completion_chunks = []
        _datetime = get_datetime()
        completion_chunks.append(str(_datetime) + "\n\n")
        for chunk in generated_output:
            try:
                completion_chunks.append(chunk.choices[0])
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
