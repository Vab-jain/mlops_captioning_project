# MLOps Deployment Project

This is a image-captioner service exposed as a API (FastAPI) deployed on a serverless cloud with CI/CD protocols integrated.

### Task Derscription

The consumer of this system is an end-user which interacts with the service using a UI. 

- Failure mode: requests can get stuck on large/bad images
- Guarantee: API completes within bounded time
- Non-goal: arbitrary images or formats
- Mitigation: reject early based on input properties
- Tests in CI/CD: minimal smoke + input rejection + error handling

### Out-of-scope

- Training a model or at least, fine-tuning it to get maximum performance.

## Design Choices

Following are some design choices I made for this project:

1. Input validation / rejection (size, format, corrupted files)
2. Model execution (takes input → produces caption)
3. Response to the user (success or error, with meaningful message)


### CI/CD validation (conceptually)

- Smoke test: Can the API start, accept a normal input, and return a caption?
- Input rejection test: Does it reject one known “bad” input quickly?
- Error response test: Does it return a meaningful error if the model fails or the input is too big?

# Challenges Overcome
- [todo] architecture mismatch
- [todo] "longer cold start" -> load model on website hit
- [done] IPv6 vs IPv4 issue
- [todo] Layer Caching

## Things I learned
- CloudWatch -> logs
- IAM Roles


# Acknowledgement

Image Captioner Used: https://huggingface.co/cnmoro/mini-image-captioning