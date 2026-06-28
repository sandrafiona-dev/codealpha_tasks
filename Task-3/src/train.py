#!/usr/bin/env python3
"""
src/train.py
Training script for the Music Transformer model.
Loads preprocessed REMI data, builds the model, trains with sparse categorical crossentropy,
and plots loss/accuracy curves.
"""

import os
import pickle
import logging
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
from datetime import datetime

import tensorflow as tf
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping,
    ReduceLROnPlateau, TensorBoard
)

from model import build_model

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/train.log')
    ]
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    import yaml
    with open('config.yaml') as f:
        return yaml.safe_load(f)


def load_training_data() -> tuple:
    """Load preprocessed numpy arrays and vocabulary mappings."""
    X = np.load('models/X_input.npy')
    y = np.load('models/y_output.npy')
    with open('models/note2int.pkl', 'rb') as f:
        note2int = pickle.load(f)
    logger.info(f'Loaded X: {X.shape}, y: {y.shape}, vocab: {len(note2int)}')
    return X, y, note2int


def get_callbacks(config: dict) -> list:
    """Build Keras training callbacks."""
    os.makedirs('models/checkpoints', exist_ok=True)
    os.makedirs('logs/tensorboard', exist_ok=True)
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    callbacks = [
        ModelCheckpoint(
            filepath='models/checkpoints/best_weights.weights.h5',
            monitor='val_loss',
            save_best_only=True,
            save_weights_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=config['training']['early_stopping_patience'],
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        TensorBoard(
            log_dir=f'logs/tensorboard/{run_id}',
            histogram_freq=1
        )
    ]
    return callbacks


def plot_training_history(history: tf.keras.callbacks.History) -> None:
    """Plot and save training vs. validation loss and accuracy curves."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Music Transformer Training History', fontsize=15, y=1.01)

    # ── Loss curve ────────────────────────────────────────────────────────
    axes[0].plot(history.history['loss'],     label='Train loss',      color='#2196F3', linewidth=2)
    axes[0].plot(history.history['val_loss'], label='Validation loss', color='#FF5722', linewidth=2, linestyle='--')
    axes[0].set_title('Loss')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # ── Accuracy curve ────────────────────────────────────────────────────
    acc_key = 'sparse_categorical_accuracy'
    val_acc_key = 'val_sparse_categorical_accuracy'
    
    if acc_key in history.history:
        axes[1].plot(history.history[acc_key],     label='Train acc',      color='#4CAF50', linewidth=2)
        axes[1].plot(history.history[val_acc_key], label='Validation acc', color='#FF9800', linewidth=2, linestyle='--')
        axes[1].set_title('Sparse Categorical Accuracy')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('outputs/training_history.png', dpi=150, bbox_inches='tight')
    plt.close()
    logger.info('Training history saved to outputs/training_history.png')


def train(config: dict) -> None:
    """Main training entry point."""
    X, y, note2int = load_training_data()
    vocab_size = len(note2int)
    seq_length = config['model']['sequence_length']

    # Build model using defaults optimized for Music Transformer
    model = build_model(
        seq_length=seq_length,
        vocab_size=vocab_size,
        embed_dim=256,
        num_heads=4,
        feed_forward_dim=512,
        num_layers=4,
        dropout_rate=config['model']['dropout_rate'],
        learning_rate=config['training']['learning_rate']
    )

    logger.info('Starting training...')
    history = model.fit(
        X, y,
        epochs=config['training']['epochs'],
        batch_size=config['training']['batch_size'],
        validation_split=config['training']['validation_split'],
        callbacks=get_callbacks(config),
        shuffle=True,
        verbose=1
    )

    # Save final weights
    model.save_weights('models/final_weights.weights.h5')
    model.save('models/music_generator.keras')
    logger.info('Model saved to models/music_generator.keras')

    # Plot results
    plot_training_history(history)

    # Print final metrics
    final_loss = history.history['val_loss'][-1]
    final_acc_key = 'val_sparse_categorical_accuracy'
    final_acc  = history.history.get(final_acc_key, [None])[-1]
    
    logger.info(f'Final val_loss: {final_loss:.4f}')
    if final_acc is not None:
        logger.info(f'Final val_accuracy: {final_acc:.4f}')


if __name__ == '__main__':
    config = load_config()
    os.makedirs('logs', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    train(config)
