import streamlit as st
import boto3

s3 = boto3.resource('s3')

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
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

streamlit_page_config()
st.sidebar.success("Bekijk een video op deze pagina.")

obj = s3.Object("gpt-ai-tool-wsc", "test_videos_streamlit/Goal by Luuk de Jong.mp4")
#body = obj.get()['Body'].read()
video_file = open(obj, 'rb')
video_bytes = video_file.read()

st.video(video_bytes)
