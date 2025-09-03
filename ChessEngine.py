""""
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
            'p' : self.get_pawn_moves , 'R' : self.get_rook_moves , 'N' : self.get_knight_moves , 'B' : self.get_bishop_moves , 'K' : self.get_king_moves, 'Q' : self.get_queen_moves
        }

        self.whiteKingLocation = (7 , 4)
        self.blackKingLocation = (0 , 4 )

        self.checkMate = False
        self.staleMate = False

        # Advanced algorithme for  Check and StaleMate
        self.inCheck = False
        self.pins = []
        self.checks = []






        self.whiteToMove = True
        self.moveLog = []

    def make_move(self, move):
        """Takes a Move as parameter and executes it (Not working with castling, en-passant and pawn promotion)"""
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

        self.whiteToMove = not self.whiteToMove

        # update the kings location if moved

        if move.pieceMoved == 'wK' :
            self.whiteKingLocation = ( move.endRow ,move.endCol)

        if move.pieceMoved == 'bK' :
            self.blackKingLocation = ( move.endRow ,move.endCol)



    def undo_move(self):
        """Undo the last move made"""
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)

            if move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)




    def get_valid_moves(self):
        """All moves considering checks"""

        moves = [ ]
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.whiteToMove :
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]

        else :
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]


        if self.inCheck :

            if len(self.checks) == 1 :
                moves = self.get_all_possible_moves()

                check = self.checks[0]

                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol][1]


                validSquares = []

                if pieceChecking == 'N':
                    validSquares = [(checkRow, checkCol)]
                else :

                    for i in range( 1 , 8 ) :
                        validSquare = ( kingRow + check[2] * i , kingCol + check[3] * i )
                        validSquares.append( validSquare )


                        if validSquare[0] == checkRow  and validSquare[1] == checkCol :
                            break

                for i in range( len(moves) -1 , -1 , -1) :
                    if moves[i].pieceMoved[1] != 'K' :
                        if not ( moves[i].endRow , moves[i].endCol ) in validSquares :
                            moves.remove(moves[i])

            else :
                self.get_king_moves(kingRow, kingCol , moves)

        else :
            moves = self.get_all_possible_moves()

        if len(moves) == 0 :
            if self.in_check() :
                self.checkMate = True
            else :
                self.staleMate = True

        else :

            self.checkMate = False
            self.staleMate = False

        if self.checkMate:
            print("Checkmate")
        if self.staleMate:
            print("Stalemate")

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

        # check sliding pieces and pins
        for j, d in enumerate(directions):
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        continue
                    if endPiece[0] == allyColor and  endPiece[1] != 'K':
                        # first allied piece in this direction — could be pinned
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            # second allied piece blocks; no pin here
                            break
                    else:  # enemy piece
                        pieceType = endPiece[1]
                        # Rook checks on orthogonal dirs (0..3), bishop on diagonal (4..7)
                        if (0 <= j <= 3 and pieceType == 'R') or \
                                (4 <= j <= 7 and pieceType == 'B') or \
                                (pieceType == 'Q') or \
                                (i == 1 and pieceType == 'K') or \
                                (i == 1 and pieceType == 'p' and
                                 ((enemyColor == 'w' and 6 <= j <= 7) or
                                  (enemyColor == 'b' and 4 <= j <= 5))):
                            if possiblePin == ():  # no blocker -> check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                # piece is giving check but blocked by one ally -> that ally is pinned
                                pins.append(possiblePin)
                                break
                        else:
                            # enemy piece not giving check along this ray
                            break
                else:
                    break

        # check knight attacks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in knight_moves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    # for knights, direction is just the knight offset (not used for blocking)
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks



    # Naive Algorithm to get valid moves and Checks
    def get_valid_moves_naive(self):
        """All moves considering checks"""
        # 1. generate all possible moves
        moves = self.get_all_possible_moves()
        # 2. for each move, make the move
        for i in range(len(moves)-1, -1 , -1 ) :
            self.make_move(moves[i])
             # 3. generate all opponent's moves
             # 4. check if opponents moves check the king

            self.whiteToMove = not self.whiteToMove

            if self.in_check() :
                moves.remove(moves[i])  # 5. if attack not valid moves

            self.whiteToMove = not self.whiteToMove
            self.undo_move()

        if len(moves) == 0 :
            if self.in_check() :
                self.checkMate = True
            else :
                self.staleMate = True

        else :

            self.checkMate = False
            self.staleMate = False

        return moves
    def in_check(self) :
        if self.whiteToMove :
            return self.square_under_attack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else :
            return self.square_under_attack(self.blackKingLocation[0], self.blackKingLocation[1])
    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        opp_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in opp_moves:
            if move.endRow == r and move.endCol == c :
                return True
        return False







    def get_all_possible_moves(self):
        """All moves without considering checks"""
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # 'w', 'b', or '-'

                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)

        return moves


    def get_pawn_moves(self, r, c, moves):
        """Get all pawn moves from position (r, c)"""

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1 , -1 , -1 ) :
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2] , self.pins[i][3])
                self.pins.remove(self.pins[i])
                break



        if self.whiteToMove:

            # Move forward one square
            if r - 1 >= 0 and self.board[r-1][c] == "--":

                if not piecePinned or pinDirection == (-1 , 0) :
                    moves.append(Move((r, c), (r-1, c), self.board))
                    # Move forward two squares from starting position
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r-2, c), self.board))

            # Capture diagonally
            if r - 1 >= 0:
                # Capture left
                if c - 1 >= 0 and self.board[r-1][c-1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                # Capture right
                if c + 1 < 8 and self.board[r-1][c+1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r-1, c+1), self.board))

        else:  # Black pawn moves
            # Move forward one square
            if r + 1 < 8 and self.board[r+1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    # Move forward two squares from starting position
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r+2, c), self.board))

            # Capture diagonally
            if r + 1 < 8:
                # Capture left
                if c - 1 >= 0 and self.board[r+1][c-1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                # Capture right
                if c + 1 < 8 and self.board[r+1][c+1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board))

    def get_rook_moves(self, r, c, moves):
        """Get all rook moves from position (r, c)"""


        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1 , -1 , -1 ) :
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2] , self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break




        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        enemy_color = 'b' if self.whiteToMove else 'w'

        for dr, dc in directions:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:

                    if not piecePinned or pinDirection == (dr , dc) or pinDirection == (-dr , -dc):

                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # Empty square
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # Enemy piece
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break  # Can't move further
                        else:  # Own piece
                            break
                else:
                    break  # Off board

    def get_knight_moves(self, r, c, moves):
        """Get all knight moves from position (r, c)"""

        piecePinned = False
        for i in range(len(self.pins) -1 , -1 , -1 ) :
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
                if not piecePinned :
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # Not own piece
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        """Get all bishop moves from position (r, c)"""

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1 , -1 , -1 ) :
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2] , self.pins[i][3])
                self.pins.remove(self.pins[i])
                break


        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # diagonals
        enemy_color = 'b' if self.whiteToMove else 'w'

        for dr, dc in directions:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piecePinned or pinDirection == (dr, dc) or pinDirection == (-dr, -dc):
                        end_piece = self.board[end_row][end_col]

                        if end_piece == "--":  # Empty square
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # Enemy piece
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break  # Can't move further
                        else:  # Own piece
                            break
                else:
                    break  # Off board

    def get_queen_moves(self, r, c, moves):
        """Get all queen moves from position (r, c)"""
        # Queen moves like both rook and bishop
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
                if end_piece[0] != ally_color:  # Not own piece

                    if ally_color == 'w' :
                        self.whiteKingLocation = (end_row, end_col)
                    else :
                        self.blackKingLocation = (end_row, end_col)

                    inCheck , pins , checks = self.check_for_pins_and_checks()

                    if not inCheck :
                         moves.append(Move((r, c), (end_row, end_col), self.board))

                    if ally_color == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)












class Move:
    # Maps keys to values
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startsq, endsq, board):
        self.startRow = startsq[0]
        self.startCol = startsq[1]
        self.endRow = endsq[0]
        self.endCol = endsq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        """Override equals method"""
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_move_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_chess_notation(self):
        """Convert move to chess notation"""
        piece = self.pieceMoved[1]
        dest_square = self.get_rank_file(self.endRow, self.endCol)

        # Pawn moves
        if piece == "p":
            if self.pieceCaptured != "--":
                return self.colsToFiles[self.startCol] + "x" + dest_square
            else:
                return dest_square

        # Non-pawn moves
        notation_piece = piece.upper()
        if self.pieceCaptured != "--":
            return notation_piece + "x" + dest_square
        else:
            return notation_piece + dest_square

    def get_rank_file(self, r, c):
        """Convert row, col to chess notation (e.g., e4)"""
        return self.colsToFiles[c] + self.rowsToRanks[r]