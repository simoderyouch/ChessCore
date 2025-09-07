"""
Main Driver
"""
import pygame as p
from Chess import ChessEngine
import os

WIDTH = HEIGHT = 500
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
        path = os.path.join(BASE_DIR, "images", piece + ".png")
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

                    # If move is legal -> make it
                    if attempted_move in valid_moves:
                        gs.make_move(attempted_move)
                        print('MOVE NOTATION : ' , attempted_move.get_chess_move_notation())
                        print('CHESS NOTATION : ', attempted_move.get_chess_notation())
                        print('----------------------------------------------------------')
                        move_made = True


                        sq_selected = ()
                        player_clicks = []
                        valid_moves_from_selected = []

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
    font = p.font.SysFont("Helvitca", 36, True, False)
    text_object = font.render(text, 0, p.Color("Black"))
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



if __name__ == "__main__":
    main()