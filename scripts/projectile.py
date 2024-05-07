import math
import random

from scripts.particles import Spark


class Projectile:
    def __init__(self, game, p_type, pos=(0, 0), velocity=(0, 0), timer=16):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.timer = timer
        self.image = game.projectile_assets[p_type]

    def update(self, tilemap):
        self.timer -= 1
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        if tilemap.solid_check(self.pos):
            for i in range(8):
                if self.velocity[0] > 0:
                    self.game.particles.add(Spark(self.pos, random.random() - 0.5 + math.pi, 2 + random.random()))
                if self.velocity[0] < 0:
                    self.game.particles.add(Spark(self.pos, random.random() - 0.5, 2 + random.random()))
                if self.velocity[1] > 0:
                    self.game.particles.add(Spark(self.pos, random.random() - 0.5 - math.pi / 2, 2 + random.random()))
                if self.velocity[1] < 0:
                    self.game.particles.add(Spark(self.pos, random.random() - 0.5 + math.pi / 2, 2 + random.random()))
            return True
        elif self.timer <= 0:
            return True
        elif self.game.player.rect().collidepoint(self.pos):
            self.game.player.die()
            return True

    def render(self, surface, offset=(0, 0)):
        surface.blit(
            self.image,
            (
                self.pos[0] - self.image.get_width() / 2 - offset[0],
                self.pos[1] - self.image.get_height() / 2 - offset[1],
            ),
        )
