#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pygame
from pygame.locals import *
from operator import add, sub, mul, div
from math import hypot, atan2, degrees

WIDTH, HEIGHT = 1280, 720 # damn projector
SCALE = 32
speed = 60

collcmp = pygame.sprite.collide_circle_ratio(0.6)
_images = {}

def imgload(name):
	if name not in _images:
		img = pygame.image.load(name).convert_alpha()
		_images[name] = dict([(deg, pygame.transform.rotate(img, deg)) for deg in range(0, 360)])
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
		m = map(mul, move1, map(add, z, (1, 1)))
		c = background0.get_at(map(int, map(div, map(add, self._pos, m), (SCALE, SCALE))))
		return c[0] == 255
	def _setrot(self):
		self._rot = int(degrees(atan2(*self._move)) - 90) % 360
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
	range = 64
	interval = 16
	time_since_last_fire = 0
	cost = 150
	def __init__(self, x, y):
		Sprite.__init__(self, "saw_red_1.png", x, y)
		self.image = self._img[90]
	def update(self):
		Sprite.update(self)
		self.time_since_last_fire += 1
		if self.time_since_last_fire >= self.interval:
			for e in enemies:
				dist = hypot(*map(sub, self._pos, e._pos))
				closest_enemy = False
				closest_dist = False
				if closest_dist == False or dist < closest_dist:
					closest_enemy = e
					closest_dist = dist
			if closest_dist <= self.range:
				self.fire(closest_enemy)
	def fire(self, enemy):
		self.time_since_last_fire = 0
		projectiles.add(Carrot(self._pos[0], self._pos[1], enemy._pos))

class Chainsaw(Sprite):
	pathy = True
	def __init__(self, x, y, colour, mx, my):
		Sprite.__init__(self, "saw_" + colour + "_1.png", x, y, [mx, my])

class Carrot(Sprite):
	max_speed=8
	def __init__(self, x, y, target_position):
		posdiff = map(sub, (x, y), target_position)
		h = hypot(*posdiff)
		s = h / self.max_speed
		Sprite.__init__(self, "carrot.png", x, y, map(mul, posdiff, (s, s)))

	def update(self):
		Sprite.update(self)

def build(what_to_build, position):
	global money
	if money >= what_to_build.cost:
		towers.add(what_to_build(position[0], position[1]))
		money -= what_to_build.cost

def main():
	global background, background0, screen, enemies, towers, projectiles, money
	screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)# FULLSCREEN)
	pygame.display.set_caption("Carrot Tower (without Rajula)")
	background0 = pygame.image.load("map1.png").convert_alpha()
	background = pygame.transform.scale(background0, map(mul, background0.get_size(), (SCALE, SCALE)))
	screen.blit(background, (0, 0))
	panel = pygame.image.load("panel.png").convert_alpha()

	pygame.font.init()

	pygame.display.flip()
	clock = pygame.time.Clock()
	going = True
	lives = 13
	money = 1000
	saw = Chainsaw(1103, 79, "red", -4, 0)
	enemies = pygame.sprite.RenderClear([saw])
	towers = pygame.sprite.RenderClear([])
	projectiles = pygame.sprite.RenderClear([])

	what_to_build = Tower
	while going and lives > 0:
		clock.tick(speed)

		# Money must be funny
		font = pygame.font.SysFont("Verdana", 16, True)
		money_render = font.render(str(money), True, (255,255,255))
		screen.blit(panel, (1088, 0))
		screen.blit(money_render, (1110, 5))

		enemies.update()
		enemies.draw(screen)
		pygame.display.flip()
		enemies.clear(screen, background)
		for event in pygame.event.get():
			if event.type == QUIT:
				going = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				going = False
			elif event.type == MOUSEBUTTONUP:
				build(what_to_build, (event.pos[0], event.pos[1]))
		towers.update()
		towers.draw(screen)
		projectiles.update()
		projectiles.draw(screen)
	pygame.quit()

if __name__ == "__main__":
	main()
