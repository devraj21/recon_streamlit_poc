import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import logging
from pathlib import Path

# Only use console logging initially
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
MAX_FILE_SIZE = 50  # in MB

# Page configuration
st.set_page_config(
    page_title="Recon File Configuration",
    page_icon="🔄",
    layout="wide"
)

def main():
    st.title("Recon File Comparison Configuration")

    # File Information
    st.header("File Information")
    col1, col2 = st.columns(2)
    
    with col1:
        file1_name = st.text_input("First File Name (e.g., transactions.csv)")
        file1 = st.file_uploader("Upload First File", type=['csv', 'xlsx', 'xls'])
        
    with col2:
        file2_name = st.text_input("Second File Name (e.g., records.csv)")
        file2 = st.file_uploader("Upload Second File", type=['csv', 'xlsx', 'xls'])

    # Process files if uploaded
    if file1 is not None and file2 is not None:
        try:
            # Read files
            if file1.name.endswith('.csv'):
                df1 = pd.read_csv(file1)
            else:
                df1 = pd.read_excel(file1)
                
            if file2.name.endswith('.csv'):
                df2 = pd.read_csv(file2)
            else:
                df2 = pd.read_excel(file2)

            # Display column information
            st.header("Column Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("File 1 Columns")
                st.write(df1.columns.tolist())
            
            with col2:
                st.subheader("File 2 Columns")
                st.write(df2.columns.tolist())

            # Column Mapping Configuration
            st.header("Column Mapping Configuration")
            
            # Initialize mapping list
            if 'mappings' not in st.session_state:
                st.session_state.mappings = [{"file1_col": "", "file2_col": "", "is_key": False}]

            # Add mapping button
            if st.button("Add New Mapping"):
                st.session_state.mappings.append({"file1_col": "", "file2_col": "", "is_key": False})

            # Mapping interface
            mappings_to_remove = []
            for idx, mapping in enumerate(st.session_state.mappings):
                col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
                
                with col1:
                    mapping["file1_col"] = st.selectbox(
                        "File 1 Column",
                        [""] + df1.columns.tolist(),
                        key=f"file1_col_{idx}"
                    )
                
                with col2:
                    mapping["file2_col"] = st.selectbox(
                        "File 2 Column",
                        [""] + df2.columns.tolist(),
                        key=f"file2_col_{idx}"
                    )
                
                with col3:
                    mapping["is_key"] = st.checkbox(
                        "Join Key",
                        key=f"is_key_{idx}"
                    )
                
                with col4:
                    if st.button("Remove", key=f"remove_{idx}"):
                        mappings_to_remove.append(idx)

            # Remove marked mappings
            for idx in reversed(mappings_to_remove):
                st.session_state.mappings.pop(idx)

            # Filter Conditions
            st.header("Filter Conditions")
            
            # Initialize filters list
            if 'filters' not in st.session_state:
                st.session_state.filters = [{"file": "", "column": "", "operator": "", "value": ""}]

            # Add filter button
            if st.button("Add New Filter"):
                st.session_state.filters.append({"file": "", "column": "", "operator": "", "value": ""})

            # Filter interface
            filters_to_remove = []
            for idx, filter_condition in enumerate(st.session_state.filters):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                
                with col1:
                    filter_condition["file"] = st.selectbox(
                        "File",
                        ["", "File 1", "File 2"],
                        key=f"filter_file_{idx}"
                    )
                
                with col2:
                    columns = df1.columns.tolist() if filter_condition["file"] == "File 1" else df2.columns.tolist() if filter_condition["file"] == "File 2" else []
                    filter_condition["column"] = st.selectbox(
                        "Column",
                        [""] + columns,
                        key=f"filter_col_{idx}"
                    )
                
                with col3:
                    filter_condition["operator"] = st.selectbox(
                        "Operator",
                        ["equals", "not equals", "greater than", "less than", "contains"],
                        key=f"filter_op_{idx}"
                    )
                
                with col4:
                    filter_condition["value"] = st.text_input(
                        "Value",
                        key=f"filter_val_{idx}"
                    )
                
                with col5:
                    if st.button("Remove", key=f"remove_filter_{idx}"):
                        filters_to_remove.append(idx)

            # Remove marked filters
            for idx in reversed(filters_to_remove):
                st.session_state.filters.pop(idx)

            # Generate JSON button
            if st.button("Generate JSON Configuration"):
                config = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "file_configuration": {
                        "file1": {
                            "name": file1_name or file1.name,
                            "columns": df1.columns.tolist(),
                            "total_rows": len(df1)
                        },
                        "file2": {
                            "name": file2_name or file2.name,
                            "columns": df2.columns.tolist(),
                            "total_rows": len(df2)
                        }
                    },
                    "column_mappings": [
                        {
                            "file1_column": m["file1_col"],
                            "file2_column": m["file2_col"],
                            "is_join_key": m["is_key"]
                        } for m in st.session_state.mappings if m["file1_col"] and m["file2_col"]
                    ],
                    "filter_conditions": [
                        {
                            "file": f["file"],
                            "column": f["column"],
                            "operator": f["operator"],
                            "value": f["value"]
                        } for f in st.session_state.filters if all(f.values())
                    ]
                }

                # Save configuration to file
                output_dir = Path("outputs")
                output_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_path = output_dir / f"reconciliation_config_{timestamp}.json"
                
                with open(json_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Display JSON
                st.header("Generated JSON Configuration")
                st.json(config)
                
                # Download button
                st.download_button(
                    label="Download JSON Configuration",
                    data=json.dumps(config, indent=2),
                    file_name=f"reconciliation_config_{timestamp}.json",
                    mime="application/json"
                )

        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            logger.error(f"Error processing files: {str(e)}")
    else:
        st.info("Please upload both files to proceed with configuration.")

if __name__ == "__main__":
    main()