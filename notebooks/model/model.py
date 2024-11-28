from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from torch import Tensor, nn

"""
torch modules we will use: linear
"""


class MultiHeadAttention(nn.Module):
    def __init__(self, n_dim, n_head):
        super().__init__()
        self.n_heads = n_head
        self.query = nn.Linear(n_dim, n_dim)
        self.key = nn.Linear(n_dim, n_dim)
        self.value = nn.Linear(n_dim, n_dim)
        self.output = nn.Linear(n_dim, n_dim)

    def forward(
        self,
        input: Tensor,
        cross_input: Optional[Tensor] = None,
        mask: Optional[Tensor] = None,
        kv_cache: Optional[Dict] = None,
    ):
        """
        If cross_input is None, the model is operating in self-attention mode, and the keys and values are derived from the same input.
        If cross_input is not None, the model is in cross-attention mode, and keys and values are derived from cross_input instead.
        """
        q = self.query(input)

        if kv_cache is None or cross_input is None or self.key not in kv_cache:
            k = self.key(input if cross_input is None else cross_input)
            v = self.value(input if cross_input is None else cross_input)
        else:
            k = kv_cache[self.key]
            v = kv_cache[self.value]


class EncoderBlock(nn.Module):
    def __init__(self, d_model=512, num_heads=8, d_ff=2048, dropout=0.1):
        super().__init__()

        # Self-attention layer
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, dropout=dropout)
        self.norm1 = nn.LayerNorm(d_model)

        # Feedforward layer
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # Self attention + Add & Norm
        attn_output, _ = self.self_attn(x, x, x)
        x = x + self.dropout(attn_output)
        x = self.norm1(x)

        # Feedforward + Add & Norm
        ff_output = self.ff(x)
        x = x + self.dropout(ff_output)
        x = self.norm2(x)

        return x
