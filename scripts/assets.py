import os
import pygame

BASE_IMG_PATH = "data/images/"
BASE_SND_PATH = "data/sounds/"
BASE_MSC_PATH = "data/music/"

LEAF_SPAWN_RECTS = [
    pygame.Rect(15, 15, 44, 38),
    pygame.Rect(20, 18, 52, 52),
    pygame.Rect(13, 13, 46, 42),
    pygame.Rect(18, 11, 24, 78),
    pygame.Rect(16, 11, 34, 38),
    pygame.Rect(13, 9, 20, 20),
]


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
        "caves/stone": load_images("caves/stone"),
        "decor/frames": load_images("decor/frames"),
        "decor/trees": load_images("decor/trees"),
        "decor/bushes": load_images("decor/bushes"),
        "decor/flowers": load_images("decor/flowers"),
        "spawners": load_images("spawners"),
        "backgrounds": load_images("backgrounds"),
    }


def load_animated_assets():
    return {
        "start/idle": Animation(load_images("checkpoints/start/idle"), image_duration=4),
        "end/idle": Animation(load_images("checkpoints/end/idle"), image_duration=4),
        "player/idle": Animation(load_images("entities/player/idle"), image_duration=6),
        "player/run": Animation(load_images("entities/player/run"), image_duration=4),
        "player/jump": Animation(load_images("entities/player/jump")),
        "player/fall": Animation(load_images("entities/player/fall")),
        "player/wall-slide": Animation(load_images("entities/player/wall-slide")),
        "player/wall-jump": Animation(load_images("entities/player/wall-jump"), image_duration=4),
        "pig/idle": Animation(load_images("entities/pig/idle"), image_duration=6),
        "pig/run": Animation(load_images("entities/pig/run"), image_duration=4),
        "snail/idle": Animation(load_images("entities/snail/idle"), image_duration=6),
        "snail/run": Animation(load_images("entities/snail/run"), image_duration=4),
        "bee/idle": Animation(load_images("entities/bee/idle"), image_duration=6),
        "bee/attack": Animation(load_images("entities/bee/attack"), image_duration=4),
        "chicken/idle": Animation(load_images("entities/chicken/idle"), image_duration=6),
        "chicken/run": Animation(load_images("entities/chicken/run"), image_duration=2),
        "bunny/idle": Animation(load_images("entities/bunny/idle"), image_duration=6),
        "bunny/run": Animation(load_images("entities/bunny/run"), image_duration=4),
        "fruits/apple/idle": Animation(load_images("fruits/apple/idle"), image_duration=4),
        "fruits/bananas/idle": Animation(load_images("fruits/bananas/idle"), image_duration=4),
        "fruits/cherries/idle": Animation(load_images("fruits/cherries/idle"), image_duration=4),
        "fruits/kiwi/idle": Animation(load_images("fruits/kiwi/idle"), image_duration=4),
        "fruits/melon/idle": Animation(load_images("fruits/melon/idle"), image_duration=4),
        "fruits/orange/idle": Animation(load_images("fruits/orange/idle"), image_duration=4),
        "fruits/pineapple/idle": Animation(load_images("fruits/pineapple/idle"), image_duration=4),
        "fruits/strawberry/idle": Animation(load_images("fruits/strawberry/idle"), image_duration=4),
        "particles/leaf": Animation(load_images("particles/leaf"), image_duration=12),
    }


def load_projectile_assets():
    return {"slime": load_image("projectiles/slime.png"), "sting": load_image("projectiles/sting.png")}


def load_music():
    return pygame.mixer.Sound(BASE_MSC_PATH + "epic-battle-153400.mp3")


def load_sounds():
    return {
        "1up": pygame.mixer.Sound(BASE_SND_PATH + "1up.wav"),
        "death": pygame.mixer.Sound(BASE_SND_PATH + "death.wav"),
        "fruit": pygame.mixer.Sound(BASE_SND_PATH + "fruit.wav"),
        "jump": pygame.mixer.Sound(BASE_SND_PATH + "jump.wav"),
        "kill": pygame.mixer.Sound(BASE_SND_PATH + "kill.wav"),
        "shoot": pygame.mixer.Sound(BASE_SND_PATH + "shoot.wav"),
    }


def get_level_list():
    levels = []
    for file in sorted(os.listdir("data/levels")):
        if str(file).endswith((".json")):
            levels.append("data/levels/" + file)
    return levels
