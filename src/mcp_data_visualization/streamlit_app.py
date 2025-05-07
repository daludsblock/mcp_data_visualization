import streamlit as st
import pandas as pd
import json
from pathlib import Path
from streamlit_folium import folium_static
from datetime import datetime
from mcp_data_visualization.geo_plotting import create_geo_viz
from streamlit_autorefresh import st_autorefresh
from mcp_data_visualization.plotly_plotting import create_plotly_plot
import os


# Set page config
st.set_page_config(
    page_title="Goose Data Visualization Hub",
    page_icon="📊",
    layout="wide",    
)

#
# 1) tell Streamlit to rerun this script every 5 000 ms
#
st_autorefresh(interval=5000, key="file_watcher")

# Constants
DATA_DIR = Path(__file__).parent / "data"
VIZ_CONFIGS_FILE = DATA_DIR / "plot_configs.json"


# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

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
    viz_type = None
    # Create the plot
    if plot_configs.get("plot_library") == "plotly":
        df = load_data(plot_configs.get("data_source"))
        fig = create_plotly_plot(df, **plot_configs['configs'])
        viz_type = "chart"
    elif plot_configs.get("plot_library") == "folium":
        # Assuming folium is used for geographic plots
        polygon_df = None
        point_df = None
        if plot_configs.get("polygon_data_source"):
            polygon_df = load_data(plot_configs.get("polygon_data_source"))
        if plot_configs.get("point_data_source"):
            point_df = load_data(plot_configs.get("point_data_source"))
        fig = create_geo_viz(polygon_df, point_df, plot_configs['configs'])
        viz_type = "map"
    else:
        st.error(f"Unsupported plot type: {plot_configs.get('type')}")
        return None, None
    
    return fig, viz_type

def main():   
    st.title("Goose Data Visualization Hub")
    
    # Controls in sidebar
    st.sidebar.title("Controls")
    
    # Clear button
    if st.sidebar.button("Clear History"):
        clear_messages()
        return

    
    # Calculate current data hash
    # current_hash = get_data_hash(df)
    
    # Check if we have new data to visualize and auto-generate is enabled
    # if current_hash != st.session_state.last_data_hash and st.session_state.auto_generate:
    #     # Add visualization
    #     content = create_plot(df, viz_config)
    #     add_message("visualization", content, viz_config.get('title', 'Data Visualization'))
        
    #     # Add geographic visualization if available
    #     if geo_config is not None:
    #         content = create_geo_viz(df_geo_polygons, df_geo_points, geo_config)
    #         add_message("geographic", content, "Geographic Distribution of Checkout Rates")
        
    #     st.session_state.last_data_hash = current_hash

    # check if we have either new data or new plot config
    if (st.session_state.last_plot_config_modify_time is None or
        st.session_state.last_plot_config_modify_time != VIZ_CONFIGS_FILE.stat().st_mtime):
        
        fig = None
        viz_type = None
        for plot_configs in json.loads(VIZ_CONFIGS_FILE.read_text()):
            fig, viz_type = make_plot(plot_configs)
            add_message(viz_type, fig)
        
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
                if content_type == "chart":
                    chart_key = f"chart_{msg_idx}"
                    st.plotly_chart(content, use_container_width=True, key=chart_key)
                elif content_type == "map":
                    folium_static(content)
                st.caption(f"Generated at: {message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")


    

if __name__ == "__main__":
    main()
