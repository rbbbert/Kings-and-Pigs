import pygame


class UI:
    def __init__(self, surface):
        # Setup
        self.display_surface = surface

        # Health
        self.health_bar = pygame.image.load('graphics/ui/health_bar.png').convert_alpha()
        self.health_bar_topleft = (54, 39)
        self.bar_max_width = 152
        self.bar_height = 4

        # Coins
        self.coin = pygame.image.load('graphics/ui/coin.png').convert_alpha()
        self.coin = pygame.transform.scale(self.coin, (26, 18))
        self.coin_rect = self.coin.get_rect(topleft=(50, 61))
        self.font = pygame.font.Font('graphics/ui/ARCADEPI.TTF', 16)

    def show_health(self, cur_health, full):
        self.display_surface.blit(self.health_bar, (20, 10))
        current_health_ration = cur_health / full
        current_bar_width = self.bar_max_width * current_health_ration
        health_bar_rect = pygame.Rect(self.health_bar_topleft, (current_bar_width, self.bar_height))
        pygame.draw.rect(self.display_surface, '#dc4949', health_bar_rect)

    def show_coins(self, amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        coin_amount_surface = self.font.render(str(amount), False, '#33323d')
        coin_amount_rect = coin_amount_surface.get_rect(midleft=(self.coin_rect.right + 4, self.coin_rect.centery + 1))
        self.display_surface.blit(coin_amount_surface, coin_amount_rect)
