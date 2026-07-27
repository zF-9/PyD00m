import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GREEN, YELLOW, BLACK, BLUE


class Menu:
    def __init__(self):
        self.font = None
        self.big_font = None
        self.state = 'title'
        self.selected_level = 0
        self.menu_items = ['Start Game', 'Quit']
        self.selected = 0
        self.title_timer = 0
        self.death_timer = 0

    def init_fonts(self):
        self.font = pygame.font.SysFont('consolas', 18, bold=True)
        self.big_font = pygame.font.SysFont('consolas', 36, bold=True)
        self.small_font = pygame.font.SysFont('consolas', 12)

    def handle_event(self, event):
        if self.state == 'title':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.menu_items)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.menu_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected == 0:
                        self.state = 'level_select'
                        return 'start'
                    elif self.selected == 1:
                        return 'quit'

        elif self.state == 'level_select':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_level = max(0, self.selected_level - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_level += 1
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return f'play_level_{self.selected_level}'
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'title'
                    self.selected = 0

        elif self.state == 'pause':
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    return 'resume'
                elif event.key == pygame.K_r:
                    return 'restart'

        elif self.state == 'victory':
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return 'next_level'
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'title'
                    self.selected = 0
                    return 'quit'

        return None

    def update(self, dt):
        self.title_timer += dt

    def render(self, screen):
        if not self.font:
            self.init_fonts()

        screen.fill(BLACK)

        if self.state == 'title':
            self._render_title(screen)
        elif self.state == 'level_select':
            self._render_level_select(screen)
        elif self.state == 'pause':
            self._render_pause(screen)
        elif self.state == 'victory':
            self._render_victory(screen)

    def _render_title(self, screen):
        title = self.big_font.render("PYG DOOM", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)

        import math
        glow = int(128 + 127 * math.sin(self.title_timer * 3))
        subtitle = self.font.render("A Python Raycasting FPS", True, (glow, glow, glow))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 130))
        screen.blit(subtitle, sub_rect)

        for i, item in enumerate(self.menu_items):
            color = YELLOW if i == self.selected else WHITE
            text = self.font.render(item, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 40))
            if i == self.selected:
                arrow = self.font.render(">", True, YELLOW)
                screen.blit(arrow, (text_rect.x - 25, text_rect.y))
            screen.blit(text, text_rect)

        controls = [
            "WASD / Arrows - Move",
            "Mouse - Look",
            "Left Click / Ctrl - Shoot",
            "E - Use (doors)",
            "1-4 - Switch Weapon",
            "M - Toggle Minimap",
            "P / ESC - Pause",
        ]
        for i, line in enumerate(controls):
            text = self.small_font.render(line, True, (150, 150, 150))
            screen.blit(text, (50, 320 + i * 16))

    def _render_level_select(self, screen):
        title = self.big_font.render("SELECT LEVEL", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title, title_rect)

        from map import ALL_LEVELS
        for i, level in enumerate(ALL_LEVELS):
            color = YELLOW if i == self.selected_level else WHITE
            text = self.font.render(f"{level.name}", True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 140 + i * 40))
            if i == self.selected_level:
                arrow = self.font.render(">", True, YELLOW)
                screen.blit(arrow, (text_rect.x - 25, text_rect.y))
            screen.blit(text, text_rect)

        hint = self.small_font.render("ENTER to play, ESC to go back", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(hint, hint_rect)

    def _render_pause(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        title = self.big_font.render("PAUSED", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(title, title_rect)

        hint = self.font.render("ESC to resume, R to restart", True, WHITE)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(hint, hint_rect)

    def _render_victory(self, screen):
        title = self.big_font.render("LEVEL COMPLETE!", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(title, title_rect)

        hint = self.font.render("ENTER for next level, ESC for menu", True, WHITE)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(hint, hint_rect)
