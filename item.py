import math
import numpy as np
from settings import ITEM_TYPES, TEXTURE_SIZE


class Item:
    def __init__(self, item_type, x, y):
        props = ITEM_TYPES[item_type]
        self.item_type = item_type
        self.item_class = props['type']
        self.x = x
        self.y = y
        self.value = props.get('value', 0)
        self.ammo_type = props.get('ammo_type')
        self.key_color = props.get('key')
        self.weapon_name = props.get('weapon')
        self.score = props.get('score', 0)
        self.alive = True
        self.bob_timer = np.random.random() * math.pi * 2
        self.distance_to_player = 0
        self._generate_texture()

    def _generate_texture(self):
        colors = {
            'health_small': (200, 40, 40),
            'health_large': (255, 60, 60),
            'ammo_bullets': (200, 180, 40),
            'ammo_shells': (200, 120, 40),
            'armor_small': (40, 120, 200),
            'armor_large': (60, 150, 255),
            'key_red': (220, 30, 30),
            'key_blue': (30, 30, 220),
            'weapon_shotgun': (180, 160, 140),
            'weapon_chaingun': (140, 140, 150),
            'weapon_chainsaw': (160, 160, 160),
        }
        color = colors.get(self.item_type, (200, 200, 200))

        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 4), dtype=np.uint8)
        cx, cy = TEXTURE_SIZE // 2, TEXTURE_SIZE // 2

        if self.item_class == 'key':
            for y in range(TEXTURE_SIZE):
                for x in range(TEXTURE_SIZE):
                    dx, dy = x - cx, y - cy
                    r = TEXTURE_SIZE // 3
                    if abs(dx) < r and abs(dy) < r:
                        inner = abs(dx) < r // 2 and abs(dy) < r // 2
                        if inner and (abs(dx) > r // 3 or abs(dy) > r // 3):
                            continue
                        tex[y, x] = [color[0], color[1], color[2], 255]
        elif self.item_class == 'health' or self.item_class == 'armor':
            for y in range(TEXTURE_SIZE):
                for x in range(TEXTURE_SIZE):
                    dx, dy = x - cx, y - cy
                    r = TEXTURE_SIZE // 3.5
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist < r:
                        tex[y, x] = [color[0], color[1], color[2], 255]
                    cross_r = r * 0.2
                    if abs(dx) < cross_r and abs(dy) < r * 0.7:
                        tex[y, x] = [255, 255, 255, 255]
                    if abs(dy) < cross_r and abs(dx) < r * 0.7:
                        tex[y, x] = [255, 255, 255, 255]
        else:
            for y in range(TEXTURE_SIZE):
                for x in range(TEXTURE_SIZE):
                    dx, dy = x - cx, y - cy
                    r = TEXTURE_SIZE // 3
                    if abs(dx) < r and abs(dy) < r * 0.6:
                        tex[y, x] = [color[0], color[1], color[2], 255]

        self.texture = tex

    def get_texture(self):
        return self.texture

    def update(self, dt):
        self.bob_timer += dt * 3

    def is_near_player(self, player, pickup_dist=0.7):
        dx = self.x - player.x
        dy = self.y - player.y
        return math.sqrt(dx * dx + dy * dy) < pickup_dist

    def apply(self, player):
        if not self.alive:
            return False

        if self.item_class == 'health':
            if player.health >= 100:
                return False
            player.heal(self.value)
        elif self.item_class == 'ammo':
            if player.ammo.get(self.ammo_type, 0) >= 200:
                return False
            player.add_ammo(self.ammo_type, self.value)
        elif self.item_class == 'armor':
            if player.armor >= 100:
                return False
            player.add_armor(self.value)
        elif self.item_class == 'key':
            player.add_key(self.key_color)
        elif self.item_class == 'weapon':
            player.add_weapon(self.weapon_name)
            if self.ammo_type is None:
                if self.weapon_name == 'shotgun':
                    player.add_ammo('shells', 8)
                elif self.weapon_name == 'chaingun':
                    player.add_ammo('bullets', 40)

        player.score += self.score
        self.alive = False
        return True
