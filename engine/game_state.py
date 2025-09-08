"""
GameState: stores the state of a chess game and computes legal moves.
Code moved verbatim from the monolithic ChessEngine.py for modularity.
"""

from .castling import CastleRights
from .move import Move


class GameState:
    def __init__(self):
        self.board= [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],   # 8th rank (black back row)
            ["bp","bp","bp","bp","bp","bp","wp","bp"],   # 7th rank (black pawns)
            ["--","--","--","--","--","--","--","--"],   # 6th rank
            ["--","--","--","--","--","--","--","--"],   # 5th rank
            ["--","--","--","--","--","--","--","--"],   # 4th rank
            ["--","--","--","--","--","--","--","--"],   # 3rd rank
            ["wp","wp","wp","wp","wp","wp","wp","wp"],   # 2nd rank (white pawns)
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],   # 1st rank (white back row)
        ]

        self.move_functions = {
            'p' : self.get_pawn_moves, 'R' : self.get_rook_moves, 'N' : self.get_knight_moves,
            'B' : self.get_bishop_moves, 'K' : self.get_king_moves, 'Q' : self.get_queen_moves
        }

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.checkMate = False
        self.staleMate = False

        # Advanced algorithm for Check and StaleMate
        self.inCheck = False
        self.pins = []
        self.checks = []

        self.enpassantPossible = ()
        self.enpassantPossibleLog = [()]  # Track en passant history for undo

        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

        self.whiteToMove = True
        self.moveLog = []

        self.halfmoveClock = 0  # For 50-move rule
        self.positionCounts = {}  # For threefold repetition
        self.drawBy50Move = False
        self.drawByRepetition = False

        self.update_position_count()

    def make_move(self, move):
        """Takes a Move as parameter and executes it"""
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

        self.whiteToMove = not self.whiteToMove

        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        if move.isPawnPromotion:
            promotedPiece = move.pieceMoved[0] + move.promotionPiece
            self.board[move.endRow][move.endCol] = promotedPiece

        # En Passant Move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        # Castle Move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]  # Move rook
                self.board[move.endRow][move.endCol+1] = '--'  # Remove rook from original position
            else:  # Queenside castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]  # Move rook
                self.board[move.endRow][move.endCol-2] = '--'  # Remove rook from original position

        # Update en passant possibility
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Update castling rights - whenever a rook or king moves
        self.update_castle_rights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

        # 50-move rule: reset on pawn move or capture
        if move.pieceMoved[1] == 'p' or move.pieceCaptured != '--':
            self.halfmoveClock = 0
        else:
            self.halfmoveClock += 1

        self.update_position_count()

    def undo_move(self):
        """Undo the last move made"""
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # Update king positions
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo en passant move
            if move.isEnpassantMove:
                if move.pieceMoved[0] == 'w':
                    self.board[move.startRow][move.endCol] = 'bp'
                else:
                    self.board[move.startRow][move.endCol] = 'wp'

            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:  # Queenside castle
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            # Restore previous en passant state
            self.enpassantPossibleLog.pop()
            if len(self.enpassantPossibleLog) > 0:
                self.enpassantPossible = self.enpassantPossibleLog[-1]
            else:
                self.enpassantPossible = ()

            # Undo the castling rights
            self.castleRightsLog.pop()
            if len(self.castleRightsLog) > 0:
                self.currentCastlingRights = self.castleRightsLog[-1]
            else:
                self.currentCastlingRights = CastleRights(True, True, True, True)

        # Undo halfmove clock
        if self.moveLog:
            last_move = self.moveLog[-1]
            if last_move.pieceMoved[1] == 'p' or last_move.pieceCaptured != '--':
                self.halfmoveClock = 0
            else:
                self.halfmoveClock -= 1
        else:
            self.halfmoveClock = 0
        # Undo position count
        fen = self.get_fen()
        if fen in self.positionCounts:
            self.positionCounts[fen] -= 1

    def update_position_count(self):
        fen = self.get_fen()
        self.positionCounts[fen] = self.positionCounts.get(fen, 0) + 1

    def get_fen(self):
        # Generate a FEN-like string for repetition detection
        board_str = '/'.join([''.join(row) for row in self.board])
        turn = 'w' if self.whiteToMove else 'b'
        castling = f"{int(self.currentCastlingRights.wks)}{int(self.currentCastlingRights.wqs)}{int(self.currentCastlingRights.bks)}{int(self.currentCastlingRights.bqs)}"
        ep = str(self.enpassantPossible)
        return f"{board_str} {turn} {castling} {ep}"

    def is_draw(self):
        # 50-move rule
        if self.halfmoveClock >= 100:
            self.drawBy50Move = True
            return True
        # Threefold repetition
        fen = self.get_fen()
        if self.positionCounts.get(fen, 0) >= 3:
            self.drawByRepetition = True
            return True
        self.drawBy50Move = False
        self.drawByRepetition = False
        return False

    def get_valid_moves(self):
        """All moves considering checks"""
        moves = []
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []

                # If knight is checking, must capture the knight
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:

                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(kingRow, kingCol, moves)
        else:
            moves = self.get_all_possible_moves()
            if self.whiteToMove:
                self.get_castle_moves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.get_castle_moves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True

            print('PGN of the game:')
            print(self.get_pgn())
        else:
            self.checkMate = False
            self.staleMate = False

        self.is_draw()

        return moves

    def get_castle_moves(self, r, c, moves):
        """Generate castle moves for the king at (r, c)"""
        if self.square_under_attack(r, c):
            return  # Can't castle if king is in check

        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        """Generate kingside castle moves"""
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def get_queenside_castle_moves(self, r, c, moves):
        """Generate queenside castle moves"""
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

    def square_under_attack(self, r, c):
        """Determine if the enemy can attack the square r, c"""
        self.whiteToMove = not self.whiteToMove
        opp_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove

        for move in opp_moves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Check sliding pieces and pins
        for j, d in enumerate(directions):
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        continue
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    else:  # enemy piece
                        pieceType = endPiece[1]
                        if (0 <= j <= 3 and pieceType == 'R') or \
                                (4 <= j <= 7 and pieceType == 'B') or \
                                (pieceType == 'Q') or \
                                (i == 1 and pieceType == 'K') or \
                                (i == 1 and pieceType == 'p' and
                                 ((enemyColor == 'w' and 6 <= j <= 7) or
                                  (enemyColor == 'b' and 4 <= j <= 5))):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        # Check knight attacks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in knight_moves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks

    def get_all_possible_moves(self):
        """All moves without considering checks"""
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]

                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)

        return moves

    def get_pawn_moves(self, r, c, moves):
        """Get all pawn moves from position (r, c)"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveDirection = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveDirection = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        # Move forward one square
        if 0 <= r + moveDirection < 8 and self.board[r + moveDirection][c] == "--":
            if not piecePinned or pinDirection == (moveDirection, 0):
                moves.append(Move((r, c), (r + moveDirection, c), self.board))

                # Move forward two squares from starting position
                if r == startRow and self.board[r + 2 * moveDirection][c] == "--":
                    moves.append(Move((r, c), (r + 2 * moveDirection, c), self.board))

        # Capture diagonally
        if 0 <= r + moveDirection < 8:
            # Capture left
            if c - 1 >= 0:
                if self.board[r + moveDirection][c - 1][0] == enemyColor:
                    if not piecePinned or pinDirection == (moveDirection, -1):
                        moves.append(Move((r, c), (r + moveDirection, c - 1), self.board))
                # En passant left
                elif (r + moveDirection, c - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (moveDirection, -1):
                        # Check if en passant would leave king in check
                        if not self.enpassant_leaves_king_in_check(r, c, r + moveDirection, c - 1):
                            moves.append(Move((r, c), (r + moveDirection, c - 1), self.board, isEnPassantMove=True))

            # Capture right
            if c + 1 < 8:
                if self.board[r + moveDirection][c + 1][0] == enemyColor:
                    if not piecePinned or pinDirection == (moveDirection, 1):
                        moves.append(Move((r, c), (r + moveDirection, c + 1), self.board))
                # En passant right
                elif (r + moveDirection, c + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (moveDirection, 1):
                        # Check if en passant would leave king in check
                        if not self.enpassant_leaves_king_in_check(r, c, r + moveDirection, c + 1):
                            moves.append(Move((r, c), (r + moveDirection, c + 1), self.board, isEnPassantMove=True))


    def enpassant_leaves_king_in_check(self, pawnRow, pawnCol, captureRow, captureCol):
        """Check if en passant move would leave own king in check using check_for_pins_and_checks"""
        originalMovingPawn = self.board[pawnRow][pawnCol]
        originalCapturedPawn = self.board[pawnRow][captureCol]
        originalDestination = self.board[captureRow][captureCol]

        self.board[pawnRow][pawnCol] = "--"
        self.board[pawnRow][captureCol] = "--"
        self.board[captureRow][captureCol] = originalMovingPawn

        inCheck, _, _ = self.check_for_pins_and_checks()

        self.board[pawnRow][pawnCol] = originalMovingPawn
        self.board[pawnRow][captureCol] = originalCapturedPawn
        self.board[captureRow][captureCol] = originalDestination

        return inCheck

    def get_rook_moves(self, r, c, moves):
        """Get all rook moves from position (r, c)"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        enemy_color = 'b' if self.whiteToMove else 'w'

        for dr, dc in directions:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piecePinned or pinDirection == (dr, dc) or pinDirection == (-dr, -dc):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        """Get all knight moves from position (r, c)"""
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        ally_color = 'w' if self.whiteToMove else 'b'

        for dr, dc in knight_moves:
            end_row = r + dr
            end_col = c + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piecePinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        """Get all bishop moves from position (r, c)"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        enemy_color = 'b' if self.whiteToMove else 'w'

        for dr, dc in directions:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piecePinned or pinDirection == (dr, dc) or pinDirection == (-dr, -dc):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        """Get all queen moves from position (r, c)"""
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        """Get all king moves from position (r, c)"""
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1)]
        ally_color = 'w' if self.whiteToMove else 'b'

        for dr, dc in king_moves:
            end_row = r + dr
            end_col = c + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    original_piece = self.board[end_row][end_col]
                    original_king_piece = self.board[r][c]

                    self.board[end_row][end_col] = original_king_piece
                    self.board[r][c] = "--"

                    if ally_color == 'w':
                        original_king_pos = self.whiteKingLocation
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        original_king_pos = self.blackKingLocation
                        self.blackKingLocation = (end_row, end_col)

                    inCheck, pins, checks = self.check_for_pins_and_checks()

                    self.board[r][c] = original_king_piece
                    self.board[end_row][end_col] = original_piece

                    if ally_color == 'w':
                        self.whiteKingLocation = original_king_pos
                    else:
                        self.blackKingLocation = original_king_pos

                    if not inCheck:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def update_castle_rights(self, move):
        """Update the castle rights given the move"""
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

        # Also update castling rights if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False


    def get_pgn(self):
        """Return the PGN string for the current game"""
        # Basic headers
        from datetime import datetime
        headers = [
            '[Event "Casual Game"]',
            '[Site "Local"]',
            f'[Date "{datetime.now().strftime("%Y.%m.%d")}"]',
            '[Round "-"]',
            '[White "White"]',
            '[Black "Black"]',
            '[Result "' + self.get_result() + '"]'
        ]
        pgn_moves = []
        move_number = 1
        for i, move in enumerate(self.moveLog):
            notation = move.get_chess_notation()
            if i % 2 == 0:
                pgn_moves.append(f"{move_number}. {notation}")
            else:
                pgn_moves[-1] += f" {notation}"
                move_number += 1
        pgn_str = '\n'.join(headers) + '\n\n' + ' '.join(pgn_moves) + f' {self.get_result()}'
        return pgn_str

    def get_result(self):
        """Return the PGN result string"""
        if self.checkMate:
            return "1-0" if not self.whiteToMove else "0-1"
        elif self.staleMate or self.drawBy50Move or self.drawByRepetition:
            return "1/2-1/2"
        else:
            return "*"


