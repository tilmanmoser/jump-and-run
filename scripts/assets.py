import os
import pygame

BASE_IMG_PATH = "data/images/"


def load_image(path):
    image = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return image


def load_images(path):
    images = []
    for file in sorted(os.listdir(BASE_IMG_PATH + path)):
        if str(file).endswith((".png")):
            images.append(load_image(path + "/" + file))
    return images


def load_tile_assets():
    return {
        "tiles/candy": load_images("tiles/candy"),
        "tiles/grass": load_images("tiles/grass"),
        "tiles/ice": load_images("tiles/ice"),
        "tiles/mud": load_images("tiles/mud"),
        "tiles/sand": load_images("tiles/sand"),
        "tiles/stone": load_images("tiles/stone"),
        "tiles/swamp": load_images("tiles/swamp"),
        "tiles/wall": load_images("tiles/wall"),
        "decor/frames": load_images("decor/frames"),
        "decor/trees": load_images("decor/trees"),
        "decor/bushes": load_images("decor/bushes"),
        "decor/flowers": load_images("decor/flowers"),
        "spawners": load_images("spawners"),
        "backgrounds": load_images("backgrounds"),
    }
