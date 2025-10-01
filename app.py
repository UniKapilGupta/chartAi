import streamlit as st
from components.data_loader import load_csv
from components.chart_generator import generate_chart
from components.chat_window import chat_window

st.set_page_config(page_title="Chart App", layout="wide")
st.title("📊 Interactive Chart Generator")

# Add an introduction and steps to use the app
st.markdown("""
### Welcome to the Interactive Chart Generator!
This app allows you to upload your data, generate insightful charts, and interact with an AI assistant to analyze your data.

#### How to Use:
1. **Upload Your Data**: Start by uploading a CSV file containing your dataset.
2. **Generate a Chart**: Select the columns, chart type, and other options to create a chart.
3. **Interact with AI**: Use the chat window on the left sidebar to ask questions about the chart.

#### Features:
- Supports multiple chart types.
- Provides AI-powered insights based on your data.
- Easy-to-use interface for data exploration.

---
""")

# Load dataset
df = load_csv()

if df is not None:
    # Generate chart and metadata
    chart_metadata = generate_chart(df)

    # Extract metadata for chat
    chart_type = chart_metadata.get("chart_type")
    selected_cols = chart_metadata.get("selected_cols")
    group_col = chart_metadata.get("group_col")
    filters = chart_metadata.get("filters")

    # Show chart in main area
    st.subheader("📈 Generated Chart")
    # TODO: render chart here (replace with your logic)

    # Chat window goes in sidebar
    with st.sidebar:
        st.header("💬 AI Assistant")
        chat_window(df, chart_type, selected_cols, group_col, filters)

else:
    st.info("⬆️ Please upload a dataset to get started.")
