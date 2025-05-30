import streamlit as st
import geopandas as gpd
import folium
from pathlib import Path
import streamlit.components.v1 as components
import tempfile
import requests
import zipfile
import zipcodes
import pycountry
us_states = {s.code.split('-')[-1] for s in
             pycountry.subdivisions.get(country_code='US')}

FIGURE_DIR = Path(tempfile.gettempdir()) / 'mcp_data_visualization/figures'

GEO_SHAPE_DIR = Path(tempfile.gettempdir()) / 'resources/geo'

ZIP_CODE_SHAPE_DIR = GEO_SHAPE_DIR / 'tl_2024_us_zcta520'
ZIP_CODE_SHAPEFILE = ZIP_CODE_SHAPE_DIR / 'tl_2024_us_zcta520.shp'
ZIP_CODE_RESOURCE_URL = "https://www2.census.gov/geo/tiger/TIGER2024/ZCTA520/tl_2024_us_zcta520.zip"

US_STATE_SHAPE_DIR = GEO_SHAPE_DIR / 'us_states'
US_STATE_RESOURCE_URL = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip"
US_STATE_SHAPEFILE = US_STATE_SHAPE_DIR / 'cb_2024_us_state_20m.shp'

US_STATE_CODES = {s.code.split('-')[-1] for s in
             pycountry.subdivisions.get(country_code='US')}
US_STATE_NAMES_LOWER = {s.name.lower() for s in
             pycountry.subdivisions.get(country_code='US')}

def download_and_extract_zip(url, extract_to):
    """Download and extract a ZIP file."""
    zip_file_path = extract_to / "temp.zip"

    # Download the ZIP file in chunks
    response = requests.get(url, stream=True, verify=False)
    if response.status_code == 200:
        with open(zip_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
        print("Download complete.")

        # Extract the ZIP file
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        print("Extraction complete.")

        # Remove the temporary ZIP file
        zip_file_path.unlink()
    else:
        raise ValueError(f"Failed to download resource from {url}")

def save_geo_figure_html(fig):
    if not FIGURE_DIR.exists():
        FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    # NamedTemporaryFile with delete=False so it sticks around
    tmp = tempfile.NamedTemporaryFile(
        suffix=".html",
        prefix="fig_",
        dir=FIGURE_DIR,
        delete=False
    )
    fig.save(tmp.name)
    # tmp.name is something like 'figures/fig_abcd1234efgh.json'
    return tmp.name    

def create_folium_GeoJson_for_points(df, lat_col, lon_col, popup_fields=None):
    """Create GeoJSON for points from DataFrame.
    
    Args:
        df: pandas DataFrame containing point data
        lat_col: Name of the column with latitude values
        lon_col: Name of the column with longitude values
        popup_fields: Optional List of fields to show in popup
    
    Returns:
        folium GeoJson object for points
    """
    # Create Point geometries from lat/lon
    geometry = gpd.points_from_xy(df[lon_col], df[lat_col])
    points_gdf = gpd.GeoDataFrame(df, geometry=geometry)

    
    return folium.GeoJson(
                    data=points_gdf.to_json(),
                    tooltip=folium.GeoJsonTooltip(
                        fields=popup_fields,
                        aliases=popup_fields,
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    )
                )

def create_folium_GeoJson_for_polygons(df, location_col, value_col=None, popup_fields=None):
    """Create GeoJSON for polygons from DataFrame.
    
    Args:
        df: pandas DataFrame containing polygon data
        location_col: Name of the column to join with shapefile
        value_col: Optional Name of the column for color mapping
        popup_fields: Optional List of fields to show in popup
    
    Returns:
        folium GeoJson object for polygons
        colormap
    """
    
    # Read shapefile and merge with data
    
    def is_valid_zipcode(value):
        """Check if a value is a valid ZIP code, defaulting to False on error."""
        try:
            return zipcodes.is_real(value) if value else False
        except ValueError:
            return False
    
    df = df.astype({location_col: str})
    df['is_zip'] = df[location_col].apply(is_valid_zipcode)
    df['is_us_state_code'] = df[location_col].str.upper().isin(US_STATE_CODES)
    df['is_us_state_name_lower'] = df[location_col].str.lower().isin(US_STATE_NAMES_LOWER)

    gdf = None
    if df['is_zip'].mean() >= 0.5:
        zip_shapes = gpd.read_file(ZIP_CODE_SHAPEFILE)
        zip_shapes = zip_shapes.rename(columns={'ZCTA5CE20': location_col})
        zip_shapes = zip_shapes.astype({location_col: str}) 
        gdf = zip_shapes.merge(df, on=location_col, how='inner')
    elif df['is_us_state_code'].mean() >= 0.5:
        state_shapes = gpd.read_file(US_STATE_SHAPEFILE)
        state_shapes = state_shapes.rename(columns={'STUSPS': location_col})
        df[location_col] = df[location_col].str.upper()
        gdf = state_shapes.merge(df, on=location_col, how='inner')
    elif df['is_us_state_name_lower'].mean() >= 0.5:  
        state_shapes = gpd.read_file(US_STATE_SHAPEFILE)
        state_shapes = state_shapes.rename(columns={'NAME': location_col})
        state_shapes[location_col] = state_shapes[location_col].str.lower()
        df[location_col] = df[location_col].str.lower()
        gdf = state_shapes.merge(df, on=location_col, how='inner')
    else:
        raise ValueError("The location column provided does not match either US states or zip codes.")
    
    poly_colormap = None
    if value_col:
        # Create color map for polygons
        poly_colors = ['blue', 'yellow', 'red']
        poly_min_val = df[value_col].min()
        poly_max_val = df[value_col].max()
        poly_colormap = folium.LinearColormap(
            colors=poly_colors,
            vmin=poly_min_val,
            vmax=poly_max_val,
            caption=f'Polygon {value_col}'  # Add legend
        )
    
    return folium.GeoJson(
                    data=gdf.to_json(),
                    style_function=lambda x: {
                        'fillColor': poly_colormap(x['properties'][value_col]) if poly_colormap else 'yellow',
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.7
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=[location_col] + popup_fields,
                        aliases=[location_col.upper()] + popup_fields,
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    )
                ), poly_colormap

def create_geo_viz(polygon_df=None, point_df=None, geo_config=None):
    """Create geographic visualization with both polygons and points.
    
    Args:
        polygon_df: DataFrame containing data for polygon visualization (optional)
        point_df: DataFrame containing data for point visualization (optional)
        geo_config: Dictionary containing visualization configuration:
            - map_settings: Dictionary with:
                - center: [lat, lon] for map center
                - zoom: Initial zoom level
                - style: Map style (e.g., "CartoDB positron")
            
            For polygons:
            - polygon_settings:
                - value_column: Column for polygon coloring
                - location_column: Column to join with shapefile
                - popup_fields: Fields to show in polygon popup
            
            For points:
            - point_settings:
                - value_column: Column for point coloring
                - coordinates:
                    - lat
                    - lon
                - popup_fields: Fields to show in point popup
    """
    m = None
    if not geo_config:
        return None
    
    try:
        # Get map settings
        map_settings = geo_config.get('map_settings', {})
        center = map_settings.get('center', [39.8283, -98.5795])  # US center
        zoom = map_settings.get('zoom', 4)
        style = map_settings.get('style', 'CartoDB positron')
        
        # Create base map
        m = folium.Map(location=center, zoom_start=zoom, tiles=style)
        
        # Handle polygons if provided
        if polygon_df is not None:
            poly_settings = geo_config.get('polygon_settings', {})
            poly_value_col = poly_settings.get('value_column')
            poly_loc_col = poly_settings.get('location_column')
            
            folium_polygons_geojson, colormap = create_folium_GeoJson_for_polygons(polygon_df, poly_loc_col, poly_value_col, poly_settings.get('popup_fields', []))
            folium_polygons_geojson.add_to(m)
            if colormap:
                m.add_child(colormap)
        
        # Handle points if provided
        if point_df is not None:
            point_settings = geo_config.get('point_settings', {})
            coord_config = point_settings.get('coordinates', {})
            
            if coord_config:          
                popup_fields = point_settings.get('popup_fields', [])
                
                # Get coordinates and create GeoDataFrame
                if 'lat' in coord_config and 'lon' in coord_config:
                    lat_col = coord_config['lat']
                    lon_col = coord_config['lon']
                    folium_points_geojson = create_folium_GeoJson_for_points(point_df, lat_col, lon_col, popup_fields)
                    folium_points_geojson.add_to(m)
                else:
                    st.warning("Missing coordinates configuration for points")
                    return None

        map_html_file = save_geo_figure_html(m)
        return {
                "type": "plot",
                "plot_data": {
                    "plot_lib": "folium",
                    "plot_html_file": map_html_file
                }
            }
        
    except Exception as e:
        st.error(f"Error creating geographic visualization: {str(e)}")
        raise(f"Error: {str(e)}")

# Function to embed Folium map with dynamic height
def display_folium_map(folium_map_html):
    # JavaScript snippet to dynamically adjust the iframe height
    js_code = """
    <script>
        const iframe = window.frameElement;
        if (iframe) {
            const containerWidth = iframe.parentElement.offsetWidth;
            iframe.style.height = (containerWidth * 0.6) + "px";  // Set height to 60% of the width
        }
    </script>
    """
    # Combine the Folium map HTML with the JavaScript snippet
    combined_html = folium_map_html + js_code

    # Render the combined HTML in Streamlit
    components.html(combined_html, height=0)  # Height is dynamically set by JavaScript