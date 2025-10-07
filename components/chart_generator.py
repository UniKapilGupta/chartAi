import streamlit as st
import plotly.express as px
import pandas as pd

def generate_chart(df: pd.DataFrame):
    # Use the cleaned DataFrame from session state if available
    if st.session_state["data_cleaned"]==True:
        # df = st.session_state["cleaned_df"]
        df = st.session_state.get("cleaned_df")
    print("here is my current data")
    print(df)
    st.subheader("Chart Configuration")
    import pdb
    # pdb.set_trace()
    chart_type = st.selectbox(
        "Chart Type",
        ["Line", "Bar", "Scatter", "Histogram", "Box", "Violin", "Distribution"]
    )

    # --- Column selection ---
    if chart_type == "Scatter":
        x_col = st.selectbox("X-axis Column", df.columns, key="scatter_x")
        y_col = st.selectbox("Y-axis Column", df.columns, key="scatter_y")
        selected_cols = [x_col, y_col]
    elif chart_type in ["Histogram", "Distribution", "Box", "Violin"]:
        selected_cols = st.multiselect("Select Columns", df.columns)
    else:
        selected_cols = st.multiselect("Select Columns to Plot", df.columns)

    # --- Optional filters ---
    filter_col = st.selectbox("Filter by Column (optional)", ["None"] + list(df.columns))
    filters = None
    if filter_col != "None":
        unique_vals = df[filter_col].dropna().unique()
        selected_vals = st.multiselect(f"Select values from '{filter_col}'", unique_vals)
        if selected_vals:
            df = df[df[filter_col].isin(selected_vals)]
            filters = {filter_col: selected_vals}

    # --- Optional grouping ---
    group_col = st.selectbox("Group by Column (optional)", ["None"] + list(df.columns))
    agg_func = st.selectbox("Aggregation Function", ["mean", "sum", "count"]) if group_col != "None" else None

    if group_col != "None" and selected_cols:
        df = df.groupby(group_col)[selected_cols].agg(agg_func).reset_index()

    # --- Chart customization ---
    st.subheader("Customize Appearance")
    title = st.text_input("Chart Title", value=f"{chart_type} Chart")
    default_x = (
        group_col if group_col != "None" else (selected_cols[0] if selected_cols else "")
    )
    x_label = st.text_input("X-axis Label", value=default_x)
    y_label = st.text_input("Y-axis Label", value=", ".join(selected_cols))

    # --- Generate chart ---
    fig = None
    if chart_type == "Line":
        fig = px.line(
            df,
            x=group_col if group_col != "None" else df.index,
            y=selected_cols,
            title=title,
            labels={default_x: x_label, "value": y_label}
        )
    elif chart_type == "Bar":
        fig = px.bar(
            df,
            x=group_col if group_col != "None" else df.index,
            y=selected_cols,
            title=title,
            labels={default_x: x_label, "value": y_label}
        )
    elif chart_type == "Scatter":
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=group_col if group_col != "None" else None,
            title=title,
            labels={x_col: x_label, y_col: y_label}
        )
    elif chart_type == "Histogram":
        if len(selected_cols) == 1:
            fig = px.histogram(
                df, x=selected_cols[0], color=group_col if group_col != "None" else None,
                title=title, labels={selected_cols[0]: x_label}
            )
        elif len(selected_cols) > 1:
            fig = px.histogram(
                df.melt(value_vars=selected_cols),
                x="value", color="variable",
                title=title, labels={"value": "Value", "variable": "Variable"}
            )
    elif chart_type == "Distribution":
        # Kernel Density Estimate plot
        if len(selected_cols) == 1:
            fig = px.density_contour(
                df, x=selected_cols[0], title=title, labels={selected_cols[0]: x_label}
            )
        elif len(selected_cols) >= 2:
            fig = px.density_heatmap(
                df, x=selected_cols[0], y=selected_cols[1], title=title,
                labels={selected_cols[0]: x_label, selected_cols[1]: y_label}
            )
    elif chart_type == "Box":
        if selected_cols:
            fig = px.box(
                df, y=selected_cols, x=group_col if group_col != "None" else None,
                title=title, labels={"variable": "Variable", "value": y_label}
            )
    elif chart_type == "Violin":
        if selected_cols:
            fig = px.violin(
                df, y=selected_cols[0], x=group_col if group_col != "None" else None,
                box=True, points="all",
                title=title, labels={selected_cols[0]: y_label}
            )

    if fig:
        st.plotly_chart(fig, use_container_width=True)

    # Return chart metadata
    return {
        "chart_type": chart_type,
        "selected_cols": selected_cols,
        "group_col": group_col,
        "filters": filters
    }