import pandas as pd
import streamlit as st

def summarize_missing_values(df):
    """Summarize missing values in the dataset."""
    missing_summary = df.isnull().sum().to_frame(name="Missing Count")
    missing_summary["Missing %"] = (missing_summary["Missing Count"] / len(df)) * 100
    return missing_summary

def handle_missing_values(df):
    """Provide options to handle missing values."""
    st.markdown("### Handle Missing Values")
    
    # Filter columns with missing values
    missing_columns = [col for col in df.columns if df[col].isnull().any()]
    
    if not missing_columns:
        st.info("No missing values found in the dataset.")
        return df

    # Create a dictionary to store default fill values
    fill_values = {}
    for col in missing_columns:
        if df[col].dtype in ["int64", "float64"]:
            fill_values[col] = df[col].mean()  # Default to mean for numerical columns
        else:
            fill_values[col] = df[col].mode()[0] if not df[col].mode().empty else ""  # Default to mode for categorical columns

    # Display a table-like interface for columns with missing values
    st.markdown("#### Fill Values for Columns with Missing Data")
    updated_fill_values = {}
    column_checkboxes = {}

    # Add a "Select All" checkbox
    select_all = st.checkbox("Select All Columns")
    
    for col in missing_columns:
        default_value = fill_values[col]
        updated_value = st.text_input(f"Fill value for '{col}'", value=str(default_value))
        updated_fill_values[col] = updated_value
        
        # Add a checkbox for each column
        column_checkboxes[col] = st.checkbox(f"Select '{col}'", value=select_all)

    # Apply the fill values to the selected columns
    if st.button("Apply"):
        selected_columns = [col for col, checked in column_checkboxes.items() if checked]
        if not selected_columns:
            st.warning("No columns selected for updating missing values.")
            return df

        for col in selected_columns:
            fill_value = updated_fill_values[col]
            if df[col].dtype in ["int64", "float64"]:
                # Convert the fill value to a numeric type for numerical columns
                fill_value = pd.to_numeric(fill_value, errors="coerce")
            df[col] = df[col].fillna(fill_value)  # Avoid inplace=True
            st.session_state["data_cleaned"] = True
        st.success(f"Updated missing values for columns: {', '.join(selected_columns)}")
    return df

def delete_columns(df):
    """Provide options to delete columns."""
    # df = st.session_state.get("cleaned_df")
    # if st.session_state["data_cleaned"]==True:
    #     # df = st.session_state["cleaned_df"]
    #     df = st.session_state.get("cleaned_df")

    st.markdown("### Delete Columns")
    import pdb
    # pdb.set_trace()
    columns_to_delete = st.multiselect("Select columns to delete:", df.columns)
    if st.button("Delete Selected Columns"):
        df = df.drop(columns=columns_to_delete)  # Avoid inplace=True
        st.session_state["data_cleaned"] = True
        st.success(f"Deleted columns: {', '.join(columns_to_delete)}")
    return df