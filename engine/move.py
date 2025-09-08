"""Move data structure and notation helpers."""


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startsq, endsq, board, isEnPassantMove=False, isCastleMove=False, promotionPiece='Q'):
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

        # Castle logic
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        """Override equals method"""
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_move_notation(self):
        """Get move in algebraic notation (e.g., e2e4)"""
        if self.isCastleMove:
            if self.endCol == 6:  # Kingside castle
                return "O-O"
            else:  # Queenside castle
                return "O-O-O"

        notation = self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)
        if self.isPawnPromotion:
            notation += self.promotionPiece.lower()
        return notation

    def get_chess_notation(self):
        """Convert move to standard chess notation"""
        if self.isCastleMove:
            if self.endCol == 6:  # Kingside castle
                return "O-O"
            else:  # Queenside castle
                return "O-O-O"

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


