from os import walk

import pygame


def import_folder(path):
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            width, height = image_surf.get_size()
            scale = 1.75
            image_surf = pygame.transform.scale(image_surf, (width * scale, height * scale))
            surface_list.append(image_surf)

    return surface_list
