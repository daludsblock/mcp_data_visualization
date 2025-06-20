# What is this MCP?

In many situations, we want to quickly visualize and interact with data through not too simple plots, for example, creating boxplot, heatmap, sunburst, etc.

However, the visualization functionalities provided by the popular data platforms, like Snowflake, are limited, and we are lazy to setup a notebook.

This MCP server gives Goose a simple and easy data visualization tool to make plots for you!

Currently, the tools provided by this MCP are:
* **open_plot_ui**: the Streamlit app UI to show plots
* **snowflake_query_executor**: a Snowflake query executor to pull data
* **create_chart_plot**: a plotting tool to create plots with Plotly. The supported Plotly charts include: line, bar, scatter, box, violin, histogram, pie, heatmap, contour, density_heatmap, area, funnel, timeline, treemap, sunburst, parallel_categories, parallel_coordinates, scatter_3d, line_3d.
* **create_geo_viz**: a plotting tool to create Geo map visualization with Folium. The supported visualization includes Geo points and Geo Polygons. For now, the Geo polygons only support US states and zipcodes.


## Getting Started

1. Initialize & activate your local Python environment:
   ```bash
   uv sync 
   source .venv/bin/activate
   ```

2. Start your server via the terminal by running: `mcp_data_visualization`. It will appear to 'hang' (no logs), but your server is indeed running (on port 3000).

## Test with MCP Inspector

The following command will start your server as a subprocess and also start up Anthropic's [Inspector](https://modelcontextprotocol.io/docs/tools/inspector) tool in the browser for testing your MCP server.

```bash
mcp dev src/mcp_data_visualization/server.py
```

Open your browser to http://localhost:5173 to see the MCP Inspector UI.

## Install the package to the virtual environment
1. Install your project locally:

   ```bash
   uv pip install .
   ```

2. Check the executable in your virtual environment:

   ```bash
   ls .venv/bin/  # Verify your CLI is available
   ```
   
## Integrating with Goose

In Goose:
1. Go to **Settings > Extensions > Add**.
2. Set **Type** to **StandardIO**.
3. Enter the absolute path to this project's CLI in your environment, for example:
   ```bash
   env SNOWFLAKE_ACCOUNT=your_account_name SNOWFLAKE_USER=your_user_name uv run /path/to/mcp_data_visualization/.venv/bin/mcp_data_visualization
   ```
4. Enable the extension and confirm that Goose identifies your tools.
