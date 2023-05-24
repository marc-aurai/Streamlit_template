import boto3
import os
import streamlit as st
import json
import pandas as pd
import datetime as dt
import requests


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
    return df


def ST_readVideo(df, dateSelected):
    try:
        s3 = boto3.resource('s3')
        # df, s3 = videoMetaData()
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%dT%H:%M:%S.%f").dt.strftime('%a %d %b %Y')
        sorted_dates = sorted(df.date.unique().tolist(), key=lambda x: dt.datetime.strptime(x, '%a %d %b %Y'), reverse=True)


        try: # Automatically render to video date, that was selected in the main page.
            indexRender = sorted_dates.index(dateSelected, 0, len(sorted_dates))
        except:
            indexRender=0
        print(indexRender)

        selected_date = st.selectbox(
                    "Selecteer datum: ", sorted_dates,
                    index=indexRender, 

                )
        df_date = df.loc[df["date"] == selected_date]

        selectedTitle = st.selectbox(
                    "Selecteer video: ", df_date.title.values,
                )
        selected_video = df_date.loc[df_date["title"] == selectedTitle]

        try:
            with st.spinner("Video aan het ophalen.."):
                st.video("https://d3r3q57kjc1ce1.cloudfront.net/uploads/"+str(selected_video.filename.values[0])+".mp4")
            # with st.spinner("Video aan het ophalen.."):
            #     obj = s3.Object("wsc-espn-site", "uploads/"+str(selected_video.filename.values[0])+".mp4")
            #     body = obj.get()['Body'].read()
            #     st.video(body)
        except:
            st.write("Video not supported.")
    except: 
        st.write("Aub wacht even, nog aan het initialiseren..")