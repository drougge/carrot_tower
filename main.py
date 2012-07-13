#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pygame
from pygame.locals import *

WIDTH, HEIGHT = 1280, 720 # damn projector
speed = 60

collcmp = pygame.sprite.collide_circle_ratio(0.6)
_images = {}

def imgload(name):
	if name not in _images:
		img = pygame.image.load(name).convert_alpha()
		_images[name] = dict([(deg, pygame.transform.rotate(img, deg - 90)) for deg in range(360, 45)])
	return _images[name]


class Sprite(pygame.sprite.Sprite):
	def __init__(self, img, x, y, dir):
		pygame.sprite.Sprite.__init__(self)
		self._img = imgload(img)
		self._pos = [x, y]
		self._dir = dir

class Tower(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, "tower.png", x, y, 0)

class Chainsaw(Sprite):
	def __init__(self, x, y):
		Sprite.__init__(self, "chainsaw.png", x, y, 270)

def main():
	screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)# FULLSCREEN)
	pygame.display.set_caption("Carrot Tower (without Rajula)")
	background = pygame.image.load("map1.png").convert()
	screen.blit(background, (0, 0))
	pygame.display.flip()
	clock = pygame.time.Clock()
	going = True
	lives = 13
	while going and lives > 0:
		clock.tick(speed)
		for event in pygame.event.get():
			if event.type == QUIT:
				going = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				going = False
	pygame.quit()

if __name__ == "__main__":
	main()
