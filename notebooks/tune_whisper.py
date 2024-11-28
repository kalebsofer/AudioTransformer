# %%
import torch
from transformers import (
    AutoModelForSpeechSeq2Seq,
    WhisperProcessor,
    pipeline,
)
from pydub import AudioSegment
import numpy as np
import librosa


# %%
MODEL_DIR = "../local_model"  # Update this path to the correct relative directory

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# %%
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL_DIR, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

# %%
processor = WhisperProcessor.from_pretrained(MODEL_DIR)

# %%
audio_path = "notebooks/wavs/sample.wav"
audio_array, sampling_rate = librosa.load(audio_path, sr=16000)

# %%
# input_features = processor(
#     audio_array,
#     sampling_rate=sampling_rate,
#     return_tensors="pt",
# ).input_features

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
# test_ds = load_dataset("mozilla-foundation/common_voice_11_0", "en", split="test[:10]", trust_remote_code=True, streaming=True)
# dataloader = DataLoader(test_ds, batch_size=1)

# %%
transcription = pipe(audio_array)["text"]

# %%
print(transcription)
# %%
