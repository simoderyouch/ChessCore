"""
Main Driver
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

    running = True
    sq_selected = ()
    player_clicks = []
    valid_moves_from_selected = []  # Store valid moves from currently selected square


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
                                print('PROMOTION MOVE:', promotion_move.get_chess_move_notation())
                                print('CHESS NOTATION:', promotion_move.get_chess_notation())
                            else:
                                gs.make_move(move)
                                print('MOVE NOTATION:', move.get_chess_move_notation())
                                print('CHESS NOTATION:', move.get_chess_notation())

                            print('----------------------------------------------------------')
                            move_made = True
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
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_from_selected = []

        if move_made:
            valid_moves = gs.get_valid_moves()
            print("Legal moves:", " ".join(move.get_chess_move_notation() for move in valid_moves))


            move_made = False


        draw_game_state(screen, gs, valid_moves_from_selected, sq_selected)
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


def draw_game_state(screen, gs, valid_moves_from_selected, sq_selected):
    """Responsible for all the graphics within a current game state"""
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves_from_selected, sq_selected)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    """Draw the chess board"""
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight_squares(screen, gs, valid_moves_from_selected, sq_selected):
    """Highlight selected square and valid moves"""
    if sq_selected != ():
        r, c = sq_selected
        piece = gs.board[r][c]
        if piece != "--":
            piece_color = piece[0]  # 'w' or 'b'
            if (piece_color == 'w' and gs.whiteToMove) or (piece_color == 'b' and not gs.whiteToMove):
                s = p.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(p.Color('blue'))
                screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('yellow'))
        for move in valid_moves_from_selected:
            screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def draw_pieces(screen, board):
    """Draw the chess pieces on the board"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

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
    #p.draw.rect(screen, p.Color("black"), dialog_rect, 3)

    font_size = max(16, SQ_SIZE // 4)
    font = p.font.SysFont("Arial", font_size, True)
    title_text = font.render("Choose Promotion Piece:", True, p.Color("black"))
    title_rect = title_text.get_rect(center=(WIDTH // 2, dialog_y + 30))
    screen.blit(title_text, title_rect)

    piece_rects = []
    for i, piece in enumerate(promotion_pieces):
        piece_image = IMAGES[piece_color + piece]
        piece_x = dialog_x + i * SQ_SIZE
        piece_y = ( dialog_y + SQ_SIZE // 2  ) + 19
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