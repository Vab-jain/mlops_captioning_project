import streamlit as st
from PIL import Image
import io
import time

import streamlit as st
import requests
import socket
import requests.packages.urllib3.util.connection as urllib3_cn

# --- FORCE IPv4 (Fixes the 6-minute hang on Mac) ---
def allowed_gai_family():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = allowed_gai_family
# ---------------------------------------------------

# URL of your Lambda function
url = "https://xma52hzedr7uvvbzxjxyfhgeta0rhhyh.lambda-url.eu-central-1.on.aws/"

st.title("Image Captioning Tool")
st.write("Upload an image and the AI will describe it for you.")

# --- HELPER FUNCTION: COMPRESS IMAGE ---
def compress_image(uploaded_file):
    """
    Resizes and compresses the image to ensure it is under the 6MB AWS Lambda limit.
    """
    image = Image.open(uploaded_file)
    
    # Convert to RGB (handles PNGs with transparency issues)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    # Resize if the image is massive (e.g., > 1024px)
    max_size = (1024, 1024)
    image.thumbnail(max_size)
    
    # Save to a BytesIO buffer with JPEG compression
    img_byte_arr = io.BytesIO()
    # quality=85 significantly reduces size with barely visible loss
    image.save(img_byte_arr, format='JPEG', quality=85) 
    
    # Reset pointer to the start of the file
    img_byte_arr.seek(0)
    return img_byte_arr

# --- MAIN UI ---

if st.sidebar.button("Test Connection"):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            st.sidebar.success("Connected to Backend!")
        else:
            st.sidebar.error(f"Backend returned error: {res.status_code}")
    except Exception as e:
        st.sidebar.error(f"Could not reach backend: {e}")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    if st.button("Generate Caption"):
        with st.spinner("Analyzing image..."):
            try:
                # 1. Measure Compression Time
                t0 = time.time()
                compressed_file = compress_image(uploaded_file)
                t1 = time.time()
                st.write(f"Compression took: {t1 - t0:.2f} seconds")
                st.write(f"File size: {compressed_file.getbuffer().nbytes / 1024:.2f} KB")
                
                # 3. Send with a timeout to handle cold starts
                from urllib.parse import urljoin
                full_url = urljoin(url, "get_caption")
                
                # 2. Measure Request (Upload + Wait) Time
                t2 = time.time()
                with st.spinner("Sending to cloud..."):
                    # Make sure you use the compressed_file here!
                    files = {"input_img": ("compressed.jpg", compressed_file, "image/jpeg")}
                    response = requests.post(full_url, files=files, timeout=60)
                t3 = time.time()
                st.write(f"Round-trip request took: {t3 - t2:.2f} seconds")
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Caption: {result['caption']}")
                    st.info(f"Processing time: {result['total_time']:.2f} seconds")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"Connection failed: {e}")