import math
import numpy as np
from settings import WEAPONS, TEXTURE_SIZE, INTERNAL_WIDTH, INTERNAL_HEIGHT


class WeaponSystem:
    def __init__(self):
        self.fire_flash_timer = 0
        self.current_anim_frame = 0
        self.bob_timer = 0
        self.projectiles = []
        self._weapon_surfs = {}
        self._flash_surf = None
        self._generate_weapon_textures()

    def _generate_weapon_textures(self):
        self.weapon_textures = {}
        S = 64

        self.weapon_textures['chainsaw'] = self._make_chainsaw(S)
        self.weapon_textures['pistol'] = self._make_pistol(S)
        self.weapon_textures['shotgun'] = self._make_shotgun(S)
        self.weapon_textures['chaingun'] = self._make_chaingun(S)

        self.flash_texture = np.zeros((16, 16, 4), dtype=np.uint8)
        yy, xx = np.mgrid[0:16, 0:16]
        dist = np.sqrt((xx - 8)**2 + (yy - 8)**2).astype(np.float64)
        mask = dist < 8
        brightness = (255 * (1 - dist / 8)).astype(np.int32)
        self.flash_texture[mask, 0] = 255
        self.flash_texture[mask, 1] = np.clip(brightness[mask] + 100, 0, 255)
        self.flash_texture[mask, 2] = (brightness[mask] // 2).astype(np.uint8)
        self.flash_texture[mask, 3] = 255

        self._prebuild_surfs()

    def _fill_rect(self, tex, y0, y1, x0, x1, color):
        tex[y0:y1, x0:x1, 0] = color[0]
        tex[y0:y1, x0:x1, 1] = color[1]
        tex[y0:y1, x0:x1, 2] = color[2]
        tex[y0:y1, x0:x1, 3] = 255

    def _fill_circle(self, tex, cx, cy, r, color):
        yy, xx = np.ogrid[:tex.shape[0], :tex.shape[1]]
        mask = ((xx - cx) ** 2 + (yy - cy) ** 2) <= r ** 2
        tex[mask, 0] = color[0]
        tex[mask, 1] = color[1]
        tex[mask, 2] = color[2]
        tex[mask, 3] = 255

    def _fill_ellipse(self, tex, cx, cy, rx, ry, color):
        yy, xx = np.ogrid[:tex.shape[0], :tex.shape[1]]
        mask = ((xx - cx) / max(rx, 1)) ** 2 + ((yy - cy) / max(ry, 1)) ** 2 <= 1.0
        tex[mask, 0] = color[0]
        tex[mask, 1] = color[1]
        tex[mask, 2] = color[2]
        tex[mask, 3] = 255

    def _make_chainsaw(self, S):
        tex = np.zeros((S, S, 4), dtype=np.uint8)
        metal = (140, 140, 145)
        dark_metal = (95, 95, 100)
        grip_brown = (110, 70, 40)
        grip_dark = (70, 45, 25)
        chain = (170, 170, 175)
        teeth = (200, 200, 210)

        self._fill_rect(tex, 42, 64, 26, 38, grip_brown)
        self._fill_rect(tex, 44, 62, 28, 36, grip_dark)
        self._fill_rect(tex, 46, 60, 30, 34, grip_brown)
        self._fill_rect(tex, 50, 56, 29, 35, (90, 60, 35))

        self._fill_rect(tex, 38, 44, 22, 42, dark_metal)
        self._fill_rect(tex, 39, 43, 23, 41, metal)
        self._fill_rect(tex, 40, 42, 25, 39, (155, 155, 160))

        self._fill_rect(tex, 8, 39, 30, 34, chain)
        self._fill_rect(tex, 10, 38, 31, 33, dark_metal)

        for i in range(8, 38, 3):
            self._fill_rect(tex, i, i + 2, 28, 30, teeth)
            self._fill_rect(tex, i, i + 2, 34, 36, teeth)

        self._fill_circle(tex, 31, 40, 4, metal)
        self._fill_circle(tex, 31, 40, 2, dark_metal)

        self._fill_rect(tex, 36, 40, 36, 40, metal)

        return tex

    def _make_pistol(self, S):
        tex = np.zeros((S, S, 4), dtype=np.uint8)
        metal = (145, 145, 150)
        dark_metal = (100, 100, 105)
        grip = (70, 55, 40)
        grip_dark = (50, 38, 28)
        barrel_dark = (80, 80, 85)

        self._fill_rect(tex, 38, 64, 26, 38, grip)
        self._fill_rect(tex, 40, 62, 28, 36, grip_dark)
        self._fill_rect(tex, 42, 60, 30, 34, grip)
        self._fill_rect(tex, 44, 58, 31, 33, grip_dark)

        self._fill_rect(tex, 36, 40, 22, 42, dark_metal)
        self._fill_rect(tex, 37, 39, 23, 41, metal)

        self._fill_rect(tex, 16, 37, 28, 36, metal)
        self._fill_rect(tex, 18, 36, 29, 35, dark_metal)
        self._fill_rect(tex, 20, 35, 30, 34, (130, 130, 135))
        self._fill_rect(tex, 16, 37, 28, 29, barrel_dark)
        self._fill_rect(tex, 16, 37, 35, 36, barrel_dark)

        self._fill_rect(tex, 14, 18, 27, 37, dark_metal)
        self._fill_rect(tex, 15, 17, 28, 36, metal)

        self._fill_rect(tex, 20, 24, 26, 28, metal)
        self._fill_rect(tex, 20, 24, 36, 38, metal)

        self._fill_rect(tex, 34, 38, 20, 24, dark_metal)

        return tex

    def _make_shotgun(self, S):
        tex = np.zeros((S, S, 4), dtype=np.uint8)
        barrel = (110, 110, 115)
        barrel_dark = (75, 75, 80)
        barrel_hi = (140, 140, 148)
        wood = (140, 90, 50)
        wood_dark = (100, 65, 35)
        wood_hi = (165, 115, 70)
        pump = (100, 100, 105)

        self._fill_rect(tex, 28, 64, 24, 40, wood)
        self._fill_rect(tex, 30, 62, 26, 38, wood_dark)
        self._fill_rect(tex, 32, 58, 28, 36, wood)
        self._fill_rect(tex, 34, 50, 30, 34, wood_dark)
        self._fill_rect(tex, 36, 48, 31, 33, wood)

        self._fill_rect(tex, 24, 30, 24, 40, wood)
        self._fill_rect(tex, 25, 29, 25, 39, wood_hi)

        self._fill_rect(tex, 8, 25, 28, 36, barrel)
        self._fill_rect(tex, 10, 24, 29, 35, barrel_dark)
        self._fill_rect(tex, 12, 23, 30, 34, barrel_hi)
        self._fill_rect(tex, 8, 25, 28, 30, barrel_dark)
        self._fill_rect(tex, 8, 25, 34, 36, barrel_dark)

        self._fill_rect(tex, 6, 10, 29, 35, barrel_dark)
        self._fill_rect(tex, 7, 9, 30, 34, barrel)

        self._fill_rect(tex, 22, 26, 26, 38, pump)
        self._fill_rect(tex, 23, 25, 27, 37, (120, 120, 125))

        self._fill_rect(tex, 30, 34, 22, 25, barrel_dark)

        return tex

    def _make_chaingun(self, S):
        tex = np.zeros((S, S, 4), dtype=np.uint8)
        metal = (135, 135, 140)
        dark_metal = (90, 90, 95)
        bright_metal = (160, 160, 168)
        barrel = (120, 120, 125)
        grip = (70, 55, 40)
        grip_dark = (50, 38, 28)

        self._fill_rect(tex, 40, 64, 24, 40, grip)
        self._fill_rect(tex, 42, 62, 26, 38, grip_dark)
        self._fill_rect(tex, 44, 58, 28, 36, grip)
        self._fill_rect(tex, 46, 56, 30, 34, grip_dark)

        self._fill_rect(tex, 36, 42, 20, 44, dark_metal)
        self._fill_rect(tex, 37, 41, 21, 43, metal)

        self._fill_rect(tex, 32, 38, 22, 28, metal)
        self._fill_rect(tex, 33, 37, 23, 27, dark_metal)
        self._fill_rect(tex, 32, 38, 36, 42, metal)
        self._fill_rect(tex, 33, 37, 37, 41, dark_metal)

        self._fill_rect(tex, 6, 33, 24, 30, barrel)
        self._fill_rect(tex, 8, 32, 25, 29, dark_metal)
        self._fill_rect(tex, 6, 33, 34, 40, barrel)
        self._fill_rect(tex, 8, 32, 35, 39, dark_metal)

        self._fill_rect(tex, 6, 33, 26, 28, bright_metal)
        self._fill_rect(tex, 6, 33, 36, 38, bright_metal)

        self._fill_rect(tex, 4, 8, 25, 29, dark_metal)
        self._fill_rect(tex, 4, 8, 35, 39, dark_metal)
        self._fill_rect(tex, 5, 7, 26, 28, barrel)
        self._fill_rect(tex, 5, 7, 36, 38, barrel)

        self._fill_rect(tex, 30, 34, 28, 36, metal)
        self._fill_rect(tex, 31, 33, 29, 35, dark_metal)

        self._fill_circle(tex, 31, 40, 3, metal)
        self._fill_circle(tex, 31, 40, 1.5, dark_metal)

        return tex

    def _prebuild_surfs(self):
        weapon_scale = 2
        for name, tex in self.weapon_textures.items():
            alpha = tex[:, :, 3]
            visible = alpha > 128
            scaled_w = tex.shape[1] * weapon_scale
            scaled_h = tex.shape[0] * weapon_scale

            mask = np.repeat(np.repeat(visible, weapon_scale, axis=0), weapon_scale, axis=1)
            rgb = np.repeat(np.repeat(tex[:, :, :3], weapon_scale, axis=0), weapon_scale, axis=1)
            self._weapon_surfs[name] = (rgb, mask, scaled_w, scaled_h)

        flash_alpha = self.flash_texture[:, :, 3] > 0
        flash_rgb = self.flash_texture[:, :, :3]
        self._flash_mask = flash_alpha
        self._flash_rgb = flash_rgb

    def get_weapon_texture(self, weapon_name, firing=False):
        return self.weapon_textures.get(weapon_name, self.weapon_textures['pistol'])

    def render_weapon(self, framebuffer, weapon_name, firing, bob_offset=0):
        rgb, mask, sw, sh = self._weapon_surfs.get(
            weapon_name, self._weapon_surfs['pistol']
        )

        start_x = INTERNAL_WIDTH // 2 - sw // 2 + int(bob_offset * 5)
        start_y = INTERNAL_HEIGHT - sh + 20

        sx0 = max(0, -start_x)
        sy0 = max(0, -start_y)
        sx1 = min(sw, INTERNAL_WIDTH - start_x)
        sy1 = min(sh, INTERNAL_HEIGHT - start_y)

        if sx0 >= sx1 or sy0 >= sy1:
            return

        fx0 = start_x + sx0
        fy0 = start_y + sy0
        fx1 = fx0 + (sx1 - sx0)
        fy1 = fy0 + (sy1 - sy0)

        region_mask = mask[sy0:sy1, sx0:sx1]
        region_rgb = rgb[sy0:sy1, sx0:sx1]

        fb_region = framebuffer[fy0:fy1, fx0:fx1]
        fb_region[region_mask] = region_rgb[region_mask]

        if firing and self.fire_flash_timer > 0:
            flash_y = start_y - 20
            flash_x = INTERNAL_WIDTH // 2 - 8
            fsx0 = max(0, -flash_x)
            fsy0 = max(0, -flash_y)
            fsx1 = min(16, INTERNAL_WIDTH - flash_x)
            fsy1 = min(16, INTERNAL_HEIGHT - flash_y)
            if fsx0 < fsx1 and fsy0 < fsy1:
                fmask = self._flash_mask[fsy0:fsy1, fsx0:fsx1]
                frgb = self._flash_rgb[fsy0:fsy1, fsx0:fsx1]
                framebuffer[flash_y + fsy0:flash_y + fsy1,
                            flash_x + fsx0:flash_x + fsx1][fmask] = frgb[fmask]

    def can_fire(self, player, weapon_name):
        w = WEAPONS[weapon_name]
        if player.shoot_cooldown > 0:
            return False
        if w['ammo_type'] and player.ammo.get(w['ammo_type'], 0) < w['ammo_cost']:
            return False
        return True

    def fire(self, player, weapon_name, enemies, game_map):
        if not self.can_fire(player, weapon_name):
            return 0, []

        w = WEAPONS[weapon_name]
        player.use_ammo(weapon_name)
        player.shoot_cooldown = w['fire_rate']
        self.fire_flash_timer = 0.1

        total_damage = 0
        hits = []
        if w['hitscan']:
            for proj in range(w['projectiles']):
                spread = (np.random.random() - 0.5) * w['spread'] * 2
                ray_angle = player.angle + spread
                ray_dir_x = math.cos(ray_angle)
                ray_dir_y = math.sin(ray_angle)

                hit_enemy = None
                hit_dist = w['range']

                for enemy in enemies:
                    if not enemy.alive:
                        continue
                    ex, ey = enemy.x - player.x, enemy.y - player.y
                    cross = ex * ray_dir_y - ey * ray_dir_x
                    if abs(cross) < enemy.size:
                        dot = ex * ray_dir_x + ey * ray_dir_y
                        if 0 < dot < hit_dist:
                            check_x = player.x + ray_dir_x * dot
                            check_y = player.y + ray_dir_y * dot
                            if not game_map.is_wall(check_x, check_y):
                                hit_enemy = enemy
                                hit_dist = dot

                if hit_enemy:
                    killed = hit_enemy.take_damage(w['damage'])
                    hits.append((hit_enemy, killed))
                    if killed:
                        total_damage += hit_enemy.score
                        player.score += hit_enemy.score
        else:
            for enemy in enemies:
                if not enemy.alive:
                    continue
                dx = enemy.x - player.x
                dy = enemy.y - player.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < w['range']:
                    angle_to = math.atan2(dy, dx)
                    angle_diff = abs(angle_to - player.angle)
                    if angle_diff > math.pi:
                        angle_diff = 2 * math.pi - angle_diff
                    if angle_diff < 0.2:
                        if not game_map.is_wall(
                            player.x + dx * 0.3,
                            player.y + dy * 0.3
                        ):
                            killed = enemy.take_damage(w['damage'])
                            hits.append((enemy, killed))
                            if killed:
                                total_damage += enemy.score
                                player.score += enemy.score

        return total_damage, hits

    def update(self, dt):
        if self.fire_flash_timer > 0:
            self.fire_flash_timer -= dt
        self.bob_timer += dt
