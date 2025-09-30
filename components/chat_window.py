import streamlit as st
from groq import Groq

# Initialize Groq client
client = Groq(api_key=st.secrets["groq_api_key"])  # set in .streamlit/secrets.toml

def chat_with_groq(prompt, chart_context):
    # Combine the user query with chart context
    full_prompt = f"""
    You are an AI assistant that helps users analyze charts. Here is the chart context:
    {chart_context}

    User's question: {prompt}
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # you can also try "llama3-70b-8192" or other models
        messages=[{"role": "user", "content": full_prompt}]
    )
    return response.choices[0].message.content

def chat_window(df, chart_type, selected_cols, group_col, filters):
    st.subheader("Chat with AI about your Chart")
    user_input = st.text_input("Ask a question about the chart:")

    # Generate chart context
    chart_context = f"""
    Chart Type: {chart_type}
    Selected Columns: {', '.join(selected_cols) if selected_cols else 'None'}
    Grouped By: {group_col if group_col != 'None' else 'None'}
    Filters Applied: {filters if filters else 'None'}
    Data Preview: {df.head(5).to_dict()}
    """

    if st.button("Send"):
        if user_input:
            response = chat_with_groq(user_input, chart_context)
            st.text_area("AI Response", value=response, height=200)