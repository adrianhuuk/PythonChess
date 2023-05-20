# Copyright (c) <year>, <copyright holder>
# All rights reserved.

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. 

# In this version of chess, check is not a forcing move. However, the king can be taken which is how the game is won/lost.

import pygame
# pygame.init()

pygame.font.init()
sprites = pygame.sprite.Group()

# Define Stuff
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
font = pygame.font.SysFont('Comic Sans MS', 30)

# Define window
window = pygame.display.set_mode((720, 720))
pygame.display.set_caption("Chess")
window.fill(BLACK)
window_width = window.get_size()[0]

# Board Definition
class Board(pygame.sprite.Sprite):
	def __init__(self, size: int, image: str, pos: list, margin: list = [0, 0]):
		self.pos = pos
		self.size = size
		self.margin = margin # TODO: Make margins 
		self.square = (self.size - 2 * self.margin[0])/8
		self.pieces = [pygame.sprite.Group(), pygame.sprite.Group()]
		self.occupied = [[i.coords for i in j] for j in self.pieces]
		self.winner = None
		self.running = True

		self.enp = [] # En passent x pos
		self.castle = [[True, True], [True, True]] # Short, Long

		self.rect = pygame.Rect(pos[0], pos[1], size, size)
		self.image = pygame.transform.scale(pygame.image.load(image), (size, size))
		pygame.sprite.Sprite.__init__(self, sprites)

	def update(self):
		self.occupied = [[i.coords for i in j] for j in self.pieces]

	def ptoc(self, pos:list):
		return [int((pos[0]-self.margin[0])/self.square), 7 - int((pos[1]-self.margin[1])/self.square)]
	
	def check_block(self, start, end, vect):
		place = [sum(i) for i in zip(start, [i / (abs(i) +  (i == 0)) for i in vect])] # increase place one at a time along the vector
		while place != end:
			if place in sum(self.occupied, []):
				print("block ", place)
				return True
			place = [sum(i) for i in zip(place, [i / (abs(i) +  (i == 0)) for i in vect])] 
	
	def make_move(self, piece, end): # Detects if the move is legal and then makes it
		set_enp = False
		self.update()
		start = piece.coords
		target = [i for j in range(2) for i in self.pieces[j].sprites() if i.coords == end]
		target = target[0] if target else None
		fw = 2 * piece.colour - 1 # Forewards Direction
		block = False # True if there is a blockade detected
		baddir = False # True if the square is not possible for the piece to get to in one move
		if start == end: # Check if a move was made
			print("no move", start, end)
			return False 
		vect = [end[0] - start[0], end[1] - start[1]] # Create vector for the pieces motion
		if target not in self.pieces[piece.colour]:
			match piece.type:
				case 0: # if pawn
					if (vect[1] == fw and abs(vect[0]) <= 1) or (abs(vect[1]) == 2 and (start[1] == (6 - int(piece.colour) * 5)) and vect[0] == 0): # if moving foreward and horzontally max 1
						if self.enp:
									if start[0] in self.enp[0] and start[1] == 3 + piece.colour:
										target = self.enp[1]
						if abs(vect[0]) == 1: # If taking
							if not target or target.colour == piece.colour: # If nothing to take
								block = True # No seperate error, counts as blockade
								print("nothing to take")
						else:
							block = self.check_block(start, end, vect)
							if not block and abs(vect[1]) == 2:
								set_enp = [[end[0] + 1, end[0] - 1], piece]
								print(set_enp)
					else:
						baddir = True
				case 1: # if knight
					if not sorted([abs(end[0] - start[0]), abs(end[1] - start[1])]) == [1, 2]: # if one of x and y were 1 and 2, legal position. No blockage (jumps).
						baddir = True
				case 2: # if bishop
					if abs(vect[0]) == abs(vect[1]): # if x is y, diagonal movement. Else illegal.
						block = self.check_block(start, end, vect)
					else:
						baddir = True
				case 3: # if rook
					if vect.count(0) == 1: # if x or y is 0 (horizontal or vertical movement)
						block = self.check_block(start, end, vect)
						self.castle[piece.colour][bool(piece.coords[0])] = False
					else:
						baddir = True
				case 4: # if queen
					if vect.count(0) == 1 or abs(vect[0]) == abs(vect[1]): # if motion is diagonal, horizontal or vertical
						block = self.check_block(start, end, vect)
					else:
						baddir = True
				case 5: 
					if not (max([abs(i) for i in vect]) == 1): # If max motion in each direction is not one
						if not vect[1] and abs(vect[0]) == 2 and self.castle[piece.colour][vect[0] < 0]: # if castles
							block = self.check_block(start, [(vect[0] > 0) * 7, end[1]], vect)
							if not block:	# If no block on castles
								for i in self.pieces[piece.colour]:
									if i.coords == [(vect[0] > 0) * 7, end[1]]:
										print([start[0] + vect[0]/2, start[1]])
										i.coords = [start[0] + vect[0]/2, start[1]]
										i.viscoords = i.coords
										self.castle[piece.colour] = [False, False]
							else:
								block = True
						else:
							baddir = True
					else:
						self.castle[piece.colour] = [False, False]
		else:
			block = True
		if not (baddir or block):
			if target in self.pieces[not piece.colour]:
				if target.type != 5:
					target.kill() 
				else:
					piece.board.winner = piece.colour
					piece.board.running = False
					target.kill()
					# TODO: Display text
			if piece.type == 0 and end[1] == 7*piece.colour:
				type = input("Promote to N, B, R or Q?")
				while type not in "NBRQ":
					print("Invalid Response.")
					input("Promote to N, B, R or Q?")
				type = "NBRQ".index(type) + 1
				piece.promote(type)
			piece.coords = end
			self.enp = set_enp
			pygame.sprite.Group.draw(sprites, window)
			pygame.display.flip()
		return not (baddir or block)

pygame.display.flip()

# Piece Class
class Piece(pygame.sprite.Sprite):
	def __init__(self, coords: list, colour: bool, name: int, board: object):
		self.board = board
		self.coords = coords              # [x, y]
		self.viscoords = coords
		self.colour = colour        # White, Black (True, False)
		self.type = name            # Pawn, Knight, Bishop, Rook, Queen, King
		self.pos = [self.viscoords[0]*self.board.square + self.board.margin[0],
					self.viscoords[1]*self.board.square + self.board.margin[1]]

		self.dragging = False

		self.rect = pygame.Rect(self.pos[0], self.pos[1], self.board.square, self.board.square)
		self.image = pygame.transform.scale(pygame.image.load("Images/{}.png".format("bw"[self.colour] + "pnbrqk"[self.type])), (self.board.square, self.board.square))

		pygame.sprite.Sprite.__init__(self, sprites, pieces, self.board.pieces[self.colour])

	def __str__(self):
		return str(str(self.type) + str(self.coords))

	def check_click(self, mousepos):
		if self.rect.collidepoint(mousepos):
			return True
		return False

	def update(self):
		self.pos = [self.viscoords[0]*self.board.square + self.board.margin[0],
					(7 - self.viscoords[1])*self.board.square + self.board.margin[1]]
		self.rect = pygame.Rect(
			self.pos[0], self.pos[1], self.board.square, self.board.square)

	def promote(self, type):
		self.type = type
		self.image = pygame.transform.scale(pygame.image.load("Images/{}.png".format("bw"[self.colour] + "pnbrqk"[type])), (self.board.square, self.board.square))
	



# Define Pieces
pieces = pygame.sprite.Group()

mBoard = Board(window_width, "Images/board.jpg", [0, 0], [15, 15])

whitelist = sum([[Piece([j, i], True, (1-i)*[3, 1, 2, 4, 5, 2, 1, 3][j], mBoard) for j in range(8)] for i in range(2)], [])
blacklist = sum([[Piece([j, 7- i], False, (1-i)*[3, 1, 2, 4, 5, 2, 1, 3][j], mBoard) for j in range(8)] for i in range(2)], [])

# Game Loop
running = True
turn = True # White, Black: True, False
dragging = False
setdragging = False

while running:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				for s in pieces:
					if s.colour == turn and s.check_click(event.pos) and s.board.running:
						if s.dragging:
							if s.board.make_move(s, s.board.ptoc(event.pos)):
								turn = not turn
							s.dragging = False
							setdragging = False
							s.viscoords = s.coords
						elif not dragging:
							s.dragging = True
							setdragging = True

		elif event.type == pygame.MOUSEMOTION:
			for s in pieces:
				if s.dragging:
					s.viscoords = s.board.ptoc(event.pos)

	dragging = setdragging
	
	if dragging:
		sprites.update()
		pygame.sprite.Group.draw(sprites, window)
		pygame.display.flip()

	pygame.time.delay(100)
