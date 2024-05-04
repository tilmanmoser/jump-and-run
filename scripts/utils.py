import os
import pygame

BASE_IMG_PATH = "data/images/"


class Animation:
    def __init__(self, images, image_duration=5, loop=True):
        self.images = images
        self.image_duration = image_duration
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.image_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.image_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.image_duration * len(self.images) - 1)
            if self.frame >= self.image_duration * len(self.images) - 1:
                self.done = True

    def image(self):
        return self.images[int(self.frame / self.image_duration)]


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


def load_animated_assets():
    return {
        "player/idle": Animation(load_images("entities/player/idle"), image_duration=6),
        "player/run": Animation(load_images("entities/player/run"), image_duration=4),
        "player/jump": Animation(load_images("entities/player/jump")),
        "player/fall": Animation(load_images("entities/player/fall")),
        "player/wall-slide": Animation(load_images("entities/player/wall-slide")),
        "player/wall-jump": Animation(load_images("entities/player/wall-jump"), image_duration=4),
    }


def get_level_list():
    levels = []
    for file in sorted(os.listdir("data/levels")):
        if str(file).endswith((".json")):
            levels.append("data/levels/" + file)
    return levels
