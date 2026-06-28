#!/usr/bin/env python3
"""
src/model.py
Transformer Decoder-based music generation model using TensorFlow/Keras.
Implements Token & Position Embedding and causal-masked Multi-Head Self-Attention.
"""

import logging
import tensorflow as tf

logger = logging.getLogger(__name__)


class TokenAndPositionEmbedding(tf.keras.layers.Layer):
    """
    Combines token embeddings with learnable positional embeddings.
    """
    def __init__(self, seq_length, vocab_size, embed_dim, **kwargs):
        super().__init__(**kwargs)
        self.token_emb = tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.pos_emb = tf.keras.layers.Embedding(input_dim=seq_length, output_dim=embed_dim)
        self.seq_length = seq_length

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions


class TransformerDecoder(tf.keras.layers.Layer):
    """
    Causal-masked Transformer Decoder Layer.
    Uses MultiHeadAttention and causal masking to predict the next token in the sequence.
    """
    def __init__(self, embed_dim, num_heads, feed_forward_dim, rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.mha = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([
            tf.keras.layers.Dense(feed_forward_dim, activation="relu"),
            tf.keras.layers.Dense(embed_dim),
        ])
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)

    def call(self, x, training=False):
        seq_len = tf.shape(x)[1]
        # Construct lower-triangular causal mask: shape (seq_len, seq_len)
        mask = tf.linalg.band_part(tf.ones((seq_len, seq_len)), -1, 0)
        mask = tf.cast(mask, tf.bool)
        mask = tf.expand_dims(mask, 0)  # Shape: (1, seq_len, seq_len)
        
        # Self-attention with mask
        attn_output = self.mha(query=x, value=x, key=x, attention_mask=mask, training=training)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)
        
        # Feed-forward network
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


def build_model(
    seq_length: int,
    vocab_size: int,
    embed_dim: int = 256,
    num_heads: int = 4,
    feed_forward_dim: int = 512,
    num_layers: int = 4,
    dropout_rate: float = 0.1,
    learning_rate: float = 0.001
) -> tf.keras.Model:
    """
    Build and compile the Transformer Decoder music generation model.

    Args:
        seq_length    : Number of tokens per input sequence.
        vocab_size    : Total unique tokens.
        embed_dim     : Embedding vector dimension size.
        num_heads     : Attention heads.
        feed_forward_dim: Hidden size in feed forward layer.
        num_layers    : Number of stacked Transformer Decoder layers.
        dropout_rate  : Dropout probability.
        learning_rate : Adam optimizer initial learning rate.

    Returns:
        Compiled Keras model ready for training.
    """
    inputs = tf.keras.layers.Input(shape=(seq_length,), dtype=tf.int32)
    
    # Embedding layer
    x = TokenAndPositionEmbedding(seq_length, vocab_size, embed_dim)(inputs)
    
    # Stack decoder blocks
    for _ in range(num_layers):
        x = TransformerDecoder(embed_dim, num_heads, feed_forward_dim, dropout_rate)(x)
        
    # Final dense layer outputs softmax probability over vocabulary
    outputs = tf.keras.layers.Dense(vocab_size, activation="softmax", name="output")(x)
    
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="MusicTransformer")
    
    # Sparse categorical crossentropy takes integer labels instead of one-hot vectors
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',
        metrics=['sparse_categorical_accuracy']
    )
    
    logger.info(f'Transformer Model built: {model.count_params():,} parameters')
    model.summary()
    return model


def load_model(weights_path: str, seq_length: int, vocab_size: int) -> tf.keras.Model:
    """
    Rebuild model architecture and load saved weights.
    """
    model = build_model(seq_length=seq_length, vocab_size=vocab_size)
    model.load_weights(weights_path)
    logger.info(f'Transformer weights loaded from {weights_path}')
    return model
