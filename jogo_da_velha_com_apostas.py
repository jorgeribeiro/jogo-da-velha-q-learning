import math
import os
import sys
import copy
import time

X='X'
O='O'
BLANK=' '

PURPLE = '\033[95m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'

DEBUG=True
def debug(string):
	if DEBUG: 
		print RED + string + ENDC

def flush():
	print chr(27) + "[2J"

def partitionByDistance():
	debug(str(time.time()) + "\tPartitioning files by distance...")
        distances = os.getcwd() + "/.distances"
        if not os.path.exists(distances):
                os.makedirs(distances)
	writers = [None for i in range(9)]
	for i in range(9):
		writers[i] = open(".distances/distance" + str(i), "w")

	f = open(".legalStates", "r")
	print "here"
	exit()
	lines = f.readlines()
	f.close()

	for line in lines:
		s=line.split(',')
		x=s[0]
		o=s[1]
		num=TTTGameNode.numMissing(int(x),int(o))
		if num == 9: continue
		writers[num].write(x + "," + o)

	for writer in writers:
		writer.close()


def getNodes(i):
	if i == 9:
		return [TTTGameNode()]

	w = open(".distances/distance" + str(i), "r")
	nodeReps = w.readlines()
	w.close()

	nodes = []
	for nodeRep in nodeReps:
		xRep,oRep = nodeRep.split(",")
		board = TTTGameNode.generateBoard(int(xRep),int(oRep))
		node = TTTGameNode(board)
		nodes.append(node)
	return nodes

class TTTGameNode:
	def __init__(self, board=None):
		if not board:
			self.board = [[BLANK,BLANK,BLANK],[BLANK,BLANK,BLANK],[BLANK,BLANK,BLANK]]
		else:
			self.board = self._unsharedCopy(board)
		self.xRep,self.oRep = TTTGameNode.generateBitReps(self.board)

	def generateMove(self, nextNode):
		nextBoard = nextNode.getBoard()
		for row in range(3):
			for col in range(3):
				if self.board[row][col] != nextBoard[row][col]: 
					return row,col
		return 0,0

	def getXRep(self):
		return self.xRep

	def getORep(self):
		return self.oRep

	def isWin(self,player):
		board = self.board
		return     ((board[0][0] == board[0][1] == board[0][2] == player) \
				or  (board[1][0] == board[1][1] == board[1][2] == player) \
				or  (board[2][0] == board[2][1] == board[2][2] == player) \
				or  (board[0][0] == board[1][0] == board[2][0] == player) \
				or  (board[0][1] == board[1][1] == board[2][1] == player) \
				or  (board[0][2] == board[1][2] == board[2][2] == player) \
				or  (board[0][0] == board[1][1] == board[2][2] == player) \
				or  (board[0][2] == board[1][1] == board[2][0] == player))

	def getBoard(self):
		return self._unsharedCopy(self.board)

	def _unsharedCopy(self,inList):
		if isinstance(inList, list):
			return list( map(self._unsharedCopy, inList) )
		return inList

	def isTerminal(self):
		return self.isWin(X) or self.isWin(O) or self._isFull()
	
	def generateLegalMoves(self):
		if self.isTerminal():
			return []
		legalMoves = []
		for row in range(3):
			for col in range(3):
				if self.board[row][col] == BLANK:
					legalMoves.append((row,col))
		return legalMoves

	def generateChild(self, player, (row,col)):
		board = self.getBoard()
		board[row][col] = player
		return TTTGameNode(board)

	def generateChildren(self, player):
		children = []
		board = self.getBoard()
		for row,col in self.generateLegalMoves():
			board[row][col] = player
			children.append(TTTGameNode(board)) 
			board[row][col] = BLANK 
		return children

	def generateLastMoves(self):
		board = self.getBoard()
		lastMoves = []
		for row in range(3):
			for col in range(3):
				if board[row][col] != BLANK:
					player = board[row][col]
					board[row][col] = BLANK
					if not self.isWin(board):
						lastMoves.append((row,col))
					board[row][col] = player
		return lastMoves			   

	def generateParent(self,lastMove):
		board = self.getBoard()
		row,col = lastMove
		board[row][col] = BLANK
		return TTTGameNode(board)


	def __hash__(self):
		return (hash(self.board[0][0]) ^ hash(self.xRep)) >> 1

	def __eq__(self,other):
		otherBoard = other.getBoard()
		for row in range(3):
			for col in range(3):
				if otherBoard[row][col] != self.board[row][col]:
					return False
		return True

	def __str__(self):
		return ' '+self.board[0][0]+' | '+self.board[0][1]+' | '+self.board[0][2]+' \n'+\
		       '---+---+---\n'+\
		       ' '+self.board[1][0]+' | '+self.board[1][1]+' | '+self.board[1][2]+' \n'+\
		       '---+---+---\n'+\
		       ' '+self.board[2][0]+' | '+self.board[2][1]+' | '+self.board[2][2]+' \n'

	@staticmethod
	def generateBoard(intX, intO):
		board = [[BLANK,BLANK,BLANK],[BLANK,BLANK,BLANK],[BLANK,BLANK,BLANK]]
		# We mask the most signficant bit (i.e., the upper left board space) first
		mask = 0b100000000 
		for row in range(3):
			for col in range(3):
				# ((intX & 1) == 1) and ((intO & 1) == 1) are mutually exclusive.
				if intX & mask:
					board[row][col] = X
				elif intO & mask:
					board[row][col] = O
				# Shift the mask right to get the next bit/space for next iteration
				mask >>= 1 
		return board

	@staticmethod
	def generateBitReps(board):
		intX = 0
		intO = 0
		mask = 0b100000000
		for row in range(3):
			for col in range(3):
				if board[row][col] == X:
					intX += mask
				elif board[row][col] == O:
					intO += mask
				mask >>= 1
		return (intX, intO)

	@staticmethod
	def numMissing(xRep,oRep):
		bits = xRep | oRep
		count = 0
		for i in range(9):
			if (bits & 1) == 0: count += 1
			bits = bits >> 1
		return count

	def _isFull(self):
		for row in range(3):
			for col in range(3):
				if self.board[row][col] == BLANK: return False
		return True

class TTTDiscretePlayer:
	def __init__(self,player,totalChips):
		self.player = player
		self.opponent = PlayTTT.getOpponent(player)
		self.totalChips = totalChips

		self.nodesToDiscreteRich = [{},{},{},{},{},{},{},{},{},{}]
		self.nodesToMoveBid = [{},{},{},{},{},{},{},{},{},{}]
		self.generateStrategy()

	def getMoveBid(self,currentNode):
		numBlanks = TTTGameNode.numMissing(currentNode.getXRep(),currentNode.getORep())
		move,bid = self.nodesToMoveBid[numBlanks][currentNode]
		return move,bid

	def generateStrategy(self):
		print "\tCarregando arquivos de treinamento..."
                distances = os.getcwd() + "/.distances"
                if not os.path.exists(distances):
                        partitionByDistance()
		nodes0 = getNodes(0)

		for node in nodes0:
			if node.isWin(self.player):
				self.nodesToDiscreteRich[0][node] = 0.0
			else:
				self.nodesToDiscreteRich[0][node] = self.totalChips + 1.0
				
		for i in range(1,10):
			nodes = getNodes(i)

			for node in nodes:
				if node.isWin(self.player):
					self.nodesToDiscreteRich[i][node] = 0.0
					continue
				elif node.isWin(self.opponent):
					self.nodesToDiscreteRich[i][node] = self.totalChips + 1.0
					continue
					
				Fmax = -1.0
				Fmin = sys.maxint 
				myChildren = node.generateChildren(self.player)
				oppChildren = node.generateChildren(self.opponent)

				for myChild in myChildren:
					if Fmin > self.nodesToDiscreteRich[i-1][myChild]:
						Fmin = self.nodesToDiscreteRich[i-1][myChild]
						favoredChild = myChild

				for oppChild in oppChildren:
					Fmax = max(Fmax,self.nodesToDiscreteRich[i-1][oppChild])
   	
				FmaxVal = math.floor(Fmax)
				FminVal = math.floor(Fmin)
				Fsum = FmaxVal + FminVal

				# If Fsum is odd and Fmin \in \N*
				if (Fsum % 2 == 1) and FminVal < Fmin:
					epsilon = 1.0
					bid = math.floor(abs(FmaxVal-FminVal)/2.0) * 1.0
				# Else if Fsum is odd and Fmin \in \N
				elif (Fsum % 2 == 1) and FminVal == Fmin:
					epsilon = 0.5
					bid = math.floor(abs(FmaxVal-FminVal)/2.0) + 0.25
				# Else if Fsum is even and Fmin \in \N*
				elif (Fsum % 2 == 0) and FminVal < Fmin:
					epsilon = 0.5
					bid = max(0,abs(FmaxVal-FminVal)/2.0 - 0.75)
				# Else (i.e., if Fsum is even and Fmin \in \N)
				else:
					epsilon = 0.0
					bid = abs(FmaxVal-FminVal)/2.0

				self.nodesToDiscreteRich[i][node] = math.floor(Fsum/2.0) + epsilon
				self.nodesToMoveBid[i][node] = (node.generateMove(favoredChild), bid)
		
class PlayTTT:	
	def __init__(self):
		self.biddingType = 'd' # discrete values
		self.gamenode = TTTGameNode()

		# chipNo = self._queryChipCount()
		chipNo = 100
		agentChips = float(math.ceil(0.5*chipNo))
		self.chips = {X:chipNo-agentChips,O:agentChips}
		self.rules = "Jogo da velha com apostas (50 fichas)."
		self.agent = TTTDiscretePlayer(O, chipNo)

		if self._queryStartWithTieBreakingChip():
			self.chips[X] += 0.5
		else:
			self.chips[O] += 0.5

		self.agentLastBid = None
		self.userWonLastBid = -1

		print "\tIniciando jogo..."
		self.playDiscrete()

	def updateGameState(self, player, move, bid):
		self.gamenode = self.gamenode.generateChild(player,move) 

		if player == X:
			self.userWonLastBid = 1
			self.chips[X] -= bid
			self.chips[O] += bid
		else:
			self.userWonLastBid = 0
			self.chips[X] += bid
			self.chips[O] -= bid

	def playDiscrete(self):
		self._printBoard()
		while not self.gamenode.isTerminal():
			userBid = self._queryBid() 
			userMove = self._queryMove()

			agentMove,agentBid = self.agent.getMoveBid(self.gamenode)
			agentHasTieBreaker = ((self.chips[O] % 1) == 0.5)

			if agentBid % 1 == 0.25:
				if agentHasTieBreaker:
					agentBid = math.floor(agentBid)
				else:
					if agentBid < self.chips[O]:
						agentBid = math.ceil(agentBid)
						
			self.agentLastBid = agentBid
			if int(userBid) > int(agentBid):
				self.updateGameState(X, userMove, userBid)

			elif int(userBid) < int(agentBid):
				self.updateGameState(O, agentMove, agentBid)
			
			elif int(userBid) == int(agentBid) and agentHasTieBreaker:
 				self.updateGameState(O, agentMove, agentBid+0.5)
			
			else: # int(userBid) == int(agentBid) and not agentHasTieBreaker
				if self._queryUseTieBreakingChip():
					self.updateGameState(X, userMove, userBid+0.5)
				else:
					self.updateGameState(O, agentMove, agentBid)
				
			self._printStatus()
			
		if self.gamenode.isWin(X):
			print "Voce venceu!"
		elif self.gamenode.isWin(O):
			print "Voce perdeu."
		else:
			print "Empate!"

		sys.exit("Fim de jogo.")

	@staticmethod
	def getOpponent(player):
		if player == X: return O
		return X

	def _printBoard(self):
		board = self.gamenode.getBoard()
		c = ['' for i in range(9)]
		i = 0
		for row in range(len(board)):
			for col in range(len(board[row])):
				cell = board[row][col]
				if cell == BLANK:
					c[i] = str(i + 1)
				else:
					c[i] = ' '
   				i += 1

		colSep = "|"
		helpRow1 = " " + c[0] + " " + colSep + " " + c[1] + " " + colSep + " " + c[2]
		helpRow2 = " " + c[3] + " " + colSep + " " + c[4] + " " + colSep + " " + c[5]
		helpRow3 = " " + c[6] + " " + colSep + " " + c[7] + " " + colSep + " " + c[8]
		helpRowSep = "---+---+---"

		bTitle = " TABULEIRO "
		hTitle = " ONDE JOGAR "
		rowSep = "---+---+---"
		tab = "\t"

		print bTitle, tab, hTitle

		print '', board[0][0] , colSep , board[0][1] , colSep , board[0][2] , tab , helpRow1
		print rowSep, tab, helpRowSep
		print '', board[1][0] , colSep , board[1][1] , colSep , board[1][2] , tab , helpRow2
		print rowSep, tab, helpRowSep
		print '', board[2][0] , colSep , board[2][1] , colSep , board[2][2] , tab , helpRow3
		print ''

	def _printChips(self):
		c1 = str(self.chips[X])
		c2 = str(self.chips[O])

		if self.biddingType == 'd':
			c1 = c1[:-2]
			c2 = c2[:-2]
			if ((self.chips[X] % 1) == 0.5):
				c1 += "*"
			if ((self.chips[O] % 1) == 0.5):
				c2 += "*"

		l = str(self.agentLastBid)
		header = " " + "VC:".rjust(len(c1)) + "\t" + "CPU:".rjust(len(c2)) + "\t" + "ULTIMA APOSTA DA CPU:".rjust(len(l))
		footer = " " + c1 + "\t" + c2 + "\t" + l
		print header
		print footer

	def _printStatus(self):
		flush()
		print self.rules
		print '\n\n\n'
		
		self._printChips()
		print ''
		self._printBoard()
		print '\n'

		if self.userWonLastBid == 1:
			print "Voce venceu a aposta.\n\n"
		elif self.userWonLastBid == 0:
			print "Voce perdeu a aposta.\n\n"
		else:
			print "\n\n"

	def _queryStartWithTieBreakingChip(self):
		while True:
			flush()
			answer = raw_input("Gostaria de iniciar com a ficha de desempate? ('s' or 'n')? ").lower()
			if answer[0] == 's':
				return True
			elif answer[0] == 'n':
				return False
			continue

	def _queryChipCount(self):
		query = "Informe o total de fichas do jogo: "
		while True:
			flush()
			try:
				chips = int(float(raw_input(query)))
			except ValueError:
				continue
			if chips >= 0: # Can't have negative chips
				break
		return chips
			
	def _queryUseTieBreakingChip(self):
		query = "Houve empate nas apostas. Gostaria de usar a ficha de desempate? ('s' ou 'n')? "
		while True:
			self._printStatus()
			answer = raw_input(query).lower()
			if answer[0] == 's':
				return True
			elif answer[0] == 'n':
				return False

	def _queryBid(self):
		query = "Informe uma aposta nao negativa de ate " + str(int(self.chips[X])) + ": "
		while True:
			self._printStatus()
			try:
				bid = int(raw_input(query))
			except ValueError:
				continue
			if self._isLegalBid(bid):
				break

   		return bid

	def _queryMove(self):
		query = "Informe onde deseja jogar: "
		while True:
			self._printStatus()
			userMoveList = raw_input(query).split()
			if len(userMoveList) != 1:
				continue
			try:
				for i in userMoveList:
					int(i)
			except ValueError:
				continue

			row,col = self._squareToCoordinates(int(userMoveList[0]))
			if self._isLegalMove(row,col): 
				break
		return (row,col)

	def _squareToCoordinates(self, square):
		if 0 < square < 10:
			col = (square-1) % 3
			row = (square-1) / 3
			return (row, col)
		return (None,None)
	
	def _isLegalMove(self, row, col):
		if row is None or col is None: 
			return False
		try:
			return self.gamenode.board[row][col] == BLANK
		except IndexError:
			return False
	
	def _isLegalBid(self, bid):
		return 0 <= bid <= self.chips[X]

if __name__ == '__main__':
	PlayTTT()