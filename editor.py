import sys
import pygame
import pygame.gfxdraw

from scripts.assets import load_tile_assets
from scripts.tilemap import Tilemap

INITIAL_DISPLAY_SIZE = [800, 500]
FPS = 60


class Editor:
    def __init__(self, path="map.json"):
        self.level_file = path

        # display
        pygame.init()
        pygame.display.set_caption("Level Editor")
        self.screen = pygame.display.set_mode(INITIAL_DISPLAY_SIZE, pygame.RESIZABLE)
        self.display = pygame.Surface(INITIAL_DISPLAY_SIZE)
        self.display_scale = 1
        self.clock = pygame.Clock()

        # user inputs & derived states
        self.movement = [False, False, False, False]
        self.shift = False
        self.click = [False, False]
        self.ongrid = True
        self.tile_type = 0
        self.tile_variant = 0
        self.scroll = [0, 0]

        # assets and tilemap
        self.tile_assets = load_tile_assets()
        self.tile_list = list(self.tile_assets)
        self.tilemap = Tilemap(self.tile_assets)
        try:
            self.tilemap.load(self.level_file)
        except FileNotFoundError:
            pass

    def run(self):
        running = True
        while running:
            # camera position
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 8
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 8
            render_offset = (int(self.scroll[0]), int(self.scroll[1]))

            # relative mouse position
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] * self.display_scale, mpos[1] * self.display_scale)

            # tile placement
            if self.click[0] and self.ongrid:  # (offgrid in events loop once per click)
                self.tilemap.add((mpos[0] + render_offset[0], mpos[1] + render_offset[1]), self.tile_list[self.tile_type], self.tile_variant, self.ongrid)
            if self.click[1]:
                self.tilemap.remove((mpos[0] + render_offset[0], mpos[1] + render_offset[1]), render_offset, self.ongrid)

            # rendering
            self.display.fill((0, 0, 0, 0))
            self.render_background()
            self.tilemap.render(self.display, render_offset)
            self.render_current_tile(mpos)

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
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.movement[2] = True
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.movement[3] = True
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        self.shift = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        self.tilemap.save(self.level_file)
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.movement[0] = False
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.movement[1] = False
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.movement[2] = False
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.movement[3] = False
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        self.shift = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click[0] = True
                        if not self.ongrid:
                            self.tilemap.add(
                                (mpos[0] + render_offset[0], mpos[1] + render_offset[1]), self.tile_list[self.tile_type], self.tile_variant, self.ongrid
                            )
                    if event.button == 3:
                        self.click[1] = True
                    if event.button == 4:
                        self.update_tile(increment=+1, variant=self.shift)
                    if event.button == 5:
                        self.update_tile(increment=-1, variant=self.shift)
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.click[0] = False
                    if event.button == 3:
                        self.click[1] = False

            self.clock.tick(FPS)

    def resize(self, size):
        # fixed height, variable width
        self.display_scale = INITIAL_DISPLAY_SIZE[1] / size[1]
        self.display = pygame.Surface((size[0] * self.display_scale, INITIAL_DISPLAY_SIZE[1]))

    def update_tile(self, increment=1, variant=False):
        if variant:
            self.tile_variant = (self.tile_variant + increment) % len(self.tile_assets[self.tile_list[self.tile_type]])
        else:
            self.tile_type = (self.tile_type + increment) % len(self.tile_list)
            self.tile_variant = 0

    def render_current_tile(self, mpos):
        tile_img = self.tile_assets[self.tile_list[self.tile_type]][self.tile_variant]
        if self.ongrid:
            self.display.blit(
                tile_img,
                (
                    ((mpos[0] + self.scroll[0]) // self.tilemap.tile_size) * self.tilemap.tile_size - self.scroll[0],
                    ((mpos[1] + self.scroll[1]) // self.tilemap.tile_size) * self.tilemap.tile_size - self.scroll[1],
                ),
            )
        else:
            self.display.blit(tile_img, mpos)

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
    file_path = sys.argv[1] if len(sys.argv) > 1 else "map.json"
    Editor(file_path).run()
