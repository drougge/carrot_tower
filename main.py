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
		_images[name] = dict([(deg, pygame.transform.rotate(img, deg - 90)) for deg in range(0, 360, 45)])
	return _images[name]

movemap = {(1, 0) : (0, 1),
           (0, 1) : (-1, 0),
           (-1, 0): (0, -1),
           (0, -1): (1, 0),
          }
class Sprite(pygame.sprite.Sprite):
	pathy = False
	def __init__(self, img, x, y, move=False):
		pygame.sprite.Sprite.__init__(self)
		self._img = imgload(img)
		self._pos = (x, y)
		self._dir = dir
		self._move = move
	def _can_move(self, z):
		m = [cmp(m, 0) * z for m, z in zip(self._move, z)]
		c = background.get_at(map(add, self._pos, m))
		return c[0] == 255
	def update(self):
		z = map(div, self.image.get_size(), (2, 2))
		if self._move:
			while self.pathy and not self._can_move(z):
				move1 = [cmp(0, m) for m in self._move]
				move1 = movemap[tuple(move1)]
				mz = max(map(abs, self._move))
				self._move = map(mul, move1, (mz, mz))
			x, y = self._pos = map(add, self._pos, self._move)
		else:
			x, y = self._pos
		xz, yz = z
		self.rect = pygame.rect.Rect(x - xz, y - yz, xz * 2, yz * 2)

class Tower(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, "tower.png", x, y)

class Chainsaw(Sprite):
	pathy = True
	def __init__(self, x, y, colour, mx, my):
		Sprite.__init__(self, "saw_" + colour + "_1.png", x, y, [mx, my])
		self.image = self._img[90]

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
	saw = Chainsaw(1100, 60, "red", -1, 0)
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
