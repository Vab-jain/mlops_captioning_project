# Serverless Image Captioning API

> **Status:** MVP / Proof of Concept<br>
> **Tech Stack:** FastAPI, AWS Lambda (Docker), Streamlit, GitHub Actions<br>
> **Pre-trained Model:** `cnmoro/mini-image-captioning`

This project demonstrates **ML Inference with Bounded Execution** in a constrained environment. It exposes a lightweight image-captioning service via a FastAPI backend deployed on AWS Lambda, with a Streamlit frontend for user interaction.

The core engineering goal was to deploy a relatively large ML model in a resource-effective way. Design choices were heavily affected by constraints like model size, minimal compute, and strict memory usage. This project showcases a limited but robust feature set without over-stretching the scope of the API.

---

## 1. Project Demonstration

*Since the AWS Lambda infrastructure is spun down to conserve costs, this section serves as the primary evidence of functionality.*

### The Interface

The user interacts with a Streamlit UI that validates and compresses images before sending them to the backend.

<!--
Source - https://stackoverflow.com/a
Posted by Tieme, modified by community. See post 'Timeline' for change history
Retrieved 2026-01-27, License - CC BY-SA 4.0
-->

<img src="/docs/images/demo.gif" alt="Demo" width="80%">


### The API Response

Below is a sample response from the FastAPI backend running on Lambda (ARM64).

```json
// Example:
{
  "caption": "a dog running on grass",
  "processing_time": 1.2,
  "status": "success"
}

```

---

## 2. Architecture & Design Choices

**The Challenge:** ML models are resource-hungry, but standard "always-on" GPU instances are expensive for sporadic workloads.
**The Solution:** Minimizing computation via serverless deployment while fighting the "cold-start" problems inherent to AWS Lambda.

![Architecture Diagram](./docs/images/arch.png)

### Key Constraints & Scope

Designed as a 3-day MVP sprint, I enforced strict boundaries on the system:

1. **Bounded Execution:** The API must complete within a specific time limit or fail gracefully. It does not attempt to process everything; it processes what it can handle efficiently.
2. **Early Rejection:** The system rejects "bad" inputs (corrupted files, large payloads >6MB) immediately at the entry point to save compute cycles.
3. **Out-of-Scope:** I deliberately excluded model fine-tuning and high-availability guarantees to focus on the deployment infrastructure.

---

## 3. Challenges Overcome

Deploying PyTorch to a serverless environment introduced several specific engineering hurdles.

### 1. Architecture Mismatch (ARM64 vs x86)

I developed on an M1 Mac (ARM64) and used GitHub Actions (x86) for CI, but the target Lambda runs on Graviton (ARM64) for cost savings.

* **Problem:** Early builds failed on Lambda with "Exec format error."
* **Solution:** Implemented cross-platform builds in Docker using `docker buildx` and QEMU within the CI pipeline to ensure binary compatibility.

### 2. The "Cold Start" Latency

Loading the model into memory takes significant time (10+ seconds), leading to a poor user experience on the first request.

* **Solution:** I implemented a **"Pre-warming" strategy**. When a user hits the Streamlit website, a background thread fires a "ping" to the Lambda function. By the time the user uploads an image, the container is often already initialized.
* **Trade-off:** This helps a specific user session but does not solve the issue for concurrent scaling.

### 3. Dependency Management

* **NumPy Compatibility:** I encountered a glibc/GCC incompatibility with Amazon Linux 2023 that caused the runtime to crash. I had to pin `numpy<2.0` to resolve this.
* **Docker Size Limits:** To stay under the Lambda 10GB container limit, I forced a CPU-only installation of PyTorch, removing the massive CUDA dependencies.

### 4. Network Configuration

During local testing, requests between Streamlit and the Docker container would hang indefinitely.

* **Root Cause:** An IPv6 vs IPv4 socket binding priority issue on macOS.
* **Solution:** Forced the application to bind explicitly to `0.0.0.0` (IPv4).

---

## 4. CI/CD & Automation

The project uses GitHub Actions for robust deployment and validation.

* **Smoke Tests:** On every commit, the pipeline ensures the API starts and accepts inputs.
* **Layer Caching:** I utilized GitHub Actions caching (`cache-to: type=gha`) to cache Docker layers. This significantly reduced build times by preventing the re-downloading of heavy PyTorch dependencies on every run.
* **Security:** Used OIDC for AWS authentication to avoid hardcoding long-lived credentials.

---

## 5. How to Run Locally

Since the production Dockerfile is optimized for AWS Lambda (using a `Mangum` handler), the easiest way to test locally is to run the FastAPI backend and Streamlit frontend in separate terminals.

**1. Clone the repository**

```bash
git clone https://github.com/your-username/serverless-image-captioning.git
cd serverless-image-captioning

```

**2. Terminal 1: Start the Backend (FastAPI)**
*This mimics the Lambda environment by running the app locally.*

```bash
cd backend
pip install -r requirements.txt
# Run uvicorn on 0.0.0.0 to avoid IPv6/localhost binding issues
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

**3. Terminal 2: Start the Frontend (Streamlit)**

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py

```

**4. Verify**

Open your browser to the URL shown in Terminal 2 (usually `http://localhost:8501`). The frontend will automatically try to connect to the backend at `http://localhost:8000`.

---

## 6. Reflections & Future Work

This project required me to move beyond "making the model work" to "making the system work."

**Key Learnings:**

* **FastAPI Lifespan:** Learned to decouple model loading from request logic using `app.state`.
* **Testing Strategy:** Moved from patching global variables (flaky) to mocking the `app.state` (robust) in `pytest`.
* **Infrastructure:** Gained hands-on experience with AWS IAM Roles and CloudWatch logs for debugging serverless functions.

**Future Improvements:**

* **Async Inference:** Decouple the upload from processing using S3 triggers and DynamoDB to handle larger loads.
* **Observability:** Add detailed metrics for latency monitoring beyond basic CloudWatch logs.
* **Model Optimization:** Explore quantization (ONNX) to further reduce the memory footprint and cold start time.
