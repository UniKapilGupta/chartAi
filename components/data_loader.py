import pandas as pd
import streamlit as st

def load_csv(uploaded_file):
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, encoding="latin1", on_bad_lines="skip")
            st.success("File loaded successfully!")
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return None
    else:
        st.info("Please upload a CSV file.")
        return None