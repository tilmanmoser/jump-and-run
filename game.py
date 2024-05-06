import random
import pygame
import pygame.gfxdraw

from scripts.clouds import Clouds
from scripts.entities import Entity, Fruit, Player
from scripts.particles import Particles
from scripts.tilemap import Tilemap
from scripts.utils import get_level_list, load_animated_assets, load_image, load_images, load_tile_assets

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

        # background
        self.bg_surface = pygame.Surface((0, 0))

        # topbar (stats)
        self.stats_surface = pygame.Surface((self.display.get_width() - 16, 16), pygame.SRCALPHA)
        self.stats_images = load_images("stats")
        self.font = pygame.Font("data/fonts/press-start-2p-latin-400-normal.ttf", 16)

        # user inputs & derived states
        self.movement = [False, False]
        self.scroll = [0, 0]
        self.render_offset = (0, 0)

        # assets
        self.tile_assets = load_tile_assets()
        self.animated_assets = load_animated_assets()
        self.mountains = load_image("mountains.png")
        self.clouds = Clouds(load_images("clouds"), count=16)

        self.levels = get_level_list()
        self.tilemap = Tilemap(self.tile_assets)

        # entities
        self.start = Entity(self, "start", (0, 0), (64, 64), (-16, -48))
        self.end = Entity(self, "end", (0, 0), (64, 64), (-16, -48))
        self.player = Player(self, pos=(0, 0))
        self.particles = Particles()
        self.fruits = {}

        # game states
        self.level = 0
        self.time = 300 * FPS
        self.transition = -30
        self.reached_level_end = False
        self.load_level()

    def reset(self):
        self.player.lives = 3
        self.player.fruits = 0
        self.level = 0
        self.load_level()

    def load_level(self):
        self.transition = -30
        self.time = 300 * FPS
        self.reached_level_end = False

        self.tilemap.load(self.levels[self.level])

        starters = self.tilemap.extract([("spawners", 0)])
        if starters:
            self.start.pos = starters[0]["pos"]
        enders = self.tilemap.extract([("spawners", 1)])
        if enders:
            self.end.pos = enders[0]["pos"]

        self.player.reset_at(self.start.pos)

        self.fruits = {}
        surface_tiles = self.tilemap.find_surface_tiles()
        for pos in random.sample(surface_tiles, int(len(surface_tiles) // 8)):
            self.fruits[str(pos[0]) + ";" + str(pos[1])] = Fruit(self, (pos[0] * self.tilemap.tile_size, pos[1] * self.tilemap.tile_size))

    def run(self):
        running = True
        while running:
            # camera position centered on player
            self.scroll[0] += self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]
            self.scroll[1] += self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]
            self.render_offset = (int(self.scroll[0]), int(self.scroll[1]))

            # level transitions
            if self.player.died:
                self.player.died += 1
                if self.player.died >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.player.died > 40:
                    if self.player.lives <= 0:
                        self.reset()
                    else:
                        self.load_level()
            elif self.reached_level_end:
                self.transition += 1
                if self.transition > 30:
                    self.level = (self.level + 1) % len(self.levels)
                    self.load_level()
            elif self.player.rect().colliderect(self.end.rect()):
                self.reached_level_end = True
            else:
                self.time -= 1
                if self.time <= 0:
                    self.player.die()

            if self.transition < 0:
                self.transition += 1

            # render display & update objects
            self.display.fill((0, 0, 0, 0))
            self.render_background()
            self.tilemap.render(self.display, self.render_offset)
            self.render_checkpoints()
            self.render_fruits()
            self.render_particles()
            self.render_player()
            self.render_stats()
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

    def render_checkpoints(self):
        self.start.update()
        self.start.render(self.display, self.render_offset)
        self.end.update()
        self.end.render(self.display, self.render_offset)

    def render_fruits(self):
        for fruit in self.fruits.copy():
            if self.fruits[fruit].update():
                del self.fruits[fruit]
            else:
                self.fruits[fruit].render(self.display, self.render_offset)

    def render_player(self):
        if not self.player.died:
            self.player.update(movement=(self.movement[1] - self.movement[0], 0), tilemap=self.tilemap)
            self.player.render(self.display, self.render_offset)

    def render_particles(self):
        self.particles.update()
        self.particles.render(self.display, self.render_offset)

    def render_stats(self):
        if self.stats_surface.get_width() != self.display.get_width() - 16:
            self.stats_surface = pygame.Surface((self.display.get_width() - 16, 16), pygame.SRCALPHA)

        self.stats_surface.fill((0, 0, 0, 0))
        # lives
        self.stats_surface.blit(self.stats_images[0], (0, 0))
        self.stats_surface.blit(self.font.render(str(self.player.lives), False, (255, 255, 255)), (20, 0))
        # fruits
        self.stats_surface.blit(self.stats_images[1], (80, 0))
        self.stats_surface.blit(self.font.render(str(self.player.fruits).zfill(2), False, (255, 255, 255)), (100, 0))
        # time
        time = self.font.render(str(self.time // FPS), False, (255, 255, 255))
        self.stats_surface.blit(time, (self.stats_surface.get_width() - time.get_width(), 0))

        stats_mask = pygame.mask.from_surface(self.stats_surface)
        stats_mask = stats_mask.convolve(pygame.Mask((5, 5), fill=True))
        silhouette = stats_mask.to_surface(setcolor=(0, 0, 33), unsetcolor=(0, 0, 0, 0))
        self.display.blit(silhouette, (6, 6))

        self.display.blit(self.stats_surface, (8, 8))

    def render_background(self):
        if self.bg_surface.get_width() != self.display.get_width():
            self.bg_surface = pygame.Surface(self.display.get_size())
            pygame.gfxdraw.textured_polygon(
                self.bg_surface,
                [
                    (0, 0),
                    (self.bg_surface.get_width(), 0),
                    self.bg_surface.get_size(),
                    (0, self.bg_surface.get_height()),
                ],
                self.tile_assets["backgrounds"][self.tilemap.background],
                self.tile_assets["backgrounds"][self.tilemap.background].get_width(),
                self.tile_assets["backgrounds"][self.tilemap.background].get_height(),
            )
            self.bg_surface.blit(
                self.mountains, ((self.bg_surface.get_width() - self.mountains.get_width()) // 2, self.bg_surface.get_height() - self.mountains.get_height())
            )

        self.display.blit(self.bg_surface, (0, 0))
        self.clouds.update()
        self.clouds.draw(self.display, self.render_offset)

    def resize(self, size):
        # fixed height, variable width
        self.display_scale = INITIAL_DISPLAY_SIZE[1] / size[1]
        self.display = pygame.Surface((size[0] * self.display_scale, INITIAL_DISPLAY_SIZE[1]))


if __name__ == "__main__":
    Game().run()
