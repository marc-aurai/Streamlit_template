import streamlit as st
import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('gpt-ai-tool-wsc')

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

all_videos = []
for obj in bucket.objects.filter(Delimiter='/', Prefix='test_videos_streamlit/'):
    all_videos.append(obj.key)

selected_video = st.selectbox(
            "Wedstrijd datum: ", all_videos
        )
st.write(selected_video)

obj = s3.Object("gpt-ai-tool-wsc", str(selected_video))
body = obj.get()['Body'].read()
st.video(selected_video)
