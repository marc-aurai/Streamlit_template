import streamlit as st
import boto3

s3 = boto3.client('s3')
# gpt_ai_bucket = s3.Bucket('gpt-ai-tool-wsc')

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
response = s3.list_objects_v2(
    Bucket='gpt-ai-tool-wsc',
    Prefix='test_videos_streamlit/')

for content in response.get('Contents', []):
    all_videos.append(content['Key'])

selected_video = st.selectbox(
            "Video: ", all_videos
        )

obj = s3.Object("gpt-ai-tool-wsc", "test_videos_streamlit/{}".format(selected_video))
body = obj.get()['Body'].read()
st.video(selected_video)
