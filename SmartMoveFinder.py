import random 



pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3


def findRandomMove(validMoves) : 
	return validMoves[random.randint(0, len(validMoves)-1)]



'''Find the best move based on material gain'''
def findBestMove(gs , validMoves) : 

	turnMultiplier = 1 if gs.whiteToMove else -1

	opponentMinMaxScore = CHECKMATE

	bestPlayerMove = None

	random.shuffle(validMoves)

	for playerMove in validMoves : 
		gs.make_move(playerMove)

		opponentsMoves = gs.get_valid_moves()
 
		opponentMaxScore = -CHECKMATE
		for opponentMove in opponentsMoves : 

			gs.make_move(opponentMove)  
			if gs.checkMate :
				
				score = -turnMultiplier * CHECKMATE

			elif gs.staleMate :

				score = STALEMATE

			else : 
				score  = -turnMultiplier * scoreBoard(gs)

			if score > opponentMaxScore :
				opponentMaxScore = score

			gs.undo_move()


		if  opponentMaxScore < opponentMinMaxScore :
			opponentMinMaxScore = opponentMaxScore
			bestPlayerMove = playerMove



		gs.undo_move()
	return bestPlayerMove



	 
	  

'''Score the board based on material'''
def scoreBoard(gs) :
	
	
	score = 0
	for row in gs.board :
		for square in row :
			if square[0] == 'w' :
				score += pieceScore[square[1]]
			elif square[0] == 'b' :
				score -= pieceScore[square[1]]
	return score