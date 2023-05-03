import streamlit as st
from PIL import Image


def streamlit_page_config():
    st.set_page_config(
        page_title="Southfields AI",
        page_icon=Image.open("assets/image/SF_icon.png"),
        layout='wide',
        initial_sidebar_state='expanded'
    )

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

@st.cache_data(show_spinner="Een momentje...")
def load_images():
    image = Image.open('assets/image/southfields_logo.png')
    image_aurai = Image.open('assets/image/aurai_logo.png')
    return image, image_aurai


streamlit_page_config()
image, image_aurai = load_images() 
st.image(image)


st.write("# Welkom bij de AI Tools van Southfields!")

st.sidebar.success("Selecteer een Tool hierboven.")
# st.sidebar.image(image_aurai)

# st.markdown(
#     """
#     Auteur: Marc Blomvliet (Aurai) \n
#     **👈 Selecteer een Tool uit de sidebar** 
# """
# )