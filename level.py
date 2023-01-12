import pygame
from tiles import Tile, StaticTile, Crate, Coin, Obstacle, Door
from enemy import Enemy
from settings import tile_size
from settings import screen_width
from player import Player
from support import import_csv_layout, import_cut_graphics
from game_data import levels
from particles import ParticleEffect


def create_tile_group(layout, tile_type):
    global sprite
    sprite_group = pygame.sprite.Group()

    for row_index, row in enumerate(layout):
        for col_index, val in enumerate(row):
            # if tile is empty
            if val != '-1':
                x = col_index * tile_size
                y = row_index * tile_size

                if tile_type == 'terrain':
                    terrain_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                    tile_surface = terrain_tile_list[int(val)]

                    sprite = StaticTile(tile_size, x, y, tile_surface)

                if tile_type == 'walls':
                    walls_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                    tile_surface = walls_tile_list[int(val)]

                    sprite = StaticTile(tile_size, x, y, tile_surface)

                if tile_type == 'crates':
                    sprite = Crate(tile_size, x, y)

                if tile_type == 'coins':
                    sprite = Coin(tile_size, x, y, 'graphics/coins/diamonds')

                if tile_type == 'obstacles':
                    obstacle_tile_list = import_cut_graphics('graphics/decorations/decorations.png')
                    tile_surface = obstacle_tile_list[int(val)]

                    sprite = Obstacle(tile_size, x, y, tile_surface)

                if tile_type == 'deco':
                    deco_tile_list = import_cut_graphics('graphics/decorations/decorations.png')
                    tile_surface = deco_tile_list[int(val)]

                    sprite = StaticTile(tile_size, x, y, tile_surface)

                if tile_type == 'doors':
                    sprite = Door(tile_size, x, y, 'graphics/decorations/door')

                if tile_type == 'enemies':
                    sprite = Enemy(tile_size, x, y)

                if tile_type == 'constraints':
                    sprite = Tile(tile_size, x, y)

                sprite_group.add(sprite)

    return sprite_group


class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health):

        # General setup
        self.current_x = None
        self.display_surface = surface
        self.world_shift = 0

        # Audio
        self.coin_sound = pygame.mixer.Sound('audio/effects/coin.wav')
        self.coin_sound.set_volume(0.13)
        self.stomp_sound = pygame.mixer.Sound('audio/effects/stomp.wav')
        self.stomp_sound.set_volume(0.13)

        # Overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # Player setup
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # User interface

        self.change_coins = change_coins

        # Death
        self.death = pygame.sprite.Group()

        # Get terrain map
        terrain_layout = import_csv_layout(level_data['walls'])
        self.terrain_sprites = create_tile_group(terrain_layout, 'terrain')

        # Get background walls
        walls_layout = import_csv_layout(level_data['bg walls'])
        self.walls_sprites = create_tile_group(walls_layout, 'walls')

        # Get crates
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprites = create_tile_group(crates_layout, 'crates')

        # Get coins (diamonds)
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = create_tile_group(coin_layout, 'coins')

        # Get wooden obstacles
        obstacles_layout = import_csv_layout(level_data['obstacles'])
        self.obstacles_sprites = create_tile_group(obstacles_layout, 'obstacles')

        # Get decorations
        deco_layout = import_csv_layout(level_data['deco'])
        self.deco_sprites = create_tile_group(deco_layout, 'deco')

        # Get doors
        door_layout = import_csv_layout(level_data['doors'])
        self.door_sprites = create_tile_group(door_layout, 'doors')

        # Enemy 
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = create_tile_group(enemy_layout, 'enemies')

        # Constraints
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = create_tile_group(constraint_layout, 'constraints')

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                # When 0 is encountered in the CSV file, that's where the player spawns
                if val == '0':
                    sprite = Player((x, y), change_health)
                    self.player.add(sprite)
                elif val != '-1':
                    # This is where the game ends
                    mark_surface = pygame.image.load('graphics/terrain/terrain_tiles.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, mark_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx

        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        collidable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.\
            obstacles_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        collidable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.\
            obstacles_sprites.sprites()

        for sprite_collide in collidable_sprites:
            if sprite_collide.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite_collide.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite_collide.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def check_death(self):
        pass

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collision(self):
        collided_coins_list = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins_list:
            self.coin_sound.play()
            for _ in collided_coins_list:
                self.change_coins(1)

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.stomp_sound.play()
                    death_sprite = ParticleEffect(enemy.rect.center)
                    self.death.add(death_sprite)
                    enemy.kill()
                    self.player.sprite.direction.y = -15
                else:
                    self.player.sprite.get_damage()

    # Run the level
    def run(self):
        # Render background walls
        self.walls_sprites.draw(self.display_surface)
        self.walls_sprites.update(self.world_shift)

        # Render coins
        self.coin_sprites.draw(self.display_surface)
        self.coin_sprites.update(self.world_shift)

        # Render wooden obstacles
        self.obstacles_sprites.draw(self.display_surface)
        self.obstacles_sprites.update(self.world_shift)

        # Render doors
        self.door_sprites.draw(self.display_surface)
        self.door_sprites.update(self.world_shift)

        # Render enemies
        self.enemy_sprites.draw(self.display_surface)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.update(self.world_shift)
        self.death.update(self.world_shift)
        self.death.draw(self.display_surface)

        # Render crates
        self.crates_sprites.draw(self.display_surface)
        self.crates_sprites.update(self.world_shift)

        # Render collision walls
        self.terrain_sprites.draw(self.display_surface)
        self.terrain_sprites.update(self.world_shift)

        # Player sprites
        self.player.update(self.world_shift)
        self.scroll_x()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.player.draw(self.display_surface)

        self.check_death()
        self.check_win()

        self.check_coin_collision()
        self.check_enemy_collisions()

        self.goal.update(self.world_shift)
