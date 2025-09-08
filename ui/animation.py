import pygame as p

from .constants import SQ_SIZE, colors
from .draw import draw_board, draw_pieces


def animate_move(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    distance = max(abs(dR), abs(dC))
    frames_per_square = 4  # Increased for smoother animation
    frame_count = distance * frames_per_square
    if frame_count == 0:
        frame_count = 1
    
    # Use floating point interpolation for smoother movement
    for frame in range(frame_count + 1):
        progress = frame / frame_count
        r = move.startRow + dR * progress
        c = move.startCol + dC * progress
        
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[0] if (move.endRow + move.endCol) % 2 == 0 else colors[1]
        end_square = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.pieceCaptured != "--":
            from .constants import IMAGES
            screen.blit(IMAGES[move.pieceCaptured], end_square)
        from .constants import IMAGES
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


