""""
Store state of a chess game and determining the valid moves at current state
"""

class GameState:
    def __init__(self):
        self.board = [
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


        self.whiteToMove = True
        self.moveLog = []

    def make_move(self, move):
        """Takes a Move as parameter and executes it (Not working with castling, en-passant and pawn promotion)"""
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undo_move(self):
        """Undo the last move made"""
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    def get_valid_moves(self):
        """All moves considering checks"""

        return self.get_all_possible_moves()

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
        if self.whiteToMove:

            # Move forward one square
            if r - 1 >= 0 and self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                # Move forward two squares from starting position
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))

            # Capture diagonally
            if r - 1 >= 0:
                # Capture left
                if c - 1 >= 0 and self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                # Capture right
                if c + 1 < 8 and self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))

        else:  # Black pawn moves
            # Move forward one square
            if r + 1 < 8 and self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                # Move forward two squares from starting position
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))

            # Capture diagonally
            if r + 1 < 8:
                # Capture left
                if c - 1 >= 0 and self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                # Capture right
                if c + 1 < 8 and self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))


    def get_rook_moves(self, r, c, moves):
        """Get all rook moves from position (r, c)"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        enemy_color = 'b' if self.whiteToMove else 'w'

        for dr, dc in directions:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
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

        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        ally_color = 'w' if self.whiteToMove else 'b'

        for dr, dc in knight_moves:
            end_row = r + dr
            end_col = c + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # Not own piece
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    def get_bishop_moves(self, r, c, moves):
        """Get all bishop moves from position (r, c)"""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # diagonals
        enemy_color = 'b' if self.whiteToMove else 'w'

        for dr, dc in directions:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
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
                    moves.append(Move((r, c), (end_row, end_col), self.board))


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

    def get_chess_notation(self):
        """Convert move to chess notation"""
        piece = self.pieceMoved[1]  # second char = piece type (p, R, N, B, Q, K)
        dest_square = self.get_rank_file(self.endRow, self.endCol)

        # Pawn moves
        if piece == "p":
            if self.pieceCaptured != "--":
                # Show capture with file of pawn
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