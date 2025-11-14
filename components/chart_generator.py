import streamlit as st
import plotly.express as px
import pandas as pd

def generate_chart(
    df: pd.DataFrame,
    chart_type=None,
    selected_cols=None,
    group_col=None,
    filters=None,
    agg=None,
    interactive=True
):
    """
    Enhanced chart generation for Streamlit with fixed single/multiple column handling.
    """

    if st.session_state.get("data_cleaned", False):
        df = st.session_state.get("cleaned_df", df)

    chart_types = [
        "Line", "Bar", "Scatter", "Histogram", "Box", "Violin", "Distribution",
        "Area", "Pie", "Sunburst", "Treemap", "Heatmap"
    ]

    if interactive:
        st.subheader("Chart Configuration")

        chart_type = st.selectbox("Chart Type", chart_types,
                                  index=chart_types.index(chart_type) if chart_type in chart_types else 0)

        if chart_type == "Scatter":
            x_col = st.selectbox("X-axis Column", df.columns)
            y_col = st.selectbox("Y-axis Column", df.columns)
            selected_cols = [x_col, y_col]
        else:
            selected_cols = st.multiselect("Select Columns", df.columns)

        # Optional filters
        filter_col = st.selectbox("Filter by Column (optional)", ["None"] + list(df.columns))
        filters = None
        if filter_col != "None":
            unique_vals = df[filter_col].dropna().unique()
            selected_vals = st.multiselect(f"Select values from '{filter_col}'", unique_vals)
            if selected_vals:
                df = df[df[filter_col].isin(selected_vals)]
                filters = {filter_col: selected_vals}

        # Grouping
        group_col = st.selectbox("Group by Column (optional)", ["None"] + list(df.columns))
        agg = st.selectbox("Aggregation Function", ["mean", "sum", "count"]) if group_col != "None" else None

        if group_col != "None" and selected_cols:
            df = df.groupby(group_col)[selected_cols].agg(agg).reset_index()

        # Labels
        st.subheader("Customize Appearance")
        title = st.text_input("Chart Title", value=f"{chart_type} Chart")
        x_label = st.text_input("X-axis Label", value="Index")
        y_label = st.text_input("Y-axis Label", value=", ".join(selected_cols) if selected_cols else "")

    else:
        if filters:
            for col, vals in filters.items():
                df = df[df[col].isin(vals)]

        if group_col and group_col != "None" and selected_cols and agg:
            df = df.groupby(group_col)[selected_cols].agg(agg).reset_index()

        title = f"{chart_type} Chart(AI Generated)"
        x_label = "Index"
        y_label = ", ".join(selected_cols) if selected_cols else ""

    # --- Chart rendering ---
    fig = None

    try:
        if chart_type in ["Line", "Bar", "Area", "Histogram", "Box"]:
            # If single column: use index as X
            if len(selected_cols) == 1:
                df_plot = df.reset_index().rename(columns={"index": "Index"})
                y_col = selected_cols[0]
                if chart_type == "Line":
                    fig = px.line(df_plot, x="Index", y=y_col, title=title, labels={"Index": x_label, y_col: y_label})
                elif chart_type == "Bar":
                    fig = px.bar(df_plot, x="Index", y=y_col, title=title, labels={"Index": x_label, y_col: y_label})
                elif chart_type == "Area":
                    fig = px.area(df_plot, x="Index", y=y_col, title=title, labels={"Index": x_label, y_col: y_label})
                elif chart_type == "Histogram":
                    fig = px.histogram(df_plot, x=y_col, title=title)
                elif chart_type == "Box":
                    fig = px.box(df_plot, y=y_col, title=title)

            # If multiple columns: melt to long format
            elif len(selected_cols) > 1:
                df_melted = df.reset_index().melt(id_vars="index", value_vars=selected_cols,
                                                  var_name="Variable", value_name="Value")
                if chart_type == "Line":
                    fig = px.line(df_melted, x="index", y="Value", color="Variable", title=title,
                                  labels={"index": x_label, "Value": y_label})
                elif chart_type == "Bar":
                    fig = px.bar(df_melted, x="index", y="Value", color="Variable", title=title,
                                 labels={"index": x_label, "Value": y_label})
                elif chart_type == "Area":
                    fig = px.area(df_melted, x="index", y="Value", color="Variable", title=title,
                                  labels={"index": x_label, "Value": y_label})
                elif chart_type == "Histogram":
                    fig = px.histogram(df_melted, x="Value", color="Variable", title=title)
                elif chart_type == "Box":
                    fig = px.box(df_melted, y="Value", color="Variable", title=title)

        elif chart_type == "Scatter":
            if len(selected_cols) >= 2:
                fig = px.scatter(df, x=selected_cols[0], y=selected_cols[1], title=title)
            else:
                st.warning("Select two columns for Scatter Plot")

        elif chart_type == "Violin":
            if selected_cols:
                fig = px.violin(df, y=selected_cols[0], box=True, points="all", title=title)

        elif chart_type == "Distribution":
            if len(selected_cols) >= 2:
                fig = px.density_heatmap(df, x=selected_cols[0], y=selected_cols[1], title=title)
            elif len(selected_cols) == 1:
                fig = px.density_contour(df, x=selected_cols[0], title=title)

        elif chart_type == "Pie":
            if len(selected_cols) >= 2:
                fig = px.pie(df, names=selected_cols[0], values=selected_cols[1], title=title)
            else:
                st.warning("Select at least 2 columns for Pie Chart (names + values)")

        elif chart_type == "Sunburst":
            if len(selected_cols) >= 2:
                fig = px.sunburst(df, path=selected_cols, title=title)

        elif chart_type == "Treemap":
            if len(selected_cols) >= 2:
                fig = px.treemap(df, path=selected_cols, title=title)

        elif chart_type == "Heatmap":
            if len(selected_cols) >= 2:
                corr = df[selected_cols].corr()
                fig = px.imshow(corr, text_auto=True, title="Heatmap of Correlations")

        if fig:
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error generating {chart_type} chart: {e}")

    return {
        "chart_type": chart_type,
        "selected_cols": selected_cols,
        "group_col": group_col,
        "filters": filters,
        "agg": agg,
    }
