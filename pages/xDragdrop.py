import streamlit.components.v1 as comp
import streamlit as st

from st_dragdrop_list import ST_DragDropList


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


st.title("DraggableList")

data = [
    {"id": "element_1", "order": 0, "name": "Test regel 1"},
    {"id": "element_2", "order": 1, "name": "Test regel 2"},
    {"id": "element_3", "order": 2, "name": "Test regel 3"},
]
slist = ST_DragDropList(data, key=None)
try:
    elements = [element['name'] for element in slist]
    # print(elements)
    st.write(elements)
except:
    pass