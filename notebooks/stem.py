import torchaudio
import torchaudio.transforms as T
from pydub import AudioSegment
import io


class AudioPreprocessor:
    def __init__(
        self, sample_rate=16000, n_fft=400, win_length=None, hop_length=160, n_mels=80
    ):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.win_length = win_length or n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.mel_spectrogram = T.MelSpectrogram(
            sample_rate=self.sample_rate,
            n_fft=self.n_fft,
            win_length=self.win_length,
            hop_length=self.hop_length,
            n_mels=self.n_mels,
        )

    def load_audio(self, audio_path):
        # Determine the file format
        file_extension = audio_path.split(".")[-1].lower()

        if file_extension in ["wav"]:
            waveform, sample_rate = torchaudio.load(audio_path)
        elif file_extension in ["mp3", "m4a"]:
            audio = AudioSegment.from_file(audio_path, format=file_extension)
            audio = audio.set_frame_rate(self.sample_rate).set_channels(1)
            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            buffer.seek(0)
            waveform, sample_rate = torchaudio.load(buffer)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        return waveform, sample_rate

    def process(self, audio_path):
        waveform, sample_rate = self.load_audio(audio_path)

        if sample_rate != self.sample_rate:
            resampler = T.Resample(orig_freq=sample_rate, new_freq=self.sample_rate)
            waveform = resampler(waveform)

        mel_spec = self.mel_spectrogram(waveform)

        return mel_spec


if __name__ == "__main__":
    preprocessor = AudioPreprocessor()
    spectrogram = preprocessor.process("notebooks/wavs/sample.m4a")
