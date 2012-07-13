#!/usr/bin/env python

import pygame
from pygame.locals import *

WIDTH, HEIGHT = 1280, 720 # damn projector

def main():
	screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)# FULLSCREEN)
	pygame.display.set_caption("Carrot Tower (without Rajula)")
	pygame.quit()

if __name__ == "__main__":
	main()
