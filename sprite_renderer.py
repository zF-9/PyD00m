import math
import numpy as np
from settings import INTERNAL_WIDTH, INTERNAL_HEIGHT, TEXTURE_SIZE, MAX_DEPTH


class SpriteRenderer:
    def __init__(self, texture_manager):
        self.tex_mgr = texture_manager
        self.sprite_cache = {}

    def render_sprites(self, framebuffer, z_buffer, sprites, px, py, dir_x, dir_y, plane_x, plane_y):
        if not sprites:
            return

        visible = []
        for sprite in sprites:
            dx = sprite.x - px
            dy = sprite.y - py
            dist_sq = dx * dx + dy * dy
            visible.append((sprite, dist_sq, dx, dy))

        visible.sort(key=lambda s: s[1], reverse=True)

        inv_det = 1.0 / (plane_x * dir_y - dir_x * plane_y)

        for sprite, dist_sq, dx, dy in visible:
            if not sprite.alive and hasattr(sprite, 'death_timer') and sprite.death_timer <= 0:
                continue

            transform_x = inv_det * (dir_y * dx - dir_x * dy)
            transform_y = inv_det * (-plane_y * dx + plane_x * dy)

            if transform_y <= 0.1:
                continue

            sprite_screen_x = int((INTERNAL_WIDTH / 2) * (1 + transform_x / transform_y))

            sprite_height = abs(int(INTERNAL_HEIGHT / transform_y))
            sprite_width = sprite_height

            draw_start_y = max(0, -sprite_height // 2 + INTERNAL_HEIGHT // 2)
            draw_end_y = min(INTERNAL_HEIGHT, sprite_height // 2 + INTERNAL_HEIGHT // 2)
            draw_start_x = max(0, -sprite_width // 2 + sprite_screen_x)
            draw_end_x = min(INTERNAL_WIDTH, sprite_width // 2 + sprite_screen_x)

            tex = sprite.get_texture()
            if tex is None:
                continue

            shade = max(0.2, 1.0 - math.sqrt(dist_sq) / MAX_DEPTH)

            stripes_x = np.arange(draw_start_x, draw_end_x)
            visible_mask = (transform_y > 0) & (stripes_x >= 0) & (stripes_x < INTERNAL_WIDTH) & (transform_y < z_buffer[stripes_x])
            visible_stripes = stripes_x[visible_mask]

            if len(visible_stripes) == 0:
                continue

            tex_xs = ((visible_stripes - (-sprite_width // 2 + sprite_screen_x)) * TEXTURE_SIZE // sprite_width).astype(np.int32)
            valid_tex = (tex_xs >= 0) & (tex_xs < TEXTURE_SIZE)
            visible_stripes = visible_stripes[valid_tex]
            tex_xs = tex_xs[valid_tex]

            if len(visible_stripes) == 0:
                continue

            ys = np.arange(draw_start_y, draw_end_y)
            tex_ys = ((ys - draw_start_y) * TEXTURE_SIZE // (draw_end_y - draw_start_y)).astype(np.int32)
            valid_ys = (tex_ys >= 0) & (tex_ys < TEXTURE_SIZE)
            ys = ys[valid_ys]
            tex_ys = tex_ys[valid_ys]

            if len(ys) == 0:
                continue

            tex_region = tex[np.ix_(tex_ys, tex_xs)]

            if tex_region.ndim == 3 and tex_region.shape[2] == 4:
                alpha = tex_region[:, :, 3] > 128
                rgb = tex_region[:, :, :3].astype(np.float64) * shade
            else:
                black = (tex_region[:, :, 0] == 0) & (tex_region[:, :, 1] == 0) & (tex_region[:, :, 2] == 0)
                alpha = ~black
                rgb = tex_region[:, :, :3].astype(np.float64) * shade

            rgb = np.clip(rgb, 0, 255).astype(np.uint8)

            for i, sx in enumerate(visible_stripes):
                col_mask = alpha[:, i]
                if np.any(col_mask):
                    fb_slice = framebuffer[ys, sx]
                    fb_slice[col_mask] = rgb[col_mask, i]
                    framebuffer[ys, sx] = fb_slice

            sprite.distance_to_player = math.sqrt(dist_sq)
