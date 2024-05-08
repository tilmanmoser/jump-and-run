import math
import random
import pygame
from scripts.particles import Bubble, Dust, Spark
from scripts.projectile import Projectile
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
            self.game.particles.add(Spark(self.rect().center, random.random() * math.pi * 2, 2 + random.random()))


class Fruit(Entity):
    TYPES = ["apple", "bananas", "cherries", "kiwi", "melon", "orange", "pineapple", "strawberry"]

    def __init__(self, game, pos):
        super().__init__(
            game,
            "fruits/" + random.sample(Fruit.TYPES, 1)[0],
            pos,
            (16, 16),
            (-8, -8),
        )

    def update(self):
        super().update()

        if self.rect().colliderect(self.game.player.rect()):
            self.game.player.collect_fruit()
            for i in range(20):
                self.game.particles.add(Bubble(pos=(int(self.pos[0] + self.size[0] / 2), int(self.pos[1] + self.size[1] / 2))))
            if not self.game.muted:
                self.game.sounds["fruit"].play()
            return True


class PhysicsEntity(Entity):
    def __init__(self, game, e_type, pos, size, animation_offset=(0, 0)):
        super().__init__(game, e_type, pos, size, animation_offset)
        self.collisions = {"up": False, "down": False, "right": False, "left": False}
        self.velocity = [0, 0]
        self.last_movement = [0, 0]

    def update(self, tilemap: Tilemap, movement=(0, 0)):
        rect = self.rect()
        surface_tile = tilemap.solid_check((rect.centerx, rect.bottom + tilemap.tile_size // 2))
        on_ice = surface_tile and surface_tile["type"] == "tiles/ice"
        on_swamp = surface_tile and surface_tile["type"] == "tiles/swamp"

        frame_movement = (
            movement[0] * (0.5 if on_swamp else 1) + self.velocity[0],
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

        # ice sliding
        if on_ice and movement[0] != self.last_movement[0] and self.last_movement[0] != 0:
            self.velocity[0] = self.last_movement[0]

        # normalize x-velocity
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - (0.1 if not on_ice else 0.05))
        else:
            self.velocity[0] = min(0, self.velocity[0] + (0.1 if not on_ice else 0.05))

        # flip animation into movement direction
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        super().update()


class Player(PhysicsEntity):
    def __init__(self, game, pos):
        super().__init__(game, "player", pos, size=(16, 16), animation_offset=(-8, -16))
        self.lives = 3
        self.fruits = 0
        self.speed = 3
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dead = False

    def spawn(self, pos=(0, 0)):
        self.pos = list(pos)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.died = 0
        self.flip = False
        self.velocity = [0, 0]

    def die(self):
        self.lives = max(0, self.lives - 1)
        self.died += 1
        self.animate_death()
        if not self.game.muted:
            self.game.sounds["death"].play()

    def collect_fruit(self):
        self.fruits += 1
        if self.fruits >= 100:
            self.fruits = self.fruits % 100
            self.lives += 1
            if not self.game.muted:
                self.game.sounds["1up"].play()

    def update(self, tilemap: Tilemap, movement=(0, 0)):
        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 1

        if self.air_time > 180:
            self.die()

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
                    if abs(self.velocity[0]) > 2:
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

        super().update(tilemap, movement=(movement[0] * self.speed, movement[1]))

        # collisions with enemies
        p_rect = self.rect()
        for enemy in self.game.enemies.copy():
            e_rect = enemy.rect()
            if p_rect.colliderect(e_rect):
                if p_rect.centery < e_rect.centery:
                    enemy.animate_death()
                    self.game.enemies.remove(enemy)
                    if not self.game.muted:
                        self.game.sounds["kill"].play()
                else:
                    self.die()

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 6
                self.velocity[1] = -3
                self.air_time = 5
                self.jumps = 0
                if not self.game.muted:
                    self.game.sounds["jump"].play()
                return True

            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -6
                self.velocity[1] = -3
                self.air_time = 5
                self.jumps = 0
                self.flip = not self.flip
                if not self.game.muted:
                    self.game.sounds["jump"].play()
                return True

        elif self.jumps:
            self.velocity[1] = -4
            self.jumps -= 1
            self.air_time = 5
            if not self.game.muted:
                self.game.sounds["jump"].play()
            return True


class RunningEnemy(PhysicsEntity):
    def __init__(self, game, e_type, pos, size, animation_offset=(0, 0), speed=1):
        super().__init__(game, e_type, pos, size, animation_offset)
        self.flip = True
        self.moving = 0
        self.speed = speed

    def update(self, tilemap: Tilemap, movement=(0, 0)):
        if self.moving > 0:
            self.moving = max(0, self.moving - 1)
            if (
                self.collisions["left"]
                or self.collisions["right"]
                or (
                    self.velocity[1] == 0
                    and not tilemap.solid_check(
                        (
                            self.rect().centerx + (-1 if self.flip else 1) * (self.size[0] // 2 + tilemap.tile_size // 2),
                            self.rect().bottom + tilemap.tile_size // 2,
                        )
                    )
                )
            ):
                self.flip = not self.flip
            else:
                movement = (movement[0] + (-self.speed if self.flip else self.speed), movement[1])
        elif random.random() < 0.01:
            self.moving = random.randint(120, 480)
            self.set_action("run")
        else:
            self.set_action("idle")

        super().update(tilemap, movement)


class Pig(RunningEnemy):
    def __init__(self, game, pos):
        super().__init__(game, "pig", pos, size=(16, 16), animation_offset=(-8, -14), speed=1)

    def update(self, tilemap: Tilemap, movement=(0, 0)):
        dx = self.game.player.pos[0] - self.pos[0]
        dy = self.game.player.pos[1] - self.pos[1]
        tiles = 6
        do_rush = False
        if abs(dy) < self.size[1] and abs(dx) < tiles * self.size[0] and ((dx > 0 and not self.flip) or (dx < 0 and self.flip)):
            do_rush = True
            for i in range(tiles):
                if tilemap.solid_check((self.pos[0] + i * (dx / tiles), self.pos[1])):
                    do_rush = False

        if do_rush:
            self.moving += 1
            self.speed = 2
            self.set_action("run")
        else:
            self.speed = 1
        super().update(tilemap, movement)


class Snail(RunningEnemy):
    def __init__(self, game, pos):
        super().__init__(game, "snail", pos, size=(16, 16), animation_offset=(-8, -8), speed=0.125)
        self.moving = 1
        self.set_action("run")
        self.shooting = 0

    def update(self, tilemap, movement=(0, 0)):
        dx = self.game.player.pos[0] - self.pos[0]
        dy = self.game.player.pos[1] - self.pos[1]

        if self.shooting:
            self.shooting = max(0, self.shooting - 1)
            if self.shooting == 200:
                if dx > 0 and not self.flip:
                    self.game.projectiles.append(Projectile(self.game, "slime", (self.rect().centerx + 20, self.rect().centery), (2, 0), 480))
                elif dx < 0 and self.flip:
                    self.game.projectiles.append(Projectile(self.game, "slime", (self.rect().centerx - 8, self.rect().centery), (-2, 0), 480))
            if self.shooting <= 0:
                self.moving = 1
                self.set_action("run")
        else:
            tiles = 12
            do_shoot = False
            if abs(dy) < self.size[1] and abs(dx) < tiles * self.size[0] and ((dx > 0 and not self.flip) or (dx < 0 and self.flip)):
                do_shoot = True
                for i in range(tiles):
                    if tilemap.solid_check((self.pos[0] + i * (dx / tiles), self.pos[1])):
                        do_shoot = False
                if do_shoot:
                    self.shooting = 240
                    self.set_action("idle")
                    self.moving = 0
        super().update(tilemap, movement=movement)


class Bee(PhysicsEntity):
    def __init__(self, game, pos):
        super().__init__(game, "bee", pos, size=(16, 16), animation_offset=(-8, -8))
        self.set_action("idle")
        self.attacking = 0
        self.projectiles = []

    def update(self, tilemap, movement=(0, 0)):
        # keep bee in air
        self.velocity[1] = 0

        if self.attacking:
            self.attacking = max(0, self.attacking - 1)
            if self.attacking == 120 + 36:
                self.game.projectiles.append(Projectile(self.game, "sting", (self.rect().centerx, self.rect().bottom), (0, 2), 360))
            if self.attacking == 120 + 0:
                self.set_action("idle")
        else:
            if random.random() < 0.01:
                self.attacking = 120 + 64
                self.set_action("attack")

        super().update(tilemap, movement)


class Chicken(RunningEnemy):
    def __init__(self, game, pos):
        super().__init__(game, "chicken", pos, size=(16, 16), animation_offset=(-8, -16), speed=4)

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        if self.moving:
            self.game.particles.add(Dust((self.rect().right if self.flip else self.rect().left, self.rect().bottom)))


class Bunny(RunningEnemy):
    def __init__(self, game, pos):
        super().__init__(game, "bunny", pos, size=(16, 16), animation_offset=(-8, -26), speed=1)

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)

        if (
            self.moving
            and self.collisions["down"]
            and random.random() < 0.1
            and tilemap.solid_check((self.rect().centerx + (-2.5 if self.flip else 2.5) * tilemap.tile_size, self.rect().bottom + tilemap.tile_size // 2))
        ):
            self.velocity[1] = -2
