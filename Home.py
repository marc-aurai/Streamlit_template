import streamlit as st
from PIL import Image


def streamlit_page_config():
    st.set_page_config(
        page_title="Aurai",
        page_icon=Image.open("assets/image/aurai_logo.png"),
        layout="wide",
        initial_sidebar_state="expanded",
    )

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                button[title="View fullscreen"]{visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


@st.cache_data(show_spinner="Een momentje...")
def load_images():
    # image = Image.open("assets/image/southfields_logo.png")
    image_aurai = Image.open("assets/image/aurai_logo.png")
    return image_aurai


streamlit_page_config()
image_aurai = load_images()

st.image(image_aurai)
st.write("# Welkom bij Aurai!")
st.sidebar.success("Selecteer een Page.")
