"""
Módulo de Entidades (Player, Professor e Interativos).
"""

import pygame
from game.config import TILE_SIZE


def _draw_name_plate(gl, text, center_x, y, color):
    """Etiqueta flutuante com fundo escuro para o nome ficar legível sobre o cenário."""
    tw, th = gl.measure_text(text, size=13, bold=True)
    gl.draw_rounded_rect(center_x - tw / 2 - 6, y - 2, tw + 12, th + 4,
                         (26, 18, 30, 190), radius=6)
    gl.draw_text(text, center_x, y, color=color, size=13, bold=True, center_x=True)


class Player:
    def __init__(self, x, y, name="Estudante"):
        self.x = float(x)
        self.y = float(y)
        self.width = 32
        self.height = 48
        self.name = name
        self.speed = 175.0 # pixels por segundo
        self.direction = "down"
        self.is_moving = False
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.step_sound_timer = 0.0

    @property
    def hitbox(self):
        """Hitbox dos pés do personagem para colisão com profundidade 2D."""
        return pygame.Rect(int(self.x + 6), int(self.y + 32), 20, 14)

    def update(self, dt, dx, dy, world, sound_manager):
        """Atualiza a posição com movimentação suave e verificação de colisão AABB."""
        self.is_moving = (dx != 0 or dy != 0)

        # Normaliza vetor diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Determina direção
        if abs(dx) > abs(dy):
            self.direction = "left" if dx < 0 else "right"
        elif dy != 0:
            self.direction = "up" if dy < 0 else "down"

        # Movimento com colisão separada no eixo X e Y
        if dx != 0:
            new_x = self.x + dx * self.speed * dt
            test_rect = pygame.Rect(int(new_x + 6), int(self.y + 32), 20, 14)
            if not world.check_collision(test_rect):
                self.x = new_x

        if dy != 0:
            new_y = self.y + dy * self.speed * dt
            test_rect = pygame.Rect(int(self.x + 6), int(new_y + 32), 20, 14)
            if not world.check_collision(test_rect):
                self.y = new_y

        # Animação de passos
        if self.is_moving:
            self.anim_timer += dt * 8
            self.anim_frame = (int(self.anim_timer) % 2) + 1 # alterna 1 e 2
            self.step_sound_timer += dt
            if self.step_sound_timer > 0.32:
                sound_manager.play("step")
                self.step_sound_timer = 0.0
        else:
            self.anim_frame = 0
            self.anim_timer = 0.0

    def draw(self, gl, assets):
        # Sombra projetada nos pés
        gl.draw_texture(assets.textures["shadow"], self.x + 4, self.y + 39, 24, 9)

        frames = assets.player_frames.get(self.direction, assets.player_frames["down"])
        tex_id = frames[self.anim_frame]
        gl.draw_texture(tex_id, self.x, self.y, self.width, self.height)

        _draw_name_plate(gl, self.name, self.x + 16, self.y - 14, (255, 236, 170))


class Teacher:
    def __init__(self, x, y, name="Prof. Roberto"):
        self.x = float(x)
        self.y = float(y)
        self.width = 32
        self.height = 48
        self.name = name
        self.anim_timer = 0.0
        self.anim_frame = 0

    @property
    def hitbox(self):
        return pygame.Rect(int(self.x + 6), int(self.y + 30), 20, 16)

    def update(self, dt):
        self.anim_timer += dt
        # Piscar / respirar suavemente
        self.anim_frame = 1 if (int(self.anim_timer * 1.5) % 4 == 0) else 0

    def draw(self, gl, assets):
        # Sombra projetada nos pés
        gl.draw_texture(assets.textures["shadow"], self.x + 4, self.y + 39, 24, 9)

        tex_id = assets.teacher_frames[self.anim_frame]
        gl.draw_texture(tex_id, self.x, self.y, self.width, self.height)

        _draw_name_plate(gl, "Prof. Roberto (Matemática)", self.x + 16, self.y - 14, (150, 226, 255))


class Interactable:
    def __init__(self, x, y, w, h, itype, label, message=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.itype = itype
        self.label = label
        self.message = message

    def is_near(self, player_rect, max_dist=42):
        """Verifica se o jogador está próximo o suficiente para interagir."""
        # Expande o retângulo para área de gatilho
        trigger_zone = self.rect.inflate(max_dist * 2, max_dist * 2)
        return trigger_zone.colliderect(player_rect)
