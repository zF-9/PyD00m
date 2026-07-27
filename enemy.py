import math
import numpy as np
from settings import ENEMY_TYPES, TEXTURE_SIZE
from pathfinding import bfs_path


class Enemy:
    def __init__(self, enemy_type, x, y):
        props = ENEMY_TYPES[enemy_type]
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        self.health = props['health']
        self.max_health = props['health']
        self.speed = props['speed']
        self.damage = props['damage']
        self.attack_range = props['attack_range']
        self.melee_range = props['melee_range']
        self.alert_range = props['alert_range']
        self.size = props['size']
        self.is_melee = props['melee']
        self.score = props['score']
        self.alive = True
        self.state = 'idle'
        self.path = []
        self.path_timer = 0
        self.attack_cooldown = 0
        self.hurt_timer = 0
        self.death_timer = 1.5
        self.distance_to_player = 0
        self.state_timer = 0
        self.alerted = False
        self.walk_frame = 0
        self.walk_timer = 0
        self.death_frame = 0
        self.death_flash = 0
        self.attack_frame = 0
        self._generate_textures()

    def _generate_textures(self):
        self.textures = {}
        S = TEXTURE_SIZE

        if self.enemy_type == 'imp':
            self._generate_imp(S)
        elif self.enemy_type == 'demon':
            self._generate_demon(S)
        elif self.enemy_type == 'baron':
            self._generate_baron(S)
        else:
            self._generate_generic(S)

    def _draw_oval(self, tex, cx, cy, rx, ry, color):
        yy, xx = np.ogrid[:tex.shape[0], :tex.shape[1]]
        mask = ((xx - cx) / max(rx, 1)) ** 2 + ((yy - cy) / max(ry, 1)) ** 2 <= 1.0
        tex[mask, 0] = np.clip(color[0], 0, 255)
        tex[mask, 1] = np.clip(color[1], 0, 255)
        tex[mask, 2] = np.clip(color[2], 0, 255)
        tex[mask, 3] = 255

    def _draw_eyes(self, tex, cx, cy, spread, size, color=(255, 0, 0)):
        for ex in [cx - spread, cx + spread]:
            yy, xx = np.ogrid[:tex.shape[0], :tex.shape[1]]
            mask = ((xx - ex) ** 2 + (yy - cy) ** 2) <= size ** 2
            tex[mask, 0] = color[0]
            tex[mask, 1] = color[1]
            tex[mask, 2] = color[2]
            tex[mask, 3] = 255

    def _draw_horns(self, tex, cx, cy, color, size=6):
        S = tex.shape[0]
        for side in [-1, 1]:
            hx = cx + side * 10
            for dy in range(-size, 0):
                for dx in range(-1, 2):
                    px, py = hx + dx + side * (-dy // 3), cy + dy
                    if 0 <= px < S and 0 <= py < S:
                        tex[py, px] = [color[0], color[1], color[2], 255]

    def _draw_mouth(self, tex, cx, cy, width, color=(40, 0, 0)):
        S = tex.shape[0]
        for dx in range(-width, width + 1):
            px, py = cx + dx, cy
            if 0 <= px < S and 0 <= py < S:
                tex[py, px] = [color[0], color[1], color[2], 255]
            if 0 <= px < S and 0 <= py + 1 < S:
                tex[py + 1, px] = [color[0], color[1], color[2], 255]

    def _draw_arms(self, tex, cx, cy, body_rx, color, spread=3):
        S = tex.shape[0]
        for side in [-1, 1]:
            ax = cx + side * (body_rx + spread)
            for dy in range(-4, 8):
                for dx in range(-2, 3):
                    px, py = ax + dx, cy + dy
                    if 0 <= px < S and 0 <= py < S:
                        tex[py, px] = [color[0], color[1], color[2], 255]

    def _draw_legs(self, tex, cx, bottom_y, color, spread=5, length=8):
        S = tex.shape[0]
        for side in [-1, 1]:
            lx = cx + side * spread
            for dy in range(length):
                for dx in range(-2, 3):
                    px, py = lx + dx, bottom_y + dy
                    if 0 <= px < S and 0 <= py < S:
                        tex[py, px] = [color[0], color[1], color[2], 255]

    def _generate_imp(self, S):
        base = (170, 90, 50)
        dark = (130, 60, 30)
        belly = (200, 140, 80)
        horn_color = (100, 50, 20)
        eye_color = (255, 50, 0)

        walk_offsets = {'idle': 0, 'walk1': -2, 'walk2': 2, 'attack': 0, 'hurt': 0, 'dead': 0}

        for state in ['idle', 'walk1', 'walk2', 'attack', 'hurt', 'dead']:
            tex = np.zeros((S, S, 4), dtype=np.uint8)
            off = walk_offsets[state]

            if state == 'dead':
                self._draw_oval(tex, S // 2, S // 2 + 8, 14, 8, (dark[0] // 2, dark[1] // 2, dark[2] // 2))
            elif state == 'hurt':
                self._draw_oval(tex, S // 2, S // 2, 10, 13, (255, 180, 180))
                self._draw_eyes(tex, S // 2, S // 2 - 4, 4, 2, (255, 255, 255))
            else:
                body_cy = S // 2 + off
                head_cy = body_cy - 14

                self._draw_oval(tex, S // 2, body_cy + 4, 11, 14, base)
                self._draw_oval(tex, S // 2, body_cy + 2, 7, 8, belly)

                self._draw_oval(tex, S // 2, head_cy, 8, 7, (base[0] + 15, base[1] + 15, base[2] + 10))
                self._draw_eyes(tex, S // 2, head_cy - 1, 4, 2, eye_color)
                self._draw_mouth(tex, S // 2, head_cy + 4, 3, (80, 20, 10))

                self._draw_horns(tex, S // 2, head_cy - 5, horn_color, size=5)

                self._draw_arms(tex, S // 2, body_cy - 2, 11, dark, spread=2)
                self._draw_legs(tex, S // 2, body_cy + 16, dark, spread=4, length=7)

                if state == 'attack':
                    fire_cx = S // 2 + 14
                    fire_cy = body_cy - 4
                    for r in range(5, 0, -1):
                        alpha = int(255 * (r / 5))
                        yy, xx = np.ogrid[:S, :S]
                        mask = ((xx - fire_cx) ** 2 + (yy - fire_cy) ** 2) <= r ** 2
                        tex[mask, 0] = 255
                        tex[mask, 1] = min(255, 100 + alpha // 2)
                        tex[mask, 2] = 0
                        tex[mask, 3] = alpha

            self.textures[state] = tex

    def _generate_demon(self, S):
        base = (160, 30, 30)
        dark = (120, 20, 20)
        belly = (190, 60, 50)
        horn_color = (80, 10, 10)
        eye_color = (255, 200, 0)

        walk_offsets = {'idle': 0, 'walk1': -2, 'walk2': 2, 'attack': 0, 'hurt': 0, 'dead': 0}

        for state in ['idle', 'walk1', 'walk2', 'attack', 'hurt', 'dead']:
            tex = np.zeros((S, S, 4), dtype=np.uint8)
            off = walk_offsets[state]

            if state == 'dead':
                self._draw_oval(tex, S // 2, S // 2 + 10, 16, 8, (dark[0] // 2, dark[1] // 2, dark[2] // 2))
            elif state == 'hurt':
                self._draw_oval(tex, S // 2, S // 2, 13, 16, (255, 180, 180))
                self._draw_eyes(tex, S // 2, S // 2 - 5, 5, 3, (255, 255, 255))
            else:
                body_cy = S // 2 + off
                head_cy = body_cy - 16

                self._draw_oval(tex, S // 2, body_cy + 4, 14, 16, base)
                self._draw_oval(tex, S // 2, body_cy + 2, 9, 10, belly)

                self._draw_oval(tex, S // 2, head_cy, 10, 8, base)
                self._draw_eyes(tex, S // 2, head_cy - 2, 5, 3, eye_color)
                self._draw_mouth(tex, S // 2, head_cy + 5, 5, (60, 0, 0))

                for side in [-1, 1]:
                    tx = S // 2 + side * 10
                    for dy in range(-7, -2):
                        for dx in range(-2, 3):
                            px, py = tx + dx + side * (-dy // 4), dy + head_cy
                            if 0 <= px < S and 0 <= py < S:
                                tex[py, px] = [horn_color[0], horn_color[1], horn_color[2], 255]

                self._draw_arms(tex, S // 2, body_cy - 4, 14, dark, spread=3)

                leg_off = 3 if state == 'walk1' else -3 if state == 'walk2' else 0
                for side in [-1, 1]:
                    lx = S // 2 + side * 7 + leg_off * side
                    for dy in range(10):
                        for dx in range(-3, 4):
                            px, py = lx + dx, body_cy + 18 + dy
                            if 0 <= px < S and 0 <= py < S:
                                tex[py, px] = [dark[0], dark[1], dark[2], 255]

                if state == 'attack':
                    for side in [-1, 1]:
                        ax = S // 2 + side * 18
                        ay = body_cy - 6
                        self._draw_oval(tex, ax, ay, 5, 4, (200, 50, 50))

            self.textures[state] = tex

    def _generate_baron(self, S):
        base = (50, 150, 50)
        dark = (30, 100, 30)
        belly = (80, 180, 70)
        horn_color = (40, 40, 40)
        eye_color = (255, 0, 0)

        walk_offsets = {'idle': 0, 'walk1': -2, 'walk2': 2, 'attack': 0, 'hurt': 0, 'dead': 0}

        for state in ['idle', 'walk1', 'walk2', 'attack', 'hurt', 'dead']:
            tex = np.zeros((S, S, 4), dtype=np.uint8)
            off = walk_offsets[state]

            if state == 'dead':
                self._draw_oval(tex, S // 2, S // 2 + 10, 18, 10, (dark[0] // 2, dark[1] // 2, dark[2] // 2))
            elif state == 'hurt':
                self._draw_oval(tex, S // 2, S // 2, 15, 18, (200, 255, 200))
                self._draw_eyes(tex, S // 2, S // 2 - 6, 6, 3, (255, 255, 255))
            else:
                body_cy = S // 2 + off + 2
                head_cy = body_cy - 18

                self._draw_oval(tex, S // 2, body_cy + 4, 16, 18, base)
                self._draw_oval(tex, S // 2, body_cy + 2, 10, 11, belly)

                self._draw_oval(tex, S // 2, head_cy, 11, 9, base)
                self._draw_eyes(tex, S // 2, head_cy - 2, 6, 3, eye_color)
                self._draw_mouth(tex, S // 2, head_cy + 6, 6, (20, 40, 20))

                self._draw_horns(tex, S // 2, head_cy - 6, horn_color, size=8)

                self._draw_arms(tex, S // 2, body_cy - 4, 16, dark, spread=3)

                leg_off = 3 if state == 'walk1' else -3 if state == 'walk2' else 0
                for side in [-1, 1]:
                    lx = S // 2 + side * 8 + leg_off * side
                    for dy in range(12):
                        for dx in range(-3, 4):
                            px, py = lx + dx, body_cy + 20 + dy
                            if 0 <= px < S and 0 <= py < S:
                                tex[py, px] = [dark[0], dark[1], dark[2], 255]

                if state == 'attack':
                    for r in range(8, 0, -1):
                        yy, xx = np.ogrid[:S, :S]
                        mask = ((xx - S // 2) ** 2 + (yy - (body_cy - 20)) ** 2) <= r ** 2
                        brightness = int(255 * (r / 8))
                        tex[mask, 0] = 50
                        tex[mask, 1] = min(255, brightness)
                        tex[mask, 2] = 50
                        tex[mask, 3] = min(255, brightness)

            self.textures[state] = tex

    def _generate_generic(self, S):
        base = (150, 50, 50)
        for state in ['idle', 'walk1', 'walk2', 'attack', 'hurt', 'dead']:
            tex = np.zeros((S, S, 4), dtype=np.uint8)
            cx, cy = S // 2, S // 2
            if state == 'dead':
                self._draw_oval(tex, cx, cy + 8, 12, 7, (60, 20, 20))
            elif state == 'hurt':
                self._draw_oval(tex, cx, cy, 10, 13, (255, 180, 180))
            else:
                off = 2 if state == 'walk2' else -2 if state == 'walk1' else 0
                self._draw_oval(tex, cx, cy + off, 11, 14, base)
                self._draw_oval(tex, cx, cy + off - 8, 7, 6, (180, 80, 80))
                self._draw_eyes(tex, cx, cy + off - 9, 3, 2, (255, 0, 0))
                self._draw_arms(tex, cx, cy + off - 2, 11, (120, 40, 40))
                self._draw_legs(tex, cx, cy + off + 14, (120, 40, 40))
            self.textures[state] = tex

    def get_texture(self):
        if not self.alive:
            if self.death_flash > 0:
                tex = self.textures.get('hurt').copy()
                white_mask = (tex[:, :, 3] > 0)
                tex[white_mask, 0] = 255
                tex[white_mask, 1] = 255
                tex[white_mask, 2] = 255
                return tex
            return self.textures.get('dead')
        if self.hurt_timer > 0:
            return self.textures.get('hurt')
        if self.state == 'attack':
            return self.textures.get('attack')
        if self.state == 'chase':
            frame = 'walk1' if self.walk_frame == 0 else 'walk2'
            return self.textures.get(frame)
        return self.textures.get('idle')

    def can_see_player(self, px, py, game_map, max_dist=15):
        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > max_dist:
            return False

        steps = int(dist * 4)
        for i in range(steps):
            t = i / steps
            cx = self.x + dx * t
            cy = self.y + dy * t
            if game_map.is_wall(cx, cy):
                return False
        return True

    def update(self, dt, player, game_map):
        if not self.alive:
            self.death_timer -= dt
            if self.death_flash > 0:
                self.death_flash -= dt
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            return

        dist_to_player = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)

        if not self.alerted:
            if dist_to_player < self.alert_range and self.can_see_player(player.x, player.y, game_map):
                self.alerted = True
                self.state = 'chase'
                return 'alert'

        if self.state == 'idle':
            if self.alerted:
                self.state = 'chase'
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if dist_to_player <= self.melee_range and self.is_melee:
            self.state = 'attack'
            self.attack_frame += dt * 8
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 1.0
                return 'melee_attack'
        elif dist_to_player <= self.attack_range and not self.is_melee and self.can_see_player(player.x, player.y, game_map):
            self.state = 'attack'
            self.attack_frame += dt * 8
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 1.5
                return 'ranged_attack'
        else:
            self.state = 'chase'
            self.walk_timer += dt * 6
            if self.walk_timer >= 1.0:
                self.walk_timer -= 1.0
                self.walk_frame = 1 - self.walk_frame

            self.path_timer -= dt
            if self.path_timer <= 0 or not self.path:
                self.path = bfs_path(game_map, self.x, self.y, player.x, player.y)
                self.path_timer = 0.5

            if self.path:
                target = self.path[0]
                dx = target[0] - self.x
                dy = target[1] - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 0.3:
                    self.path.pop(0)
                else:
                    move_speed = self.speed * dt
                    new_x = self.x + (dx / dist) * move_speed
                    new_y = self.y + (dy / dist) * move_speed
                    if game_map.is_walkable(new_x, self.y, self.size):
                        self.x = new_x
                    if game_map.is_walkable(self.x, new_y, self.size):
                        self.y = new_y
            else:
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0.5:
                    move_speed = self.speed * dt
                    new_x = self.x + (dx / dist) * move_speed
                    new_y = self.y + (dy / dist) * move_speed
                    if game_map.is_walkable(new_x, self.y, self.size):
                        self.x = new_x
                    if game_map.is_walkable(self.x, new_y, self.size):
                        self.y = new_y

        return None

    def take_damage(self, amount):
        if not self.alive:
            return False
        self.health -= amount
        self.hurt_timer = 0.2
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.death_flash = 0.15
            return True
        return False
