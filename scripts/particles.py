import math
import random

import pygame
from scripts.assets import Animation


class Dust:
    def __init__(self, pos):
        self.pos = list(pos)
        self.ttl = random.randint(5, 15)
        self.radius = int(random.random() * 6)
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (192, 192, 192), (self.radius, self.radius), self.radius)

    def update(self):
        self.ttl -= 1
        return not self.ttl

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        surface.blit(self.image, (self.pos[0] - offset[0], self.pos[1] - offset[1] - self.radius))


class Bubble:
    COLORS = [(250, 145, 137), (252, 174, 124), (255, 230, 153), (249, 255, 181), (179, 245, 188), (214, 246, 255), (226, 203, 247), (209, 189, 255)]

    def __init__(self, pos):
        self.pos = list(pos)
        self.speed = random.random() * 5 + 2
        self.angle = random.random() * (math.pi * 2)
        self.ttl = random.randint(90, 120)
        radius = int(random.random() * 4)
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, random.sample(Bubble.COLORS, 1)[0], (radius, radius), radius)

    def update(self):
        self.ttl -= 1
        if self.ttl <= 0:
            return True

        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        surface.blit(self.image, (self.pos[0] - offset[0], self.pos[1] - offset[1]))


class Spark:
    def __init__(self, pos, angle, speed):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed

    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        self.speed = max(0, self.speed - 0.1)
        return not self.speed

    def render(self, surface, offset=(0, 0)):
        render_points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),
            (
                self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0],
                self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1],
            ),
            (
                self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0],
                self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1],
            ),
            (
                self.pos[0] + math.cos(self.angle - math.pi) * self.speed * 0.5 - offset[0],
                self.pos[1] + math.sin(self.angle - math.pi) * self.speed * 0.5 - offset[1],
            ),
        ]

        pygame.draw.polygon(surface, (255, 255, 255), render_points)


class Leaf:
    def __init__(self, pos, animation: Animation):
        self.pos = list(pos)
        self.animation = animation.copy()
        self.ttl = random.randint(120, 240)

    def update(self):
        self.ttl -= 1
        if self.ttl <= 0:
            return True

        self.pos[0] += math.sin(self.animation.frame * 0.035) * 0.3
        self.pos[1] += 0.3

        self.animation.update()

    def render(self, surface, offset=(0, 0)):
        img = self.animation.image()
        surface.blit(
            img,
            (
                self.pos[0] - offset[0] - img.get_width() // 2,
                self.pos[1] - offset[1] - img.get_height() // 2,
            ),
        )


class Particles:
    def __init__(self):
        self.particles = []

    def update(self):
        for particle in self.particles.copy():
            if particle.update():
                self.particles.remove(particle)

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        for particle in self.particles:
            particle.render(surface, offset)

    def add(self, particle):
        self.particles.append(particle)
