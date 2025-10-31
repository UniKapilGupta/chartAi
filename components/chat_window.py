import streamlit as st
import re
import json
from groq import Groq
from components.chart_generator import generate_chart

# Initialize Groq client
client = Groq(api_key=st.secrets["groq_api_key"])

# -------------------------------
# 🔹 Common LLM Interaction Function
# -------------------------------
def chat_with_groq(prompt, chart_context, mode="query"):
    """
    Calls Groq model.
    - mode='generate' → strict JSON chart creation
    - mode='query' → natural descriptive answers
    Returns (response_text, parsed_json or None)
    """

    if mode == "generate":
        full_prompt = f"""
        You are an AI data visualization assistant.
        You help users create charts from tabular data.

        Chart context (column names, data types, and sample data):
        {chart_context}

        User request: "{prompt}"

        Respond ONLY with a valid JSON object and nothing else.

        The JSON must strictly follow this format:
        ```json
        {{
            "intent": "plot",
            "chart_type": "<one of ['Line', 'Bar', 'Scatter', 'Histogram', 'Box', 'Violin', 'Distribution',
            'Area', 'Pie', 'Sunburst', 'Treemap', 'Heatmap']>",
            "x": "<column name or list of columns>",
            "y": "<column name or list of columns or null>",
            "color": "<group column name or null>",
            "agg": "<aggregation function like 'mean', 'sum', 'count' or null>"
        }}
        ```

        --- Chart-Specific Rules ---

        • **Line / Bar / Area / Histogram / Box**
          - Allow selecting one or more numeric columns for `"x"` (as a list).
          - Use `"y": null` since these are plotted over the index or grouped.
          - Example: {{"chart_type": "Bar", "x": ["sales", "profit"], "y": null, "color": "region", "agg": "mean"}}

        • **Scatter**
          - Must include exactly **one X** and **one Y** numeric column.
          - Example: {{"chart_type": "Scatter", "x": "area", "y": "price", "color": "region"}}

        • **Violin**
          - One categorical `"x"` and one numeric `"y"`.
          - Example: {{"chart_type": "Violin", "x": "ocean_proximity", "y": "median_income"}}

        • **Distribution**
          - Up to two numeric columns in `"x"`. `"y"` must be null.
          - Example: {{"chart_type": "Distribution", "x": ["sales", "profit"], "y": null}}

        • **Pie**
          - One categorical `"x"` for names and one numeric `"y"` for values.
          - Example: {{"chart_type": "Pie", "x": "category", "y": "sales"}}

        • **Sunburst / Treemap**
          - Hierarchical: multiple categorical columns in `"x"` as a list (e.g., ["region","category","sub_category"])
          - `"y"` can be numeric (like "sales") or null.
          - Example: {{"chart_type": "Sunburst", "x": ["region","category"], "y": "sales"}}

        • **Heatmap**
          - Select at least two numeric columns for correlation matrix.
          - `"x"` should be the list of numeric columns, `"y"` = null.
          - Example: {{"chart_type": "Heatmap", "x": ["sales","profit","discount"], "y": null}}

        --- General Rules ---
        - Always use valid JSON — no text or comments outside the JSON.
        - Match column names exactly from the chart context.
        - Use lists (["col1","col2"]) when multiple columns are needed.
        - Use null for unused fields.
        - Choose numeric columns for numeric plots, and categorical columns for groupings.
        - Do not wrap JSON in code blocks or explanations.
        """

    else:  # mode == "query"
        full_prompt = f"""
        You are an expert data analyst who explains charts in a clear, insightful way.

        The current chart context is:
        {chart_context}

        User question: "{prompt}"

        Provide a concise, human-readable analytical summary:
        - Describe key insights, trends, correlations, or outliers.
        - Use 2–3 lines maximum.
        - Avoid returning JSON or bullet points.
        - Be conversational and insightful, not technical.
        """

    # --- Call LLM ---
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.2 if mode == "query" else 0
    )

    raw_text = response.choices[0].message.content.strip()

    # --- Extract JSON only in generate mode ---
    parsed_json = None
    if mode == "generate":
        json_match = re.search(r"\{[\s\S]*\}", raw_text)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                parsed_json = None

    return raw_text, parsed_json


# -------------------------------
# 🔹 Chart Generation Chat Window
# -------------------------------
def chart_generation_chat(df, chart_type, selected_cols, group_col, filters):
    """Chat interface for generating new charts via AI."""
    st.write("### 🤖 Chart Generation Assistant")

    suggestive_queries = [
        "Visualize patterns or correlations in the dataset.",
        "Create a histogram visualization comparing all columns.",
        "Plot a line chart to show changes across all numeric columns.",
        "Visualize the spread and outliers using a box plot.",
        "Generate a heatmap showing relationships between all variables."
    ]

    cols = st.columns(2)
    for i, query in enumerate(suggestive_queries):
        with cols[i % 2]:
            if st.button(query, key=f"gen_query_{i}"):
                st.session_state["gen_user_input"] = query

    user_input = st.text_input(
        "Describe the chart you want to create:",
        value=st.session_state.get("gen_user_input", "")
    )

    if "gen_chat_history" not in st.session_state:
        st.session_state["gen_chat_history"] = []

    chart_context = f"""
    Columns: {list(df.columns)}
    Data Types: {df.dtypes.to_dict()}
    Sample: {df.head(3).to_dict()}
    """

    for msg in st.session_state["gen_chat_history"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if st.button("Generate Chart", key="gen_send"):
        if user_input.strip():
            st.session_state["gen_chat_history"].append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)

            # Step 1: Generate chart spec (JSON)
            response_text, parsed = chat_with_groq(user_input, chart_context, mode="generate")

            if parsed and parsed.get("intent") == "plot":
                st.chat_message("assistant").write(f"Creating {parsed['chart_type']} chart...")

                new_chart_metadata = {
                    "chart_type": parsed.get("chart_type"),
                    "selected_cols": [
                        col
                        for c in [parsed.get("x"), parsed.get("y")]
                        if c not in [None, "None"]
                        for col in (c if isinstance(c, list) else [c])
                        if col not in [None, "None"]
                    ],
                    "group_col": parsed.get("color"),
                    "filters": filters,
                    "agg": parsed.get("agg"),
                    "interactive": False,
                }

                # Step 2: Generate the chart
                generate_chart(df, **new_chart_metadata)

                # Step 3: Ask Groq for a 2–3 line summary of chart insights
                summary_prompt = (
                    f"Provide 2-3 bullet points summarizing the key insights from a "
                    f"{parsed['chart_type']} chart created using columns "
                    f"{new_chart_metadata['selected_cols']} grouped by {parsed.get('color')}."
                )

                summary_text, _ = chat_with_groq(summary_prompt, chart_context, mode="query")

                # Step 4: Display summary below chart
                st.markdown("#### 🔍 Key Insights:")
                st.markdown(f"<div style='background-color:#f6f8fa;padding:10px;border-radius:8px;'>"
                            f"{summary_text}</div>", unsafe_allow_html=True)

            else:
                st.chat_message("assistant").write("⚠️ Could not interpret chart request.")
                st.session_state["gen_chat_history"].append(
                    {"role": "assistant", "content": response_text}
                )


# -------------------------------
# 🔹 Chart Query Chat Window
# -------------------------------
def chart_query_chat(df, chart_type, selected_cols, group_col, filters):
    """Chat interface for analyzing existing charts."""
    st.write("### 💬 Chart Query Assistant")

    suggestive_queries = [
        "Summarize the trend in this chart.",
        "What are the key insights from this plot?",
        "Are there any outliers?",
        "Which group performs best?",
        "Explain the relationship between X and Y."
    ]

    cols = st.columns(2)
    for i, query in enumerate(suggestive_queries):
        with cols[i % 2]:
            if st.button(query, key=f"query_query_{i}"):
                st.session_state["query_user_input"] = query

    user_input = st.text_input(
        "Ask about this chart:",
        value=st.session_state.get("query_user_input", "")
    )

    if "query_chat_history" not in st.session_state:
        st.session_state["query_chat_history"] = []

    chart_context = f"""
    Chart Type: {chart_type}
    Columns: {selected_cols}
    Grouped By: {group_col}
    Filters: {filters}
    """

    for msg in st.session_state["query_chat_history"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if st.button("Send Question", key="query_send"):
        if user_input.strip():
            st.session_state["query_chat_history"].append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)

            response_text, _ = chat_with_groq(user_input, chart_context, mode="query")

            st.chat_message("assistant").write(response_text)
            st.session_state["query_chat_history"].append(
                {"role": "assistant", "content": response_text}
            )
