import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import os

# Set up local directory paths
MODEL_DIR = "/minio/models/whisper-large-v3"

# Set device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Load model from local directory
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL_DIR, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

# Load processor from local directory
processor = AutoProcessor.from_pretrained(MODEL_DIR)

# Set up the inference pipeline
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

# Load a sample dataset for testing
# You can replace this with your own audio input
dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
sample = dataset[0]["audio"]

# Perform inference
result = pipe(sample)
print(result["text"])
