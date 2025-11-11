import streamlit as st
from PIL import Image
from fractions import Fraction
import io

def app():
    """
    Streamlit application function to upload an image, display it, 
    and show analysis results in a two-column layout.
    
    The layout uses st.columns to put the uploader/preview on the left 
    and the analysis controls/report on the right.
    """
    # --- Configuration and Title ---
    st.set_page_config(
        page_title="Image Dimension Analyzer",
        layout="wide", # Use 'wide' layout for better side-by-side display
        initial_sidebar_state="auto"
    )

    st.title("🖼️ Image Dimension Analyzer")
    st.markdown("Upload an image on the left, and click the button to see the dimensions and aspect ratio in the report on the right.")

    # --- Setup Two Columns for Layout ---
    # Split the screen into two equal columns
    col_upload, col_analysis = st.columns([1, 1]) 

    image_data = None
    uploaded_file = None
    
    # --- Left Column: Uploader and Preview ---
    with col_upload:
        st.subheader("1. Upload Image")
        # 1. File Uploader Widget
        uploaded_file = st.file_uploader(
            "Choose an image file...", 
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_file is not None:
            try:
                # Read the uploaded file into a PIL Image object
                image_data = Image.open(uploaded_file)
                
                # Display the Uploaded Image
                st.subheader("2. Image Preview")
                # Using st.container() to ensure a clean visual separation
                with st.container(border=True):
                    st.image(image_data, caption=uploaded_file.name, use_container_width=True)

            except Exception as e:
                # Handle cases where the file is corrupted or not a valid image
                st.error(f"An error occurred while processing the image: {e}")
                image_data = None # Ensure analysis is skipped on error
                uploaded_file = None 

    # --- Right Column: Analysis Button and Report ---
    with col_analysis:
        st.subheader("3. Image Analysis Report")
        
        # Placeholder to display the report results
        report_container = st.empty()
        
        # Only show the button if a file has been successfully uploaded and processed
        if uploaded_file is not None and image_data is not None:
            
            # 2. Analyze Button
            # use_container_width=True makes the button fill the column width
            if st.button("Analyze Image Dimensions", type="primary", use_container_width=True):
                
                # --- Perform Analysis ---
                width, height = image_data.size
                
                # Calculate Aspect Ratio (simplified to a fraction for common ratios)
                # Aspect Ratio is simplified to its lowest terms
                try:
                    aspect_ratio_fraction = Fraction(width, height)
                    aspect_ratio_str = f"{aspect_ratio_fraction.numerator}:{aspect_ratio_fraction.denominator}"
                except ZeroDivisionError:
                    aspect_ratio_str = "N/A" # Should not happen with valid images
                
                # Write results to the report container
                with report_container.container(border=True):
                    st.success("✅ Analysis Complete!")
                    st.write(f"**File Name:** `{uploaded_file.name}`")
                    
                    st.markdown("---")
                    
                    # Display Dimensions and Aspect Ratio using metrics
                    col1_r, col2_r, col3_r = st.columns(3)
                    
                    with col1_r:
                        # Add thousands separator for large numbers
                        st.metric(label="Width (Pixels)", value=f"{width:,} px")
                    
                    with col2_r:
                        st.metric(label="Height (Pixels)", value=f"{height:,} px")

                    with col3_r:
                        st.metric(label="Aspect Ratio", value=aspect_ratio_str)
                        
                    st.caption("Dimensions are retrieved using the Pillow (PIL) library.")

            else:
                # Initial message before analysis
                report_container.info("Click the button above to analyze the uploaded image.")

        else:
            # Message when no file is uploaded or processing failed
            report_container.warning("Upload a supported image file (PNG, JPG) in the left column to begin analysis.")

# Run the app function
if __name__ == "__main__":
    app()