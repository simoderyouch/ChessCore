import pygame as p

from .constants import WIDTH, HEIGHT, SQ_SIZE, IMAGES , colors


def show_promotion_dialog(screen, is_white_pawn):
    overlay = p.Surface((WIDTH, HEIGHT), p.SRCALPHA)
    overlay.set_alpha(128)
    overlay.fill(p.Color("black"))
    screen.blit(overlay, (0, 0))

    promotion_pieces = ['Q', 'R', 'B', 'N']
    piece_color = 'w' if is_white_pawn else 'b'

    piece_size = SQ_SIZE - 20
    dialog_padding = 20

    dialog_width = 4 * piece_size + 5 * dialog_padding
    dialog_height = piece_size + 3 * dialog_padding + 40
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2
    

    dialog_rect = p.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    p.draw.rect(screen, colors[1], dialog_rect)

    font_size = max(13, SQ_SIZE // 4)
    font = p.font.SysFont("Arial", font_size, True)
    title_text = font.render("Choose Promotion Piece:", True, p.Color("black"))
    title_rect = title_text.get_rect(center=(WIDTH // 2, dialog_y + 30))
    screen.blit(title_text, title_rect)

    piece_rects = []
    for i, piece in enumerate(promotion_pieces):


        piece_x = dialog_x +  dialog_padding + i * (piece_size + dialog_padding)
        piece_y = dialog_y + dialog_padding + 40

        piece_surface = p.Surface((piece_size, piece_size), p.SRCALPHA)
        piece_surface.fill(colors[1])
        p.draw.rect(piece_surface, p.Color("black"), piece_surface.get_rect(), 1)
        piece_image = p.transform.smoothscale(IMAGES[piece_color + piece], (piece_size - 10, piece_size - 10))
        piece_surface.blit(piece_image, (5, 5))
        piece_rect = p.Rect(piece_x, piece_y, piece_size, piece_size)
        piece_rects.append((piece_rect, piece))
        screen.blit(piece_surface, piece_rect)


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


