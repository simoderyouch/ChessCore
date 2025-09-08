"""
Main Driver with Chess.com Style Highlighting
"""
import pygame as p
from Chess import ChessEngine
import os

WIDTH = HEIGHT = 700
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
colors = [p.Color("white"), p.Color("gray")]


def load_images():
    """Initialize a global dictionary of images. This will be called exactly once in the main"""
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK",
              "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        path = os.path.join(BASE_DIR, "pieces/classic", piece.lower() + ".png")
        IMAGES[piece] = p.transform.scale(p.image.load(path), (SQ_SIZE, SQ_SIZE))

def main():
    """Main driver for our code. This will handle user input and updating the graphics"""
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    p.display.set_caption('Chess')

    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    load_images()

    animate = False

    running = True
    sq_selected = ()
    player_clicks = []
    valid_moves_from_selected = []  # Store valid moves from currently selected square
    last_move = None  # Store last move for highlighting

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                # --- Case 1: clicked same square → deselect
                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_from_selected = []

                # --- Case 2: first click (must be your own piece)
                elif not player_clicks:
                    piece = gs.board[row][col]
                    if piece != "--":
                        piece_color = piece[0]
                        if (piece_color == 'w' and gs.whiteToMove) or (piece_color == 'b' and not gs.whiteToMove):
                            sq_selected = (row, col)
                            player_clicks = [sq_selected]
                            # collect valid moves for highlighting
                            valid_moves_from_selected = [
                                mv for mv in valid_moves if mv.startRow == row and mv.startCol == col
                            ]
                        else:
                            # clicked opponent piece -> ignore (no selection)
                            sq_selected = ()
                            player_clicks = []
                            valid_moves_from_selected = []
                    else:
                        # clicked empty square -> ignore
                        sq_selected = ()
                        player_clicks = []
                        valid_moves_from_selected = []

                # --- Case 3: second click → destination
                else:
                    dest = (row, col)
                    attempted_move = ChessEngine.Move(player_clicks[0], dest, gs.board)

                    for move in valid_moves_from_selected:
                        if attempted_move == move:
                            if move.isPawnPromotion:
                                is_white_pawn = move.pieceMoved[0] == 'w'
                                chosen_piece = show_promotion_dialog(screen, is_white_pawn)
                                promotion_move = ChessEngine.Move(
                                    player_clicks[0], dest, gs.board,
                                    promotionPiece=chosen_piece
                                )
                                gs.make_move(promotion_move)
                                last_move = promotion_move  # Store for highlighting
                                print('PROMOTION MOVE:', promotion_move.get_chess_move_notation())
                                print('CHESS NOTATION:', promotion_move.get_chess_notation())
                            else:
                                gs.make_move(move)
                                last_move = move  # Store for highlighting
                                print('MOVE NOTATION:', move.get_chess_move_notation())
                                print('CHESS NOTATION:', move.get_chess_notation())

                            print('----------------------------------------------------------')
                            move_made = True
                            animate = True
                            sq_selected = ()
                            player_clicks = []
                            valid_moves_from_selected = []
                            break  # important: stop after making a move

                    # Move invalid -> check if clicked your own piece to switch selection
                    else:
                        clicked_piece = gs.board[row][col]
                        if clicked_piece != "--":
                            clicked_color = clicked_piece[0]
                            # If clicked one of your pieces, switch selection to that new piece
                            if (clicked_color == 'w' and gs.whiteToMove) or (
                                    clicked_color == 'b' and not gs.whiteToMove):
                                sq_selected = (row, col)
                                player_clicks = [sq_selected]
                                valid_moves_from_selected = [
                                    mv for mv in valid_moves if mv.startRow == row and mv.startCol == col
                                ]
                            else:
                                sq_selected = ()
                                player_clicks = []
                                valid_moves_from_selected = []
                        else:
                            sq_selected = ()
                            player_clicks = []
                            valid_moves_from_selected = []

            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    animate = False
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_from_selected = []
                    # Clear last move on undo
                    if len(gs.moveLog) > 0:
                        last_move = gs.moveLog[-1]
                    else:
                        last_move = None

                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    last_move = None
                    valid_moves_from_selected = []

        if move_made:
            valid_moves = gs.get_valid_moves()
            print("Legal moves:", " ".join(move.get_chess_move_notation() for move in valid_moves))
            if animate :
                animate_move(last_move, screen, gs.board, clock)
            move_made = False

        draw_game_state(screen, gs, valid_moves_from_selected, sq_selected, last_move)

        if gs.checkMate:
            if gs.whiteToMove:
                drawEndGameText(screen, "Black wins by Checkmate!")
            else:
                drawEndGameText(screen, "White wins by Checkmate!")
        elif gs.staleMate:
            drawEndGameText(screen, "Stalemate - Draw")

        clock.tick(MAX_FPS)
        p.display.flip()

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

def draw_game_state(screen, gs, valid_moves_from_selected, sq_selected, last_move=None):
    """Responsible for all the graphics within a current game state"""
    draw_board(screen)
    draw_game_highlights(screen, gs, valid_moves_from_selected, sq_selected, last_move)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    """Draw the chess board"""
    global colors
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_game_highlights(screen, gs, valid_moves_from_selected, sq_selected, last_move=None):
    """Main function to draw all game highlights like Chess.com"""

    # 1. Check highlight (if king is in check)
    if gs.inCheck:
        king_pos = gs.whiteKingLocation if gs.whiteToMove else gs.blackKingLocation
        highlight_check_square(screen, king_pos)

    # 2. All other highlights
    highlight_squares(screen, gs, valid_moves_from_selected, sq_selected, last_move)

def highlight_squares(screen, gs, valid_moves_from_selected, sq_selected, last_move=None):
    """Highlight squares like Chess.com - selected piece, valid moves, and last move"""

    # 1. Highlight last move (if any) - subtle yellow/green tint
    if last_move:
        highlight_last_move(screen, last_move)

    # 2. Highlight selected square and valid moves
    if sq_selected != ():
        r, c = sq_selected
        piece = gs.board[r][c]
        if piece != "--":
            piece_color = piece[0]  # 'w' or 'b'
            # Only highlight if it's the current player's piece
            if (piece_color == 'w' and gs.whiteToMove) or (piece_color == 'b' and not gs.whiteToMove):

                # Highlight selected square with a bright border
                highlight_selected_square(screen, r, c)

                # Highlight valid moves with dots and capture indicators
                highlight_valid_moves(screen, gs, valid_moves_from_selected)

def highlight_last_move(screen, last_move):
    """Highlight the last move made with subtle coloring"""
    # Light yellow/green tint for last move
    color = p.Color(255, 255, 153, 80)  # Light yellow with transparency

    # Highlight start square
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(80)
    s.fill(color)
    screen.blit(s, (last_move.startCol * SQ_SIZE, last_move.startRow * SQ_SIZE))

    # Highlight end square
    screen.blit(s, (last_move.endCol * SQ_SIZE, last_move.endRow * SQ_SIZE))

def highlight_selected_square(screen, r, c):
    """Highlight the selected square with a bright border like Chess.com"""
    border_color = p.Color(247, 247, 105, 120)
    border_width = 2

    # Draw border around selected square
    rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
    p.draw.rect(screen, border_color, rect, border_width)

    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)
    s.fill(p.Color('yellow'))
    screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

def highlight_valid_moves(screen, gs, valid_moves):
    """Highlight valid moves with dots and capture rings like Chess.com"""
    for move in valid_moves:
        end_r, end_c = move.endRow, move.endCol
        target_piece = gs.board[end_r][end_c]

        # Calculate center of the square
        center_x = end_c * SQ_SIZE + SQ_SIZE // 2
        center_y = end_r * SQ_SIZE + SQ_SIZE // 2

        if target_piece == "--":
            # Empty square - draw a semi-transparent dot
            if move.isCastleMove:
                # Castle moves get a special indicator
                draw_castle_indicator(screen, center_x, center_y)
            else:
                # Regular move - small dot
                draw_move_dot(screen, center_x, center_y)
        else:
            # Capture move - draw a ring around the piece
            draw_capture_ring(screen, center_x, center_y)

def draw_move_dot(screen, center_x, center_y):
    """Draw a small dot for regular moves"""
    dot_color = p.Color(128, 128, 128, 180)  # Semi-transparent green
    dot_radius = SQ_SIZE // 7  # Small dot

    # Create a surface for the dot with alpha
    dot_surface = p.Surface((dot_radius * 2, dot_radius * 2), p.SRCALPHA)
    p.draw.circle(dot_surface, dot_color, (dot_radius, dot_radius), dot_radius)

    # Blit the dot at the center of the square
    screen.blit(dot_surface, (center_x - dot_radius, center_y - dot_radius))

def draw_capture_ring(screen, center_x, center_y):
    """Draw a ring around capturable pieces"""
    ring_color = p.Color(128, 128, 128, 180)  # Semi-transparent green
    outer_radius = SQ_SIZE // 2 - 3
    inner_radius = SQ_SIZE // 2 - 8

    # Create a surface for the ring
    ring_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)

    # Draw outer circle
    p.draw.circle(ring_surface, ring_color, (SQ_SIZE // 2, SQ_SIZE // 2), outer_radius)
    # Draw inner circle (transparent) to create ring effect
    p.draw.circle(ring_surface, p.Color(0, 0, 0, 0), (SQ_SIZE // 2, SQ_SIZE // 2), inner_radius)

    # Blit the ring
    screen.blit(ring_surface, (center_x - SQ_SIZE // 2, center_y - SQ_SIZE // 2))

def draw_castle_indicator(screen, center_x, center_y):
    """Draw a special indicator for castle moves"""
    castle_color = p.Color(128, 128, 128, 180)

    # Draw a rounded rectangle for castle moves
    castle_width = SQ_SIZE // 3
    castle_height = SQ_SIZE // 6

    castle_surface = p.Surface((castle_width, castle_height), p.SRCALPHA)
    castle_rect = p.Rect(0, 0, castle_width, castle_height)
    p.draw.rect(castle_surface, castle_color, castle_rect, border_radius=castle_height // 4)

    screen.blit(castle_surface, (center_x - castle_width // 2, center_y - castle_height // 2))

def highlight_check_square(screen, king_pos):
    """Highlight the king's square when in check"""
    if king_pos:
        r, c = king_pos
        # Red highlight for check
        check_color = p.Color(255, 0, 0, 120)  # Semi-transparent red

        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        s.fill(check_color)
        screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

        # Add a red border
        border_rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, p.Color(220, 20, 20), border_rect, 3)



def draw_pieces(screen, board):
    """Draw the chess pieces on the board"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animate_move(move, screen, board, clock):
    """Animate a move"""
    global IMAGES
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol

    distance = max(abs(dR), abs(dC))
    frames_per_square = 6
    frame_count = distance * frames_per_square


    if frame_count == 0:
        frame_count = 1
    for frame in range(frame_count + 1):
        r, c = (move.startRow + dR * frame / frame_count,
                move.startCol + dC * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = p.Color("white") if (move.endRow + move.endCol) % 2 == 0 else p.Color("gray")
        end_square = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)

        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], end_square)

        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def show_promotion_dialog(screen, is_white_pawn):
    """Show promotion dialog and return selected piece"""
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(p.Color("black"))
    screen.blit(overlay, (0, 0))

    # Define promotion pieces
    promotion_pieces = ['Q', 'R', 'B', 'N']
    piece_color = 'w' if is_white_pawn else 'b'

    # Calculate dialog position (center of screen)
    dialog_width = 4 * SQ_SIZE
    dialog_height = (2 * SQ_SIZE) - 11
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2

    # Draw dialog background
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

        # Draw piece
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

if __name__ == "__main__":
    main()