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
collcmp = pygame.sprite.collide_mask
_images = {}


def imgload(names):
	for name in names:
		if name not in _images:
			img = pygame.image.load(name).convert_alpha()
			def rot(deg):
				i = pygame.transform.rotate(img, deg)
				return i, pygame.mask.from_surface(i)
			_images[name] = dict([(deg, rot(deg)) for deg in range(0, 360)])
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
			self.image, self.mask = self._img[0]
	def _can_move(self, z, move):
		move1 = [cmp(m, 0) for m in move]
		m = map(mul, move1, map(add, z, (1, 1)))
		c = background0.get_at(map(int, map(div, map(add, self._pos, m), (SCALE, SCALE))))
		return c[0] == 255
	def _pathify(self, z):
		pass
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
	range = 100
	interval = 16
	time_since_last_fire = 0
	cost = 150
	damage = 2
	sprite_filenames = ("hat.png", )
	__anim = 0
	fire_anim_interval = 10
	fire_sound = None
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
					self.__anim = self.fire_anim_interval
	def fire(self, enemy, dist):
		self.time_since_last_fire = 0
		dist = ceil(dist / SCALE * 3)
		epos = map(add, enemy._pos, map(mul, enemy._move, (dist, dist)))
		projectiles.add(Carrot(self._pos[0], self._pos[1], epos, self.range, self.damage))
		self._fired = True
		if self.fire_sound:
			self.fire_sound.play()

class Krisseh(Tower):
	sprite_filenames = ("hat.png", "hat_krisseh_full.png", "hat_krisseh_half.png")
	_offset = (0, -32)

class SuperKrisseh(Tower):
	cost = 800
	damage = 4
	interval = 4
	range = 120
	sprite_filenames = ("superhat.png", "superkrisseh_full.png", "superkrisseh_half.png")
	_offset = (0, -32)

class Pringles(Tower):
	cost = 650
	damage = 50
	interval = 64
	range = 400
	sprite_filenames = ("pringles_1.png", "pringles_2.png", "pringles_1.png", "pringles_3.png")

class ExtTower(Tower):
	cost = 600
	damage = 12
	interval = 8
	fire_anim_interval = 4
	range = 200
	sprite_filenames = ("exttower_1.png", "exttower_2.png", "exttower_3.png", "exttower_4.png")
	def __init__(self, *a):
		Tower.__init__(self, *a)
		self.fire_sound = _snd_blurgh

class Life(Sprite):
	def __init__(self, enemy):
		Sprite.__init__(self, _lifeimgs, *enemy._pos)
		self._enemy = enemy
	def update(self):
		e = self._enemy
		self._pos = e._pos[0], e._pos[1] - 18
		left = int((float(e.life) / e.max_life) * 16)
		self._cur_img = max(left, 0)
		Sprite.update(self)
		if e not in enemies:
			self.kill()

class Enemy(Sprite):
	life = 1
	max_life = 1
	bounty = 0
	def __init__(self, *a):
		Sprite.__init__(self, *a)
		bars.add(Life(self))
	def im_hit(self, p, snd):
		global money, _snd_carrot
		print "I'm hit!", self.life
		self.life -= p.damage
		if self.life <= 0:
			self.kill()
			money += self.bounty
			snd.play()
	def update(self):
		Sprite.update(self)
		c = background0.get_at(map(int, map(div, self._pos, (SCALE, SCALE))))
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
	animate = 2
	bounty = 5
	def __init__(self, x, y, colour, life, mx, my, flashy=False):
		if flashy:
			imgs = []
			for colour in ["red", "black", "green", "blue"]:
				imgs += ["saw_" + colour + "_" + str(n) + ".png" for n in 1, 2] * 2
		else:
			imgs = ["saw_" + colour + "_" + str(n) + ".png" for n in 1, 2]
		Enemy.__init__(self, imgs, x, y, [mx, my])
		self.life = self.max_life = life

class Ext(Enemy):
	animate = 2
	bounty = 50
	def __init__(self, x, y, colour, life, mx, my):
		Enemy.__init__(self, ["ext_" + str(n) + ".png" for n in 1,2,3,4,3,2], x, y, [mx, my])
		self.life = self.max_life = life

class SmartChainsaw(Chainsaw):
	bounty = 15
	def __init__(self, *a):
		Chainsaw.__init__(self, *a, flashy=True)
		self._choices = [2, 2, 2, 1, 2]
		self._wait = 0
		self._soon = 0
	def _pathify(self, z):
		move = self._move
		sign = 1
		can = []
		while len(can) < 3:
			can.append((self._can_move(z, move), move))
			move = self._move[1] * sign, self._move[0] * sign
			sign = -sign
		self._wait -= 1
		self._soon -= 1
		if self._soon == 0:
			self._move = can[self._choices.pop()][1]
			self._wait = 10
		elif self._wait <= 0 and self._soon < 0 and [c[0] for c in can] == [True, True, True]:
			self._soon = 4
		else:
			self._move = [c[1] for c in can if c[0]][0]
		self._setrot()

class Weapon(Sprite):
	damage = 1

class Carrot(Weapon):
	max_speed=8
	def __init__(self, x, y, target_position, range, damage=None):
		if damage is None:
			damage = Weapon.damage
		self.damage = damage
		posdiff = map(sub, target_position, (x, y))
		h = hypot(*posdiff)
		s = h / self.max_speed
		Weapon.__init__(self, ("carrot.png",), x, y, map(div, posdiff, (s, s)))
		self._range = range

	def update(self):
		Sprite.update(self)
		self._range -= self.max_speed
		if self._range < 0:
			self.kill()

class Agurka(Weapon):
	cost = 40
	damage = 50
	def __init__(self, x, y):
		Weapon.__init__(self, ("agurk.png",), x, y)

class Box(Sprite):
	sprite_filenames = "box.png", 
	def __init__(self, x, y):
		Sprite.__init__(self, self.sprite_filenames, x, y)

class Knappy(Sprite):
	pass

def build(what_to_build, position, cost=None):
	global money
	if cost == None:
		cost = what_to_build.cost
	if money >= cost:
		towers.add(what_to_build(position[0]*64+32, position[1]*64+32))
		money -= cost

def upgrade(tower, what_to_build):
	global money
	if money >= (what_to_build.cost - tower.cost):
		pos = int(tower._pos[0] / 64), int(tower._pos[1] / 64)
		towers.remove(tower)
		cost = what_to_build.cost - tower.cost
		if cost < 0:
			cost = 0
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
	          (Chainsaw, 5, "blue", 4),
	          (Chainsaw, 7, "red", 5),
	          (Chainsaw, 7, "blue", 7),
	          (Chainsaw, 4, "red", 10),
	          (SmartChainsaw, 1, "black", 23),
	          (Chainsaw, 5, "pink", 14),
	          (Chainsaw, 8, "green", 17),
	          (Ext, 1, "pink", 42),
	         ]

	if level < len(spawns):
		enemy, count, colour, life = spawns[level]
	else:
		enemy, count, colour, life = Chainsaw, 6, "pink", level*2
	spawned_on_this_level += 1
	enemies.add(enemy(1071, 79, colour, life, -4, 0))

	if spawned_on_this_level >= count:
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
	

def loading(nr):
	screen.blit(pygame.image.load("load." + str(nr) + ".jpeg"), (0, 0))
	zx, zy = loading_text.get_size()
	screen.blit(loading_text, (1200 - zx, 700 - zy))
	for i in range(36):
		pygame.display.flip()
		clock.tick(speed)
		pygame.event.get()

class Mouse(Sprite):
	pass

def select_tower(what, img):
	global what_to_build, mouse
	what_to_build = what
	mouse._imgs = imgload([img])

def main():
	if not pygame.mixer: print 'Warning, sound disabled'
	global background, background0, screen, enemies, towers, projectiles, bars, money, lives, going, level, spawn_countdown, loading_text, clock, hilight_box, mouse
	global _snd_blurgh
	screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)# FULLSCREEN)
	pygame.display.set_caption("Carrot Tower (with some Rajula)")

	pygame.font.init()
	clock = pygame.time.Clock()

	font = pygame.font.SysFont("Verdana", 128, True)
	loading_text = font.render("Loading", True, (0,0,0))
	pygame.event.get()
	loading(1)

	pygame.mixer.init(44100, -16, 2, 2048)
	_snd_death = pygame.mixer.Sound("trollandi_death.wav")
	_snd_woop = pygame.mixer.Sound("rajula_woop.wav")
	_snd_cucumber = pygame.mixer.Sound("cucumber.wav")
	_snd_carrot = pygame.mixer.Sound("carrot.wav")
	_snd_blurgh = pygame.mixer.Sound("blurgh.wav")

	background0 = pygame.image.load("map1.png").convert_alpha()
	background = pygame.transform.scale(background0, map(mul, background0.get_size(), (SCALE, SCALE)))
	panel = pygame.image.load("panel.png").convert_alpha()
	loading(2)

	going = True
	level = 0
	lives = 13
	money = 1000
	spawn_countdown = 6
	enemies = pygame.sprite.RenderClear([])
	towers = pygame.sprite.RenderClear([])
	projectiles = pygame.sprite.RenderClear([])
	bars = pygame.sprite.RenderClear([])
	hilight_box = Box(32, 32)
	things = [enemies, towers, projectiles, bars, pygame.sprite.RenderClear([hilight_box])]
	loading(3)

	imgload(("agurk.png", "carrot.png", "box.png"))
	imgload(("hat.png", "hat_krisseh_full.png", "hat_krisseh_half.png"))
	imgload(("superhat.png", "superkrisseh_full.png", "superkrisseh_half.png"))
	imgload(("exttower_1.png", "exttower_2.png", "exttower_3.png", "exttower_4.png"))
	imgload(("pringles_1.png", "pringles_2.png", "pringles_3.png"))
	loading(4)
	colours = ["red", "green", "blue", "black"]
	imgload(["saw_" + c + "_1.png" for c in colours])
	imgload(["saw_" + c + "_2.png" for c in colours])
	imgload(["ext_" + str(i) + ".png" for i in range(1, 5)])
	font = pygame.font.SysFont("Verdana", 16, True)

	# Fix Krisseh collisions
	full = _images["hat_krisseh_full.png"]
	half = _images["hat_krisseh_half.png"]
	for i in range(360):
		full[i] = (full[i][0], half[i][1])
	full = _images["superkrisseh_full.png"]
	half = _images["superkrisseh_half.png"]
	for i in range(360):
		full[i] = (full[i][0], half[i][1])

	knapps = []
	for y, fn in ((336, "hat.png"), (400, "superhat.png"), (480, "exttower_1.png"), (544, "pringles_1.png"), (608, "agurk.png")):
		knapps.append(Knappy((fn,), 1184, y))
	mouse = Mouse(["hat.png"], 0, 0)
	things.append(pygame.sprite.RenderClear(knapps + [mouse]))

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
			spawn_countdown = 30
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
				if ruta[0] > 16: # panel
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
				if ruta[0] > 16: # panel
					mouse._pos = (10000, 0)
				else:
					x, y = ruta[0] * 64 + 32, ruta[1] * 64 + 32
					yz = mouse.image.get_size()[1]
					if yz > 64:
						y -= 16
					mouse._pos = (x, y)
	pygame.quit()

if __name__ == "__main__":
	main()
