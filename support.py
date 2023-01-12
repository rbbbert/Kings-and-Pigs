from os import walk

import pygame
from csv import reader
from settings import tile_size


def import_folder(path):
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            width, height = image_surf.get_size()
            scale = 1.25
            image_surf = pygame.transform.scale(image_surf, (width * scale, height * scale))
            surface_list.append(image_surf)

    return surface_list


# Used for reading the CSV files containing the level map
def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        level = reader(level_map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))

        return terrain_map


def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_width() / tile_size)
    tile_num_y = int(surface.get_height() / tile_size)

    cut_tiles = []

    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size

            # Flag turns the empty pixels to transparent
            new_surf = pygame.Surface((tile_size, tile_size), flags=pygame.SRCALPHA)

            # Get a slice of the image onto the surface (the tile)
            new_surf.blit(surface, (0, 0), pygame.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new_surf)

    return cut_tiles
