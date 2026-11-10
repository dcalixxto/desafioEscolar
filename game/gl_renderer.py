"""
Módulo de Renderização em OpenGL 2D com Pygame.
Gerencia viewport, projeção ortográfica, texturas, primitivas gráficas e renderização de fontes.
"""

import math
import pygame
from OpenGL.GL import *
from game.config import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG

class GLRenderer:
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.fonts = {}
        self.text_texture_cache = {}
        self.camera_x = 0.0
        self.camera_y = 0.0
        self._init_gl()

    def _init_gl(self):
        """Configura o pipeline ortográfico 2D do OpenGL."""
        glViewport(0, 0, self.width, self.height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glEnable(GL_TEXTURE_2D)

    def clear(self, color=COLOR_BG):
        r = color[0] / 255.0
        g = color[1] / 255.0
        b = color[2] / 255.0
        a = (color[3] / 255.0) if len(color) > 3 else 1.0
        glClearColor(r, g, b, a)
        glClear(GL_COLOR_BUFFER_BIT)

    def set_camera(self, target_x, target_y, world_w=None, world_h=None):
        self.camera_x = target_x - self.width / 2.0
        self.camera_y = target_y - self.height / 2.0

        if world_w is not None and world_h is not None:
            max_x = max(0, world_w - self.width)
            max_y = max(0, world_h - self.height)
            self.camera_x = max(0, min(self.camera_x, max_x))
            self.camera_y = max(0, min(self.camera_y, max_y))

    def apply_camera(self):
        glPushMatrix()
        glTranslatef(-round(self.camera_x), -round(self.camera_y), 0)

    def reset_camera(self):
        glPopMatrix()

    @staticmethod
    def create_texture(surface):
        if surface.get_bytesize() != 4:
            surface = surface.convert_alpha()

        width, height = surface.get_size()
        texture_data = pygame.image.tostring(surface, "RGBA", True)

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glBindTexture(GL_TEXTURE_2D, 0)
        return tex_id, width, height

    def draw_texture(self, tex_id, x, y, w, h, src_rect=None, tex_w=None, tex_h=None, flip_x=False, color_tint=(255, 255, 255, 255)):
        if tex_id == 0:
            return

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        r = color_tint[0] / 255.0
        g = color_tint[1] / 255.0
        b = color_tint[2] / 255.0
        a = (color_tint[3] / 255.0) if len(color_tint) > 3 else 1.0
        glColor4f(r, g, b, a)

        u0, v0, u1, v1 = 0.0, 0.0, 1.0, 1.0
        if src_rect is not None and tex_w and tex_h:
            rx, ry, rw, rh = src_rect
            u0 = rx / float(tex_w)
            v0 = (tex_h - ry - rh) / float(tex_h)
            u1 = (rx + rw) / float(tex_w)
            v1 = (tex_h - ry) / float(tex_h)

        if flip_x:
            u0, u1 = u1, u0

        glBegin(GL_QUADS)
        glTexCoord2f(u0, v1); glVertex2f(x, y)
        glTexCoord2f(u1, v1); glVertex2f(x + w, y)
        glTexCoord2f(u1, v0); glVertex2f(x + w, y + h)
        glTexCoord2f(u0, v0); glVertex2f(x, y + h)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)

    @staticmethod
    def _set_color(color):
        r = color[0] / 255.0
        g = color[1] / 255.0
        b = color[2] / 255.0
        a = (color[3] / 255.0) if len(color) > 3 else 1.0
        glColor4f(r, g, b, a)

    def draw_rect(self, x, y, w, h, color, filled=True, border_width=1):
        glDisable(GL_TEXTURE_2D)
        self._set_color(color)

        if filled:
            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + w, y)
            glVertex2f(x + w, y + h)
            glVertex2f(x, y + h)
            glEnd()
        else:
            glLineWidth(border_width)
            glBegin(GL_LINE_LOOP)
            glVertex2f(x, y)
            glVertex2f(x + w, y)
            glVertex2f(x + w, y + h)
            glVertex2f(x, y + h)
            glEnd()

        glEnable(GL_TEXTURE_2D)

    def draw_vertical_gradient(self, x, y, w, h, color_top, color_bottom):
        glDisable(GL_TEXTURE_2D)
        rt, gt, bt = color_top[0] / 255.0, color_top[1] / 255.0, color_top[2] / 255.0
        at = (color_top[3] / 255.0) if len(color_top) > 3 else 1.0
        rb, gb, bb = color_bottom[0] / 255.0, color_bottom[1] / 255.0, color_bottom[2] / 255.0
        ab = (color_bottom[3] / 255.0) if len(color_bottom) > 3 else 1.0

        glBegin(GL_QUADS)
        glColor4f(rt, gt, bt, at); glVertex2f(x, y)
        glColor4f(rt, gt, bt, at); glVertex2f(x + w, y)
        glColor4f(rb, gb, bb, ab); glVertex2f(x + w, y + h)
        glColor4f(rb, gb, bb, ab); glVertex2f(x, y + h)
        glEnd()
        glEnable(GL_TEXTURE_2D)

    def draw_circle(self, cx, cy, radius, color, filled=True, segments=24, border_width=1):
        glDisable(GL_TEXTURE_2D)
        self._set_color(color)

        mode = GL_TRIANGLE_FAN if filled else GL_LINE_LOOP
        if not filled:
            glLineWidth(border_width)
        glBegin(mode)
        if filled:
            glVertex2f(cx, cy)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            glVertex2f(cx + math.cos(theta) * radius, cy + math.sin(theta) * radius)
        glEnd()
        glEnable(GL_TEXTURE_2D)

    def _rounded_rect_points(self, x, y, w, h, radius, segments=6):
        radius = max(0, min(radius, w / 2.0, h / 2.0))
        corners = [
            (x + w - radius, y + radius, -90, 0),
            (x + w - radius, y + h - radius, 0, 90),
            (x + radius, y + h - radius, 90, 180),
            (x + radius, y + radius, 180, 270),
        ]
        points = []
        for ccx, ccy, start_deg, end_deg in corners:
            for i in range(segments + 1):
                t = start_deg + (end_deg - start_deg) * (i / segments)
                theta = math.radians(t)
                points.append((ccx + math.cos(theta) * radius, ccy + math.sin(theta) * radius))
        return points

    def draw_rounded_rect(self, x, y, w, h, color, radius=8, filled=True, border_width=1):
        if radius <= 0:
            self.draw_rect(x, y, w, h, color, filled=filled, border_width=border_width)
            return

        points = self._rounded_rect_points(x, y, w, h, radius)

        glDisable(GL_TEXTURE_2D)
        self._set_color(color)

        if filled:
            cx = x + w / 2.0
            cy = y + h / 2.0
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx, cy)
            for px, py in points:
                glVertex2f(px, py)
            glVertex2f(points[0][0], points[0][1])
            glEnd()
        else:
            glLineWidth(border_width)
            glBegin(GL_LINE_LOOP)
            for px, py in points:
                glVertex2f(px, py)
            glEnd()

        glEnable(GL_TEXTURE_2D)

    def draw_panel(self, x, y, w, h, bg_color, border_color=None, border_width=2, radius=10,
                   shadow=True, shadow_offset=(4, 5), shadow_color=(0, 0, 0, 90)):
        if shadow:
            sx, sy = shadow_offset
            self.draw_rounded_rect(x + sx, y + sy, w, h, shadow_color, radius=radius)
        self.draw_rounded_rect(x, y, w, h, bg_color, radius=radius, filled=True)
        if border_color is not None:
            self.draw_rounded_rect(x, y, w, h, border_color, radius=radius, filled=False, border_width=border_width)

    def draw_vignette(self, strength=90):
        w, h = self.width, self.height
        t = 90
        a = max(0, min(180, int(strength)))
        self.draw_vertical_gradient(0, 0, w, t, (0, 0, 0, a), (0, 0, 0, 0))
        self.draw_vertical_gradient(0, h - t, w, t, (0, 0, 0, 0), (0, 0, 0, a))
        self.draw_rect(0, 0, t, h, (0, 0, 0, int(a * 0.55)))
        self.draw_rect(w - t, 0, t, h, (0, 0, 0, int(a * 0.55)))

    def draw_glow_rect(self, x, y, w, h, color, layers=4, spread=6):
        r, g, b = color[0], color[1], color[2]
        base_a = color[3] if len(color) > 3 else 80
        for i in range(layers, 0, -1):
            s = i * spread
            a = int(base_a * (i / layers) * 0.35)
            self.draw_rounded_rect(x - s, y - s, w + s * 2, h + s * 2, (r, g, b, a), radius=12 + s // 2)

    def get_font(self, size=20, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            try:
                self.fonts[key] = pygame.font.SysFont("Segoe UI", size, bold=bold)
            except Exception:
                self.fonts[key] = pygame.font.Font(None, size)
        return self.fonts[key]

    def draw_text(self, text, x, y, color=(255, 255, 255), size=20, bold=False, center_x=False, center_y=False):
        if not text:
            return 0, 0

        cache_key = (text, size, bold, color)
        if cache_key in self.text_texture_cache:
            tex_id, tw, th = self.text_texture_cache[cache_key]
        else:
            font = self.get_font(size, bold)
            surface = font.render(text, True, color[:3])
            tex_id, tw, th = self.create_texture(surface)
            if len(self.text_texture_cache) > 500:
                self.clear_text_cache()
            self.text_texture_cache[cache_key] = (tex_id, tw, th)

        draw_x = x - (tw / 2.0) if center_x else x
        draw_y = y - (th / 2.0) if center_y else y

        self.draw_texture(tex_id, draw_x, draw_y, tw, th)
        return tw, th

    def measure_text(self, text, size=20, bold=False):
        font = self.get_font(size, bold)
        return font.size(text)

    def clear_text_cache(self):
        for tex_id, _, _ in self.text_texture_cache.values():
            try:
                glDeleteTextures(1, [tex_id])
            except Exception:
                pass
        self.text_texture_cache.clear()
