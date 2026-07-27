import sys
import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INTERNAL_WIDTH, INTERNAL_HEIGHT,
    FPS, TITLE, WEAPONS, MAP_DOOR, MAP_DOOR_RED, MAP_DOOR_BLUE, MAP_EXIT,
)
from texture_manager import TextureManager
from map import ALL_LEVELS
from raycaster import Raycaster
from renderer import Renderer
from sprite_renderer import SpriteRenderer
from player import Player
from enemy import Enemy
from item import Item
from weapon import WeaponSystem
from hud import HUD
from menu import Menu
from sound import SoundManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.tex_mgr = TextureManager()
        self.raycaster = Raycaster()
        self.renderer = Renderer(self.tex_mgr)
        self.sprite_renderer = SpriteRenderer(self.tex_mgr)
        self.weapon_system = WeaponSystem()
        self.hud = HUD()
        self.menu = Menu()
        self.sound = SoundManager()

        self.state = 'menu'
        self.current_level_index = 0
        self.game_map = None
        self.player = None
        self.enemies = []
        self.items = []
        self.fps = 0
        self.framebuffer = self.renderer.framebuffer

    def load_level(self, level_index):
        if level_index >= len(ALL_LEVELS):
            self.state = 'menu'
            self.menu.state = 'title'
            return

        self.current_level_index = level_index
        self.game_map = ALL_LEVELS[level_index]
        for door in self.game_map.doors.values():
            door['open'] = False
            door['offset'] = 0.0
            door['state'] = 'closed'
            door['timer'] = 0
        px, py, pa = self.game_map.player_start
        self.player = Player(px, py, pa)
        self.enemies = []
        self.items = []

        for enemy_type, ex, ey in self.game_map.enemies:
            self.enemies.append(Enemy(enemy_type, ex, ey))

        for item_type, ix, iy in self.game_map.items:
            self.items.append(Item(item_type, ix, iy))

    def reset_level(self):
        self.load_level(self.current_level_index)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

            if self.state == 'menu':
                result = self.menu.handle_event(event)
                if result == 'quit':
                    return 'quit'
                elif result and result.startswith('play_level_'):
                    level_idx = int(result.split('_')[-1])
                    self.load_level(level_idx)
                    self.state = 'playing'
                elif result == 'start':
                    self.menu.state = 'level_select'
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'playing':
                        self.state = 'paused'
                        self.menu.state = 'pause'
                    elif self.state == 'paused':
                        self.state = 'playing'
                    return None

                if self.state == 'paused':
                    result = self.menu.handle_event(event)
                    if result == 'resume':
                        self.state = 'playing'
                    elif result == 'restart':
                        self.reset_level()
                        self.state = 'playing'
                    return None

                if self.state == 'victory':
                    result = self.menu.handle_event(event)
                    if result == 'next_level':
                        self.load_level(self.current_level_index + 1)
                        self.state = 'playing'
                    elif result == 'quit':
                        self.state = 'menu'
                        self.menu.state = 'title'
                    return None

                if not self.player.alive and event.key == pygame.K_r:
                    self.reset_level()
                    self.state = 'playing'
                    return None

                if self.state == 'playing':
                    if event.key == pygame.K_e:
                        tx, ty = self.player.get_looking_tile(self.game_map)
                        opened = self.game_map.try_open_door(tx, ty, self.player.keys)
                        if opened:
                            self.sound.play('door')

                    if event.key == pygame.K_m:
                        self.hud.minimap_visible = not self.hud.minimap_visible

                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        weapon_names = ['chainsaw', 'pistol', 'shotgun', 'chaingun']
                        idx = event.key - pygame.K_1
                        if idx < len(weapon_names):
                            name = weapon_names[idx]
                            if self.player.weapons.get(name):
                                self.player.current_weapon = name

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == 'playing' and self.player.alive:
                    if event.button == 1:
                        self._player_shoot()

        return None

    def _player_shoot(self):
        if not self.player.alive:
            return
        if not self.weapon_system.can_fire(self.player, self.player.current_weapon):
            self.sound.play('no_ammo')
            return
        score = self.weapon_system.fire(self.player, self.player.current_weapon, self.enemies, self.game_map)
        self.sound.play_weapon(self.player.current_weapon)
        if isinstance(score, tuple):
            score, hits = score
            for enemy, killed in hits:
                if killed:
                    self.sound.play_enemy_sound(enemy.enemy_type, 'die')
                else:
                    self.sound.play_enemy_sound(enemy.enemy_type, 'pain')

    def update(self, dt):
        if self.state == 'menu':
            self.menu.update(dt)
            return

        if self.state != 'playing':
            return

        keys_pressed = pygame.key.get_pressed()
        mouse_rel = pygame.mouse.get_rel()
        self.player.handle_input(keys_pressed, mouse_rel, dt, self.game_map)

        self.game_map.update_doors(dt)

        for enemy in self.enemies:
            result = enemy.update(dt, self.player, self.game_map)
            if result == 'alert':
                self.sound.play_enemy_sound(enemy.enemy_type, 'alert')
            elif result == 'melee_attack':
                self.sound.play_enemy_sound(enemy.enemy_type, 'attack')
                if enemy.can_see_player(self.player.x, self.player.y, self.game_map, max_dist=3):
                    self.player.take_damage(enemy.damage)
                    self.sound.play('player_hurt')
                    self.hud.damage_flash = 0.3
            elif result == 'ranged_attack':
                self.sound.play_enemy_sound(enemy.enemy_type, 'attack')
                dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                if dist < enemy.attack_range and enemy.can_see_player(self.player.x, self.player.y, self.game_map):
                    hit_chance = max(0.3, 1.0 - dist / enemy.attack_range)
                    if __import__('random').random() < hit_chance:
                        self.player.take_damage(enemy.damage)
                        self.sound.play('player_hurt')
                        self.hud.damage_flash = 0.3

        for item in self.items:
            item.update(dt)
            if item.is_near_player(self.player):
                if item.apply(self.player):
                    self.sound.play('weapon_pickup' if item.item_class == 'weapon' else 'pickup')
                    self.hud.show_pickup(f"Picked up {item.item_type.replace('_', ' ').title()}")

        keys_held = pygame.key.get_pressed()
        if keys_held[pygame.K_LCTRL] or keys_held[pygame.K_RCTRL] or pygame.mouse.get_pressed()[0]:
            self._player_shoot()

        self.weapon_system.update(dt)
        self.hud.update(dt)

        if self.game_map.is_exit(self.player.x, self.player.y):
            alive_enemies = sum(1 for e in self.enemies if e.alive)
            if alive_enemies == 0:
                self.state = 'victory'
                self.menu.state = 'victory'

    def render(self):
        if self.state == 'menu':
            self.menu.render(self.screen)
            pygame.display.flip()
            return

        self.raycaster.cast_rays(
            self.player.x, self.player.y,
            self.player.dir_x, self.player.dir_y,
            self.player.plane_x, self.player.plane_y,
            self.game_map
        )

        self.renderer.render_frame(
            self.screen, self.raycaster,
            self.player.x, self.player.y,
            self.player.dir_x, self.player.dir_y,
            self.player.plane_x, self.player.plane_y,
            self.game_map
        )

        all_sprites = self.enemies + self.items
        self.sprite_renderer.render_sprites(
            self.framebuffer, self.raycaster.get_z_buffer(),
            all_sprites,
            self.player.x, self.player.y,
            self.player.dir_x, self.player.dir_y,
            self.player.plane_x, self.player.plane_y
        )

        bob = 0
        if self.player.alive:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                bob = math.sin(self.weapon_system.bob_timer * 8) * 0.5

        self.weapon_system.render_weapon(
            self.framebuffer, self.player.current_weapon,
            self.weapon_system.fire_flash_timer > 0, bob
        )

        surf = pygame.surfarray.make_surface(self.framebuffer.swapaxes(0, 1))
        scaled = pygame.transform.scale(surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))

        self.hud.render(self.screen, self.player, self.enemies, self.game_map, self.fps)

        if self.state == 'victory':
            self.menu.render(self.screen)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.fps = self.clock.get_fps()

            result = self.handle_events()
            if result == 'quit':
                running = False
                break

            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()
