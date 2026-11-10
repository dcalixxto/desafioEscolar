"""
Módulo de Entidades (Player, Professor e Interativos).
"""

import pygame
from game.config import TILE_SIZE


def _draw_name_plate(gl, text, center_x, y, color):
    tw, th = gl.measure_text(text, size=13, bold=True)
    gl.draw_rounded_rect(center_x - tw / 2 - 6, y - 2, tw + 12, th + 4, (26, 18, 30, 190), radius=6)
    gl.draw_text(text, center_x, y, color=color, size=13, bold=True, center_x=True)


class Player:
    def __init__(self, x, y, name="Estudante", gender="masculino"):
        self.x = float(x)
        self.y = float(y)
        self.width = 32
        self.height = 48
        self.name = name
        self.gender = gender
        self.speed = 175.0
        self.direction = "down"
        self.is_moving = False
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.step_sound_timer = 0.0

    @property
    def hitbox(self):
        return pygame.Rect(int(self.x + 6), int(self.y + 32), 20, 14)

    def update(self, dt, dx, dy, world, sound_manager):
        self.is_moving = (dx != 0 or dy != 0)
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        if abs(dx) > abs(dy):
            self.direction = "left" if dx < 0 else "right"
        elif dy != 0:
            self.direction = "up" if dy < 0 else "down"

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

        if self.is_moving:
            self.anim_timer += dt * 8
            self.anim_frame = (int(self.anim_timer) % 2) + 1
            self.step_sound_timer += dt
            if self.step_sound_timer > 0.32:
                sound_manager.play("step")
                self.step_sound_timer = 0.0
        else:
            self.anim_frame = 0
            self.anim_timer = 0.0

    def draw(self, gl, assets):
        gl.draw_texture(assets.textures["shadow"], self.x + 4, self.y + 39, 24, 9)
        pf = getattr(assets, "player_frames_by_gender", None)
        if pf and self.gender in pf:
            frames = pf[self.gender].get(self.direction, pf[self.gender]["down"])
        else:
            frames = assets.player_frames.get(self.direction, assets.player_frames["down"])
        tex_id = frames[self.anim_frame]
        gl.draw_texture(tex_id, self.x, self.y, self.width, self.height)
        _draw_name_plate(gl, self.name, self.x + 16, self.y - 14, (255, 236, 170))


class Teacher:
    def __init__(self, x, y, name="Prof. Roberto", subject_label="Matemática", subject_id="math"):
        self.x = float(x)
        self.y = float(y)
        self.width = 32
        self.height = 48
        self.name = name
        self.subject_label = subject_label
        self.subject_id = subject_id
        self.anim_timer = 0.0
        self.anim_frame = 0

    @property
    def hitbox(self):
        return pygame.Rect(int(self.x + 6), int(self.y + 30), 20, 16)

    def update(self, dt):
        self.anim_timer += dt
        self.anim_frame = 1 if (int(self.anim_timer * 1.5) % 4 == 0) else 0

    def draw(self, gl, assets):
        gl.draw_texture(assets.textures["shadow"], self.x + 4, self.y + 39, 24, 9)
        frames = None
        if hasattr(assets, "teacher_frames_by_subject"):
            frames = assets.teacher_frames_by_subject.get(getattr(self, "subject_id", "math"))
        if not frames:
            frames = getattr(assets, "teacher_frames", [])
        tex_id = frames[self.anim_frame] if frames else 0
        if tex_id:
            gl.draw_texture(tex_id, self.x, self.y, self.width, self.height)
        label = f"{self.name} ({self.subject_label})"
        _draw_name_plate(gl, label, self.x + 16, self.y - 14, (150, 226, 255))


class StudentNPC:
    """Aluno NPC que anda pela escola e conversa com outros alunos."""
    CHAT_LINES = [
        "Oi!", "E aí?", "Tudo bem?", "Beleza?", "Bom dia!", "Boa tarde!",
        "Bora estudar?", "Vamos revisar?", "Você estudou pra prova?", "Essa prova tá difícil...",
        "Você entendeu a matéria?", "Me explica essa parte?", "Preciso de ajuda!", "Valeu pela dica!",
        "Boa sorte no desafio!", "Boa sorte na prova!", "Hoje tô confiante!", "Tô um pouco nervoso...",
        "Vamos pra sala?", "Qual sala agora?", "Corre que vai começar!", "A aula já vai começar!",
        "Que legal!", "Muito bom!", "Show!", "Haha!", "Rsrs!", "Kkk!",
        "Partiu lanche?", "Vamos pro intervalo?", "Tô com fome!", "Cadê meu lanche?",
        "Consegui responder!", "Acertei de primeira!", "Quase acertei!", "Errei, mas aprendi!",
        "O professor é gente boa.", "A professora explica bem!", "Essa aula tá incrível!",
        "Amanhã tem teste!", "Tem lição de casa?", "Você fez a tarefa?", "Esqueci meu caderno...",
        "Cadê meu caderno?", "Cadê meu lápis?", "Empresta uma caneta?", "Tenho que anotar isso!",
        "Vamos revisar juntos?", "Bora fazer o quiz?", "Você já fez o desafio?", "Fui bem no quiz!",
        "Acabei de passar de nível!", "Desbloqueei o próximo nível!", "Quero fechar todas as matérias!",
        "Matemática é treino!", "História é incrível!", "Geografia eu gosto!", "Biologia é demais!",
        "O Espírito da Dúvida apareceu!", "Venci a dúvida!", "Vou tentar de novo!",
        "Você viu o mural?", "Olha o quadro!", "Que mapa legal!", "Adorei o experimento!",
        "Tô com sono...", "Preciso de água!", "Vamos no bebedouro?", "Senta aqui!",
        "Até já!", "Tchau!", "Falou!", "Nos vemos na próxima aula!",
        "Essa questão é fácil!", "Essa questão é complicada!", "Pensa com calma!", "Não desiste!",
        "Você é bom nisso!", "Mandou bem!", "Arrasou!", "Orgulho da turma!",
        "Vamos explorar a escola?", "Todas as salas estão abertas!", "Que dia legal!",
    ]
    CHAT_PAIRS = [
        ("Oi, tudo bem?", "Tudo ótimo! E você?"),
        ("E aí, beleza?", "Beleza!"),
        ("Bom dia!", "Bom dia! Vamos estudar?"),
        ("Vamos estudar juntos?", "Bora sim!"),
        ("Bora revisar a matéria?", "Claro, me ajuda nessa parte?"),
        ("Você entendeu essa questão?", "Mais ou menos, vamos ver!"),
        ("Me explica esse exercício?", "Vamos pensar juntos!"),
        ("Boa prova pra você!", "Valeu, pra você também!"),
        ("Boa sorte no quiz!", "Obrigado! Você também!"),
        ("Qual sala agora?", "A próxima é ali!"),
        ("Vamos pra sala?", "Vamos, tá na hora!"),
        ("Corre que vai começar!", "Tô indo!"),
        ("Você já respondeu o quiz?", "Já, foi legal!"),
        ("Fui bem no desafio!", "Parabéns!"),
        ("Acabei de passar de nível!", "Mandou bem!"),
        ("O Espírito da Dúvida me pegou!", "Sério? Boa sorte!"),
        ("Venci o combate de conhecimento!", "Arrasou!"),
        ("Bora revisar no intervalo?", "Fechado!"),
        ("Partiu lanche?", "Bora!"),
        ("Você fez a lição de casa?", "Fiz sim! E você?"),
        ("Cadê seu caderno?", "Acho que deixei na sala!"),
        ("Você viu o mural?", "Vi sim, tem aviso novo!"),
        ("História é incrível!", "Eu também acho!"),
        ("Matemática é treino!", "Quanto mais pratica, melhor!"),
        ("Geografia é muito legal!", "Adoro ver os mapas!"),
        ("Biologia é demais!", "Os experimentos são top!"),
        ("Essa questão é difícil!", "Com calma a gente consegue!"),
        ("Não desiste!", "Valeu, vou tentar de novo!"),
        ("Até já!", "Tchau!"),
        ("Nos vemos na próxima aula!", "Combinado!"),
    ]

    def __init__(self, x, y, name="Aluno", tint=(255, 255, 255), wander_rect=None, phrases=None, style=None):
        self.x = float(x)
        self.y = float(y)
        self.width = 32
        self.height = 48
        self.name = name
        self.tint = tint
        self.style = (style or name or "aluno").lower()
        self.speed = 55.0
        self.direction = "down"
        self.is_moving = False
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.wander_rect = wander_rect
        self.move_dir = [0, 0]
        self.move_timer = 0.0
        self.pause_timer = 0.0
        self.chat_text = ""
        self.chat_timer = 0.0
        self.chat_cooldown = 1.0
        self.phrases = phrases or self.CHAT_LINES

    @property
    def hitbox(self):
        return pygame.Rect(int(self.x + 6), int(self.y + 32), 20, 14)

    def _pick_new_move(self):
        import random
        choices = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0), (0, 0)]
        self.move_dir = list(random.choice(choices))
        self.move_timer = random.uniform(0.8, 2.4)
        self.pause_timer = random.uniform(0.4, 1.6) if self.move_dir == [0, 0] else 0.0

    def say(self, text=None):
        import random
        self.chat_text = text or random.choice(self.phrases)
        self.chat_timer = random.uniform(2.2, 3.8)
        self.chat_cooldown = random.uniform(2.0, 5.0)

    def update(self, dt, world):
        import random
        if self.chat_timer > 0:
            self.chat_timer -= dt
            if self.chat_timer <= 0:
                self.chat_text = ""
        else:
            self.chat_cooldown -= dt

        if self.move_timer <= 0 and self.pause_timer <= 0:
            self._pick_new_move()
        if self.pause_timer > 0:
            self.pause_timer -= dt
            dx = dy = 0
        else:
            self.move_timer -= dt
            dx, dy = self.move_dir[0], self.move_dir[1]

        self.is_moving = (dx != 0 or dy != 0)
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        if abs(dx) > abs(dy):
            self.direction = "left" if dx < 0 else "right"
        elif dy != 0:
            self.direction = "up" if dy < 0 else "down"

        if dx != 0:
            new_x = self.x + dx * self.speed * dt
            rect = pygame.Rect(int(new_x + 6), int(self.y + 32), 20, 14)
            if not world.check_collision(rect) and (self.wander_rect is None or self.wander_rect.contains(rect)):
                self.x = new_x
            else:
                self.move_dir[0] *= -1
        if dy != 0:
            new_y = self.y + dy * self.speed * dt
            rect = pygame.Rect(int(self.x + 6), int(new_y + 32), 20, 14)
            if not world.check_collision(rect) and (self.wander_rect is None or self.wander_rect.contains(rect)):
                self.y = new_y
            else:
                self.move_dir[1] *= -1

        if self.is_moving:
            self.anim_timer += dt * 7
            self.anim_frame = (int(self.anim_timer) % 2) + 1
        else:
            self.anim_frame = 0
            self.anim_timer = 0.0

        if self.chat_timer <= 0 and self.chat_cooldown <= 0 and random.random() < 0.015:
            self.say()

    def maybe_chat_with(self, other):
        import random
        if self.chat_timer > 0 or other.chat_timer > 0:
            return
        if self.chat_cooldown > 0 or other.chat_cooldown > 0:
            return
        dist2 = (self.x - other.x) ** 2 + (self.y - other.y) ** 2
        if dist2 < 70 * 70 and random.random() < 0.03:
            a, b = random.choice(self.CHAT_PAIRS)
            self.say(a)
            other.say(b)

    def draw(self, gl, assets):
        gl.draw_texture(assets.textures["shadow"], self.x + 4, self.y + 39, 24, 9)
        frames_map = getattr(assets, "student_frames_by_style", {}).get(self.style)
        if frames_map:
            frames = frames_map.get(self.direction, frames_map.get("down"))
            tex_id = frames[self.anim_frame] if frames else 0
            if tex_id:
                gl.draw_texture(tex_id, self.x, self.y, self.width, self.height)
        else:
            frames = assets.player_frames.get(self.direction, assets.player_frames["down"])
            tex_id = frames[self.anim_frame]
            gl.draw_texture(tex_id, self.x, self.y, self.width, self.height, color_tint=(*self.tint, 255))
        _draw_name_plate(gl, self.name, self.x + 16, self.y - 14, (220, 240, 255))
        if self.chat_text:
            text = self.chat_text
            tw, th = gl.measure_text(text, size=12, bold=True)
            bx = self.x + 16 - tw / 2 - 6
            by = self.y - 36
            gl.draw_rounded_rect(bx, by, tw + 12, th + 8, (250, 250, 245, 235), radius=8)
            gl.draw_rounded_rect(bx, by, tw + 12, th + 8, (60, 70, 90), radius=8, filled=False, border_width=1)
            gl.draw_text(text, self.x + 16, by + 4, color=(30, 35, 45), size=12, bold=True, center_x=True)


class Interactable:
    def __init__(self, x, y, w, h, itype, label, message=None, subject=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.itype = itype
        self.label = label
        self.message = message
        self.subject = subject

    def is_near(self, player_rect, max_dist=42):
        trigger_zone = self.rect.inflate(max_dist * 2, max_dist * 2)
        return trigger_zone.colliderect(player_rect)
