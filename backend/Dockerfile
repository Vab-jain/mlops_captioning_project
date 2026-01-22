FROM public.ecr.aws/lambda/python:3.11

# 1. Install build tools (GCC)
RUN yum update -y && yum install -y gcc-c++ 

WORKDIR ${LAMBDA_TASK_ROOT}

# 2. Install Torch CPU-only & NumPy < 2.0
# We do this manually to control the version and size
RUN pip install --no-cache-dir \
    "numpy<2.0" \
    torch torchvision \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --target "${LAMBDA_TASK_ROOT}"

# 3. Copy the CLEAN requirements.txt (No Streamlit! No Torch!)
COPY requirements.txt .

# 4. Install the rest of the dependencies
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# ... previous steps ...

# Copy the download script
COPY download_model.py .

# Run it during the build (this saves the model into the image)
# We set the HF_HOME to /tmp just to be safe during the build process
RUN export HF_HOME=/tmp && python download_model.py

# Copy your main application
COPY main.py .

CMD [ "main.handler" ]