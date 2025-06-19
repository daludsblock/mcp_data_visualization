# mcp_data_visualization

This is an MCP server for "mcp_data_visualization", using the [python-sdk](https://github.com/modelcontextprotocol/python-sdk).

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
