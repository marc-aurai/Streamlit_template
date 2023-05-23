import boto3
import os
import streamlit as st
import json
import pandas as pd
import datetime as dt


def videoMetaData():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('wsc-espn-site')

    all_videos = []
    for obj in bucket.objects.filter(Delimiter='/', Prefix='uploads/'):
        if ".mp4" in obj.key:
            all_videos.append(str(obj.key).replace(".mp4", ".json"))

    videoData = []
    for file in all_videos:
        obj = s3.Object('wsc-espn-site', file)
        data = obj.get()['Body'].read().decode('utf-8')
        json_data = json.loads(data)
        file_name = file.strip("uploads/")
        file_name = file_name.strip(".json")
        videoData.append([file_name, json_data["title"], json_data["publishDate"]])

    df = pd.DataFrame(videoData, columns=["filename", "title", "date"]).sort_values(by="date", ascending=False)
    return df, s3

def ST_readVideo():
    try:
        df, s3 = videoMetaData()
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%dT%H:%M:%S.%f").dt.strftime('%a %d %b %Y')
        sorted_dates = sorted(df.date.unique().tolist(), key=lambda x: dt.datetime.strptime(x, '%a %d %b %Y'), reverse=True)

        selected_date = st.selectbox(
                    "Selecteer datum: ", sorted_dates
                )
        df_date = df.loc[df["date"] == selected_date]


        selectedTitle = st.selectbox(
                    "Selecteer video: ", df_date.title.values
                )
        selected_video = df_date.loc[df_date["title"] == selectedTitle]
        try:
            obj = s3.Object("wsc-espn-site", "uploads/"+str(selected_video.filename.values[0])+".mp4")
            body = obj.get()['Body'].read()
            st.video(body)
        except:
            st.write("Video not supported.")
    except: 
        st.write("Aub wacht even, nog aan het initialiseren..")