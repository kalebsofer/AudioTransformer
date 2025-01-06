import torch
from data_loader_hugface import data_loader
from transformers import GPT2Tokenizer
from transformer import Transformer
from datasets import load_dataset

# Load the tokenizer and add special tokens
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
special_tokens = [
    "<pad>",
    "<start>",
    "<end>",
    "<transcribe>",
    "<translate>",
    "<en>",
    "<ar>",
]
tokenizer.add_tokens(special_tokens)
tokenizer.pad_token = "<pad>"

# Configuration matching the training setup
encoder_config = {
    "batch_size": 1,  # Batch size set to 1 for inference
    "n_mel_bins": 80,
    "emb_dim": 256,
    "n_time_frames": 800,
    "n_attention_heads": 8,
    "hidden_dim": 64,
    "n_blocks": 12,
}

decoder_config = {
    "batch_size": 1,
    "Wemb_dim": 768,
    "Pemb_dim": 256,
    "num_heads": 4,
    "hidden_dim": 64,
    "mlp_dim": 128,
    "n_blocks": 12,
    "voc_size": 50264,
}

# Function for running inference
# def run_inference(audio_file_path):
#     """
#     Perform inference on a single audio file.
#     Args:
#         audio_file_path (str): Path to the audio file.
#     Returns:
#         str: Transcribed text.
#     """
#     # Load and preprocess the audio file (assuming `data_loader` can handle single audio files)
#     # Replace with the actual preprocessing function for the audio
#     audio_sample = data_loader(audio_file_path, batch_size=5)  # Modify data_loader if needed for single file

#     with torch.no_grad():
#         for batch in audio_sample:
#             # Extract data from the batch
#             audio = batch["audio"].to(device)
#             input_ids = batch["input_ids"].to(device)

#             # Run the model for inference
#             outputs = model(audio, input_ids)

#             # Decode the outputs to text
#             predicted_ids = torch.argmax(outputs, dim=-1)  # Get predicted token indices
#             transcription = tokenizer.decode(predicted_ids[0], skip_special_tokens=True)

#             return transcription

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Transformer(encoder_config, decoder_config).to(device)
model.load_state_dict(torch.load("transformer_model_epoch_1.pt", map_location=device))


def run_inference(dataset, max_transcriptions=None, batch_size=64):
    """
    Perform inference on a dataset and return both predictions and true transcriptions.

    Args:
        dataset: Dataset object to load audio and text data.
        max_transcriptions (int, optional): Maximum number of transcriptions to return.
        batch_size (int): Number of samples per batch for inference.

    Returns:
        list of dict: List of dictionaries containing predicted and true transcriptions.
    """
    results = []  # Store all transcriptions
    model.eval()  # Set the model to evaluation mode

    # Initialize the data loader
    data_gen = data_loader(dataset, batch_size)

    with torch.no_grad():  # Disable gradient computation for inference
        for batch in data_gen:
            if max_transcriptions and len(results) >= max_transcriptions:
                break  # Stop once the maximum number of transcriptions is reached

            # Extract audio and true input IDs
            audio = batch["audio"].to(device)
            true_input_ids = batch["input_ids"]

            # Perform inference
            outputs = model(
                audio, true_input_ids
            )  # Forward pass with the model in eval mode

            # Decode predicted outputs
            predicted_ids = torch.argmax(outputs, dim=-1)  # Get predicted token indices
            predicted_transcriptions = [
                tokenizer.decode(pred, skip_special_tokens=True)
                for pred in predicted_ids
            ]

            # Decode true input IDs
            true_transcriptions = [
                tokenizer.decode(true_ids, skip_special_tokens=True)
                for true_ids in true_input_ids
            ]

            # Combine results
            batch_results = [
                {"predicted": predicted, "true": true}
                for predicted, true in zip(
                    predicted_transcriptions, true_transcriptions
                )
            ]

            results.extend(batch_results)

    # Limit to the specified number of transcriptions
    return results[:max_transcriptions] if max_transcriptions else results


# Example usage
audio_file = load_dataset(
    "mozilla-foundation/common_voice_17_0", "en", split="train", streaming=True
)  # Replace with the path to your audio file
# Example dataset
max_transcriptions = 1000
results = run_inference(
    audio_file, max_transcriptions=max_transcriptions, batch_size=64
)

print(f"Total transcriptions: {len(results)}")
for i, result in enumerate(results[:10]):  # Print the first 10 for verification
    print(f"Result {i + 1}:")
    print(f"  Predicted: {result['predicted']}")
    print(f"  True:      {result['true']}")
