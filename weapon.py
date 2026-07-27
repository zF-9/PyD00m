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

        tex = np.zeros((64, 64, 4), dtype=np.uint8)
        tex[40:58, 28:36] = [100, 100, 100, 255]
        tex[30:42, 30:34] = [80, 80, 80, 255]
        self.weapon_textures['chainsaw'] = tex

        tex = np.zeros((64, 64, 4), dtype=np.uint8)
        tex[35:60, 28:36] = [120, 120, 130, 255]
        tex[25:38, 30:34] = [90, 90, 95, 255]
        tex[22:26, 26:38] = [140, 140, 140, 255]
        self.weapon_textures['pistol'] = tex

        tex = np.zeros((64, 64, 4), dtype=np.uint8)
        tex[35:60, 24:40] = [110, 100, 90, 255]
        tex[20:38, 26:38] = [130, 120, 110, 255]
        tex[18:22, 24:40] = [100, 100, 100, 255]
        self.weapon_textures['shotgun'] = tex

        tex = np.zeros((64, 64, 4), dtype=np.uint8)
        tex[35:60, 22:42] = [100, 100, 105, 255]
        tex[15:38, 26:38] = [120, 120, 125, 255]
        tex[12:16, 28:36] = [150, 150, 150, 255]
        self.weapon_textures['chaingun'] = tex

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

    def _prebuild_surfs(self):
        weapon_scale = 4
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
        start_y = INTERNAL_HEIGHT - sh + 10

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
