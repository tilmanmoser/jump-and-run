import pygame
import pygame.gfxdraw

from scripts.entities import Player
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

        # entities
        self.sparks = []
        self.player = Player(self, pos=(300, 60))

        # transition
        self.transition = -30

        self.load_level()

    def load_level(self):
        self.transition = -30
        self.tilemap.load(self.levels[self.level])
        self.sparks = []
        self.player.reset_at((300, 60))

    def run(self):
        running = True
        while running:

            if self.transition < 0:
                self.transition += 1

            if self.player.died:
                self.player.died += 1
                if self.player.died >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.player.died > 40:
                    self.load_level()

            if False:
                # player reached target
                self.transition += 1
                if self.transition > 30:
                    self.level = (self.level + 1) % len(self.levels)
                    self.load_level(self.level)

            # camera position centered on player
            self.scroll[0] += self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]
            self.scroll[1] += self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]
            render_offset = (int(self.scroll[0]), int(self.scroll[1]))

            # render display & update objects
            self.display.fill((0, 0, 0, 0))
            self.render_background()
            self.tilemap.render(self.display, render_offset)
            self.render_sparks(render_offset)
            self.render_player(render_offset)
            self.render_transition()

            # render display to screen
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
                    if event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                        self.player.jump()
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.movement[0] = False
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.movement[1] = False

            self.clock.tick(FPS)

    def render_transition(self):
        if self.transition:
            transition_surface = pygame.Surface(self.display.get_size())
            pygame.draw.circle(
                transition_surface,
                (255, 255, 255),
                (self.display.get_width() // 2, self.display.get_height() // 2),
                (30 - abs(self.transition)) * self.tilemap.tile_size,
            )
            transition_surface.set_colorkey((255, 255, 255))
            self.display.blit(transition_surface, (0, 0))

    def render_player(self, render_offset):
        if not self.player.died:
            self.player.update(movement=(self.movement[1] - self.movement[0], 0), tilemap=self.tilemap)
            self.player.render(self.display, render_offset)

    def render_sparks(self, render_offset):
        for spark in self.sparks.copy():
            if not spark.update():
                spark.render(self.display, render_offset)
            else:
                self.sparks.remove(spark)

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

    def resize(self, size):
        # fixed height, variable width
        self.display_scale = INITIAL_DISPLAY_SIZE[1] / size[1]
        self.display = pygame.Surface((size[0] * self.display_scale, INITIAL_DISPLAY_SIZE[1]))


if __name__ == "__main__":
    Game().run()
