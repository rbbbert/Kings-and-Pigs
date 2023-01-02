import pygame
from tiles import Tile, StaticTile, Crate, Coin, Obstacle, Door
from enemy import Enemy
from settings import tile_size
from settings import screen_width
from player import Player
from support import import_csv_layout, import_cut_graphics


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.world_shift = 0

        # Player setup
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        # Get terrain map
        terrain_layout = import_csv_layout(level_data['walls'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        # Get background walls
        walls_layout = import_csv_layout(level_data['bg walls'])
        self.walls_sprites = self.create_tile_group(walls_layout, 'walls')

        # Get crates
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprites = self.create_tile_group(crates_layout, 'crates')

        # Get coins (diamonds)
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        # Get wooden obstacles
        obstacles_layout = import_csv_layout(level_data['obstacles'])
        self.obstacles_sprites = self.create_tile_group(obstacles_layout, 'obstacles')

        # Get decorations
        deco_layout = import_csv_layout(level_data['deco'])
        self.deco_sprites = self.create_tile_group(deco_layout, 'deco')

        # Get doors
        door_layout = import_csv_layout(level_data['doors'])
        self.door_sprites = self.create_tile_group(door_layout, 'doors')

        # Enemy 
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

        # Constraints
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraints')


    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                # if tile is empty
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]

                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    
                    if type == 'walls':
                        walls_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                        tile_surface = walls_tile_list[int(val)]

                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    
                    if type == 'crates':
                        sprite = Crate(tile_size, x, y)
                    
                    if type == 'coins':
                        sprite = Coin(tile_size, x, y, 'graphics/coins/diamonds')
                    
                    if type == 'obstacles':
                        obstacle_tile_list = import_cut_graphics('graphics/decorations/decorations.png')
                        tile_surface = obstacle_tile_list[int(val)]

                        sprite = Obstacle(tile_size, x, y, tile_surface)
                    
                    if type == 'deco':
                        deco_tile_list = import_cut_graphics('graphics/decorations/decorations.png')
                        tile_surface = deco_tile_list[int(val)]

                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    
                    if type == 'doors':
                        sprite = Door(tile_size, x, y, 'graphics/decorations/door')
                    
                    if type == 'enemies':
                        sprite = Enemy(tile_size, x, y)
                    
                    if type == 'constraints':
                        sprite = Tile(tile_size, x, y)

                    
                    sprite_group.add(sprite)


        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):     
                x = col_index * tile_size
                y = row_index * tile_size
                # When 0 is encountered in the CSV file, that's where the player spawns
                if val == '0':
                    sprite = Player((x, y))
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
        player.rect.x += player.direction.x * player.speed

        collidable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.obstacles_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        collidable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.obstacles_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

       
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

        self.goal.update(self.world_shift)
