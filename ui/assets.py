import pygame as p
import os

from .constants import SQ_SIZE, IMAGES, ASSETS_DIR


def load_images():
    """Initialize a global dictionary of images. This will be called exactly once in the main"""
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK",
              "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        path = os.path.join(ASSETS_DIR, piece.lower() + ".png")
        IMAGES[piece] = p.transform.scale(p.image.load(path), (SQ_SIZE, SQ_SIZE))
