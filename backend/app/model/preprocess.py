import whisper
import numpy as np
import librosa
import numpy as np
import whisper
import librosa


def pad_or_trim_custom(audio, max_time=5, sr=16000):
    """
    Pads or trims the audio to the specified target length.

    Args:
        audio (np.ndarray): Input audio array.
        target_length (int): Desired length in samples (default is 80,000 for 5 seconds at 16kHz).

    Returns:
        np.ndarray: Audio array of length `target_length`.
    """
    target_length = max_time * 16000
    if len(audio) > target_length:
        # Trim the audio to the target length
        return audio[:target_length]
    elif len(audio) < target_length:
        # Pad with zeros at the end to match the target length
        padding = target_length - len(audio)
        return np.pad(audio, (0, padding), mode="constant")
    else:
        # Audio is already the correct length
        return audio


def processsingle_audio(audio_path, max_time=10, sr=16000):
    """
    Processes a single audio file by padding/trimming to the specified duration
    and converting it to a log Mel spectrogram.

    Args:
        audio_path (str): Path to the audio file.
        max_time (int): Target duration in seconds (default is 10 seconds).
        sr (int): Sampling rate (default is 16kHz).

    Returns:
        np.ndarray: Log Mel spectrogram of the processed audio.
    """
    # Load the audio file
    (audio,) = librosa.load(audio_path, sr=sr)

    audio = pad_or_trim_custom(audio, max_time, sr)

    log_mel_spectrogram = whisper.log_mel_spectrogram(audio).numpy()

    return log_mel_spectrogram

