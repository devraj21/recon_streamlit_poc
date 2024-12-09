import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import logging
from pathlib import Path
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_svg_content(svg_path):
    """
    Read SVG file and process it for both header and tab icon use.
    We need different formats for different purposes:
    - Header: Needs proper sizing and styling for visible display
    - Tab Icon: Needs to be more compact and browser-friendly
    """
    try:
        with open(svg_path, "r") as svg_file:
            svg_content = svg_file.read()
            
            # Create a tab-optimized version of the SVG
            # This ensures the SVG is properly scaled for favicon use
            tab_svg = svg_content.replace('<svg', '<svg viewBox="0 0 32 32"')
            
            return svg_content, tab_svg
    except Exception as e:
        logger.error(f"Error reading SVG file: {str(e)}")
        return None, None

def render_svg_icon(svg_content):
    """
    Convert SVG content to a base64 encoded image for the header display.
    The header needs a larger, more visible version of the icon.
    """
    if svg_content:
        b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        html = f'''
            <div style="display: flex; justify-content: left; align-items: left; height: 200px;">
                <img src="data:image/svg+xml;base64,{b64}"
                     style="height: 200px; width: 200px; object-fit: contain; margin: auto;"
                />
            </div>
        '''
        return html
    return None

# Get the image path relative to the script
current_dir = Path(__file__).parent
image_path = current_dir / "assets" / "FacctumLogo.svg"
#image_path = Path("/app/assets/facct_icon.svg")
#logger.info(f'image path is: {image_path}')
#logging.debug(f'{image_path=}')

# Page configuration with custom SVG icon
if image_path and image_path.exists():
    # Get both versions of the SVG content
    header_svg, tab_svg = get_svg_content(str(image_path))
    
    if header_svg and tab_svg:
        # Set up the page with the tab-optimized SVG
        st.set_page_config(
            page_title="FacctRecon Configuration",
            page_icon=tab_svg,  # Using the tab-optimized version
            layout="wide"
        )
        
        # Render the header icon with the full-size SVG
        icon_html = render_svg_icon(header_svg)
        if icon_html:
            st.markdown(icon_html, unsafe_allow_html=True)
    else:
        st.set_page_config(
            page_title="FacctRecon Configuration",
            page_icon="🔄",
            layout="wide"
        )
else:
    st.set_page_config(
        page_title="FacctRecon Configuration",
        page_icon="🔄",
        layout="wide"
    )

# # Page configuration
# st.set_page_config(
#     page_title="FacctRecon Configuration",
#     page_icon=icon,
#     layout="wide"
# )

# # Display custom CSS to ensure proper SVG rendering
# st.markdown("""
#     <style>
#         /* Custom styling for SVG icon */
#         .stApp > header {
#             background-color: transparent !important;
#         }
        
#         /* Specific styling for the header SVG icon */
#         .stApp > header svg {
#             width: 32px !important;
#             height: 32px !important;
#             display: block !important;
#             margin: auto !important;
#             fill: currentColor !important;
#             stroke: currentColor !important;
#             visibility: visible !important;
#             opacity: 1 !important;
#         }
        
#         /* Ensure SVG container is visible */
#         .stApp > header div:first-child {
#             display: flex !important;
#             align-items: center !important;
#             justify-content: center !important;
#             visibility: visible !important;
#             opacity: 1 !important;
#         }
        
#         /* Override any default hiding */
#         .stApp > header [data-testid="stHeader"] {
#             visibility: visible !important;
#             display: flex !important;
#         }
#     </style>
# """, unsafe_allow_html=True)

# Constants
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
MAX_FILE_SIZE = 50  # in MB

def initialize_session_state():
    """Initialize all session state variables for both journey and file comparison"""
    if 'journey_name' not in st.session_state:
        st.session_state.journey_name = ""
    if 'categories' not in st.session_state:
        st.session_state.categories = []
    if 'subcategories' not in st.session_state:
        st.session_state.subcategories = {}
    if 'filters' not in st.session_state:
        st.session_state.filters = []
    if 'mappings' not in st.session_state:
        st.session_state.mappings = []

def add_category():
    """Add a new category to the journey configuration"""
    new_category = st.session_state.new_category_input  # Get value from input widget
    if new_category and new_category not in st.session_state.categories:
        st.session_state.categories.append(new_category)
        st.session_state.subcategories[new_category] = []
        st.session_state.new_category_input = ""  # Reset input
        logger.info(f"Added new category: {new_category}")

def add_subcategory(category, subcategory_name):
    """Add a new subcategory to a specified category"""
    if subcategory_name and subcategory_name not in st.session_state.subcategories[category]:
        st.session_state.subcategories[category].append(subcategory_name)
        logger.info(f"Added new subcategory {subcategory_name} to category {category}")

def handle_category_addition():
    """
    Callback function to handle category addition.
    This function is called when the Add Category button is clicked.
    """
    if st.session_state.category_input:  # Check if input is not empty
        new_category = st.session_state.category_input
        if new_category not in st.session_state.categories:
            st.session_state.categories.append(new_category)
            st.session_state.subcategories[new_category] = []
            logger.info(f"Added new category: {new_category}")

def render_journey_config():
    """Render the journey configuration section with simplified structure"""
    st.header("Journey Details")
    
    # Journey Name
    st.session_state.journey_name = st.text_input(
        "Journey Name",
        value=st.session_state.journey_name
    )
    
    # Category Section
    st.subheader("Categories")
    
    # New Category Input using columns
    col1, col2 = st.columns([3, 1])
    with col1:
        # Use a simple key for the text input
        st.text_input(
            "New Category Name",
            key="category_input",
            placeholder="Enter category name"
        )
    with col2:
        # Use the callback function with the button
        st.button("Add Category", 
                 key="add_category_button",
                 on_click=handle_category_addition)
    
    # Display existing categories
    if st.session_state.categories:
        for category in st.session_state.categories:
            st.markdown("---")
            st.markdown(f"### Category: {category}")
            
            # Subcategory section
            st.markdown("#### Subcategories")
            subcategory_col1, subcategory_col2 = st.columns([3, 1])
            with subcategory_col1:
                new_subcategory = st.text_input(
                    "New Subcategory Name",
                    key=f"new_subcategory_{category}",
                    placeholder="Enter subcategory name"
                )
            with subcategory_col2:
                if st.button("Add Subcategory", key=f"add_subcategory_{category}"):
                    add_subcategory(category, new_subcategory)
            
            # Display subcategories
            for subcategory in st.session_state.subcategories.get(category, []):
                st.markdown(f"##### • {subcategory}")

def add_filter():
    """Add a new filter to the file comparison section"""
    if 'new_filter' not in st.session_state:
        st.session_state.new_filter = {
            'source': 'source1',
            'column': '',
            'operator': 'equals',
            'value': ''
        }
    st.session_state.filters.append(st.session_state.new_filter.copy())
    logger.info("Added new filter")

def render_file_comparison():
    """Render the file comparison section with added filter functionality"""
    st.header("Recon Configuratioin")
    
    # File Upload Section
    col1, col2 = st.columns(2)
    with col1:
        source1 = st.text_input("Source 1 Name", key="source1")
        file1 = st.file_uploader("Upload Source 1 File", type=['csv', 'xlsx', 'xls'])
    
    with col2:
        source2 = st.text_input("Source 2 Name", key="source2")
        file2 = st.file_uploader("Upload Source 2 File", type=['csv', 'xlsx', 'xls'])

    if file1 is not None and file2 is not None:
        try:
            # Read files
            df1 = pd.read_csv(file1) if file1.name.endswith('.csv') else pd.read_excel(file1)
            df2 = pd.read_csv(file2) if file2.name.endswith('.csv') else pd.read_excel(file2)

            # Column Mapping Section
            st.subheader("Column Mapping")
            if st.button("Add New Mapping"):
                st.session_state.mappings.append({
                    "file1_col": "",
                    "file2_col": "",
                    "is_join_key": False,
                    "is_recon_key": False
                })

            # Display mappings
            mappings_to_remove = []
            for idx, mapping in enumerate(st.session_state.mappings):
                col1, col2, col3, col4, col5 = st.columns([3, 3, 1.5, 1.5, 1])
                
                with col1:
                    mapping["file1_col"] = st.selectbox(
                        "Source 1 Column",
                        [""] + df1.columns.tolist(),
                        key=f"file1_col_{idx}"
                    )
                
                with col2:
                    mapping["file2_col"] = st.selectbox(
                        "Source 2 Column",
                        [""] + df2.columns.tolist(),
                        key=f"file2_col_{idx}"
                    )
                
                with col3:
                    mapping["is_join_key"] = st.checkbox(
                        "Join Key",
                        key=f"is_join_key_{idx}"
                    )
                
                with col4:
                    mapping["is_recon_key"] = st.checkbox(
                        "Recon Key",
                        key=f"is_recon_key_{idx}"
                    )
                
                with col5:
                    if st.button("Remove", key=f"remove_mapping_{idx}"):
                        mappings_to_remove.append(idx)

            for idx in reversed(mappings_to_remove):
                st.session_state.mappings.pop(idx)

            # Filter Section
            st.subheader("Filters")
            if st.button("Add Filter"):
                add_filter()

            # Display filters
            filters_to_remove = []
            for idx, filter_item in enumerate(st.session_state.filters):
                st.markdown("---")
                cols = st.columns([2, 2, 2, 2, 1])
                
                with cols[0]:
                    filter_item['source'] = st.selectbox(
                        "Source",
                        ["source1", "source2"],
                        key=f"filter_source_{idx}"
                    )
                
                with cols[1]:
                    df = df1 if filter_item['source'] == 'source1' else df2
                    filter_item['column'] = st.selectbox(
                        "Column",
                        df.columns.tolist(),
                        key=f"filter_column_{idx}"
                    )
                
                with cols[2]:
                    filter_item['operator'] = st.selectbox(
                        "Operator",
                        ["equals", "not equals", "greater than", "less than", "contains"],
                        key=f"filter_operator_{idx}"
                    )
                
                with cols[3]:
                    filter_item['value'] = st.text_input(
                        "Value",
                        key=f"filter_value_{idx}"
                    )
                
                with cols[4]:
                    if st.button("Remove", key=f"remove_filter_{idx}"):
                        filters_to_remove.append(idx)

            for idx in reversed(filters_to_remove):
                st.session_state.filters.pop(idx)

            # Add configuration buttons at the end of File Comparison tab
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate Configuration"):
                    config = generate_config_json()
                    st.header("Generated Configuration")
                    st.json(config)
                    
                    # Save configuration
                    output_dir = Path("outputs")
                    output_dir.mkdir(exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_path = output_dir / f"facct_config_{timestamp}.json"
                    
                    with open(json_path, 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    with col2:
                        st.download_button(
                            label="Download Configuration",
                            data=json.dumps(config, indent=2),
                            file_name=f"facct_config_{timestamp}.json",
                            mime="application/json"
                        )

        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            logger.error(f"Error processing files: {str(e)}")

def generate_config_json():
    """Generate the complete configuration JSON"""
    config = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "journey_name": st.session_state.journey_name,
        "categories": {
            category: {
                "subcategories": st.session_state.subcategories.get(category, [])
            }
            for category in st.session_state.categories
        },
        "file_configuration": {
            "mappings": [
                {
                    "file1_column": m["file1_col"],
                    "file2_column": m["file2_col"],
                    "is_join_key": m["is_join_key"],
                    "is_recon_key": m["is_recon_key"]
                }
                for m in st.session_state.mappings
                if m["file1_col"] and m["file2_col"]
            ],
            "filters": st.session_state.filters
        }
    }
    return config

def main():
    st.title("FacctRecon Configuration")
    
    # Initialize session state
    initialize_session_state()
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Journey Details", "Recon Configuration"])
    
    with tab1:
        render_journey_config()
    
    with tab2:
        render_file_comparison()

if __name__ == "__main__":
    main()