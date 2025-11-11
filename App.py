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

    if uploaded_file is not None:
        try:
            #read the image file into a PIL Image Object
            image_data = Image.open(uploaded_file)

            #Display the Uploaded Image
            st.subheader("Uploaded Image Preview")
            st.image(image_data, caption=uploaded_file.name, use_column_width=True)

            #Analyze button
            st.markdown("---")
            if st.button("Analyze", type="primary"):
                if image_data:
                    width, height = image_data.size
                    st.success("✅ Analysis Complete!")

                    #Result of analysis
                    st.subheader("Analysis Report")

                    #using column for a cleaner display
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(label="Width (Pixels)", value=f"{width} px")
                    with col2:
                        st.metric(label="Height (Pixels)", value=f"{height} px")
                    st.info(f"The image '{uploaded_file.name}' is **{width}** pixels wide by **{height}** pixels high.")
                else:
                    st.error("Could not process the image data")

        except Exception as e:
            st.error(f"An error while: {e}")
            st.warning("Please ensure the file is a valid image format (PNG, JPG).")


# Run the app function
if __name__ == "__main__":
    app()