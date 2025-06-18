import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import json
import plotly.io as pio
from pathlib import Path
import tempfile

FIGURE_DIR = Path(tempfile.gettempdir()) / 'mcp_data_visualization/figures'

def save_figure_json(fig):
    if not FIGURE_DIR.exists():
        FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    # NamedTemporaryFile with delete=False so it sticks around
    tmp = tempfile.NamedTemporaryFile(
        suffix=".json",
        prefix="fig_",
        dir=FIGURE_DIR,
        delete=False
    )
    pio.write_json(fig, tmp.name)
    # tmp.name is something like 'figures/fig_abcd1234efgh.json'
    return tmp.name

def create_plotly_plot(
    data: pd.DataFrame,
    plot_type: str,
    x: str,
    y: Optional[str] = None,
    title: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_row: Optional[str] = None,
    category_orders: Optional[Dict[str, List]] = None,
    labels: Optional[Dict[str, str]] = None,
    hover_data: Optional[List[str]] = None,
    text: Optional[str] = None,
    color_discrete_map: Optional[Dict[str, str]] = None,
    color_continuous_scale: Optional[str] = None,
    range_x: Optional[List[float]] = None,
    range_y: Optional[List[float]] = None,
    log_x: bool = False,
    log_y: bool = False,
    error_x: Optional[str] = None,
    error_y: Optional[str] = None,
    trendline: Optional[str] = None,
    marginal_x: Optional[str] = None,
    marginal_y: Optional[str] = None,
    custom_data: Optional[List[str]] = None,
    animation_frame: Optional[str] = None,
    animation_group: Optional[str] = None,
    symbol: Optional[str] = None,
    pattern_shape: Optional[str] = None,
    multiple_y: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Creates an advanced plot from the provided data.
    
    Args:
        data: DataFrame containing the data to plot
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
    try:
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        
        # Common parameters for all plot types
        common_params = {
            'title': title,
            'labels': labels or {},
            'category_orders': category_orders or {},
            'hover_data': hover_data,
            'custom_data': custom_data,
        }
        
        # Add parameters if they are provided
        if color is not None:
            common_params['color'] = color
        if facet_col is not None:
            common_params['facet_col'] = facet_col
        if facet_row is not None:
            common_params['facet_row'] = facet_row
        if color_discrete_map is not None:
            common_params['color_discrete_map'] = color_discrete_map
        if color_continuous_scale is not None:
            common_params['color_continuous_scale'] = color_continuous_scale
        if text is not None:
            common_params['text'] = text
        if animation_frame is not None:
            common_params['animation_frame'] = animation_frame
        if animation_group is not None:
            common_params['animation_group'] = animation_group
            
        # Create layout options
        layout_params = {}
        if range_x is not None:
            layout_params['xaxis'] = {'range': range_x}
        if range_y is not None:
            layout_params['yaxis'] = {'range': range_y}
        if log_x:
            layout_params['xaxis'] = layout_params.get('xaxis', {})
            layout_params['xaxis']['type'] = 'log'
        if log_y:
            layout_params['yaxis'] = layout_params.get('yaxis', {})
            layout_params['yaxis']['type'] = 'log'
        
        # Handle multiple y columns
        if multiple_y and plot_type in ['line', 'bar', 'scatter']:
            fig = go.Figure()
            
            # Add a trace for each y column
            for y_col in multiple_y:
                if plot_type == 'line':
                    fig.add_trace(go.Scatter(x=data[x], y=data[y_col], mode='lines', name=y_col))
                elif plot_type == 'bar':
                    fig.add_trace(go.Bar(x=data[x], y=data[y_col], name=y_col))
                elif plot_type == 'scatter':
                    fig.add_trace(go.Scatter(x=data[x], y=data[y_col], mode='markers', name=y_col))
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title=labels.get(x, x) if labels else x,
                **layout_params
            )
        else:
            # Create plot based on type
            if plot_type == "line":
                fig = px.line(data, x=x, y=y, **common_params)
                if trendline:
                    fig.update_traces(line=dict(width=2))
                    trend_fig = px.scatter(data, x=x, y=y, trendline=trendline)
                    for trend_trace in trend_fig.select_traces(selector=dict(mode='lines')):
                        trend_trace.update(line=dict(width=2, dash='dash'))
                        fig.add_trace(trend_trace)
            
            elif plot_type == "bar":
                fig = px.bar(data, x=x, y=y, **common_params)
                if error_y:
                    fig.update_traces(error_y=dict(type='data', array=data[error_y], visible=True))
            
            elif plot_type == "scatter":
                scatter_params = common_params.copy()
                if size is not None:
                    scatter_params['size'] = size
                if symbol is not None:
                    scatter_params['symbol'] = symbol
                if trendline:
                    scatter_params['trendline'] = trendline
                if marginal_x:
                    scatter_params['marginal_x'] = marginal_x
                if marginal_y:
                    scatter_params['marginal_y'] = marginal_y
                
                fig = px.scatter(data, x=x, y=y, **scatter_params)
            
            elif plot_type == "box":
                fig = px.box(data, x=x, y=y, **common_params)
            
            elif plot_type == "violin":
                fig = px.violin(data, x=x, y=y, box=True, **common_params)
            
            elif plot_type == "histogram":
                hist_params = {k: v for k, v in common_params.items() if k != 'hover_data' and k != 'custom_data'}
                if y:
                    # If y is provided, create a histogram with both x and y
                    fig = px.histogram(data, x=x, y=y, **hist_params)
                else:
                    # Otherwise, create a simple histogram
                    fig = px.histogram(data, x=x, **hist_params)
                
                if marginal_x:
                    # For marginal plots, we need to recreate the histogram as a scatter plot
                    fig = px.scatter(data, x=x, y=y, marginal_x=marginal_x, **common_params)
            
            elif plot_type == "pie":
                fig = px.pie(data, values=y, names=x, **common_params)
            
            elif plot_type == "heatmap":
                # For heatmaps, we need to pivot the data
                if y and color:
                    pivot_data = data.pivot(index=y, columns=x, values=color)
                    fig = px.imshow(pivot_data, labels=labels)
                else:
                    # Correlation matrix if no specific columns provided
                    corr_matrix = data.select_dtypes(include=[np.number]).corr()
                    fig = px.imshow(corr_matrix, labels=labels)
            
            elif plot_type == "contour":
                fig = px.density_contour(data, x=x, y=y, **common_params)
            
            elif plot_type == "density_heatmap":
                fig = px.density_heatmap(data, x=x, y=y, **common_params)
            
            elif plot_type == "area":
                fig = px.area(data, x=x, y=y, **common_params)
            
            elif plot_type == "funnel":
                fig = px.funnel(data, x=x, y=y, **common_params)
            
            elif plot_type == "timeline":
                # For timeline plots, we need start and end dates
                if 'start_date' in data.columns and 'end_date' in data.columns:
                    fig = px.timeline(data, x_start='start_date', x_end='end_date', y=y, **common_params)
                else:
                    raise ValueError("Timeline plots require 'start_date' and 'end_date' columns")
            
            elif plot_type == "treemap":
                # For treemap, we need path columns
                path_cols = [x]
                if y:
                    path_cols.append(y)
                if color and color not in path_cols:
                    path_cols.append(color)
                
                fig = px.treemap(data, path=path_cols, **common_params)
            
            elif plot_type == "sunburst":
                # For sunburst, we need path columns
                path_cols = [x]
                if y:
                    path_cols.append(y)
                if color and color not in path_cols:
                    path_cols.append(color)
                
                fig = px.sunburst(data, path=path_cols, **common_params)
            
            elif plot_type == "parallel_categories":
                # For parallel categories, we need dimension columns
                dim_cols = [x]
                if y:
                    dim_cols.append(y)
                if color and color not in dim_cols:
                    dim_cols.append(color)
                
                fig = px.parallel_categories(data, dimensions=dim_cols, **common_params)
            
            elif plot_type == "parallel_coordinates":
                # For parallel coordinates, we need dimension columns
                dim_cols = [x]
                if y:
                    dim_cols.append(y)
                
                # Add numeric columns as dimensions
                for col in data.select_dtypes(include=[np.number]).columns:
                    if col not in dim_cols and col != color:
                        dim_cols.append(col)
                
                fig = px.parallel_coordinates(data, dimensions=dim_cols, **common_params)
            
            elif plot_type == "scatter_3d":
                # For 3D scatter, we need z column
                if 'z' in kwargs:
                    z = kwargs.pop('z')
                    fig = px.scatter_3d(data, x=x, y=y, z=z, **common_params)
                else:
                    raise ValueError("3D scatter plots require a 'z' parameter")
            
            elif plot_type == "line_3d":
                # For 3D line, we need z column
                if 'z' in kwargs:
                    z = kwargs.pop('z')
                    fig = px.line_3d(data, x=x, y=y, z=z, **common_params)
                else:
                    raise ValueError("3D line plots require a 'z' parameter")
            
            else:
                raise ValueError(f"Unsupported plot type: {plot_type}")
            
            # Update layout with additional parameters
            fig.update_layout(**layout_params)
        

        
        # Save figure to JSON file
        fig_file_path = save_figure_json(fig)
        # Convert to JSON for transmission
        return {
            'type': 'plot',
            'plot_data': {
                'plot_lib': 'plotly',
                'plot_json_file': fig_file_path
            }
        }
        
    except Exception as e:
        import traceback
        return {
            'type': 'error',
            'content': f"Failed to create plot: {str(e)}\n{traceback.format_exc()}"
        }
