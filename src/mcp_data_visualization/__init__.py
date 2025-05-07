# __init__.py

import argparse
from .server import mcp

import os
import sys
import subprocess
import threading
import time

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

def main():
    """
    Entry point for the MCP server.
    Parses any CLI arguments and starts the server.
    """
    parser = argparse.ArgumentParser(description="mcp_data_visualization")
    parser.parse_args()
    
    mcp.run()

if __name__ == "__main__":
    main()
