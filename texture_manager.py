import numpy as np
import pygame
from settings import TEXTURE_SIZE


class TextureManager:
    def __init__(self):
        self.textures = {}
        self.sprite_textures = {}
        self.floor_texture = None
        self.ceiling_texture = None
        self._generate_procedural_textures()

    def _generate_procedural_textures(self):
        self.textures[1] = self._make_stone_texture()
        self.textures[2] = self._make_brick_texture()
        self.textures[3] = self._make_metal_texture()
        self.textures[4] = self._make_wood_texture()
        self.textures[5] = self._make_mossy_texture()
        self.textures[6] = self._make_blue_texture()
        self.textures[7] = self._make_door_texture()
        self.textures[8] = self._make_door_texture(color=(180, 40, 40))
        self.textures[9] = self._make_door_texture(color=(40, 40, 180))
        self.textures[10] = self._make_exit_texture()
        self.floor_texture = self._make_floor_texture()
        self.ceiling_texture = self._make_ceiling_texture()

    def _make_stone_texture(self):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        rng = np.random.RandomState(42)
        base = rng.randint(80, 110, (TEXTURE_SIZE, TEXTURE_SIZE))
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                base[y, x] = max(0, min(255, base[y, x] + rng.randint(-10, 10)))
        tex[:, :, 0] = base
        tex[:, :, 1] = base
        tex[:, :, 2] = base
        for i in range(0, TEXTURE_SIZE, 16):
            tex[i:i+1, :, :] = np.clip(tex[i:i+1, :, :].astype(np.int16) - 40, 0, 255).astype(np.uint8)
            tex[:, i:i+1, :] = np.clip(tex[:, i:i+1, :].astype(np.int16) - 40, 0, 255).astype(np.uint8)
        return tex

    def _make_brick_texture(self):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        rng = np.random.RandomState(12)
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                by = y % 16
                offset = 8 if (y // 16) % 2 else 0
                bx = (x + offset) % 16
                if by == 0 or bx == 0:
                    r, g, b = 140, 130, 120
                else:
                    r = 180 + rng.randint(-15, 15)
                    g = 70 + rng.randint(-10, 10)
                    b = 50 + rng.randint(-10, 10)
                tex[y, x] = [max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))]
        return tex

    def _make_metal_texture(self):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        rng = np.random.RandomState(7)
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                v = 130 + rng.randint(-8, 8) + int(15 * np.sin(y * 0.3))
                tex[y, x] = [max(0, min(255, v)), max(0, min(255, v + 5)), max(0, min(255, v + 10))]
        for i in range(0, TEXTURE_SIZE, 32):
            tex[i:i+2, :, :] = np.clip(tex[i:i+2, :, :].astype(np.int16) - 50, 0, 255).astype(np.uint8)
            tex[:, i:i+2, :] = np.clip(tex[:, i:i+2, :].astype(np.int16) - 50, 0, 255).astype(np.uint8)
        return tex

    def _make_wood_texture(self):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        rng = np.random.RandomState(99)
        for y in range(TEXTURE_SIZE):
            grain = int(20 * np.sin(y * 0.5 + rng.random() * 2))
            for x in range(TEXTURE_SIZE):
                r = 140 + grain + rng.randint(-8, 8)
                g = 90 + grain // 2 + rng.randint(-5, 5)
                b = 40 + rng.randint(-5, 5)
                tex[y, x] = [max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))]
        for i in range(0, TEXTURE_SIZE, 16):
            tex[i, :, :] = np.clip(tex[i, :, :].astype(np.int16) - 30, 0, 255).astype(np.uint8)
        return tex

    def _make_mossy_texture(self):
        tex = self._make_stone_texture()
        rng = np.random.RandomState(55)
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                if rng.random() < 0.3:
                    g = tex[y, x, 1] + rng.randint(20, 60)
                    tex[y, x, 1] = min(255, g)
                    tex[y, x, 0] = max(0, int(tex[y, x, 0]) - 10)
        return tex

    def _make_blue_texture(self):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        rng = np.random.RandomState(33)
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                v = 60 + rng.randint(-5, 5)
                tex[y, x] = [v // 2, v // 2, min(255, v + 80 + rng.randint(-10, 10))]
        for i in range(0, TEXTURE_SIZE, 16):
            tex[i:i+1, :, :] = np.clip(tex[i:i+1, :, :].astype(np.int16) - 30, 0, 255).astype(np.uint8)
            tex[:, i:i+1, :] = np.clip(tex[:, i:i+1, :].astype(np.int16) - 30, 0, 255).astype(np.uint8)
        return tex

    def _make_door_texture(self, color=(120, 120, 120)):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        rng = np.random.RandomState(77)
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                v = rng.randint(-5, 5)
                tex[y, x] = [max(0, min(255, color[0] + v)),
                             max(0, min(255, color[1] + v)),
                             max(0, min(255, color[2] + v))]
        for y in range(TEXTURE_SIZE):
            tex[y, 30:34] = [min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40)]
        tex[28:36, 28:36] = [200, 200, 50]
        return tex

    def _make_exit_texture(self):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        tex[:, :] = [20, 120, 20]
        tex[8:56, 8:56] = [40, 180, 40]
        tex[16:48, 20:44] = [200, 200, 0]
        return tex

    def _make_floor_texture(self):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        rng = np.random.RandomState(200)
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                tile = ((x // 32) + (y // 32)) % 2
                base = 60 + tile * 25 + rng.randint(-5, 5)
                tex[y, x] = [base, base, base]
        return tex

    def _make_ceiling_texture(self):
        tex = np.zeros((TEXTURE_SIZE, TEXTURE_SIZE, 3), dtype=np.uint8)
        rng = np.random.RandomState(201)
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                v = 50 + rng.randint(-5, 5)
                tex[y, x] = [v // 2, v // 2, v]
        return tex

    def get_texture(self, tile_id):
        return self.textures.get(tile_id, self.textures[1])

    def get_floor_texture(self):
        return self.floor_texture

    def get_ceiling_texture(self):
        return self.ceiling_texture

    def generate_sprite_texture(self, name, size=TEXTURE_SIZE, color=(200, 50, 50), shape='circle'):
        tex = np.zeros((size, size, 4), dtype=np.uint8)
        cx, cy = size // 2, size // 2
        r = size // 3
        rng = np.random.RandomState(hash(name) % 2**31)
        for y in range(size):
            for x in range(size):
                dx, dy = x - cx, y - cy
                dist = (dx*dx + dy*dy) ** 0.5
                if shape == 'circle' and dist < r:
                    tex[y, x] = [min(255, color[0] + rng.randint(-20, 20)),
                                 min(255, color[1] + rng.randint(-20, 20)),
                                 min(255, color[2] + rng.randint(-20, 20)), 255]
                elif shape == 'diamond' and (abs(dx) + abs(dy)) < r:
                    tex[y, x] = [min(255, color[0] + rng.randint(-20, 20)),
                                 min(255, color[1] + rng.randint(-20, 20)),
                                 min(255, color[2] + rng.randint(-20, 20)), 255]
                elif shape == 'square' and abs(dx) < r and abs(dy) < r:
                    tex[y, x] = [min(255, color[0] + rng.randint(-20, 20)),
                                 min(255, color[1] + rng.randint(-20, 20)),
                                 min(255, color[2] + rng.randint(-20, 20)), 255]
        if shape == 'circle' and 'eye' in name:
            er = max(1, r // 3)
            for y in range(cy - er, cy + er):
                for x in range(cx - er, cx + er):
                    if 0 <= x < size and 0 <= y < size and ((x-cx)**2 + (y-cy)**2) < er**2:
                        tex[y, x] = [255, 0, 0, 255]
        return tex
