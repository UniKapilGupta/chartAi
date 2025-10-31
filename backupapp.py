import streamlit as st
from components.data_loader import load_csv
from components.data_cleaner import summarize_missing_values, handle_missing_values, delete_columns
from components.chart_generator import generate_chart
from components.chat_window import chat_window

st.set_page_config(page_title="Chart App", layout="wide")

# --- Global Header ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("📊 Interactive Chart Generator")
with col2:
    if st.button("🔄 Restart Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("---")  # visual separator below the top bar

# --- Initialize session state ---
if "raw_df" not in st.session_state:
    st.session_state["raw_df"] = None
if "cleaned_df" not in st.session_state:
    st.session_state["cleaned_df"] = None
if "data_cleaned" not in st.session_state:
    st.session_state["data_cleaned"] = False

# --- Create Tabs ---
tab1, tab2, tab3 = st.tabs(["🏠 Home", "🧹 Data Cleaning", "📈 Chart & Query"])

# ---------------------------
# 🏠 Home Tab
# ---------------------------
with tab1:
    st.header("Welcome to the Interactive Chart Generator!")
    st.markdown("""
        ### Instructions:
        1. Upload your dataset in CSV format.
        2. Navigate to the **Data Cleaning** tab to handle missing values and clean your data.
        3. Use the **Chart & Query** tab to generate charts and interact with the AI assistant.
    """)

    st.subheader("📂 Upload Your Dataset")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        uploaded_df = load_csv(uploaded_file)
        st.session_state["raw_df"] = uploaded_df

    if st.session_state.get("raw_df") is not None:
        st.subheader("📂 Uploaded Data Preview")
        st.dataframe(st.session_state["raw_df"])
    else:
        st.info("⬆️ Please upload a dataset to get started.")

# ---------------------------
# 🧹 Data Cleaning Tab
# ---------------------------
with tab2:
    if st.session_state.get("raw_df") is not None:
        st.header("🧹 Data Cleaning")

        df = (
            st.session_state["cleaned_df"]
            if st.session_state["data_cleaned"]
            else st.session_state["raw_df"].copy()
        )

        st.markdown("### Missing Value Summary")
        st.dataframe(summarize_missing_values(df))

        df = handle_missing_values(df)
        df = delete_columns(df)

        # Save cleaned data only if changes were made
        if st.session_state["data_cleaned"]:
            st.session_state["cleaned_df"] = df

        st.subheader("📂 Cleaned Data Preview")
        st.dataframe(
            st.session_state["cleaned_df"]
            if st.session_state["data_cleaned"]
            else st.session_state["raw_df"].head(10)
        )
    else:
        st.warning("Please upload a dataset in the Home tab first.")

# ---------------------------
# 📈 Chart & Query Tab
# ---------------------------
with tab3:
    if st.session_state.get("raw_df") is not None:
        st.header("📈 Chart Generator")

        chart_df = (
            st.session_state["cleaned_df"]
            if st.session_state["data_cleaned"]
            else st.session_state["raw_df"]
        )

        chart_metadata = generate_chart(chart_df)

        # Extract metadata for chat
        chart_type = chart_metadata.get("chart_type")
        selected_cols = chart_metadata.get("selected_cols")
        group_col = chart_metadata.get("group_col")
        filters = chart_metadata.get("filters")

        # --- Two-column layout for chart and chat ---
        chart_col, chat_col = st.columns([0.65, 0.35])

        with chart_col:
            st.subheader("📊 Chart View")
            st.info("Your generated chart will appear here based on selections.")
            # The generate_chart() likely already plots inside itself

        with chat_col:
            st.subheader("💬 AI Assistant")
            chat_window(chart_df, chart_type, selected_cols, group_col, filters)
    else:
        st.warning("Please upload and clean your dataset before generating charts.")
