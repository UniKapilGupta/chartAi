import streamlit as st
from components.data_loader import load_csv
from components.data_cleaner import summarize_missing_values, handle_missing_values, delete_columns
from components.chart_generator import generate_chart
from components.chat_window import chat_window

st.set_page_config(page_title="Chart App", layout="wide")
st.title("📊 Interactive Chart Generator")

# --- Initialize session state ---
if "raw_df" not in st.session_state:
    st.session_state["raw_df"] = None
if "cleaned_df" not in st.session_state:
    st.session_state["cleaned_df"] = None
if "data_cleaned" not in st.session_state:
    st.session_state["data_cleaned"] = False

# --- Add session reload option ---
with st.sidebar:
    if st.button("🔄 Restart Session"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()  # Updated from st.experimental_rerun() to st.rerun()

# --- Load Data ---
if st.session_state.get("raw_df") is None:
    uploaded_df = load_csv()
    if uploaded_df is not None:
        st.session_state["raw_df"] = uploaded_df
else:
    uploaded_df = st.session_state["raw_df"]

# --- Proceed if data is loaded ---
if uploaded_df is not None:
    st.subheader("📂 Uploaded Data Preview")
    st.dataframe(uploaded_df.head(10))

    # --- Data Cleaning Section ---
    st.subheader("🧹 Data Cleaning")

    df = (
        st.session_state["cleaned_df"]
        if st.session_state["data_cleaned"]
        else uploaded_df.copy()
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
        else uploaded_df.head(10)
    )

    # --- Generate Chart ---
    st.subheader("📈 Chart Generator")
    chart_df = (
        st.session_state["cleaned_df"]
        if st.session_state["data_cleaned"]
        else uploaded_df
    )
    chart_metadata = generate_chart(chart_df)

    # Extract metadata for chat
    chart_type = chart_metadata.get("chart_type")
    selected_cols = chart_metadata.get("selected_cols")
    group_col = chart_metadata.get("group_col")
    filters = chart_metadata.get("filters")

    # Sidebar chat window
    with st.sidebar:
        st.header("💬 AI Assistant")
        chat_window(chart_df, chart_type, selected_cols, group_col, filters)

else:
    st.info("⬆️ Please upload a dataset to get started.")
