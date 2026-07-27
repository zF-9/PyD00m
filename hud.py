import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INTERNAL_WIDTH, INTERNAL_HEIGHT,
    WHITE, RED, GREEN, YELLOW, HUD_BG, HUD_RED, HUD_YELLOW, BLACK,
)


class HUD:
    def __init__(self):
        self.font = None
        self.big_font = None
        self.minimap_visible = True
        self.damage_flash = 0
        self.pickup_message = ""
        self.pickup_timer = 0

    def init_fonts(self):
        self.font = pygame.font.SysFont('consolas', 14, bold=True)
        self.big_font = pygame.font.SysFont('consolas', 28, bold=True)
        self.small_font = pygame.font.SysFont('consolas', 10)

    def show_pickup(self, message):
        self.pickup_message = message
        self.pickup_timer = 2.0

    def update(self, dt):
        if self.pickup_timer > 0:
            self.pickup_timer -= dt
        if self.damage_flash > 0:
            self.damage_flash -= dt

    def render(self, screen, player, enemies, game_map, fps=0):
        if not self.font:
            self.init_fonts()

        hud_height = 50
        hud_surface = pygame.Surface((SCREEN_WIDTH, hud_height))
        hud_surface.fill(HUD_BG)

        health_color = GREEN if player.health > 50 else YELLOW if player.health > 25 else RED
        health_text = self.font.render(f"HEALTH: {player.health}", True, health_color)
        hud_surface.blit(health_text, (10, 5))

        armor_color = GREEN if player.armor > 50 else YELLOW if player.armor > 25 else RED
        armor_text = self.font.render(f"ARMOR: {player.armor}", True, armor_color)
        hud_surface.blit(armor_text, (10, 25))

        ammo_text = self.font.render(f"AMMO: {player.ammo.get('bullets', 0)}", True, WHITE)
        hud_surface.blit(ammo_text, (180, 5))

        shells_text = self.font.render(f"SHELLS: {player.ammo.get('shells', 0)}", True, WHITE)
        hud_surface.blit(shells_text, (180, 25))

        weapon_text = self.font.render(f"WEAPON: {player.current_weapon.upper()}", True, HUD_YELLOW)
        hud_surface.blit(weapon_text, (340, 5))

        score_text = self.font.render(f"SCORE: {player.score}", True, WHITE)
        hud_surface.blit(score_text, (340, 25))

        keys_text = ""
        if 'red' in player.keys:
            keys_text += "R "
        if 'blue' in player.keys:
            keys_text += "B "
        if keys_text:
            key_surface = self.font.render(f"KEYS: {keys_text}", True, YELLOW)
            hud_surface.blit(key_surface, (500, 5))

        screen.blit(hud_surface, (0, SCREEN_HEIGHT - hud_height))

        alive_enemies = sum(1 for e in enemies if e.alive)
        enemies_text = self.small_font.render(f"ENEMIES: {alive_enemies}", True, WHITE)
        screen.blit(enemies_text, (10, 5))

        fps_text = self.small_font.render(f"FPS: {int(fps)}", True, GREEN)
        screen.blit(fps_text, (SCREEN_WIDTH - 80, 5))

        if self.minimap_visible:
            self._render_minimap(screen, player, enemies, game_map)

        if player.hurt_timer > 0 or self.damage_flash > 0:
            hurt_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(80 * (player.hurt_timer / 0.3)) if player.hurt_timer > 0 else int(60 * self.damage_flash)
            hurt_surface.fill((255, 0, 0, min(255, alpha)))
            screen.blit(hurt_surface, (0, 0))

        if self.pickup_timer > 0 and self.pickup_message:
            msg_surface = self.font.render(self.pickup_message, True, YELLOW)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            bg_rect = msg_rect.inflate(10, 4)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 160))
            screen.blit(bg_surface, bg_rect)
            screen.blit(msg_surface, msg_rect)

        if not player.alive:
            death_text = self.big_font.render("YOU DIED", True, RED)
            death_rect = death_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(death_text, death_rect)

            restart_text = self.font.render("Press R to restart or ESC to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(restart_text, restart_rect)

    def _render_minimap(self, screen, player, enemies, game_map):
        scale = 5
        map_w = game_map.width * scale
        map_h = game_map.height * scale
        map_x = SCREEN_WIDTH - map_w - 10
        map_y = 25

        minimap = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        minimap.fill((0, 0, 0, 128))

        tile_colors = {
            0: (40, 40, 40),
            1: (120, 120, 120),
            2: (180, 70, 50),
            3: (130, 130, 140),
            4: (140, 90, 40),
            5: (80, 120, 80),
            6: (40, 40, 140),
            7: (100, 100, 100),
            8: (180, 40, 40),
            9: (40, 40, 180),
            10: (40, 180, 40),
        }

        for y in range(game_map.height):
            for x in range(game_map.width):
                tile = game_map.layout[y, x]
                color = tile_colors.get(tile, (60, 60, 60))
                if tile in game_map.doors:
                    door = game_map.doors[(x, y)]
                    if door['open']:
                        color = (40, 40, 40)
                pygame.draw.rect(minimap, color, (x * scale, y * scale, scale, scale))

        px_map = int(player.x * scale)
        py_map = int(player.y * scale)
        pygame.draw.circle(minimap, (0, 255, 0), (px_map, py_map), 2)
        pygame.draw.line(minimap, (0, 255, 0), (px_map, py_map),
                        (px_map + int(math.cos(player.angle) * 8),
                         py_map + int(math.sin(player.angle) * 8)), 1)

        for enemy in enemies:
            if enemy.alive:
                ex_map = int(enemy.x * scale)
                ey_map = int(enemy.y * scale)
                pygame.draw.circle(minimap, (255, 0, 0), (ex_map, ey_map), 2)

        screen.blit(minimap, (map_x, map_y))
