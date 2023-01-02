import pygame
import sys
from settings import screen_width
from settings import screen_height
from level import Level
from game_data import level_1

# Pygame setup
pygame.init()
pygame.display.set_caption("Kings and Pigs")
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
level = Level(level_1, screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('black')
    level.run()

    pygame.display.update()
    clock.tick(60)
