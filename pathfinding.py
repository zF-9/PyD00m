import numpy as np
from collections import deque


def bfs_path(game_map, start_x, start_y, goal_x, goal_y, max_steps=500):
    sx, sy = int(start_x), int(start_y)
    gx, gy = int(goal_x), int(goal_y)

    if sx == gx and sy == gy:
        return []

    def is_walkable(x, y):
        if not (0 <= x < game_map.width and 0 <= y < game_map.height):
            return False
        tile = int(game_map.layout[y, x])
        if tile == 0:
            return True
        if (x, y) in game_map.doors:
            door = game_map.doors[(x, y)]
            if door['open'] and door['offset'] >= 0.9:
                return True
        return False

    if not is_walkable(gx, gy):
        return []

    visited = set()
    queue = deque([(sx, sy, [])])
    visited.add((sx, sy))

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                  (1, 1), (1, -1), (-1, 1), (-1, -1)]

    steps = 0
    while queue and steps < max_steps:
        cx, cy, path = queue.popleft()
        steps += 1

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy

            if (nx, ny) in visited:
                continue
            if not is_walkable(nx, ny):
                continue

            new_path = path + [(nx + 0.5, ny + 0.5)]

            if nx == gx and ny == gy:
                return new_path

            visited.add((nx, ny))
            queue.append((nx, ny, new_path))

    return []
