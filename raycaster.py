import math
import numpy as np
from settings import (
    INTERNAL_WIDTH, INTERNAL_HEIGHT, NUM_RAYS, FOV, HALF_FOV,
    MAX_DEPTH, DELTA_ANGLE, PLAYER_SIZE,
)


class Raycaster:
    def __init__(self):
        self.z_buffer = np.full(INTERNAL_WIDTH, MAX_DEPTH, dtype=np.float64)
        self.wall_dists = np.zeros(NUM_RAYS, dtype=np.float64)
        self.wall_hits_x = np.zeros(NUM_RAYS, dtype=np.float64)
        self.wall_hits_y = np.zeros(NUM_RAYS, dtype=np.float64)
        self.wall_types = np.zeros(NUM_RAYS, dtype=np.int32)
        self.side_hits = np.zeros(NUM_RAYS, dtype=np.int32)
        self.tex_x_hits = np.zeros(NUM_RAYS, dtype=np.float64)
        self.num_rays_cast = 0
        self._ray_dir_x_cache = {}
        self._ray_dir_y_cache = {}

    def cast_rays(self, px, py, dir_x, dir_y, plane_x, plane_y, game_map):
        self.z_buffer[:] = MAX_DEPTH
        self.num_rays_cast = 0
        self._ray_dir_x_cache = {}
        self._ray_dir_y_cache = {}

        for x in range(NUM_RAYS):
            camera_x = 2.0 * x / INTERNAL_WIDTH - 1.0
            ray_dir_x = dir_x + plane_x * camera_x
            ray_dir_y = dir_y + plane_y * camera_x

            self._ray_dir_x_cache[x] = ray_dir_x
            self._ray_dir_y_cache[x] = ray_dir_y

            map_x = int(px)
            map_y = int(py)

            if abs(ray_dir_x) < 1e-10:
                ray_dir_x = 1e-10
            if abs(ray_dir_y) < 1e-10:
                ray_dir_y = 1e-10

            delta_dist_x = abs(1.0 / ray_dir_x)
            delta_dist_y = abs(1.0 / ray_dir_y)

            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (px - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - px) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (py - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - py) * delta_dist_y

            hit = False
            side = 0
            tile_id = 0

            for _ in range(MAX_DEPTH * 2):
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1

                if 0 <= map_x < game_map.width and 0 <= map_y < game_map.height:
                    tile = int(game_map.layout[map_y, map_x])
                    if tile != 0:
                        if tile in game_map.doors:
                            door = game_map.doors[(map_x, map_y)]
                            if door['open'] and door['offset'] >= 0.9:
                                continue
                        hit = True
                        tile_id = tile
                        break
                else:
                    break

            if hit:
                if side == 0:
                    perp_wall_dist = side_dist_x - delta_dist_x
                else:
                    perp_wall_dist = side_dist_y - delta_dist_y

                if perp_wall_dist < 0.01:
                    perp_wall_dist = 0.01

                if side == 0:
                    wall_x = py + perp_wall_dist * ray_dir_y
                else:
                    wall_x = px + perp_wall_dist * ray_dir_x
                wall_x -= math.floor(wall_x)

                self.wall_dists[x] = perp_wall_dist
                self.z_buffer[x] = perp_wall_dist
                self.wall_hits_x[x] = px + perp_wall_dist * ray_dir_x
                self.wall_hits_y[x] = py + perp_wall_dist * ray_dir_y
                self.wall_types[x] = tile_id
                self.side_hits[x] = side
                self.tex_x_hits[x] = wall_x
            else:
                self.wall_dists[x] = MAX_DEPTH
                self.z_buffer[x] = MAX_DEPTH
                self.wall_types[x] = 0

            self.num_rays_cast += 1

    def get_z_buffer(self):
        return self.z_buffer
