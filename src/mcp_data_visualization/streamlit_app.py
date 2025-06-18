import streamlit as st
import pandas as pd
import json
from pathlib import Path
from geo_plotting import display_folium_map
import plotly.io as pio
from datetime import datetime
from mcp_data_visualization.geo_plotting import create_geo_viz
from streamlit_autorefresh import st_autorefresh
from mcp_data_visualization.plotly_plotting import create_plotly_plot
from mcp_data_visualization.geo_plotting import download_and_extract_zip, ZIP_CODE_SHAPE_DIR, ZIP_CODE_RESOURCE_URL, US_STATE_SHAPE_DIR, US_STATE_RESOURCE_URL
from mcp_data_visualization.server import VIZ_CONFIGS_FILE

# Set page config
st.set_page_config(
    page_title="Goose Data Visualization Hub",
    page_icon="📊",
    layout="wide",    
)

# # Constants
# VIZ_CONFIG_DIR=Path(tempfile.gettempdir()) / "mcp_data_visualization/viz_config"
# VIZ_CONFIG_DIR.mkdir(exist_ok=True)

# VIZ_CONFIGS_FILE = VIZ_CONFIG_DIR / "plot_configs.json"
# if not VIZ_CONFIGS_FILE.exists():
#     # Create a default configuration file
#     VIZ_CONFIGS_FILE.write_text(json.dumps([], indent=4))

# Check if the ZIP_CODE_SHAPE_DIR exists
if not ZIP_CODE_SHAPE_DIR.exists():
    print(f"{ZIP_CODE_SHAPE_DIR} does not exist. Downloading and extracting resources...")
    ZIP_CODE_SHAPE_DIR.mkdir(parents=True, exist_ok=True)
    download_and_extract_zip(ZIP_CODE_RESOURCE_URL, ZIP_CODE_SHAPE_DIR)

if not US_STATE_SHAPE_DIR.exists():
    print(f"{US_STATE_SHAPE_DIR} does not exist. Downloading and extracting resources...")
    US_STATE_SHAPE_DIR.mkdir(parents=True, exist_ok=True)
    download_and_extract_zip(US_STATE_RESOURCE_URL, US_STATE_SHAPE_DIR)

#
# 1) tell Streamlit to rerun this script every 5 000 ms
#
st_autorefresh(interval=5000, key="file_watcher")


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_plot_config_modify_time" not in st.session_state:
    st.session_state.last_plot_config_modify_time = None

def load_data(data_file_path):
    """Load the latest data and visualization config."""
    try:
        df = pd.read_csv(data_file_path, index_col=False)
        
        # Convert date columns to datetime
        date_columns = df.select_dtypes(include=['object']).columns
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                continue
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def clear_messages():
    """Clear all messages and reset state."""
    st.session_state.messages = []
    st.rerun()



def add_message(content_type, content, title=None):
    """Add a message to the chat history."""
    message = {
        "role": "assistant",
        "type": content_type,
        "content": content,
        "title": title,
        "timestamp": datetime.now()
    }
    st.session_state.messages.append(message)


def make_plot(plot_configs):
    """Create a plot based on the provided configuration."""
    # Create the plot
    if plot_configs.get("plot_library") == "plotly":
        df = load_data(plot_configs.get("data_source"))
        plot_info = create_plotly_plot(df, **plot_configs['configs'])
    elif plot_configs.get("plot_library") == "folium":
        # Assuming folium is used for geographic plots
        polygon_df = None
        point_df = None
        if plot_configs.get("polygon_data_source"):
            polygon_df = load_data(plot_configs.get("polygon_data_source"))
        if plot_configs.get("point_data_source"):
            point_df = load_data(plot_configs.get("point_data_source"))
        plot_info = create_geo_viz(polygon_df, point_df, plot_configs['configs'])
    else:
        st.error(f"Unsupported plot type: {plot_configs.get('type')}")
        return None
    
    return plot_info

def main():   
    try:
        st.title("Goose Data Visualization Hub")
        
        # Controls in sidebar
        st.sidebar.title("Controls")
        
        # Clear button
        if st.sidebar.button("Clear History"):
            clear_messages()
            return

        # Check if we have either new data or new plot config
        if (st.session_state.last_plot_config_modify_time is None or
            st.session_state.last_plot_config_modify_time != VIZ_CONFIGS_FILE.stat().st_mtime):
            
            fig_file = None
            viz_type = None
            for plot_configs in json.loads(VIZ_CONFIGS_FILE.read_text()):
                # st.write(plot_configs)
                plot_info = make_plot(plot_configs)
                # st.write(plot_info)
                if plot_info is not None:
                    viz_type = plot_info['plot_data']['plot_lib']
                    if viz_type == "plotly":
                        fig_file = plot_info['plot_data']['plot_json_file']
                    elif viz_type == "folium":
                        fig_file = plot_info['plot_data']['plot_html_file']
                add_message(viz_type, fig_file)
            
            # Update last modified times
            st.session_state.last_plot_config_modify_time = VIZ_CONFIGS_FILE.stat().st_mtime
        
        # Display messages
        for msg_idx, message in enumerate(st.session_state.messages):
            if message["role"] == "assistant":
                with st.chat_message("assistant"):
                    if message["title"]:
                        st.subheader(message["title"])
                    
                    # Display content based on type
                    content_type = message["type"]
                    content = message["content"]
                    if content_type == "plotly":
                        chart_key = f"chart_{msg_idx}"
                        fig_file_path = content
                        fig = pio.read_json(fig_file_path)
                        st.plotly_chart(fig, use_container_width=True, key=chart_key)
                    elif content_type == "folium":
                        folium_map_html_file = content
                        with open(folium_map_html_file, 'r') as f:
                            folium_map = f.read()
                        display_folium_map(folium_map)
                    st.caption(f"Generated at: {message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


    

if __name__ == "__main__":
    main()
