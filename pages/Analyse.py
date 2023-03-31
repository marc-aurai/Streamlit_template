import pandas as pd
import seaborn as sns
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

from analysis.utils.analyse_plots import plot_all_axes

sns.set(
    rc={
        "axes.facecolor": "#100c44",
        "figure.facecolor": "#100c44",
        "xtick.color": "white",
        "ytick.color": "white",
        "text.color": "white",
        "axes.labelcolor": "white",
        "font.size": 30,
        "axes.titlesize": 30,
        "axes.labelsize": 30,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
    }
)


@st.cache_data(show_spinner="Een momentje...")
def load_images():
    image = Image.open("assets/image/southfields_logo.png")
    return image


@st.cache_data(show_spinner="Een momentje...")
def load_dataset():
    df = pd.read_csv("./espn_scraper/scraper_data/articles_ereD_notna.csv", sep=";")
    df["word_count"] = df["article"].apply(lambda x: len(x.split()))
    return df


def streamlit_page_config():
    st.set_page_config(page_title="Analyse Dashboard", page_icon="📊")
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


streamlit_page_config()
image = load_images()
df = load_dataset()
st.image(image)

st.write(""" # South-Fields Analyse """)
selected_sport = st.sidebar.multiselect(
    "Selecteer een type sport:",
    max_selections=1,
    options=df.cup.unique(),
    default="2022-23 Eredivisie, Regulier seizoen",
)

amount_words = st.sidebar.slider(
    "Aantal 'meest' voorkomende woorden", max_value=20, min_value=3, value=10
)

with st.spinner("Een momentje..."):
    if selected_sport != []:
        fig = plt.figure(figsize=(16, 50))
        ax1 = fig.add_subplot(4, 1, 1)
        ax2 = fig.add_subplot(4, 1, 2)
        #ax3 = fig.add_subplot(5, 1, 3)
        ax4 = fig.add_subplot(4, 1, 3)
        ax5 = fig.add_subplot(4, 1, 4)
        plt.subplots_adjust(hspace=0.5)

        ax1, ax2, ax4, ax5 = plot_all_axes(
            ax1=ax1,
            ax2=ax2,
            ax4=ax4,
            ax5=ax5,
            df=df,
            amount_words=amount_words,
        )

        st.pyplot(fig, clear_figure=True)
