import math
import pygame
from settings import (
    PLAYER_SPEED, PLAYER_ROT_SPEED, PLAYER_SIZE, INTERNAL_WIDTH,
    INTERNAL_HEIGHT, MAP_EMPTY, MAP_EXIT,
)


class Player:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.dir_x = math.cos(angle)
        self.dir_y = math.sin(angle)
        self.plane_x = -math.sin(angle) * 0.66
        self.plane_y = math.cos(angle) * 0.66
        self.health = 100
        self.armor = 0
        self.keys = set()
        self.score = 0
        self.alive = True
        self.shoot_cooldown = 0
        self.hurt_timer = 0
        self.current_weapon = 'pistol'
        self.weapons = {'pistol': True, 'chainsaw': False, 'shotgun': False, 'chaingun': False}
        self.ammo = {'bullets': 50, 'shells': 0}

    def handle_input(self, keys_pressed, mouse_rel, dt, game_map):
        speed = PLAYER_SPEED * dt
        rot_speed = PLAYER_ROT_SPEED * dt

        if keys_pressed[pygame.K_LEFT] : #or keys_pressed[pygame.K_a]:
            self.angle -= rot_speed
        if keys_pressed[pygame.K_RIGHT] : #or keys_pressed[pygame.K_d]:
            self.angle += rot_speed

        if mouse_rel[0] != 0:
            self.angle += mouse_rel[0] * 0.003

        self.dir_x = math.cos(self.angle)
        self.dir_y = math.sin(self.angle)
        self.plane_x = -math.sin(self.angle) * 0.66
        self.plane_y = math.cos(self.angle) * 0.66

        move_x, move_y = 0, 0
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            move_x += self.dir_x * speed
            move_y += self.dir_y * speed
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            move_x -= self.dir_x * speed
            move_y -= self.dir_y * speed
        if keys_pressed[pygame.K_a]:
            move_x += self.dir_y * speed
            move_y -= self.dir_x * speed
        if keys_pressed[pygame.K_d]:
            move_x -= self.dir_y * speed
            move_y += self.dir_x * speed

        if move_x != 0 or move_y != 0:
            new_x = self.x + move_x
            new_y = self.y + move_y
            if game_map.is_walkable(new_x, self.y, PLAYER_SIZE):
                self.x = new_x
            if game_map.is_walkable(self.x, new_y, PLAYER_SIZE):
                self.y = new_y

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.hurt_timer > 0:
            self.hurt_timer -= dt

    def take_damage(self, amount):
        if not self.alive:
            return
        absorbed = min(self.armor, amount // 2)
        self.armor -= absorbed
        self.health -= amount - absorbed
        self.hurt_timer = 0.3
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def heal(self, amount):
        self.health = min(100, self.health + amount)

    def add_armor(self, amount):
        self.armor = min(100, self.armor + amount)

    def add_ammo(self, ammo_type, amount):
        self.ammo[ammo_type] = min(200, self.ammo.get(ammo_type, 0) + amount)

    def add_weapon(self, weapon_name):
        self.weapons[weapon_name] = True
        self.current_weapon = weapon_name

    def add_key(self, key_color):
        self.keys.add(key_color)

    def can_use_weapon(self, weapon_name):
        if not self.weapons.get(weapon_name, False):
            return False
        from settings import WEAPONS
        w = WEAPONS[weapon_name]
        if w['ammo_type'] and self.ammo.get(w['ammo_type'], 0) < w['ammo_cost']:
            return False
        return True

    def use_ammo(self, weapon_name):
        from settings import WEAPONS
        w = WEAPONS[weapon_name]
        if w['ammo_type']:
            self.ammo[w['ammo_type']] -= w['ammo_cost']

    def get_looking_tile(self, game_map=None, max_dist=1.5):
        step = 0.25
        n_steps = int(max_dist / step) + 1
        prev_tx, prev_ty = int(self.x), int(self.y)
        for i in range(1, n_steps + 1):
            dist = i * step
            check_x = self.x + self.dir_x * dist
            check_y = self.y + self.dir_y * dist
            tx, ty = int(check_x), int(check_y)
            if (tx, ty) != (prev_tx, prev_ty):
                if game_map is not None and game_map.is_wall(tx, ty):
                    return tx, ty
                prev_tx, prev_ty = tx, ty
        return prev_tx, prev_ty
