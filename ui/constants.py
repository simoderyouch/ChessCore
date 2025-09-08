import os
import pygame as p


WIDTH = HEIGHT = 700
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(BASE_DIR), "pieces", "neo")
colors = [p.Color(181, 136, 99), p.Color(240, 217, 181)]

