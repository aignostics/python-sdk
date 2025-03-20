"""
Streamlit web application that demonstrates a simple interface for Aignostics Python SDK.

This module creates a web interface using Streamlit to demonstrate the usage of the service provided by
Aignostics Python SDK.
"""

import streamlit as st

from aignostics import (
    Service,
    __version__,
)

sidebar = st.sidebar
sidebar.write(
    f" [Aignostics Python SDK v{__version__}](https://aignostics.readthedocs.io/en/latest/)",
)
sidebar.write("Built with love in Berlin 🐻")

st.title("🔬 Aignostics Python SDK ")

# Initialize the service
service = Service()

# Get the message
message = service.get_hello_world()

# Print the message
st.write(f"{message}")
