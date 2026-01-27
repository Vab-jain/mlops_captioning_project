import pytest
import io
import PIL
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app 

client = TestClient(app)

# Define fixtures for mocks
### Three main mocks: 1. AutoTokenizer, 2. VisionEncoderDecoderModel, 3. AutoImageProcessor
@pytest.fixture
def mock_tokenizer():
    return MagicMock()

@pytest.fixture
def mock_model():
    return MagicMock()

@pytest.fixture
def mock_processor():
    return MagicMock()

# Automatically inject these into app.state for EVERY test
@pytest.fixture(autouse=True)
def setup_app_state(mock_tokenizer, mock_model, mock_processor):
    app.state.tokenizer = mock_tokenizer
    app.state.model = mock_model
    app.state.image_processor = mock_processor
    yield
    # Clean up after each test because these can be heavy models
    del app.state.tokenizer
    del app.state.model
    del app.state.image_processor

# TESTS: Follow the AAA pattern: 
## Arrange : Setup the mock/fake files and settings
## Act : Perform the request/function call with the fake files
## Assert : Check if this results in success (or intended faliure)
def test_get_caption_success(mock_tokenizer, mock_model, mock_processor):
    """
    Test Case: A valid image is uploaded and returns a successful caption.
    Follows the AAA (Arrange, Act, Assert) pattern.
    """
    # --- ARRANGE ---
    # Setup specific mock returns
    mock_model.generate.return_value = [[1, 2, 3]]
    mock_tokenizer.batch_decode.return_value = ["a sample caption"]
    mock_processor.return_value = MagicMock(pixel_values="fake_pixels")

    img = PIL.Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # --- ACT ---
    response = client.post("/get_caption", files={"input_img": ("test.png", img_bytes, "image/png")})

    # --- ASSERT ---
    assert response.status_code == 200
    assert response.json()["caption"] == "a sample caption"

def test_get_caption_invalid_file_type(mock_model):
    # --- ARRANGE ---
    test_file = io.BytesIO(b"This is a fake text file content")
    fake_image_payload = {"input_img": ("test.txt", test_file, "text/plain")}
    
    # --- ACT ---
    response = client.post("/get_caption", files=fake_image_payload)

    # --- ASSERT ---
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file"
    mock_model.generate.assert_not_called()

