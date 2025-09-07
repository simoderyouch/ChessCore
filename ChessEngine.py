"""
Store state of a chess game and determining the valid moves at current state
"""

class GameState:
    def __init__(self):
        self.board= [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],   # 8th rank (black back row)
            ["bp","bp","bp","bp","bp","bp","bp","bp"],   # 7th rank (black pawns)
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

        self.whiteToMove = True
        self.moveLog = []

    def make_move(self, move):
        """Takes a Move as parameter and executes it"""
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

        self.whiteToMove = not self.whiteToMove

        # Update the kings location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        if move.isPawnPromotion:
            # Default to Queen promotion, but this can be modified to allow user choice
            promotedPiece = move.pieceMoved[0] + move.promotionPiece
            self.board[move.endRow][move.endCol] = promotedPiece

        # En Passant Move
        if move.isEnpassantMove:
            # Remove the captured pawn (which is on the same rank as the moving pawn)
            self.board[move.startRow][move.endCol] = '--'

        # Update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            # Pawn moved two squares, en passant is now possible
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # Log en passant state for undo functionality
        self.enpassantPossibleLog.append(self.enpassantPossible)

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
                # Restore the captured pawn
                if move.pieceMoved[0] == 'w':  # White pawn captured black pawn
                    self.board[move.startRow][move.endCol] = 'bp'
                else:  # Black pawn captured white pawn
                    self.board[move.startRow][move.endCol] = 'wp'

            # Restore previous en passant state
            self.enpassantPossibleLog.pop()
            if len(self.enpassantPossibleLog) > 0:
                self.enpassantPossible = self.enpassantPossibleLog[-1]
            else:
                self.enpassantPossible = ()

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
            if len(self.checks) == 1:  # Only one check, can block or capture
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
                    # Can block the check or capture the checking piece
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                # Remove moves that don't block or capture
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # Multiple checks, only king can move
                self.get_king_moves(kingRow, kingCol, moves)
        else:
            moves = self.get_all_possible_moves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

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
        # Save current state
        originalMovingPawn = self.board[pawnRow][pawnCol]
        originalCapturedPawn = self.board[pawnRow][captureCol]  # The pawn being captured
        originalDestination = self.board[captureRow][captureCol]

        # Make the en passant move temporarily
        self.board[pawnRow][pawnCol] = "--"  # Remove moving pawn
        self.board[pawnRow][captureCol] = "--"  # Remove captured pawn
        self.board[captureRow][captureCol] = originalMovingPawn  # Place moving pawn

        # Check if king is now in check using the existing method
        inCheck, _, _ = self.check_for_pins_and_checks()

        # Restore original state
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


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startsq, endsq, board, isEnPassantMove=False, promotionPiece='Q'):
        self.startRow = startsq[0]
        self.startCol = startsq[1]
        self.endRow = endsq[0]
        self.endCol = endsq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn promotion logic
        self.isPawnPromotion = ((self.pieceMoved == 'wp' and self.endRow == 0) or
                               (self.pieceMoved == 'bp' and self.endRow == 7))
        self.promotionPiece = promotionPiece  # Default to Queen, can be 'Q', 'R', 'B', 'N'

        # En passant logic
        self.isEnpassantMove = isEnPassantMove
        if self.isEnpassantMove:
            # In en passant, the captured piece is not at the destination square
            if self.pieceMoved == 'wp':
                self.pieceCaptured = 'bp'
            else:
                self.pieceCaptured = 'wp'

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        """Override equals method"""
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_move_notation(self):
        """Get move in algebraic notation (e.g., e2e4)"""
        notation = self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)
        if self.isPawnPromotion:
            notation += self.promotionPiece.lower()
        return notation

    def get_chess_notation(self):
        """Convert move to standard chess notation"""
        piece = self.pieceMoved[1]
        dest_square = self.get_rank_file(self.endRow, self.endCol)

        if piece == "p":
            if self.pieceCaptured != "--":
                notation = self.colsToFiles[self.startCol] + "x" + dest_square
            else:
                notation = dest_square

            if self.isPawnPromotion:
                notation += "=" + self.promotionPiece
        else:
            notation_piece = piece.upper()
            if self.pieceCaptured != "--":
                notation = notation_piece + "x" + dest_square
            else:
                notation = notation_piece + dest_square

        return notation

    def get_rank_file(self, r, c):
        """Convert row, col to chess notation (e.g., e4)"""
        return self.colsToFiles[c] + self.rowsToRanks[r]