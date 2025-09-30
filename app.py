import streamlit as st
from components.data_loader import load_csv
from components.chart_generator import generate_chart
from components.chat_window import chat_window

st.set_page_config(page_title="Chart App", layout="wide")
st.title("📊 Interactive Chart Generator")

df = load_csv()

if df is not None:
    # Generate the chart and get metadata
    chart_metadata = generate_chart(df)

    # Extract metadata for the chat window
    chart_type = chart_metadata.get("chart_type")
    selected_cols = chart_metadata.get("selected_cols")
    group_col = chart_metadata.get("group_col")
    filters = chart_metadata.get("filters")

    # Display the chat window
    chat_window(df, chart_type, selected_cols, group_col, filters)