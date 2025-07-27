import os
from PIL import Image
import streamlit as st

def load_email_images():
    """Load email screenshot images from assets folder."""
    images = {}
    for file in os.listdir("assets"):
        if file.endswith((".jpg", ".png")):
            images[file] = Image.open(f"assets/{file}")
    return images