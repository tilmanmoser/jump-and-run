import math
import random
import pygame
from scripts.spark import Spark
from scripts.tilemap import Tilemap


class Entity:
    def __init__(self, game, e_type, pos, size, animation_offset=(0, 0)):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = list(size)
        self.animation_offset = list(animation_offset)
        self.flip = False
        self.action = ""
        self.set_action("idle")

    def rect(self):
        return pygame.Rect((self.pos[0], self.pos[1], self.size[0], self.size[1]))

    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.animation = self.game.animated_assets[self.type + "/" + self.action].copy()

    def update(self):
        self.animation.update()

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        surface.blit(
            pygame.transform.flip(self.animation.image(), self.flip, False),
            (
                self.pos[0] - offset[0] + self.animation_offset[0],
                self.pos[1] - offset[1] + self.animation_offset[1],
            ),
        )

    def animate_death(self):
        for i in range(30):
            self.game.sparks.append(Spark(self.rect().center, random.random() * math.pi * 2, 2 + random.random()))


class PhysicsEntity(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collisions = {"up": False, "down": False, "right": False, "left": False}
        self.velocity = [0, 0]
        self.last_movement = [0, 0]

    def update(self, tilemap: Tilemap, movement=(0, 0)):
        frame_movement = (
            movement[0] + self.velocity[0],
            movement[1] + self.velocity[1],
        )

        # self.size[0/1] _MUST_ be <= tilemap.tile_size for collision detection to work right
        self.collisions = {"up": False, "down": False, "right": False, "left": False}

        # move on y-axis
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = entity_rect.y
        if self.collisions["up"] or self.collisions["down"]:
            self.velocity[1] = 0
        else:
            self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # move on x-axis
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

        # flip animation into movement direction
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        super().update()


class Player(PhysicsEntity):
    def __init__(self, animations, pos):
        super().__init__(animations, "player", pos, size=(16, 16), animation_offset=(-8, -16))
        self.speed = 2
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dead = False

    def reset_at(self, pos=(0, 0)):
        self.pos = list(pos)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.died = 0
        self.flip = False
        self.velocity = [0, 0]

    def update(self, tilemap: Tilemap, movement=(0, 0)):
        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 1

        if self.air_time > 180:
            self.animate_death()
            self.died += 1

        self.wall_slide = False
        if (self.collisions["right"] or self.collisions["left"]) and self.air_time > 4:
            self.wall_slide = True
            self.air_time = 5
            self.velocity[1] = min(1, self.velocity[1])
            if self.collisions["right"]:
                self.flip = False
            else:
                self.flip = True
            self.set_action("fall")

        if self.wall_slide:
            self.set_action("wall-slide")
        else:
            if self.air_time > 4:
                if self.velocity[1] < 0:
                    if self.velocity[0] != 0:
                        self.set_action("wall-jump")
                    else:
                        self.set_action("jump")
                else:
                    self.set_action("fall")
                    self.jumps = 0
            elif movement[0] != 0:
                self.set_action("run")
            else:
                self.set_action("idle")

        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1)
        else:
            self.velocity[0] = min(0, self.velocity[0] + 0.1)

        super().update(tilemap, movement=(movement[0] * self.speed, movement[1]))

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 5
                self.velocity[1] = -3
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True

            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -5
                self.velocity[1] = -3
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                self.flip = not self.flip
                return True

        elif self.jumps:
            self.velocity[1] = -4
            self.jumps -= 1
            self.air_time = 5
            return True


class Fruit(Entity):
    TYPES = ["apple", "bananas", "cherries", "kiwi", "melon", "orange", "pineapple", "strawberry"]
    COLORS = [(250, 145, 137), (252, 174, 124), (255, 230, 153), (249, 255, 181), (179, 245, 188), (214, 246, 255), (226, 203, 247), (209, 189, 255)]

    def __init__(self, game, pos):
        super().__init__(
            game,
            "fruits/" + random.sample(Fruit.TYPES, 1)[0],
            pos,
            (16, 16),
            (-8, -8),
        )
        self.collected = 0
        self.bubbles = []

    def update(self):
        super().update()

        if not self.collected:
            if self.rect().colliderect(self.game.player.rect()):
                self.collected += 1
                for i in range(20):
                    self.bubbles.append(
                        {
                            "pos": [int(self.pos[0] + self.size[0] / 2), int(self.pos[1] + self.size[1] / 2)],
                            "radius": random.random() * self.size[0] / 4,
                            "speed": random.random() * 5 + 2,
                            "angle": random.random() * (math.pi * 2),
                            "color": random.sample(Fruit.COLORS, 1)[0],
                        }
                    )
        else:
            self.collected += 1
            for bubble in self.bubbles:
                bubble["pos"][0] += math.cos(bubble["angle"]) * bubble["speed"]
                bubble["pos"][1] += math.sin(bubble["angle"]) * bubble["speed"]
                bubble["radius"] *= 1.01

            if self.collected >= 120:
                return True

    def render(self, surface, offset):
        if not self.collected:
            super().render(surface, offset)
        for bubble in self.bubbles:
            pygame.draw.circle(surface, bubble["color"], (bubble["pos"][0] - offset[0], bubble["pos"][1] - offset[1]), bubble["radius"])


class Enemy(Entity):
    def __init__(self) -> None:
        super().__init__()


class Pig(Enemy, PhysicsEntity):
    def __init__(self) -> None:
        super().__init__()
