import pygame
import pygame.gfxdraw

from scripts.tilemap import Tilemap
from scripts.utils import get_level_list, load_animated_assets, load_tile_assets

INITIAL_DISPLAY_SIZE = [800, 500]
FPS = 60


class Game:
    def __init__(self):
        # display
        pygame.init()
        pygame.display.set_caption("Jump 'n' Run")
        self.screen = pygame.display.set_mode(INITIAL_DISPLAY_SIZE, pygame.RESIZABLE)
        self.display = pygame.Surface(INITIAL_DISPLAY_SIZE)
        self.display_scale = 1
        self.clock = pygame.Clock()

        # user inputs & derived states
        self.movement = [False, False]
        self.scroll = [0, 0]

        # assets
        self.tile_assets = load_tile_assets()
        self.animated_assets = load_animated_assets()

        # levelmaps
        self.level = 0
        self.levels = get_level_list()
        self.tilemap = Tilemap(self.tile_assets)
        self.tilemap.load(self.levels[self.level])

    def run(self):
        running = True
        while running:
            # camera position
            render_offset = (int(self.scroll[0]), int(self.scroll[1]))

            # rendering
            self.display.fill((0, 0, 0, 0))
            self.render_background()
            self.tilemap.render(self.display, render_offset)

            self.screen.fill((0, 0, 0, 0))
            self.screen.blit(
                pygame.transform.scale(self.display, (self.display.get_width() / self.display_scale, self.display.get_height() / self.display_scale)), (0, 0)
            )
            pygame.display.update()

            # user inputs
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.VIDEORESIZE:
                    self.resize(event.dict["size"])
                if event.type == pygame.VIDEOEXPOSE:
                    self.resize(self.screen.get_size())
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.movement[0] = True
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.movement[0] = False
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.movement[1] = False

            self.clock.tick(FPS)

    def resize(self, size):
        # fixed height, variable width
        self.display_scale = INITIAL_DISPLAY_SIZE[1] / size[1]
        self.display = pygame.Surface((size[0] * self.display_scale, INITIAL_DISPLAY_SIZE[1]))

    def render_background(self):
        pygame.gfxdraw.textured_polygon(
            self.display,
            [
                (0, 0),
                (self.display.get_width(), 0),
                self.display.get_size(),
                (0, self.display.get_height()),
            ],
            self.tile_assets["backgrounds"][self.tilemap.background],
            self.tile_assets["backgrounds"][self.tilemap.background].get_width(),
            self.tile_assets["backgrounds"][self.tilemap.background].get_height(),
        )


if __name__ == "__main__":
    Game().run()
