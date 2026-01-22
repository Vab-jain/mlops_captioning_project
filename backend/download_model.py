from transformers import AutoTokenizer, AutoImageProcessor, VisionEncoderDecoderModel

model_id = "cnmoro/mini-image-captioning"
save_directory = "./model_local"

print("Downloading model...")
model = VisionEncoderDecoderModel.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)
processor = AutoImageProcessor.from_pretrained(model_id)

# Save to a local folder inside the container
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)
processor.save_pretrained(save_directory)
print("Model baked successfully!")