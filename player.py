import pygame
from support import import_folder
from math import sin


def wave_value():
    value = sin(pygame.time.get_ticks())
    if value > 0:
        return 255
    else:
        return 0


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, change_health):
        super().__init__()

        self.animations = {}
        self.frame_index = 0
        self.animation_speed = 0.15
        self.import_character_assets()
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # player movement
        self.speed = 10000
        self.direction = pygame.math.Vector2(0, 0)
        self.gravity = 0.8
        self.jump_speed = -16
        self.collision_rect = pygame.rect.Rect(self.rect.topleft, (50, self.rect.height))

        # player status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False

        # Health management
        self.change_health = change_health
        self.invincible = False
        self.invincibility_duration = 800
        self.hurt_time = 0

        # Audio
        self.jump_sound = pygame.mixer.Sound('audio/effects/jump.wav')
        self.jump_sound.set_volume(0.13)
        self.hit_sound = pygame.mixer.Sound('audio/effects/hit.wav')
        self.hit_sound.set_volume(0.13)

    def import_character_assets(self):
        character_path = 'graphics/character/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'attack': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]

        # loop over frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
            self.rect.bottomleft = self.collision_rect.bottomleft
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image
            self.rect.bottomright = self.collision_rect.bottomright

        if self.invincible:
            alpha = wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_UP] and self.on_ground:
            self.jump()

    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.collision_rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        self.jump_sound.play()

    def get_damage(self):
        if not self.invincible:
            self.change_health(-34)
            self.invincible = True
            self.hurt_time = pygame.time.get_ticks()
            self.hit_sound.play()

    def invincibility_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False

    def update(self, shift):
        self.rect.x += shift
        self.get_input()
        self.get_status()
        self.animate()
        self.invincibility_timer()
