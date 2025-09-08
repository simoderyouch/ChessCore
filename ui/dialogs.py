import pygame as p

from .constants import WIDTH, HEIGHT, SQ_SIZE, IMAGES


def show_promotion_dialog(screen, is_white_pawn):
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(p.Color("black"))
    screen.blit(overlay, (0, 0))

    promotion_pieces = ['Q', 'R', 'B', 'N']
    piece_color = 'w' if is_white_pawn else 'b'

    dialog_width = 4 * SQ_SIZE
    dialog_height = (2 * SQ_SIZE) - 11
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2

    dialog_rect = p.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    p.draw.rect(screen, p.Color("white"), dialog_rect)

    font_size = max(16, SQ_SIZE // 4)
    font = p.font.SysFont("Arial", font_size, True)
    title_text = font.render("Choose Promotion Piece:", True, p.Color("black"))
    title_rect = title_text.get_rect(center=(WIDTH // 2, dialog_y + 30))
    screen.blit(title_text, title_rect)

    piece_rects = []
    for i, piece in enumerate(promotion_pieces):
        piece_image = IMAGES[piece_color + piece]
        piece_x = dialog_x + i * SQ_SIZE
        piece_y = (dialog_y + SQ_SIZE // 2) + 19
        piece_rect = p.Rect(piece_x, piece_y, SQ_SIZE, SQ_SIZE)
        piece_rects.append((piece_rect, piece))
        screen.blit(piece_image, piece_rect)
        p.draw.rect(screen, p.Color("gray"), piece_rect, 2)

    p.display.flip()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                for piece_rect, piece in piece_rects:
                    if piece_rect.collidepoint(mouse_pos):
                        return piece
            elif event.type == p.KEYDOWN:
                if event.key == p.K_q:
                    return 'Q'
                elif event.key == p.K_r:
                    return 'R'
                elif event.key == p.K_b:
                    return 'B'
                elif event.key == p.K_n:
                    return 'N'


