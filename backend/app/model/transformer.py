import torch.nn as nn


class Transformer(nn.Module):
    def __init__(self, encoder_config: dict, decoder_config: dict):
        """
        Combined Transformer class consisting of an Encoder and a Decoder.

        Args:
        - encoder_config (dict): Configuration dictionary for the Encoder.
        - decoder_config (dict): Configuration dictionary for the Decoder.
        """
        super(Transformer, self).__init__()

        # Initialize Encoder
        self.encoder = nn.Encoder(**encoder_config)

        # Initialize Decoder
        self.decoder = nn.Decoder(**decoder_config)

    def forward(self, mel_spectrogram, tokens):
        """
        Forward pass for the Transformer.

        Args:
        - mel_spectrogram (torch.Tensor): Input mel spectrogram for the Encoder.
        - tokens (torch.Tensor): Tokenized input for the Decoder.

        Returns:
        - torch.Tensor: Final output from the Decoder.
        """
        # Pass through Encoder
        patches = self.encoder(mel_spectrogram)  # Output of the Encoder

        # Pass through Decoder
        output = self.decoder(tokens, patches)

        return output
