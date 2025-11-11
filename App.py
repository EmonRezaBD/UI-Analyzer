import streamlit as st
from PIL import Image
import io

def app(): 
    #Streamlit application function to upload an image and display its dimensions.s
    # --- Configuration and Title ---
    st.set_page_config(
         page_title="TruePixel",
         layout="centered",
         initial_sidebar_state="auto"
    )
    st.title("🖼️ Image Dimension Analyzer")
    st.markdown("Upload an image (PNG, JPG, etc.) to view its dimensions (width and height in pixels).")

    # --- 1. File Uploader Widget ---
    uploaded_file = st.file_uploader(
        "Choose an image file...", 
        type=["png", "jpg", "jpeg"]
    )
    image_data = None

# Run the app function
if __name__ == "__main__":
    app()