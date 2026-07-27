import pygame
import numpy as np
from settings import (
    INTERNAL_WIDTH, INTERNAL_HEIGHT, TEXTURE_SIZE, MAX_DEPTH,
)


class Renderer:
    def __init__(self, texture_manager):
        self.tex_mgr = texture_manager
        self.framebuffer = np.zeros((INTERNAL_HEIGHT, INTERNAL_WIDTH, 3), dtype=np.uint8)

        self._x_coords = np.arange(INTERNAL_WIDTH, dtype=np.float64)
        self._half_h = INTERNAL_HEIGHT // 2
        self._floor_ys = np.arange(self._half_h + 1, INTERNAL_HEIGHT, dtype=np.float64)
        self._p = self._floor_ys - self._half_h
        self._pos_z = 0.5 * INTERNAL_HEIGHT
        self._row_dist = self._pos_z / self._p

        self._shade_floor = np.clip(1.0 - self._row_dist / MAX_DEPTH, 0.15, 1.0)

    def render_frame(self, screen, raycaster, px, py, dir_x, dir_y, plane_x, plane_y, game_map):
        self.framebuffer[:] = 0
        self._render_floor_ceiling(px, py, dir_x, dir_y, plane_x, plane_y)
        self._render_walls(raycaster)

    def _render_floor_ceiling(self, px, py, dir_x, dir_y, plane_x, plane_y):
        floor_tex = self.tex_mgr.get_floor_texture()
        ceil_tex = self.tex_mgr.get_ceiling_texture()

        ray_dir_x0 = dir_x - plane_x
        ray_dir_y0 = dir_y - plane_y
        ray_dir_x1 = dir_x + plane_x
        ray_dir_y1 = dir_y + plane_y

        dr_x = ray_dir_x1 - ray_dir_x0
        dr_y = ray_dir_y1 - ray_dir_y0

        floor_starts_x = px + self._row_dist * ray_dir_x0
        floor_starts_y = py + self._row_dist * ray_dir_y0

        floor_step_x = self._row_dist * dr_x / INTERNAL_WIDTH
        floor_step_y = self._row_dist * dr_y / INTERNAL_WIDTH

        floor_xs = floor_starts_x[:, None] + self._x_coords[None, :] * floor_step_x[:, None]
        floor_ys = floor_starts_y[:, None] + self._x_coords[None, :] * floor_step_y[:, None]

        tx = (floor_xs * TEXTURE_SIZE).astype(np.int32) % TEXTURE_SIZE
        ty = (floor_ys * TEXTURE_SIZE).astype(np.int32) % TEXTURE_SIZE

        shade_f = self._shade_floor[:, None, None].astype(np.float64)
        shade_c = shade_f * 0.6

        floor_pixels = floor_tex[ty, tx].astype(np.float64) * shade_f
        ceil_pixels = ceil_tex[ty, tx].astype(np.float64) * shade_c

        n_floor = len(self._floor_ys)
        self.framebuffer[self._half_h + 1:, :] = np.clip(floor_pixels, 0, 255).astype(np.uint8)
        self.framebuffer[:n_floor, :] = np.clip(ceil_pixels[::-1], 0, 255).astype(np.uint8)

    def _render_walls(self, raycaster):
        for x in range(raycaster.num_rays_cast):
            dist = raycaster.wall_dists[x]
            if dist >= MAX_DEPTH:
                continue

            tile_id = raycaster.wall_types[x]
            tex = self.tex_mgr.get_texture(tile_id)
            side = raycaster.side_hits[x]
            wall_x = raycaster.tex_x_hits[x]

            line_height = int(INTERNAL_HEIGHT / dist)
            draw_start = max(0, -line_height // 2 + self._half_h)
            draw_end = min(INTERNAL_HEIGHT, line_height // 2 + self._half_h)

            tex_x = int(wall_x * TEXTURE_SIZE)
            ray_dir_x = raycaster._ray_dir_x_cache.get(x, 0)
            ray_dir_y = raycaster._ray_dir_y_cache.get(x, 0)
            if side == 0 and ray_dir_x > 0:
                tex_x = TEXTURE_SIZE - tex_x - 1
            if side == 1 and ray_dir_y < 0:
                tex_x = TEXTURE_SIZE - tex_x - 1
            tex_x = max(0, min(TEXTURE_SIZE - 1, tex_x))

            shade = max(0.3, 1.0 - dist / MAX_DEPTH)
            if side == 1:
                shade *= 0.7

            ys = np.arange(draw_start, draw_end)
            d = ys - self._half_h + line_height // 2
            tex_y = (d * TEXTURE_SIZE // line_height) % TEXTURE_SIZE

            colors = tex[tex_y, tex_x].astype(np.float64) * shade
            self.framebuffer[draw_start:draw_end, x] = np.clip(colors, 0, 255).astype(np.uint8)
