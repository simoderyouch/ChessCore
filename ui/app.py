import pygame as p

from .. import ChessEngine , MinMaxMoveFinder
from .constants import WIDTH, HEIGHT, SQ_SIZE, MAX_FPS
from .assets import load_images
from .draw import draw_game_state, drawEndGameText
from .animation import animate_move
from .dialogs import show_promotion_dialog


def main():
    p.init()
    # Enable anti-aliasing for better graphics quality
    p.display.set_mode((WIDTH, HEIGHT), p.DOUBLEBUF | p.HWSURFACE)
    screen = p.display.get_surface()
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





    valid_moves_from_selected = []
    last_move = None

    playerOne = True 
    playerTwo = False  



    while running:


        human_turn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:

                if gs.checkMate or gs.staleMate:
                    continue
                if not human_turn:
                    continue



                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_from_selected = []

                elif not player_clicks:
                    piece = gs.board[row][col]
                    if piece != "--":
                        piece_color = piece[0]
                        if (piece_color == 'w' and gs.whiteToMove) or (piece_color == 'b' and not gs.whiteToMove):
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
                                last_move = promotion_move
                                print('PROMOTION MOVE:', promotion_move.get_chess_move_notation())
                                print('CHESS NOTATION:', promotion_move.get_chess_notation())
                            else:
                                gs.make_move(move)
                                last_move = move
                                print('MOVE NOTATION:', move.get_chess_move_notation())
                                print('CHESS NOTATION:', move.get_chess_notation())

                            print('----------------------------------------------------------')
                            move_made = True
                            animate = True
                            sq_selected = ()
                            player_clicks = []
                            valid_moves_from_selected = []
                            break

                    else:
                        clicked_piece = gs.board[row][col]
                        if clicked_piece != "--":
                            clicked_color = clicked_piece[0]
                            if (clicked_color == 'w' and gs.whiteToMove) or (clicked_color == 'b' and not gs.whiteToMove):
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

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    animate = False
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_from_selected = []

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

        
        if not human_turn and not (gs.checkMate or gs.staleMate) and not move_made:
            
            ai_move = MinMaxMoveFinder.find_best_move(gs)
            if ai_move is not None:
                gs.make_move(ai_move)
                print('AI MOVE:', ai_move.get_chess_move_notation())
                print('CHESS NOTATION:', ai_move.get_chess_notation())
                print('----------------------------------------------------------')
                move_made = True
                animate = True
                last_move = ai_move
                sq_selected = ()
                player_clicks = []
                valid_moves_from_selected = []

        if move_made:
            valid_moves = gs.get_valid_moves()
            print("Legal moves:", " ".join(move.get_chess_move_notation() for move in valid_moves))
            if animate:
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
        elif gs.drawBy50Move:
            drawEndGameText(screen, "Draw by 50-move rule")
        elif gs.drawByRepetition:
            drawEndGameText(screen, "Draw by threefold repetition")

        clock.tick(MAX_FPS)
        p.display.flip()


