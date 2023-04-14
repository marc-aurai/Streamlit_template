import calendar
import datetime
import ast
import time

import pandas as pd
import pytz
import streamlit as st
from PIL import Image
from streamlit_chat import message as st_message

from pages.utils_streamlit.chat import GPT_3, GPT_chat_completion, GPT_chat_completion_streaming
from pages.utils_streamlit.st_login import check_password
from pages.utils_streamlit.plot_winstreak import plot_winstreak

if "message_history" not in st.session_state:
    st.session_state.message_history = []


@st.cache_data(show_spinner="Een momentje...")
def load_images():
    return Image.open("assets/image/southfields_logo.png")


@st.cache_data(show_spinner="Een momentje...")
def load_dataset() -> pd.DataFrame:  # Elke dag bijvoorbeeld als job schedulen
    df = pd.read_csv("./pages/data/eredivisie_test.csv", sep=",")
    df = df.sort_values(by="date", ascending=False)
    return df


def streamlit_page_config():
    st.set_page_config(
        page_title="Genereer Samenvatting",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


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


if check_password():
    streamlit_page_config()
    st.sidebar.success("Genereer een samenvatting op deze demo pagina.")
    image = load_images()
    df = load_dataset()
    st.image(image)
    st.write(""" # Southfields AI Tool """)

    # SIDEBAR
    TOKENS = st.sidebar.number_input(
        label="Maximum length (Tokens)", min_value=50, max_value=500, value=350
    )
    temperature_GPT = st.sidebar.number_input(
        label="Model Temperature", min_value=0.0, max_value=1.0, value=0.4
    )
    openai_model = st.sidebar.selectbox(
        "Selecteer een model",
        (
            "gpt-3.5-turbo",
            "curie:ft-southfields-2023-04-05-11-53-31",
            "davinci:ft-southfields-2023-04-07-18-26-14",
        ),
    )
    st.sidebar.success("Geselecteerd: " + str(openai_model))

    # Main page
    select1, select2 = st.columns(2)
    with select1:
        selected_match_date = st.selectbox(
            "Selecteer wedstrijd datum: ", df.date.unique().tolist()
        )
    matches_on_date = df.loc[df["date"] == selected_match_date]
    with select2:
        selected_match = st.selectbox(
            "Selecteer wedstrijd: ", matches_on_date.match.values.tolist()
        )

    match_prompt = str(df["prompt"].loc[df["match"] == selected_match].to_list()[0])
    match_streak_home = (
        df["last_six_home"].loc[df["match"] == selected_match].to_list()[0]
    )
    match_streak_away = (
        df["last_six_away"].loc[df["match"] == selected_match].to_list()[0]
    )
    home_team = df["home_team"].loc[df["match"] == selected_match].to_list()[0]
    away_team = df["away_team"].loc[df["match"] == selected_match].to_list()[0]

    select_match_injuries = df.loc[df["match"] == selected_match]
    select3, select4 = st.columns(2)
    with select3:
        injuries_home = ast.literal_eval(select_match_injuries.home_injuries.values[0])
        injuries_home = [injury for injury in injuries_home if injury != "None"]
        selected_home_injuries = st.multiselect(
            "Selecteer {} blessures: ".format(
                select_match_injuries["home_team"].values[0]
            ),
            options=injuries_home,
        )
        if selected_home_injuries:
            match_prompt = match_prompt.replace(
                "competitie.", "competitie.\n" + str("\n".join(selected_home_injuries))
            )
    with select4:
        injuries_away = ast.literal_eval(select_match_injuries.away_injuries.values[0])
        injuries_away = [injury for injury in injuries_away if injury != "None"]

        selected_away_injuries = st.multiselect(
            "Selecteer {} blessures: ".format(
                select_match_injuries["away_team"].values[0]
            ),
            options=injuries_away,
        )
        if selected_away_injuries:
            match_prompt = match_prompt.replace(
                "competitie.", "competitie.\n" + str("\n".join(selected_away_injuries))
            )

    input_data = st.text_area(
        label="Wedstrijd Data", value=match_prompt, height=400, max_chars=None
    )
    submit = st.button("Genereer")

    if submit:
        with st.spinner("Even een samenvatting aan het schrijven, momentje..."):
            if input_data != "..":
                if str(openai_model) in ("gpt-3.5-turbo", "gpt-4"):
                    generated_output = GPT_chat_completion_streaming(
                        prompt=input_data,
                        model_engine=openai_model,
                        MAX_TOKENS=TOKENS,
                        TEMP=temperature_GPT,
                    )
                    chats = st.empty()
                    completion_chunks = []
                    for chunk in generated_output:
                        try:
                            completion_chunks.append(chunk.choices[0].delta.content)
                        except:
                            completion_chunks.append("")
                        with chats.container():
                            st.write(
                            " ".join(completion_chunks))
                            #time.sleep(0.01)

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

                plot_col1, plot_col2, plot_col3 = st.columns(3)
                try:
                    with plot_col1:
                        st.pyplot(
                            plot_winstreak(
                                match_streak_home, title_plt=str(home_team) + "\n"
                            )
                        )
                except:
                    with plot_col1:
                        st.warning("Winstreak Home team not available.")
                try:
                    with plot_col3:
                        st.pyplot(
                            plot_winstreak(
                                match_streak_away, title_plt=str(away_team) + "\n"
                            )
                        )
                except:
                    with plot_col3:
                        st.warning("Winstreak Away team not available.")

                _datetime = get_datetime()
                st.session_state.message_history.append(_datetime + generated_output)
                for message_ in reversed(st.session_state.message_history):
                    st_message(
                        message_,
                        avatar_style="bottts-neutral",
                        seed="Aneka",
                        is_user=False,
                    )

    st.info(
        """Model temperature:\n - Hogere waarden zoals 0.8 zal de output meer random 
            maken\n - Lagere waarden zoals 0.2 zal de output meer gericht en deterministisch maken""",
        icon="ℹ️",
    )
