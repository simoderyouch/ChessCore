import random

# Base material scores
PIECE_SCORES = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "p": 100}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3



# Piece-Square Tables (PST) for positional evaluation
PST = {
    'p': [  # Pawn
        [0,   0,   0,   0,   0,   0,   0,   0],
        [50,  50,  50,  50,  50,  50,  50,  50],
        [10,  10,  20,  30,  30,  20,  10,  10],
        [5,   5,  10,  25,  25,  10,   5,   5],
        [0,   0,   0,  20,  20,   0,   0,   0],
        [5,  -5, -10,   0,   0, -10,  -5,   5],
        [5,  10,  10, -20, -20,  10,  10,   5],
        [0,   0,   0,   0,   0,   0,   0,   0],
    ],
    'N': [  # Knight
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20,   0,   5,   5,   0, -20, -40],
        [-30,   5,  10,  15,  15,  10,   5, -30],
        [-30,   0,  15,  20,  20,  15,   0, -30],
        [-30,   5,  15,  20,  20,  15,   5, -30],
        [-30,   0,  10,  15,  15,  10,   0, -30],
        [-40, -20,   0,   0,   0,   0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50],
    ],
    'B': [  # Bishop
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10,   5,   0,   0,   0,   0,   5, -10],
        [-10,  10,  10,  10,  10,  10,  10, -10],
        [-10,   0,  10,  10,  10,  10,   0, -10],
        [-10,   5,   5,  10,  10,   5,   5, -10],
        [-10,   0,   5,  10,  10,   5,   0, -10],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20],
    ],
    'R': [  # Rook
        [0,   0,   5,  10,  10,   5,   0,   0],
        [-5,   0,   0,   0,   0,   0,   0,  -5],
        [-5,   0,   0,   0,   0,   0,   0,  -5],
        [-5,   0,   0,   0,   0,   0,   0,  -5],
        [-5,   0,   0,   0,   0,   0,   0,  -5],
        [-5,   0,   0,   0,   0,   0,   0,  -5],
        [5,  10,  10,  10,  10,  10,  10,   5],
        [0,   0,   0,   0,   0,   0,   0,   0],
    ],
    'Q': [  # Queen
        [-20, -10, -10,  -5,  -5, -10, -10, -20],
        [-10,   0,   5,   0,   0,   0,   0, -10],
        [-10,   5,   5,   5,   5,   5,   0, -10],
        [ -5,   0,   5,   5,   5,   5,   0,  -5],
        [  0,   0,   5,   5,   5,   5,   0,  -5],
        [-10,   5,   5,   5,   5,   0,   0, -10],
        [-10,   0,   5,   0,   0,   0,   0, -10],
        [-20, -10, -10,  -5,  -5, -10, -10, -20],
    ],
    'K': [  # King (middlegame)
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [ 20,  20,   0,   0,   0,   0,  20,  20],
        [ 20,  30,  10,   0,   0,  10,  30,  20],
    ]
}

# Endgame king table (when material is low)
PST_KING_ENDGAME = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10,   0,   0, -10, -20, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -30,   0,   0,   0,   0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50],
]


def find_random_move(valid_moves):
    """Return a random move from valid moves."""
    if not valid_moves:
        return None
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def is_endgame(gs):
    """Determine if we're in endgame based on material count."""
    total_material = 0
    for row in gs.board:
        for square in row:
            if square != '--':
                piece = square[1]
                if piece != 'K':  
                    total_material += PIECE_SCORES.get(piece, 0)
    return total_material < 1300  


def evaluate_position(gs):
    """Evaluate the current position."""
    
    if gs.checkMate:
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    if gs.staleMate:
        return STALEMATE

    score = 0
    endgame = is_endgame(gs)
    
    
    for r, row in enumerate(gs.board):
        for c, square in enumerate(row):
            if square == '--':
                continue
            
            color = 1 if square[0] == 'w' else -1
            piece = square[1]
            
            # Material value
            base_score = PIECE_SCORES[piece]
            
            
            pst_table = PST.get(piece)
            if pst_table:
                if color == 1:  # White
                    pst_bonus = pst_table[r][c]
                else:  # Black (mirror the table)
                    pst_bonus = pst_table[7 - r][c]
            else:
                pst_bonus = 0
            
            
            if piece == 'K' and endgame:
                if color == 1:
                    pst_bonus = PST_KING_ENDGAME[r][c]
                else:
                    pst_bonus = PST_KING_ENDGAME[7 - r][c]
            
            score += color * (base_score + pst_bonus)
    
    return score


def minimax_alpha_beta(gs, valid_moves, depth, alpha, beta, white_to_move):
    """Minimax with alpha-beta pruning."""
    
    if gs.checkMate:
        return (-CHECKMATE if white_to_move else CHECKMATE), None
    if gs.staleMate:
        return STALEMATE, None
    if depth == 0:
        return evaluate_position(gs), None

    best_move = None
    
    if white_to_move: 
        max_eval = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            eval_score, _ = minimax_alpha_beta(gs, next_moves, depth - 1, alpha, beta, False)
            gs.undo_move()

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:  # Beta cutoff
                break
        
        return max_eval, best_move
    
    else:  # Minimizing player
        min_eval = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            eval_score, _ = minimax_alpha_beta(gs, next_moves, depth - 1, alpha, beta, True)
            gs.undo_move()

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:  # Alpha cutoff
                break
        
        return min_eval, best_move


def move_ordering_key(move):
    """Key function for move ordering (captures first)."""
    if hasattr(move, 'pieceCaptured') and move.pieceCaptured != '--':
        return -PIECE_SCORES.get(move.pieceCaptured[1], 0)
    return 0


def find_best_move(gs, depth=DEPTH):
    """Find the best move using minimax with alpha-beta pruning."""

        
    valid_moves = gs.get_valid_moves()
    if not valid_moves:
        return None
    
    # Order moves (captures first for better alpha-beta pruning)
    ordered_moves = sorted(valid_moves, key=move_ordering_key)
    
    best_score = -CHECKMATE if gs.whiteToMove else CHECKMATE
    best_moves = []

    for move in ordered_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score, _ = minimax_alpha_beta(gs, next_moves, depth - 1, -CHECKMATE, CHECKMATE, not gs.whiteToMove)
        gs.undo_move()
        
        if gs.whiteToMove:  # Maximizing
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        else:  # Minimizing
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

    if not best_moves:
        return random.choice(valid_moves)

    # Anti-repetition: avoid immediately undoing the last move with major pieces
    if len(gs.moveLog) >= 1:
        last_move = gs.moveLog[-1]
        filtered_moves = []
        for move in best_moves:
            # Check if this move would undo the last move
            is_repetition = (
                hasattr(move, 'pieceMoved') and 
                move.pieceMoved[1] in ('R', 'B', 'Q') and
                move.startRow == last_move.endRow and
                move.startCol == last_move.endCol and
                move.endRow == last_move.startRow and
                move.endCol == last_move.startCol
            )
            if not is_repetition:
                filtered_moves.append(move)
        
        if filtered_moves:
            best_moves = filtered_moves

    return best_moves[0] if best_moves else valid_moves[0]




