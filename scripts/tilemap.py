import json
import math

import pygame

AUTOTILE_MAP = {
    # tiles are created in a 4x4 grid;
    # numbering is done from 00 (top left) to 15 (bottom right)
    #
    # .---.---.---.---.
    # | a | a | a | c |  a = area
    # +---+---+---+---+
    # | a | a | a | c |  c = single column
    # +---+---+---+---+
    # | a | a | a | c |  r = single row
    # +---+---+---+---+
    # | r | r | r | s |  s = single block
    # `---^---^---^---´
    #
    # areas
    tuple(sorted([(1, 0), (0, 1)])): 0,  # top left
    tuple(sorted([(1, 0), (-1, 0), (0, 1)])): 1,  # top center
    tuple(sorted([(-1, 0), (0, 1)])): 2,  # top right
    tuple(sorted([(1, 0), (0, 1), (0, -1)])): 4,  ## middle left
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 5,  ## middle
    tuple(sorted([(-1, 0), (0, 1), (0, -1)])): 6,  ## middle right
    tuple(sorted([(1, 0), (0, -1)])): 8,  # # bottom left
    tuple(sorted([(1, 0), (-1, 0), (0, -1)])): 9,  # bottom middle
    tuple(sorted([(-1, 0), (0, -1)])): 10,  # bottom right
    # single row
    tuple(sorted([(1, 0)])): 12,  # left
    tuple(sorted([(1, 0), (-1, 0)])): 13,  # center
    tuple(sorted([(-1, 0)])): 14,  # right
    # single col
    tuple(sorted([(0, 1)])): 3,  # top
    tuple(sorted([(0, 1), (0, -1)])): 7,  # middle
    tuple(sorted([(0, -1)])): 11,  # bottom
    # single block
    tuple(): 15,
}

NEIGHBOR_OFFSETS = [
    (-1, 0),
    (-1, -1),
    (0, -1),
    (-1, -1),
    (1, 0),
    (0, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]


class Tilemap:
    def __init__(self, assets={}):
        self.assets = assets
        self.background = 0
        self.tile_size = 16
        self.tiles = {}
        self.offgrid = []

    def load(self, path):
        f = open(path, "r")
        data = json.load(f)
        f.close()
        self.tile_size = data["tile_size"]
        self.tiles = data["tiles"]
        self.offgrid = data["offgrid"]
        self.background = data["background"]

    def save(self, path):
        f = open(path, "w")
        json.dump({"background": self.background, "tile_size": self.tile_size, "tiles": self.tiles, "offgrid": self.offgrid}, f)
        f.close()

    def add(self, pos, t_type, variant, ongrid=True):
        if t_type == "backgrounds":
            self.background = variant
        elif ongrid:
            pos = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
            self.tiles[str(pos[0]) + ";" + str(pos[1])] = {"type": t_type, "variant": variant, "pos": pos}
        else:
            self.offgrid.append({"type": t_type, "variant": variant, "pos": pos})

    def remove(self, pos=(0, 0), offset=(0, 0), ongrid=True):
        if ongrid:
            tile_loc = str(int(pos[0] // self.tile_size)) + ";" + str(int(pos[1] // self.tile_size))
            if tile_loc in self.tiles:
                del self.tiles[tile_loc]
        else:
            for tile in self.offgrid.copy():
                tile_img = self.assets[tile["type"]][tile["variant"]]
                tile_rect = pygame.Rect(
                    tile["pos"][0],
                    tile["pos"][1],
                    tile_img.get_width(),
                    tile_img.get_height(),
                )
                if tile_rect.collidepoint(pos):
                    self.offgrid.remove(tile)

    def autotile(self):
        for loc in self.tiles:
            tile = self.tiles[loc]
            if str(tile["type"]).startswith("tiles/"):
                neighbors = set()
                for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    check_loc = str(tile["pos"][0] + shift[0]) + ";" + str(tile["pos"][1] + shift[1])
                    if check_loc in self.tiles:
                        if self.tiles[check_loc]["type"] == tile["type"]:
                            neighbors.add(shift)
                neighbors = tuple(sorted(neighbors))
                if neighbors in AUTOTILE_MAP:
                    tile["variant"] = AUTOTILE_MAP[neighbors]

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ";" + str(tile_loc[1] + offset[1])
            if check_loc in self.tiles:
                tiles.append(self.tiles[check_loc])
        return tiles

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile["type"].startswith("tiles/"):
                rects.append(
                    pygame.Rect(
                        tile["pos"][0] * self.tile_size,
                        tile["pos"][1] * self.tile_size,
                        self.tile_size,
                        self.tile_size,
                    )
                )
        return rects

    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ";" + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tiles:
            if self.tiles[tile_loc]["type"].startswith("tiles"):
                return self.tiles[tile_loc]

    def find_surface_tiles(self):
        pos = []
        for tile_loc in self.tiles:
            tile = self.tiles[tile_loc]
            if tile["type"].startswith("tiles") and tile["variant"] in (0, 1, 2, 3, 12, 13, 14, 15):
                above = (tile["pos"][0], tile["pos"][1] - 1)
                if not self.solid_check((above[0] * self.tile_size, above[1] * self.tile_size)):
                    pos.append(above)
        return pos

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid.remove(tile)

        for loc in self.tiles.copy():
            tile = self.tiles[loc]
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                matches[-1]["pos"] = matches[-1]["pos"].copy()
                matches[-1]["pos"][0] *= self.tile_size
                matches[-1]["pos"][1] *= self.tile_size
                if not keep:
                    del self.tiles[loc]

        return matches

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        for tile in self.offgrid:
            surface.blit(
                self.assets[tile["type"]][tile["variant"]],
                (tile["pos"][0] - offset[0], tile["pos"][1] - offset[1]),
            )

        # only render visible ongrid tiles
        for x in range(
            offset[0] // self.tile_size,
            (offset[0] + surface.get_width()) // self.tile_size + 1,
        ):
            for y in range(
                offset[1] // self.tile_size,
                (offset[1] + surface.get_height()) // self.tile_size + 1,
            ):
                loc = str(x) + ";" + str(y)
                if loc in self.tiles:
                    tile = self.tiles[loc]
                    surface.blit(
                        self.assets[tile["type"]][tile["variant"]],
                        (
                            tile["pos"][0] * self.tile_size - offset[0],
                            tile["pos"][1] * self.tile_size - offset[1],
                        ),
                    )
