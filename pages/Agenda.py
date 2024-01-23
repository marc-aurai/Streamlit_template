import streamlit as st

def streamlit_page_config():
    st.set_page_config(
        page_title="Video",
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
    #st.markdown(hide_streamlit_style, unsafe_allow_html=True)

streamlit_page_config()

selected_data = st.date_input("Kies een datum")

print(selected_data)