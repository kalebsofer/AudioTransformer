# %%
import torch
from transformers import (
    AutoModelForSpeechSeq2Seq,
    WhisperTokenizer,
    WhisperProcessor,
    pipeline,
)
from datasets import load_dataset

# %%
MODEL_DIR = "./minio/model/whisper-large-v3"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# %%
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL_DIR, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

# %%
tokenizer = WhisperTokenizer.from_pretrained(MODEL_DIR)

# %%
processor = WhisperProcessor.from_pretrained(MODEL_DIR)

# %%
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

# %%
# Load a sample dataset for testing
# replace this with own audio input
dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
sample = dataset[0]["audio"]

# %%
# Perform inference
result = pipe(sample)
print(result["text"])
