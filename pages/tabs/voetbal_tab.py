import streamlit as st


def voetbal_tab(input_str_1: str, input_str_2: str):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(input_str_1)
    with col2:
        st.markdown(input_str_2)