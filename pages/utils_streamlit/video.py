import boto3
import streamlit as st

def ST_readVideo():
    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('wsc-espn-site')

        all_videos = []
        for obj in bucket.objects.filter(Delimiter='/', Prefix='uploads/'):
            all_videos.append(obj.key)
        st.text_area(all_videos)
        # all_videos.remove("test_videos_streamlit/")

        # selected_video = st.selectbox(
        #             "Selecteer video: ", all_videos
        #         )

        # obj = s3.Object("gpt-ai-tool-wsc", str(selected_video))
        # body = obj.get()['Body'].read()
        # st.video(body)

    except:
        st.write("Video not supported.")