#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pygame
from pygame.locals import *
from operator import add, sub, mul, div
from math import hypot, atan2, degrees, ceil
from time import sleep

WIDTH, HEIGHT = 1280, 720 # damn projector
SCALE = 32
speed = 60

collcmp = pygame.sprite.collide_circle_ratio(0.6)
_images = {}

def imgload(names):
	for name in names:
		if name not in _images:
			img = pygame.image.load(name).convert_alpha()
			_images[name] = dict([(deg, pygame.transform.rotate(img, deg)) for deg in range(0, 360)])
	return [_images[name] for name in names]

_lifeimgs = []
for i in range(17):
	bar = pygame.Surface((16, 3))
	bar.fill((255, 0, 0))
	bar.fill((0, 255, 0), pygame.rect.Rect(0, 0, i, 3))
	n = "life" + str(i)
	_images[n] = {0: bar}
	_lifeimgs.append(n)

class Sprite(pygame.sprite.Sprite):
	pathy = False
	animate = False
	_offset = (0, 0)
	def __init__(self, imgs, x, y, move=False):
		pygame.sprite.Sprite.__init__(self)
		self._imgs = imgload(imgs)
		self._pos = (x, y)
		self._dir = dir
		self._move = move
		self._cur_img = 0
		self._rot = 0
		self._anim = 0
		if move:
			self._setrot()
			self._newimg()
		else:
			self._img = self._imgs[0]
			self.image = self._img[0]
	def _can_move(self, z, move):
		move1 = [cmp(m, 0) for m in move]
		m = map(mul, move1, map(add, z, (1, 1)))
		c = background0.get_at(map(int, map(div, map(add, self._pos, m), (SCALE, SCALE))))
		return c[0] == 255
	def _setrot(self):
		self._rot = int(degrees(atan2(*self._move)) - 90) % 360
	def _newimg(self, force=False):
		if self.animate:
			self._anim += 1
		if force or self.animate is self._anim:
			self._anim = 0
			self._cur_img += 1
			self._cur_img %= len(self._imgs)
		self._img = self._imgs[self._cur_img]
		self.image = self._img[self._rot]
	def update(self):
		z = map(div, map(add, self.image.get_size(), self._offset), (2, 2))
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
		self._newimg()
		x, y = map(int, self._pos)
		xz, yz = z
		xo, yo = self._offset
		self.rect = pygame.rect.Rect(x - xz + xo, y - yz + yo, xz * 2, yz * 2)

class Tower(Sprite):
	range = 100
	interval = 16
	time_since_last_fire = 0
	cost = 150
	sprite_filenames = ("hat.png", )
	__anim = 0
	def __init__(self, x, y):
		Sprite.__init__(self, self.sprite_filenames, x, y)
		self._fired = False
	def update(self):
		Sprite.update(self)
		self.time_since_last_fire += 1
		if self.time_since_last_fire >= self.interval:
			closest_dist = 100000 # Lots!
			for e in enemies:
				dist = hypot(*map(sub, self._pos, e._pos))
				if dist < closest_dist:
					closest_enemy = e
					closest_dist = dist
			if closest_dist <= self.range:
				self.fire(closest_enemy, closest_dist)
		if self._fired:
			self.__anim = 1
			self._fired = False
		if self.__anim:
			self.__anim -= 1
			if not self.__anim:
				self._newimg(True)
				if self._cur_img:
					self.__anim = 10
	def fire(self, enemy, dist):
		self.time_since_last_fire = 0
		dist = ceil(dist / SCALE * 0.95)
		epos = map(add, enemy._pos, map(mul, enemy._move, (dist, dist)))
		projectiles.add(Carrot(self._pos[0], self._pos[1], epos, self.range))
		self._fired = True

class Krisseh(Tower):
	sprite_filenames = ("hat.png", "hat_krisseh_full.png", "hat_krisseh_half.png")
	_offset = (0, -32)

class Life(Sprite):
	def __init__(self, enemy):
		Sprite.__init__(self, _lifeimgs, *enemy._pos)
		self._enemy = enemy
	def update(self):
		e = self._enemy
		self._pos = e._pos[0], e._pos[1] - 18
		left = int((float(e.life) / e.max_life) * 16)
		self._cur_img = left
		Sprite.update(self)
		if e not in enemies:
			bars.remove(self)

class Enemy(Sprite):
	pathy = True
	life = 1
	max_life = 1
	bounty = 0
	def __init__(self, *a):
		Sprite.__init__(self, *a)
		bars.add(Life(self))
	def im_hit(self, p):
		global money
		print "I'm hit!", self.life
		self.life -= p.damage
		if self.life <= 0:
			enemies.remove(self)
			money += self.bounty
	def update(self):
		Sprite.update(self)
		c = background0.get_at(map(int, map(div, self._pos, (SCALE, SCALE))))
		if c[0] == 255 and c[1] == 0:
			lose_life()
			enemies.remove(self)

class Chainsaw(Enemy):
	animate = 2
	bounty = 5
	def __init__(self, x, y, colour, life, mx, my):
		Enemy.__init__(self, ["saw_" + colour + "_" + str(n) + ".png" for n in 1, 2], x, y, [mx, my])
		self.life = self.max_life = life


class Weapon(Sprite):
	damage = 1

class Carrot(Weapon):
	max_speed=8
	def __init__(self, x, y, target_position, range):
		posdiff = map(sub, target_position, (x, y))
		h = hypot(*posdiff)
		s = h / self.max_speed
		Weapon.__init__(self, ("carrot.png",), x, y, map(div, posdiff, (s, s)))
		self._range = range

	def update(self):
		Sprite.update(self)
		self._range -= self.max_speed
		if self._range < 0:
			projectiles.remove(self)

def build(what_to_build, position):
	global money
	if money >= what_to_build.cost:
		towers.add(what_to_build(position[0], position[1]))
		money -= what_to_build.cost

def lose_life():
	global lives, going
	print "DEATH!!!"
	lives -= 1
	if lives < 1:
		game_over()

spawned_on_this_level = 0
def spawn():
	global level, spawned_on_this_level, spawn_countdown
	spawns = [(3, "green", 3), (5, "blue", 4), (7, "red", 5), (7, "blue", 7), (4, "red", 10), (1, "black", 23), (5, "red", 14)]

	count, colour, life = spawns[level]
	spawned_on_this_level += 1
	print "spånat: " + str(spawned_on_this_level)
	enemies.add(Chainsaw(1071, 79, colour, life, -4, 0))

	if spawned_on_this_level >= count:
		print "OMFG LELVE"
		level += 1
		spawned_on_this_level = 0
		spawn_countdown = 600

def game_over():
	global going
	font = pygame.font.SysFont("Verdana", 128, True)
	game_over_render = font.render("GAME OVER", True, (0,0,0))
	screen.blit(game_over_render, (1280/2 - game_over_render.get_size()[0]/2, 720/2 - game_over_render.get_size()[1]/2))
	pygame.display.flip()
	sleep(3)
	going = False
	
def main():
	global background, background0, screen, enemies, towers, projectiles, bars, money, lives, going, level, spawn_countdown
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
	level = 0
	lives = 13
	money = 1000
	spawn_countdown = 600
	enemies = pygame.sprite.RenderClear([])
	towers = pygame.sprite.RenderClear([])
	projectiles = pygame.sprite.RenderClear([])
	bars = pygame.sprite.RenderClear([])
	things = [enemies, towers, projectiles, bars]

	what_to_build = Krisseh
	while going and lives > 0:
		clock.tick(speed)
		spawn_countdown -= 1
		if spawn_countdown <= 0:
			spawn_countdown = 30
			spawn()

		# Money must be funny
		font = pygame.font.SysFont("Verdana", 16, True)
		money_render = font.render(str(money), True, (0,0,0))
		lives_render = font.render(str(lives), True, (0,0,0))
		level_render = font.render(str(level), True, (0,0,0))
		next_render = font.render(str(spawn_countdown), True, (0,0,0))
		screen.blit(panel, (1088, 0))
		screen.blit(money_render, (1280-16-money_render.get_size()[0], 7))
		screen.blit(lives_render, (1280-16-lives_render.get_size()[0], 35))
		screen.blit(level_render, (1280-16-level_render.get_size()[0], 35+28))
		screen.blit(next_render, (1280-16-next_render.get_size()[0], 35+28+28))
		#screen.blit(lives_render, (1110, 25))

		for thing in things:
			thing.update()
			thing.draw(screen)
		for e in list(enemies):
			for c in pygame.sprite.spritecollide(e, projectiles, False, collcmp):
				projectiles.remove(c)
				e.im_hit(c)
		pygame.display.flip()
		for thing in things:
			thing.clear(screen, background)
		for event in pygame.event.get():
			if event.type == QUIT:
				going = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				going = False
			elif event.type == MOUSEBUTTONUP:
				build(what_to_build, (event.pos[0], event.pos[1]))
	pygame.quit()

if __name__ == "__main__":
	main()
