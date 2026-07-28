import numpy as np
from settings import (
    MAP_EMPTY, MAP_WALL_STONE, MAP_WALL_BRICK, MAP_WALL_METAL,
    MAP_WALL_WOOD, MAP_WALL_MOSSY, MAP_WALL_BLUE, MAP_DOOR,
    MAP_DOOR_RED, MAP_DOOR_BLUE, MAP_EXIT,
)


class GameMap:
    def __init__(self, layout, player_start, enemies=None, items=None, name="Untitled"):
        self.layout = np.array(layout, dtype=np.int32)
        self.height, self.width = self.layout.shape
        self.player_start = player_start
        self.enemies = enemies or []
        self.items = items or []
        self.name = name
        self.doors = {}
        self._init_doors()

    def _init_doors(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.layout[y, x]
                if tile in (MAP_DOOR, MAP_DOOR_RED, MAP_DOOR_BLUE):
                    self.doors[(x, y)] = {
                        'state': 'closed',
                        'offset': 0.0,
                        'timer': 0,
                        'open': False,
                        'tile': tile,
                    }

    def is_wall(self, x, y):
        ix, iy = int(x), int(y)
        if 0 <= ix < self.width and 0 <= iy < self.height:
            tile = self.layout[iy, ix]
            if tile == MAP_EMPTY:
                return False
            if (ix, iy) in self.doors:
                door = self.doors[(ix, iy)]
                if door['open'] and door['offset'] >= 0.9:
                    return False
            return tile in {MAP_WALL_STONE, MAP_WALL_BRICK, MAP_WALL_METAL,
                           MAP_WALL_WOOD, MAP_WALL_MOSSY, MAP_WALL_BLUE,
                           MAP_DOOR, MAP_DOOR_RED, MAP_DOOR_BLUE, MAP_EXIT}
        return True

    def get_tile(self, x, y):
        ix, iy = int(x), int(y)
        if 0 <= ix < self.width and 0 <= iy < self.height:
            return self.layout[iy, ix]
        return MAP_WALL_STONE

    def is_exit(self, x, y):
        return self.get_tile(x, y) == MAP_EXIT

    def try_open_door(self, x, y, keys):
        ix, iy = int(x), int(y)
        if (ix, iy) in self.doors:
            door = self.doors[(ix, iy)]
            if door['open']:
                return False
            tile = door['tile']
            if tile == MAP_DOOR_RED and 'red' not in keys:
                return False
            if tile == MAP_DOOR_BLUE and 'blue' not in keys:
                return False
            door['open'] = True
            return True
        return False

    def update_doors(self, dt):
        for pos, door in self.doors.items():
            if door['open']:
                door['offset'] = min(1.0, door['offset'] + dt * 2.0)
            elif door['offset'] > 0 and not door['open']:
                door['offset'] = max(0.0, door['offset'] - dt * 2.0)

    def is_walkable(self, x, y, size=0.0):
        for dy in (-size, 0, size):
            for dx in (-size, 0, size):
                if self.is_wall(x + dx, y + dy):
                    return False
        return True


# ── Level definitions ────────────────────────────────────────────

W = MAP_WALL_STONE
B = MAP_WALL_BRICK
M = MAP_WALL_METAL
D = MAP_DOOR
DR = MAP_DOOR_RED
DB = MAP_DOOR_BLUE
E = MAP_EXIT
_ = MAP_EMPTY

LEVEL1_LAYOUT = [
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, _, _, _, W, _, _, _, _, _, _, _, W, _, _, _, _, _, _, _, _, _, _, W],
    [W, _, _, _, W, _, _, _, _, _, _, _, W, _, _, _, _, _, _, _, _, _, _, W],
    [W, _, _, _, W, _, _, _, _, _, _, _, D, _, _, _, _, _, _, _, _, _, _, W],
    [W, W, D, W, W, _, _, _, _, _, _, _, W, _, _, _, B, B, B, B, B, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, W, _, _, _, B, _, _, _, B, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, W, W, D, W, B, _, _, _, B, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, B, _, _, _, B, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, _, _, _, B, _, _, W],
    [W, W, W, D, W, W, _, _, _, _, _, _, _, _, _, _, B, _, _, _, B, _, _, W],
    [W, _, _, _, _, W, _, _, _, _, _, _, W, _, _, _, B, B, D, B, B, _, _, W],
    [W, _, _, _, _, W, _, _, _, _, _, _, W, _, _, _, _, _, _, _, _, _, _, W],
    [W, _, _, _, _, W, W, W, D, W, W, W, W, _, _, _, _, _, _, _, _, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M, M, M, M, M, M, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M, _, _, _, _, M, _, _, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, M, _, _, _, _, M, W, W, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M, _, _, _, _, M, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, _, _, _, _, E, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M, _, _, _, _, M, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M, M, M, M, M, M, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, W],
    [W, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
]

LEVEL1 = GameMap(
    LEVEL1_LAYOUT,
    player_start=(2.0, 2.0, 0.0),
    enemies=[
        ('imp', 6.5, 6.5),
        ('imp', 10.5, 3.5),
        ('demon', 15.5, 7.5),
        ('imp', 7.5, 13.5),
        ('imp', 3.5, 18.5),
        ('demon', 10.5, 18.5),
        ('imp', 14.5, 19.5),
        ('baron', 19.5, 18.5),
    ],
    items=[
        ('health_small', 4.5, 1.5),
        ('ammo_bullets', 1.5, 5.5),
        ('weapon_shotgun', 7.5, 5.5),
        ('health_large', 15.5, 1.5),
        ('ammo_shells', 20.5, 5.5),
        ('key_red', 1.5, 14.5),
        ('ammo_bullets', 5.5, 18.5),
        ('health_small', 12.5, 17.5),
        ('armor_small', 18.5, 1.5),
    ],
    name="E1M1: Tech Base",
)

LEVEL2_LAYOUT = [
    [B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B],
    [B, _, _, _, _, _, _, _, _, _, B, _, _, _, _, _, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, D, _, _, _, _, _, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, B, _, _, _, _, _, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, B, B, B, D, B, B, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, B, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, B, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, B, B, B, B, B, B, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, B],
    [B, B, B, D, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, B],
    [B, _, _, _, _, B, _, _, _, _, _, _, _, _, _, _, _, _, _, B],
    [B, _, _, _, _, D, _, _, _, _, _, _, _, _, _, _, _, _, _, B],
    [B, _, _, _, _, B, _, _, _, _, _, _, _, _, _, _, _, _, _, B],
    [B, _, _, _, _, B, B, B, D, B, B, B, B, _, _, _, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, _, _, B, _, _, _, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, _, _, D, _, _, _, _, _, _, B],
    [B, _, _, _, _, _, _, _, _, _, _, _, B, _, _, _, _, _, E, B],
    [B, _, _, _, _, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B],
    [B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B],
]

LEVEL2 = GameMap(
    LEVEL2_LAYOUT,
    player_start=(1.5, 1.5, 0.0),
    enemies=[
        ('imp', 5.5, 2.5),
        ('imp', 8.5, 6.5),
        ('demon', 3.5, 11.5),
        ('demon', 8.5, 11.5),
        ('imp', 15.5, 2.5),
        ('demon', 17.5, 5.5),
        ('imp', 14.5, 8.5),
        ('baron', 10.5, 16.5),
        ('imp', 17.5, 12.5),
        ('demon', 4.5, 16.5),
    ],
    items=[
        ('health_small', 3.5, 1.5),
        ('ammo_bullets', 6.5, 3.5),
        ('weapon_chaingun', 9.5, 1.5),
        ('ammo_shells', 1.5, 8.5),
        ('key_blue', 2.5, 12.5),
        ('health_large', 15.5, 6.5),
        ('armor_large', 8.5, 9.5),
        ('ammo_bullets', 14.5, 16.5),
        ('health_small', 17.5, 11.5),
    ],
    name="E1M2: Hellish Outpost",
)

LEVEL3_LAYOUT = [
    [M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, W, W, W, D, W, W, W, _, _, _, _, M],
    [M, _, _, _, W, _, _, _, _, _, W, _, _, _, _, M],
    [M, _, _, _, W, _, _, _, _, _, D, _, _, _, _, M],
    [M, _, _, _, W, _, _, _, _, _, W, _, _, _, _, M],
    [M, _, _, _, W, W, D, W, W, W, W, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, E, M],
    [M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M],
]

LEVEL3 = GameMap(
    LEVEL3_LAYOUT,
    player_start=(1.5, 1.5, 0.0),
    enemies=[
        ('demon', 7.5, 6.5),
        ('demon', 5.5, 2.5),
        ('baron', 7.5, 1.5),
        ('imp', 2.5, 8.5),
        ('imp', 12.5, 9.5),
        ('baron', 12.5, 1.5),
        ('demon', 4.5, 11.5),
        ('imp', 10.5, 11.5),
        ('demon', 13.5, 8.5),
    ],
    items=[
        ('health_large', 2.5, 12.5),
        ('ammo_shells', 1.5, 3.5),
        ('weapon_chainsaw', 14.5, 1.5),
        ('armor_large', 13.5, 12.5),
        ('ammo_bullets', 5.5, 10.5),
        ('health_small', 11.5, 5.5),
        ('ammo_shells', 8.5, 9.5),
        ('key_red', 2.5, 6.5),
    ],
    name="E1M3: Fortress of Doom",
)

LEVEL4_LAYOUT = [
    [M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M],
    [M, _, _, _, _, M, _, _, _, _, _, _, _, _, _, M, _, _, _, M],
    [M, _, _, _, _, D, _, _, _, _, _, _, _, _, _, D, _, _, _, M],
    [M, _, _, _, _, M, _, _, _, _, _, _, _, _, _, M, _, _, _, M],
    [M, _, _, _, _, M, M, M, D, M, M, M, M, M, M, M, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, M, M, D, M, M, _, _, _, _, _, _, _, _, _, M, M, D, M, M],
    [M, _, _, _, _, M, _, _, _, _, _, _, _, _, _, M, _, _, _, M],
    [M, _, _, _, _, M, _, _, _, _, _, _, _, _, _, M, _, _, _, M],
    [M, _, _, _, _, M, _, _, _, _, _, _, _, _, _, M, _, _, _, M],
    [M, _, _, _, _, M, M, M, M, D, M, M, M, M, M, M, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, E, M],
    [M, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, M],
    [M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M, M],
]

LEVEL4 = GameMap(
    LEVEL4_LAYOUT,
    player_start=(2.0, 2.0, 0.0),
    enemies=[
        ('imp', 8.0, 2.0),
        ('imp', 12.0, 2.0),
        ('demon', 8.0, 8.0),
        ('demon', 12.0, 8.0),
        ('baron', 10.0, 11.0),
        ('imp', 2.0, 8.0),
        ('imp', 17.0, 8.0),
        ('demon', 5.0, 15.0),
        ('demon', 14.0, 15.0),
        ('baron', 10.0, 17.0),
    ],
    items=[
        ('health_large', 2.0, 5.0),
        ('ammo_shells', 17.0, 5.0),
        ('key_red', 8.0, 2.0),
        ('key_blue', 12.0, 2.0),
        ('weapon_shotgun', 2.0, 11.0),
        ('weapon_chaingun', 17.0, 11.0),
        ('ammo_bullets', 5.0, 15.0),
        ('ammo_bullets', 14.0, 15.0),
        ('health_large', 10.0, 15.0),
        ('armor_large', 10.0, 17.0),
    ],
    name="E1M4: The Final Challenge",
)

ALL_LEVELS = [LEVEL1, LEVEL2, LEVEL3, LEVEL4]
