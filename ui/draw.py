import pygame as p

from .constants import DIMENSION, SQ_SIZE, colors, IMAGES, WIDTH, HEIGHT


def draw_game_state(screen, gs, valid_moves_from_selected, sq_selected, last_move=None):
    draw_board(screen)
    from .highlights import draw_game_highlights
    draw_game_highlights(screen, gs, valid_moves_from_selected, sq_selected, last_move)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            # Use per-surface alpha blend to avoid jagged edges on highlights overlaying squares
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawEndGameText(screen, text):
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(p.Color("Black"))
    screen.blit(overlay, (0, 0))

    font = p.font.SysFont("Helvetica", 30, True, False)
    text_object = font.render(text, True, p.Color("White"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH // 2 - text_object.get_width() // 2,
        HEIGHT // 2 - text_object.get_height() // 2
    )
    screen.blit(text_object, text_location)


