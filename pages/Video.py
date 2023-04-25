import streamlit as st
import boto3

s3 = boto3.resource('s3')
gpt_ai_bucket = s3.Bucket('gpt-ai-tool-wsc')

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
prefix = "test_videos_streamlit/"
for objects in gpt_ai_bucket.objects.filter(Prefix=prefix):
    all_videos.append(str(objects.key).replace(prefix, ''))

selected_video = st.selectbox(
            "Wedstrijd datum: ", all_videos
        )
st.writ(selected_video)

obj = s3.Object("gpt-ai-tool-wsc", "test_videos_streamlit/{}".format(selected_video))
body = obj.get()['Body'].read()
st.video(selected_video)
