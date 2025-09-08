import pygame as p

from .constants import SQ_SIZE, colors


def draw_game_highlights(screen, gs, valid_moves_from_selected, sq_selected, last_move=None):
    # 1. Check highlight
    if gs.inCheck:
        king_pos = gs.whiteKingLocation if gs.whiteToMove else gs.blackKingLocation
        highlight_check_square(screen, king_pos)

    # 2. All other highlights
    highlight_squares(screen, gs, valid_moves_from_selected, sq_selected, last_move)


def highlight_squares(screen, gs, valid_moves_from_selected, sq_selected, last_move=None):
    if last_move:
        highlight_last_move(screen, last_move)

    if sq_selected != ():
        r, c = sq_selected
        piece = gs.board[r][c]
        if piece != "--":
            piece_color = piece[0]
            if (piece_color == 'w' and gs.whiteToMove) or (piece_color == 'b' and not gs.whiteToMove):
                highlight_selected_square(screen, r, c)
                highlight_valid_moves(screen, gs, valid_moves_from_selected)


def highlight_last_move(screen, last_move):
    color = p.Color(255, 255, 100, 250)
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(80)
    s.fill(color)
    screen.blit(s, (last_move.startCol * SQ_SIZE, last_move.startRow * SQ_SIZE))
    screen.blit(s, (last_move.endCol * SQ_SIZE, last_move.endRow * SQ_SIZE))


def highlight_selected_square(screen, r, c):
    border_color = p.Color(247, 247, 105, 120)
    border_width = 2
    rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
    p.draw.rect(screen, border_color, rect, border_width)
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)
    s.fill(p.Color('yellow'))
    screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))


def highlight_valid_moves(screen, gs, valid_moves):
    for move in valid_moves:
        end_r, end_c = move.endRow, move.endCol
        target_piece = gs.board[end_r][end_c]
        center_x = end_c * SQ_SIZE + SQ_SIZE // 2
        center_y = end_r * SQ_SIZE + SQ_SIZE // 2
        if target_piece == "--":
            if move.isCastleMove:
                draw_castle_indicator(screen, center_x, center_y)
            else:
                draw_move_dot(screen, center_x, center_y)
        else:
            draw_capture_ring(screen, center_x, center_y)


def draw_move_dot(screen, center_x, center_y):
    dot_color = p.Color(0, 0, 0, 70)
    dot_radius = SQ_SIZE // 5
    dot_surface = p.Surface((dot_radius * 2, dot_radius * 2), p.SRCALPHA)
    p.draw.circle(dot_surface, dot_color, (dot_radius, dot_radius), dot_radius)
    screen.blit(dot_surface, (center_x - dot_radius, center_y - dot_radius))


def draw_capture_ring(screen, center_x, center_y):
    ring_color = p.Color(0, 0, 0, 70)
    outer_radius = SQ_SIZE // 2 - 3
    inner_radius = SQ_SIZE // 2 - 8
    ring_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
    center = (SQ_SIZE // 2, SQ_SIZE // 2)
    p.draw.circle(ring_surface, ring_color, center, outer_radius)
    p.draw.circle(ring_surface, p.Color(0, 0, 0, 0), center, inner_radius)
    screen.blit(ring_surface, (center_x - SQ_SIZE // 2, center_y - SQ_SIZE // 2))


def draw_castle_indicator(screen, center_x, center_y):
    castle_color = p.Color(0, 0, 0, 70)
    castle_width = SQ_SIZE // 3
    castle_height = SQ_SIZE // 6
    castle_surface = p.Surface((castle_width, castle_height), p.SRCALPHA)
    castle_rect = p.Rect(0, 0, castle_width, castle_height)
    p.draw.rect(castle_surface, castle_color, castle_rect, border_radius=castle_height // 4)
    screen.blit(castle_surface, (center_x - castle_width // 2, center_y - castle_height // 2))


def highlight_check_square(screen, king_pos):
    if king_pos:
        r, c = king_pos
        check_color = p.Color(255, 0, 0, 120)
        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        s.fill(check_color)
        screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
        border_rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, p.Color(220, 20, 20), border_rect, 3)


