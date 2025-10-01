import streamlit as st
from groq import Groq

# Initialize Groq client
client = Groq(api_key=st.secrets["groq_api_key"])

def chat_with_groq(prompt, chart_context):
    full_prompt = f"""
    You are an AI assistant that helps users analyze charts. Here is the chart context:
    {chart_context}

    User's question: {prompt}
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": full_prompt}]
    )
    return response.choices[0].message.content

def chat_window(df, chart_type, selected_cols, group_col, filters):
    # Suggested queries
    suggestive_queries = [
        "What is the trend in the data?",
        "Can you summarize the chart?",
        "What are the key insights from the chart?",
        "Are there any anomalies in the data?",
        "How does the data vary across groups?"
    ]

    st.write("### Suggested Questions:")
    for query in suggestive_queries:
        if st.button(query, key=f"query_{query}"):
            st.session_state["user_input"] = query

    # Input field
    user_input = st.text_input("Ask a question about the chart:", value=st.session_state.get("user_input", ""))

    # Context for the model
    chart_context = f"""
    Chart Type: {chart_type}
    Selected Columns: {', '.join(selected_cols) if selected_cols else 'None'}
    Grouped By: {group_col if group_col else 'None'}
    Filters Applied: {filters if filters else 'None'}
    Data Preview: {df.head(5).to_dict()}
    """

    if st.button("Send", key="send_button"):
        if user_input:
            response = chat_with_groq(user_input, chart_context)
            st.text_area("AI Response", value=response, height=200)
