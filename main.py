import pygame
import sys
from settings import screen_width
from settings import screen_height
from level import Level
from overworld import Overworld
from ui import UI


class Game:
    def __init__(self):

        # Game attributes
        self.max_level = 0
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0

        # Audio
        self.level_bg_music = pygame.mixer.Sound('audio/level_music.wav')
        self.level_bg_music.set_volume(0.13)
        self.overworld_bg_movie = pygame.mixer.Sound('audio/overworld_music.wav')
        self.overworld_bg_movie.set_volume(0.13)

        # Overworld creation
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        self.level = None
        self.status = 'overworld'
        self.overworld_bg_movie.play(loops=-1)

        # User interface
        self.ui = UI(screen)

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.create_overworld, self.change_coins, self.change_health)
        self.status = 'level'
        self.overworld_bg_movie.stop()
        self.level_bg_music.play(loops=-1)

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        self.overworld_bg_movie.play(loops=-1)
        self.level_bg_music.stop()

    def change_coins(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.cur_health += amount

    def check_game_over(self):
        if self.cur_health < 0:
            self.cur_health = 100
            self.coins = 0
            self.max_level = 0
            self.overworld = Overworld(0, self.max_level, screen, self.create_level)
            self.status = 'overworld'
            self.level_bg_music.stop()
            self.overworld_bg_movie.play(loops=-1)

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.cur_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()


# Pygame setup
pygame.init()
pygame.display.set_caption("Kings and Pigs")
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()
background = pygame.image.load('graphics/overworld/sky_middle.png')
background = pygame.transform.scale(background, (screen_width, screen_height))
title = pygame.image.load('graphics/overworld/Kings and Pigs.png')
title = pygame.transform.scale(title, (512, 64))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(background, (0, 0))
    screen.blit(title, (350, 40))
    game.run()

    pygame.display.update()
    clock.tick(60)
