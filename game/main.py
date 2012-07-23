#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pygame
from pygame.locals import *
from operator import add, sub, mul, div
from math import hypot, atan2, degrees, ceil
from time import sleep

WIDTH, HEIGHT = 1280, 720 # damn projector
SCALE = 32
SCALE2 = (SCALE, SCALE)
MIDDLE = (SCALE // 2 - 1, SCALE // 2 - 1)
speed = 60

collcmp = pygame.sprite.collide_mask
_images = {}

def imgload(names, step=1):
	for name in names:
		if name not in _images:
			img = pygame.image.load(name).convert_alpha()
			def rot(deg):
				i = pygame.transform.rotate(img, deg)
				return i, pygame.mask.from_surface(i)
			_images[name] = dict([(deg, rot(deg)) for deg in range(0, 360, step or 360)])
	return [_images[name] for name in names]

_lifeimgs = []
for i in range(17):
	bar = pygame.Surface((16, 3))
	bar.fill((255, 0, 0))
	bar.fill((0, 255, 0), pygame.rect.Rect(0, 0, i, 3))
	n = "life" + str(i)
	_images[n] = {0: [bar, None]}
	_lifeimgs.append(n)

class Sprite(pygame.sprite.Sprite):
	_animate = False
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
			self.image, self.mask = self._img[0]
	def _can_move(self, z, move):
		move1 = [cmp(m, 0) for m in move]
		m = map(mul, move1, map(add, z, (1, 1)))
		c = background0.get_at(map(int, map(div, map(add, self._pos, m), SCALE2)))
		return c[0] == 255
	def _pathify(self, z):
		pass
	def _setrot(self):
		self._rot = int(degrees(atan2(*self._move)) - 90) % 360
	def _newimg(self, force=False):
		if self._animate:
			self._anim += 1
		if force or self._animate is self._anim:
			self._anim = 0
			self._cur_img += 1
			self._cur_img %= len(self._imgs)
		self._img = self._imgs[self._cur_img]
		self.image, self.mask = self._img[self._rot]
	def update(self):
		z = map(div, map(add, self.image.get_size(), self._offset), (2, 2))
		if self._move:
			self._pathify(z)
			self._pos = map(add, self._pos, self._move)
		self._newimg()
		x, y = map(int, self._pos)
		xz, yz = z
		xo, yo = self._offset
		self.rect = pygame.rect.Rect(x - xz + xo, y - yz + yo, xz * 2, yz * 2)

class Tower(Sprite):
	_range = 100
	_interval = 16
	_time_since_last_fire = 0
	_cost = 150
	_damage = 2
	_sprite_filenames = ("hat.png",)
	__anim = 0
	_fire_anim_interval = 10
	_fire_sound = None
	def __init__(self, x, y):
		Sprite.__init__(self, self._sprite_filenames, x, y)
		self._fired = False
	def update(self):
		Sprite.update(self)
		self._time_since_last_fire += 1
		if self._time_since_last_fire >= self._interval:
			closest_dist = 100000 # Lots!
			for e in enemies:
				dist = hypot(*map(sub, self._pos, e._pos))
				if dist < closest_dist:
					closest_enemy = e
					closest_dist = dist
			if closest_dist <= self._range:
				self.fire(closest_enemy, closest_dist)
		if self._fired:
			self.__anim = 1
			self._fired = False
		if self.__anim:
			self.__anim -= 1
			if not self.__anim:
				self._newimg(True)
				if self._cur_img:
					self.__anim = self._fire_anim_interval
	def fire(self, enemy, dist):
		self._time_since_last_fire = 0
		dist = ceil(dist / SCALE * 3)
		epos = map(add, enemy._pos, map(mul, enemy._move, (dist, dist)))
		projectiles.add(Carrot(self._pos[0], self._pos[1], epos, self._range, self._damage))
		self._fired = True
		if self._fire_sound:
			self._fire_sound.play()

class Krisseh(Tower):
	_sprite_filenames = ("hat.png", "hat_krisseh_full.png", "hat_krisseh_half.png",)
	_offset = (0, -32)

class SuperKrisseh(Tower):
	_cost = 800
	_damage = 2
	_interval = 8
	_range = 120
	_sprite_filenames = ("superhat.png", "superkrisseh_full.png", "superkrisseh_half.png",)
	_offset = (0, -32)

class Pringles(Tower):
	_cost = 650
	_damage = 50
	_interval = 64
	_range = 400
	_sprite_filenames = ("pringles_1.png", "pringles_2.png", "pringles_1.png", "pringles_3.png",)

class ExtTower(Tower):
	_cost = 900
	_damage = 4
	_interval = 8
	_fire_anim_interval = 4
	_range = 200
	_sprite_filenames = ("exttower_1.png", "exttower_2.png", "exttower_3.png", "exttower_4.png",)
	def __init__(self, *a):
		Tower.__init__(self, *a)
		self._fire_sound = _snd_blurgh

class Life(Sprite):
	def __init__(self, enemy):
		Sprite.__init__(self, _lifeimgs, *enemy._pos)
		self._enemy = enemy
	def update(self):
		e = self._enemy
		self._pos = e._pos[0], e._pos[1] - 18
		left = int((float(e._life) / e._max_life) * 16)
		self._cur_img = max(left, 0)
		Sprite.update(self)
		if e not in enemies:
			self.kill()

class Enemy(Sprite):
	_life = 1
	_max_life = 1
	_bounty = 0
	def __init__(self, *a):
		Sprite.__init__(self, *a)
		bars.add(Life(self))
	def im_hit(self, p, snd):
		global money, _snd_carrot
		self._life -= p._damage
		if self._life <= 0:
			self.kill()
			money += int(self._bounty * level * 0.5)
			snd.play()
	def update(self):
		Sprite.update(self)
		c = background0.get_at(map(int, map(div, self._pos, SCALE2)))
		if c[0] == 255 and c[1] == 0:
			lose_life()
			self.kill()
	def _pathify(self, z):
		sign = 1
		move = self._move
		while not self._can_move(z, move):
			move = self._move[1] * sign, self._move[0] * sign
			sign = -sign
		self._move = move
		self._setrot()

class Chainsaw(Enemy):
	_animate = 2
	_bounty = 5
	def __init__(self, x, y, colour, life, mx, my, flashy=False):
		if flashy:
			imgs = []
			for colour in ["red", "black", "green", "blue"]:
				imgs += ["saw_" + colour + "_" + str(n) + ".png" for n in 1, 2] * 2
		else:
			imgs = ["saw_" + colour + "_" + str(n) + ".png" for n in 1, 2]
		Enemy.__init__(self, imgs, x, y, [mx, my])
		self._life = self._max_life = life

class Ext(Enemy):
	_animate = 2
	_bounty = 50
	def __init__(self, x, y, colour, life, mx, my):
		Enemy.__init__(self, ["ext_" + str(n) + ".png" for n in 1,2,3,4,3,2], x, y, [mx, my])
		self._life = self._max_life = life

def build_path(level, start_pos):
	"""Builds path[x][y] => movement for shortest route from start_pos to red"""
	path = [[False] * 22 for i in range(34)]
	test = [[True] * 22 for i in range(34)]
	test[start_pos[0]][start_pos[1]] = False
	def good(x, y):
		if x <= 33 and y <= 21 and x >= 0 and y >= 0 and test[x][y]:
			test[x][y] = False
			return True
	def check(xy):
		c = level.get_at(xy)
		if c[0] == 255: # road
			if c[1] == 0: # goal area
				return True
			else:
				for m in (-1, 0), (0, 1), (1, 0), (0, -1):
					pos = map(add, xy, m)
					if good(*pos) and check(pos):
						path[xy[0]][xy[1]] = m
						return True
	check(start_pos)
	return path

class SmartChainsaw(Chainsaw):
	_bounty = 15
	def __init__(self, *a):
		Chainsaw.__init__(self, *a, flashy=True)
		speed = max(map(abs, self._move))
		self._speed = (speed, speed)
	def _pathify(self, z):
		x, y = map(div, self._pos, SCALE2)
		if self._pos == map(add, map(mul, (x, y), SCALE2), MIDDLE):
			self._move = map(mul, level_path[x][y], self._speed)
			self._setrot()

class Weapon(Sprite):
	_damage = 1

class Carrot(Weapon):
	max_speed=8
	def __init__(self, x, y, target_position, _range, damage=Weapon._damage):
		self._damage = damage
		posdiff = map(sub, target_position, (x, y))
		h = hypot(*posdiff)
		s = h / self.max_speed
		Weapon.__init__(self, ("carrot.png",), x, y, map(div, posdiff, (s, s)))
		self._range = _range

	def update(self):
		Sprite.update(self)
		self._range -= self.max_speed
		if self._range < 0:
			self.kill()

class Agurka(Weapon):
	_cost = 40
	_damage = 50
	def __init__(self, x, y):
		Weapon.__init__(self, ("agurk.png",), x, y)

class Box(Sprite):
	_sprite_filenames = ("box.png",)
	def __init__(self, x, y):
		Sprite.__init__(self, self._sprite_filenames, x, y)

class Knappy(Sprite):
	pass

def build(what_to_build, position, cost=None):
	global money
	if cost == None:
		cost = what_to_build._cost
	if money >= cost:
		towers.add(what_to_build(position[0]*64+32, position[1]*64+32))
		money -= cost

def upgrade(tower, what_to_build):
	global money
	if money >= (what_to_build._cost - tower._cost):
		pos = int(tower._pos[0] / 64), int(tower._pos[1] / 64)
		towers.remove(tower)
		cost = max(what_to_build._cost - tower._cost, 0)
		build(what_to_build, pos, cost)

def lose_life():
	global lives, going, _snd_death
	print "DEATH!!!"
	lives -= 1
	_snd_death.play()
	if lives < 1:
		game_over()

spawned_on_this_level = 0
def spawn():
	global level, spawned_on_this_level, spawn_countdown
	spawns = [(Chainsaw, 3, "green", 3),
	          (Chainsaw, 6, "blue", 5),
	          (Chainsaw, 6, "red", 7),
	          (Ext, 1, "pink", 36),
	          (Chainsaw, 6, "blue", 10),
	          (Chainsaw, 6, "red", 14),
	          (SmartChainsaw, 1, "black", 24),
	          (Chainsaw, 6, "pink", 20),
	          (Chainsaw, 12, "green", 20),
	          (SmartChainsaw, 3, "black", 24),
	          (Ext, 1, "pink", 360),
	          (Chainsaw, 6, "blue", 30),
	          (Chainsaw, 4, "red", 38),
	          (SmartChainsaw, 2, "black", 44),
	          (Chainsaw, 6, "blue", 50),
	         ]

	if level < len(spawns):
		enemy, count, colour, life = spawns[level]
	else:
		difficulty = level * (level * 0.4)
		enemy, count, colour, life = SmartChainsaw, 3 + level*0.1, "pink", difficulty
	spawned_on_this_level += 1
	enemies.add(enemy(1071, 79, colour, life, -4, 0))

	if spawned_on_this_level >= count:
		level += 1
		spawned_on_this_level = 0
		spawn_countdown = max(400 - level*10, 0)

def game_over():
	global going
	font = pygame.font.SysFont("Verdana", 128, True)
	game_over_render = font.render("GAME OVER", True, (0,0,0))
	screen.blit(game_over_render, (1280/2 - game_over_render.get_size()[0]/2, 720/2 - game_over_render.get_size()[1]/2))
	pygame.display.flip()
	sleep(3)
	going = False
	

def loading(nr):
	screen.blit(pygame.image.load("load." + str(nr) + ".jpeg"), (0, 0))
	zx, zy = loading_text.get_size()
	screen.blit(loading_text, (1200 - zx, 700 - zy))
	for i in range(36):
		pygame.display.flip()
		clock.tick(speed)
		for event in pygame.event.get():
			if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
				pygame.quit()
				raise Exception("Loading aborted")

class Mouse(Sprite):
	pass

def select_tower(what, img):
	global what_to_build, mouse
	what_to_build = what
	mouse._imgs = imgload([img])

def main(flags):
	if not pygame.mixer: print 'Warning, sound disabled'
	global background, background0, screen, enemies, towers, projectiles, bars, money, lives, going, level, spawn_countdown, loading_text, clock, hilight_box, mouse, level_path
	global _snd_death, _snd_blurgh
	pygame.display.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
	pygame.display.set_caption("Carrot Tower (with some Rajula)")

	pygame.font.init()
	clock = pygame.time.Clock()

	font = pygame.font.SysFont("Verdana", 128, True)
	loading_text = font.render("Loading", True, (0,0,0))
	loading(1)

	pygame.mixer.init(44100, -16, 2, 2048)
	_snd_death = pygame.mixer.Sound("trollandi_death.wav")
	_snd_woop = pygame.mixer.Sound("rajula_woop.wav")
	_snd_cucumber = pygame.mixer.Sound("cucumber.wav")
	_snd_carrot = pygame.mixer.Sound("carrot.wav")
	_snd_blurgh = pygame.mixer.Sound("blurgh.wav")

	background0 = pygame.image.load("map1.png").convert_alpha()
	level_path = build_path(background0, [32, 2])
	background = pygame.transform.scale(background0, map(mul, background0.get_size(), SCALE2))
	panel = pygame.image.load("panel.png").convert_alpha()
	loading(2)

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
	loading(3)

	imgload(("carrot.png",))
	imgload(("agurk.png", "box.png"), 0)
	imgload(("hat.png", "hat_krisseh_full.png", "hat_krisseh_half.png"), 0)
	imgload(("superhat.png", "superkrisseh_full.png", "superkrisseh_half.png"), 0)
	imgload(("exttower_1.png", "exttower_2.png", "exttower_3.png", "exttower_4.png"), 0)
	imgload(("pringles_1.png", "pringles_2.png", "pringles_3.png"), 0)
	loading(4)
	colours = ["red", "green", "blue", "black"]
	imgload(["saw_" + c + "_1.png" for c in colours], 90)
	imgload(["saw_" + c + "_2.png" for c in colours], 90)
	imgload(["ext_" + str(i) + ".png" for i in range(1, 5)], 90)
	font = pygame.font.SysFont("Verdana", 16, True)

	# Fix Krisseh collisions
	for bn in ("hat_krisseh", "superkrisseh"):
		full = _images[bn + "_full.png"]
		half = _images[bn + "_half.png"]
		full[0] = (full[0][0], half[0][1])

	knapps = []
	for y, fn in ((336, "hat.png"), (400, "superhat.png"), (480, "exttower_1.png"), (544, "pringles_1.png"), (608, "agurk.png")):
		knapps.append(Knappy((fn,), 1184, y))
	things.append(pygame.sprite.RenderClear(knapps))
	mouse = Mouse(["hat.png"], 10000, 0)
	things.append(pygame.sprite.RenderClear([mouse]))
	hilight_box = Box(10000, 0)
	things.append(pygame.sprite.RenderClear([hilight_box]))

	buttons = {(18, 5): (Krisseh, "hat.png"),
	           (18, 6): (SuperKrisseh, "superhat.png"),
	           (18, 7): (ExtTower, "exttower_1.png"),
	           (18, 8): (Pringles, "pringles_1.png"),
	           (18, 9): (Agurka, "agurk.png"),
	          }
	select_tower(*buttons[(18, 5)])

	screen.fill((255, 0, 228))
	screen.blit(background, (0, 0))
	screen.blit(panel, (1088, 0))
	pygame.display.flip()

	while going and lives > 0:
		clock.tick(speed)
		spawn_countdown -= 1
		if spawn_countdown <= 0:
			spawn_countdown = max(30 - level/2, 0)
			spawn()

		# Money must be funny
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
		coll = list(projectiles)
		for e in list(enemies):
			for c in pygame.sprite.spritecollide(e, coll, False, collcmp):
				c.kill()
				e.im_hit(c, _snd_carrot)
		coll = list(towers)
		for e in list(enemies):
			for c in pygame.sprite.spritecollide(e, coll, False, collcmp):
				c.kill()
				e.im_hit(c, _snd_cucumber)
		pygame.display.flip()
		for thing in things:
			thing.clear(screen, background)
		for event in pygame.event.get():
			if event.type == QUIT:
				going = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				going = False
			elif event.type == KEYDOWN and event.key == K_RETURN:
				spawn_countdown = 0
			elif event.type == MOUSEBUTTONUP:
				upgrade_done = False
				if ruta[0] > 16 or ruta[1] > 10: # panel
					if ruta in buttons:
						select_tower(*buttons[ruta])
				else:
					for t in towers:
						if int(t._pos[0] / 64) == ruta[0] and int(t._pos[1] / 64) == ruta[1]:
							upgrade(t, what_to_build)
							upgrade_done = True
					if not upgrade_done:
						build(what_to_build, (ruta[0], ruta[1]))
			elif event.type == MOUSEMOTION:
				ruta = int(event.pos[0] / 64), int(event.pos[1] / 64)
				hilight_box._pos = (ruta[0] * 64 + 32, ruta[1] * 64 + 32)
				if ruta[0] > 16 or ruta[1] > 10: # panel
					if ruta not in buttons:
						hilight_box._pos = (10000, 0)
					mouse._pos = (10000, 0)
				else:
					x, y = ruta[0] * 64 + 32, ruta[1] * 64 + 32
					yz = mouse.image.get_size()[1]
					if yz > 64:
						y -= 16
					mouse._pos = (x, y)
	pygame.quit()

if __name__ == "__main__":
	from sys import argv
	flags = 0
	if "-f" in argv: flags = FULLSCREEN
	if "-h" in argv:
		print "-f for FULLSCREEN, no other options"
	else:
		main(flags)
