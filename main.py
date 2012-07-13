#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pygame
from pygame.locals import *
from operator import add, mul, div

WIDTH, HEIGHT = 1280, 720 # damn projector
speed = 60

collcmp = pygame.sprite.collide_circle_ratio(0.6)
_images = {}

def imgload(name):
	if name not in _images:
		img = pygame.image.load(name).convert_alpha()
		_images[name] = dict([(deg, pygame.transform.rotate(img, deg)) for deg in range(0, 360, 45)])
	return _images[name]

class Sprite(pygame.sprite.Sprite):
	pathy = False
	def __init__(self, img, x, y, move=False):
		pygame.sprite.Sprite.__init__(self)
		self._img = imgload(img)
		self._pos = (x, y)
		self._dir = dir
		self._move = move
		if move:
			self._setrot()
		else:
			self.image = self._img[0]
	def _can_move(self, z, move):
		move1 = [cmp(m, 0) for m in move]
		m = [m * oz for m, oz in zip(move1, z)]
		c = background.get_at(map(int, map(add, self._pos, m)))
		if c[0] == 255: return True
	def _setrot(self):
		move = tuple([cmp(m, 0) for m in self._move])
		self._rot = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}[move]
		self.image = self._img[self._rot]
	def update(self):
		z = map(div, self.image.get_size(), (2, 2))
		if self._move:
			if self.pathy:
				sign = 1
				move = self._move
				while not self._can_move(z, move):
					move = self._move[1] * sign, self._move[0] * sign
					sign = -sign
				self._move = move
				self._setrot()
			self._pos = map(add, self._pos, self._move)
		x, y = map(int, self._pos)
		xz, yz = z
		self.rect = pygame.rect.Rect(x - xz, y - yz, xz * 2, yz * 2)

class Tower(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, "tower.png", x, y)

class Chainsaw(Sprite):
	pathy = True
	def __init__(self, x, y, colour, mx, my):
		Sprite.__init__(self, "saw_" + colour + "_1.png", x, y, [mx, my])

class Carrot(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, "carrot.png", x, y)

def main():
	global background
	screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)# FULLSCREEN)
	pygame.display.set_caption("Carrot Tower (without Rajula)")
	background = pygame.image.load("map1.png").convert_alpha()
	screen.blit(background, (0, 0))
	pygame.display.flip()
	clock = pygame.time.Clock()
	going = True
	lives = 13
	saw = Chainsaw(1100, 68, "red", -4, 0)
	enemies = pygame.sprite.RenderClear([saw])
	while going and lives > 0:
		clock.tick(speed)
		enemies.update()
		enemies.draw(screen)
		pygame.display.flip()
		enemies.clear(screen, background)
		for event in pygame.event.get():
			if event.type == QUIT:
				going = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				going = False
	pygame.quit()

if __name__ == "__main__":
	main()
