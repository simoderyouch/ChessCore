"""
Backwards-compatible facade re-exporting the engine modules.
This keeps existing imports (from Chess import ChessEngine) working.
"""

from .engine import GameState, Move, CastleRights

__all__ = [
    "GameState",
    "Move",
    "CastleRights",
]


