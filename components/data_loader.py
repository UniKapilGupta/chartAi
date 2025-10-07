import pandas as pd
import streamlit as st

def load_csv():
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file, encoding="latin1", on_bad_lines="skip")
        st.success("File loaded successfully!")
        return df
    else:
        st.info("Please upload a CSV file.")
        return None