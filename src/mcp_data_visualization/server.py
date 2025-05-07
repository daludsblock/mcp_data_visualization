from mcp.server.fastmcp import FastMCP
import os
import sys
import subprocess
import threading
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import tempfile


# Update the instructions for your MCP server
instructions = """
This is the instruction / prompt for your MCP server. Include instructions on when to use this MCP server and what it can do.
""".strip()

# Create an MCP server
mcp = FastMCP("mcp_data_visualization", instructions=instructions)

VIZ_CONFIG_DIR=Path(tempfile.gettempdir()) / "mcp_data_visualization/viz_config"
VIZ_CONFIGS_FILE = Path(tempfile.gettempdir()) / "mcp_data_visualization/viz_config/plot_configs.json"


def start_streamlit():
    """
    Launch the streamlit subprocess.
    """
    # Adjust this path so that it points at your Streamlit script
    here    = os.path.dirname(__file__)
    script  = os.path.join(here, "streamlit_app.py")
    cmd     = [
        sys.executable,
        "-m", "streamlit",
        "run", script,
        "--server.port=8501",                # adjust port if you like
        "--browser.serverAddress=127.0.0.1", # optional
    ]
    # Use Popen so that it doesn't block this thread
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@mcp.tool()
def open_plot_ui()->Dict[str, Any]:
    """
    Launches the Streamlit app for data visualization.
    """

    # Create the directory if it doesn't exist
    if not VIZ_CONFIG_DIR.exists():
        VIZ_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not VIZ_CONFIGS_FILE.exists():
    # Create a default configuration file
        VIZ_CONFIGS_FILE.write_text(json.dumps([], indent=4))
    
    t = threading.Thread(target=start_streamlit, daemon=True)
    t.start()
    time.sleep(2)
    return {"status": "success", "message": "Plot UI launched successfully"}

# Tool for chart plotting with Plotly
@mcp.tool()
def create_chart_plot(
    data_file_path: str,
    plot_type: str,
    x: str,
    y=None,
    title=None,
    color=None,
    size=None,
    facet_col=None,
    facet_row=None,
    category_orders=None,
    labels=None,
    hover_data=None,
    text=None,
    color_discrete_map=None,
    color_continuous_scale=None,
    range_x=None,
    range_y=None,
    log_x=None,
    log_y=None,
    error_x=None,
    error_y=None,
    trendline=None,
    marginal_x=None,
    marginal_y=None,
    custom_data=None,
    animation_frame=None,
    animation_group=None,
    symbol=None,
    pattern_shape=None,
    multiple_y=None,
    **kwargs
) -> Dict[str, Any]:
    """
    Creates an advanced plot from the provided data.
    
    Args:
        data_file_path: Path to the data file (CSV)
        plot_type: Type of plot (line, bar, scatter, box, histogram, pie, etc.)
        x: Column name for x-axis
        y: Column name for y-axis (optional for some plots like histogram)
        title: Plot title
        color: Column name to use for color mapping
        size: Column name to use for size mapping (for scatter plots)
        facet_col: Column name for faceting by column
        facet_row: Column name for faceting by row
        category_orders: Dictionary to specify the order of categorical variables
        labels: Dictionary mapping column names to displayed labels
        hover_data: List of column names to show on hover
        text: Column name to use for text labels
        color_discrete_map: Dictionary mapping categories to colors
        color_continuous_scale: Name of a plotly color scale
        range_x: List with min and max values for x-axis
        range_y: List with min and max values for y-axis
        log_x: Whether to use log scale for x-axis
        log_y: Whether to use log scale for y-axis
        error_x: Column name for x-axis error bars
        error_y: Column name for y-axis error bars
        trendline: Type of trendline to add ('ols', 'lowess', etc.)
        marginal_x: Type of marginal plot for x-axis ('histogram', 'box', etc.)
        marginal_y: Type of marginal plot for y-axis ('histogram', 'box', etc.)
        custom_data: List of column names for custom data
        animation_frame: Column name to use for animation frames
        animation_group: Column name to identify same objects across animation frames
        symbol: Column name to use for symbol mapping
        pattern_shape: Column name to use for pattern shape mapping
        multiple_y: List of column names to plot multiple y-axes
        **kwargs: Additional plotting parameters
        
    Returns:
        Dictionary containing plot data and layout
    """

    """
    Creates an advanced plot from the provided data.
    """
    # Create a dictionary with all arguments
    plot_args = locals()

    # Remove 'kwargs' from the dictionary as it's already included
    plot_args.pop("kwargs", None)

    # Remove 'data' from the dictionary as it's not needed in the JSON
    plot_args.pop("data_file_path", None)

    # Add any additional keyword arguments to the dictionary
    plot_args.update(kwargs)
    
    # Create the directory if it doesn't exist
    if not VIZ_CONFIG_DIR.exists():
        VIZ_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not VIZ_CONFIGS_FILE.exists():
        # Create a default configuration file
        VIZ_CONFIGS_FILE.write_text(json.dumps([], indent=4))

    with open(VIZ_CONFIGS_FILE, 'w') as f:
        json.dump([{
            "name": "test_plot",
            "plot_library": "plotly",
            "data_source": data_file_path,
            "configs": plot_args
        }], f, indent=4)
        
    return {"status": "success", "message": "Plot created successfully"}


@mcp.tool()
def create_geo_viz(
        polygon_data_file_path=None,
        point_data_file_path=None,
        point_lat = None,
        point_lon = None,
        polygon_join_col = None,
        polygon_value_col = None,
        point_popup_fields: Optional[List[str]] = None,
        polygon_popup_fields: Optional[List[str]] = None,
        map_center = [39.8283, -98.5795],
        map_zoom = 4,
    ) -> Dict[str, Any]:
        """
        Create a geographic visualization.

        Args:
            polygon_data_file_path (Optional[str]): Path to the file containing polygon data.
            point_data_file_path (Optional[str]): Path to the file containing point data.
            point_lat (Optional[str]): Column name for latitude in the point data file.
            point_lon (Optional[str]): Column name for longitude in the point data file.
            polygon_join_col (Optional[str]): Column name used to join polygon geometry with data. Currently only supports US zip codes as the joining column.
            polygon_value_col (Optional[str]): Column name containing values to display on polygons.
            point_popup_fields (Optional[List[str]]): List of column names to display in popups for points.
            polygon_popup_fields (Optional[List[str]]): List of column names to display in popups for polygons.
            map_center (List[float]): Coordinates [latitude, longitude] for the initial map center. Defaults to [39.8283, -98.5795].
            map_zoom (int): Initial zoom level for the map. Defaults to 4.

        Returns:
            Dict[str, Any]: A dictionary containing the status and configuration of the geographic visualization.
        """
        geo_config = {
            "name": "test_geo_plot", 
            "plot_library": "folium",
            "configs": {
                "map_settings": {
                    "center": map_center,
                    "zoom": map_zoom,
                    "style": "CartoDB positron"
                }
            }
        }

        if polygon_data_file_path is None and point_data_file_path is None:
            return {
                "status": "error",
                "message": "At least one of the point or polygon data sources must be provided."
            }

        if polygon_data_file_path is not None and polygon_join_col is not None:
            geo_config["polygon_data_source"] = polygon_data_file_path
            geo_config["configs"]["polygon_settings"] = {}
            geo_config["configs"]["polygon_settings"]["location_column"] = polygon_join_col
            if polygon_value_col is not None:
                geo_config["configs"]["polygon_settings"]["value_column"] = polygon_value_col
            if polygon_popup_fields is not None:
                geo_config["configs"]["polygon_settings"]["popup_fields"] = polygon_popup_fields
        elif polygon_data_file_path is not None and polygon_join_col is None:
            return {
                "status": "error",
                "polygon_data_file_path": polygon_data_file_path,
                "message": "For plotting polygon data, the column used to join for polygon geomotry is missing."
            }

        if point_data_file_path is not None and point_lat is not None and point_lon is not None:   
            geo_config["point_data_source"] = point_data_file_path
            geo_config["configs"]["point_settings"] = {}
            geo_config["configs"]["point_settings"]["coordinates"] = {
                "lat": point_lat,
                "lon": point_lon
            }
            if point_popup_fields is not None:
                geo_config["configs"]["point_settings"]["popup_fields"] = point_popup_fields
        elif point_data_file_path is not None and (point_lat is None or point_lon is None):
            return {
                "status": "error",
                "message": "For plotting point data, the latitude and longitude columns are missing."
            }
            
        # Create the directory if it doesn't exist
        if not VIZ_CONFIG_DIR.exists():
            VIZ_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not VIZ_CONFIGS_FILE.exists():
            # Create a default configuration file
            VIZ_CONFIGS_FILE.write_text(json.dumps([], indent=4))


        with open(VIZ_CONFIGS_FILE, 'w') as f:
            json.dump([geo_config], f, indent=4)
        
        return {"status": "success", "message": "Geo plot created successfully"}

# Static resource
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"