#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pygame
from pygame.locals import *
from operator import add, mul

WIDTH, HEIGHT = 1280, 720 # damn projector
TILESIZE = 32
speed = 60

collcmp = pygame.sprite.collide_circle_ratio(0.6)
_images = {}

def imgload(name):
	if name not in _images:
		img = pygame.image.load(name).convert_alpha()
		_images[name] = dict([(deg, pygame.transform.rotate(img, deg - 90)) for deg in range(0, 360, 45)])
	return _images[name]


class Sprite(pygame.sprite.Sprite):
	def __init__(self, img, x, y, move=False):
		pygame.sprite.Sprite.__init__(self)
		self._img = imgload(img)
		self._pos = [x, y]
		self._dir = dir
		self._move = move
	def update(self):
		if not self._move: return
		pos = map(add, self._pos, self._move)
		self._pos = pos
		self.rect  = pygame.rect.Rect(pos[0], pos[1], 32, 32)

class Tower(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, "tower.png", x, y)

class Chainsaw(Sprite):
	def __init__(self, x, y, colour, mx, my):
		Sprite.__init__(self, "saw_" + colour + "_1.png", x, y, [mx, my])
		self.image = self._img[90]
		self.rect  = pygame.rect.Rect(x, y, 32, 32)

class Carrot(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, "carrot.png", x, y)

def main():
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
