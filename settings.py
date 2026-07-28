import math

# ── Display ──────────────────────────────────────────────────────
INTERNAL_WIDTH = 320
INTERNAL_HEIGHT = 200
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
FPS = 60
TITLE = "DOOM Python"

# ── Raycasting ───────────────────────────────────────────────────
FOV = math.pi / 3          # 60 degrees
HALF_FOV = FOV / 2
NUM_RAYS = INTERNAL_WIDTH
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20
SCALE = SCREEN_WIDTH // NUM_RAYS
DELTA_TIME = 1 / FPS

# ── Player ───────────────────────────────────────────────────────
PLAYER_SPEED = 3.0
PLAYER_ROT_SPEED = 2.5
PLAYER_SIZE = 0.3
MAX_HEALTH = 100
MAX_ARMOR = 100

# ── Map tile codes ───────────────────────────────────────────────
MAP_EMPTY = 0
MAP_WALL_STONE = 1
MAP_WALL_BRICK = 2
MAP_WALL_METAL = 3
MAP_WALL_WOOD = 4
MAP_WALL_MOSSY = 5
MAP_WALL_BLUE = 6
MAP_DOOR = 7
MAP_DOOR_RED = 8
MAP_DOOR_BLUE = 9
MAP_EXIT = 10

WALL_TILES = {
    MAP_WALL_STONE, MAP_WALL_BRICK, MAP_WALL_METAL,
    MAP_WALL_WOOD, MAP_WALL_MOSSY, MAP_WALL_BLUE,
}

TILE_SIZE = 1  # each cell is 1x1 unit

# ── Sprite / texture size ────────────────────────────────────────
TEXTURE_SIZE = 64

# ── Colors ───────────────────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (200, 200, 0)
CYAN = (0, 200, 200)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (120, 120, 120)
HUD_BG = (80, 0, 0)
HUD_RED = (180, 0, 0)
HUD_YELLOW = (200, 180, 0)

# ── Weapon definitions ──────────────────────────────────────────
WEAPONS = {
    'chainsaw': {
        'damage': 15, 'fire_rate': 0.4, 'ammo_type': None,
        'ammo_cost': 0, 'spread': 0, 'range': 1.5, 'hitscan': False,
        'projectiles': 1, 'pickup': 'weapon_chainsaw',
    },
    'pistol': {
        'damage': 20, 'fire_rate': 0.5, 'ammo_type': 'bullets',
        'ammo_cost': 1, 'spread': 0.02, 'range': 20, 'hitscan': True,
        'projectiles': 1, 'pickup': None,
    },
    'shotgun': {
        'damage': 12, 'fire_rate': 0.9, 'ammo_type': 'shells',
        'ammo_cost': 1, 'spread': 0.08, 'range': 10, 'hitscan': True,
        'projectiles': 7, 'pickup': 'weapon_shotgun',
    },
    'chaingun': {
        'damage': 12, 'fire_rate': 0.12, 'ammo_type': 'bullets',
        'ammo_cost': 1, 'spread': 0.06, 'range': 15, 'hitscan': True,
        'projectiles': 1, 'pickup': 'weapon_chaingun',
    },
}

# ── Enemy definitions ───────────────────────────────────────────
ENEMY_TYPES = {
    'imp': {
        'health': 40, 'speed': 1.5, 'damage': 8, 'attack_range': 8,
        'melee_range': 1.2, 'alert_range': 10, 'size': 0.4,
        'melee': False, 'score': 100,
    },
    'demon': {
        'health': 80, 'speed': 2.5, 'damage': 15, 'attack_range': 1.5,
        'melee_range': 1.5, 'alert_range': 8, 'size': 0.5,
        'melee': True, 'score': 200,
    },
    'baron': {
        'health': 200, 'speed': 1.2, 'damage': 20, 'attack_range': 10,
        'melee_range': 1.8, 'alert_range': 12, 'size': 0.6,
        'melee': False, 'score': 500,
    },
}

# ── Item definitions ────────────────────────────────────────────
ITEM_TYPES = {
    'health_small': {'type': 'health', 'value': 10, 'score': 0},
    'health_large': {'type': 'health', 'value': 25, 'score': 0},
    'ammo_bullets': {'type': 'ammo', 'ammo_type': 'bullets', 'value': 20, 'score': 0},
    'ammo_shells': {'type': 'ammo', 'ammo_type': 'shells', 'value': 8, 'score': 0},
    'armor_small': {'type': 'armor', 'value': 25, 'score': 0},
    'armor_large': {'type': 'armor', 'value': 50, 'score': 0},
    'key_red': {'type': 'key', 'key': 'red', 'score': 0},
    'key_blue': {'type': 'key', 'key': 'blue', 'score': 0},
    'weapon_shotgun': {'type': 'weapon', 'weapon': 'shotgun', 'score': 100},
    'weapon_chaingun': {'type': 'weapon', 'weapon': 'chaingun', 'score': 100},
    'weapon_chainsaw': {'type': 'weapon', 'weapon': 'chainsaw', 'score': 100},
}
