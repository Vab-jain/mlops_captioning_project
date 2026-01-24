from transformers import AutoTokenizer, AutoImageProcessor, VisionEncoderDecoderModel
import requests, time
from PIL import Image
from fastapi import FastAPI, UploadFile
from mangum import Mangum
from contextlib import asynccontextmanager

# SETUP
@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = "./model_local"
    # load the image captioning model and corresponding tokenizer and image processor
    model = VisionEncoderDecoderModel.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    image_processor = AutoImageProcessor.from_pretrained(model_path)
    yield

app = FastAPI(lifespan=lifespan)
handler = Mangum(app)

@app.get("/")
def health_ok():
    return {'health_ok': True}

@app.post("/get_caption")
def get_caption(input_img: UploadFile):
    start = time.time()
    
    # LOADING IMAGE
    image = Image.open(input_img.file)
    pixel_values = image_processor(image, return_tensors="pt").pixel_values

    # generate caption - suggested settings
    generated_ids = model.generate(
        pixel_values,
        temperature=0.7,
        top_p=0.8,
        top_k=50,
        num_beams=3 # you can use 1 for even faster inference with a small drop in quality
    )
    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    end = time.time()
    # print(generated_text)
    # print(f"Time taken: {end - start} seconds")
    return {'status': 'success',
            'caption': generated_text,
            'total_time': end - start}