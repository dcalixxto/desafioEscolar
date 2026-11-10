"""
Módulo do Mundo Escolar (Corredores, Salas por Matéria e Colisões).
"""

import pygame
from game.config import TILE_SIZE, SUBJECTS, SUBJECTS_BY_ZONE, SUBJECT_MATH
from game.entities import Interactable, Teacher, StudentNPC

ZONE_HALLWAY = "HALLWAY"
ZONE_CLASSROOM = "CLASSROOM_MATH"  # compatibilidade legado (matemática)

class SchoolWorld:
    BENCH_XS = [160, 300, 640, 780]
    SOUTH_PLANT_XS = [96, 900]
    RUG_Y = 288
    RUG_X0 = 64
    RUG_X1 = 1024

    DESK_COLS_X = [160, 352, 544, 736]
    DESK_ROWS_Y = [220, 296, 372]
    CLASS_DOOR_X = 448
    TEACHER_DESK = (176, 112)
    BOOKSHELF_X = 864
    BOARD_X = 288
    CLASS_PLANT_XS = [40, 880]

    def __init__(self):
        self.current_zone = ZONE_HALLWAY
        self.current_subject = None
        self.teacher = Teacher(320, 110, name="Prof. Roberto", subject_label="Matemática", subject_id=SUBJECT_MATH)
        self.students = []
        self.solids = []
        self.interactables = []
        self.zone_w = 0
        self.zone_h = 0
        self._build_current_zone()

    def set_zone(self, zone_id, player=None, subject_id=None):
        # compatibilidade com testes/código antigo
        if zone_id == "CLASSROOM":
            zone_id = ZONE_CLASSROOM
        self.current_zone = zone_id
        self.current_subject = subject_id or SUBJECTS_BY_ZONE.get(zone_id)
        self._build_current_zone()
        if player is not None:
            if self.current_zone == ZONE_HALLWAY:
                if self.current_subject and self.current_subject in SUBJECTS:
                    player.x = SUBJECTS[self.current_subject]["hall_x"] + 16
                elif subject_id and subject_id in SUBJECTS:
                    player.x = SUBJECTS[subject_id]["hall_x"] + 16
                else:
                    player.x = 736
                player.y = 200
                player.direction = "down"
            else:
                player.x = self.CLASS_DOOR_X
                player.y = 440
                player.direction = "up"

    def _build_current_zone(self):
        self.solids.clear()
        self.interactables.clear()
        self.students.clear()

        if self.current_zone == ZONE_HALLWAY:
            self._build_hallway()
        else:
            self._build_classroom()

    def _build_hallway(self):
        cols = 34
        rows = 17
        self.zone_w = cols * TILE_SIZE
        self.zone_h = rows * TILE_SIZE

        self.solids.append(pygame.Rect(0, 0, self.zone_w, TILE_SIZE * 3))
        self.solids.append(pygame.Rect(0, self.zone_h - TILE_SIZE, self.zone_w, TILE_SIZE))
        self.solids.append(pygame.Rect(0, 0, TILE_SIZE, self.zone_h))
        self.solids.append(pygame.Rect(self.zone_w - TILE_SIZE, 0, TILE_SIZE, self.zone_h))

        for sid, cfg in SUBJECTS.items():
            hx = cfg["hall_x"]
            self.interactables.append(Interactable(
                hx, TILE_SIZE * 2, 64, 32, cfg["door_type"],
                cfg["door_label"],
                f"Entrando na {cfg['name']}..."
            ))

        for lx in [600, 632, 800, 832, 864]:
            self.solids.append(pygame.Rect(lx, TILE_SIZE * 2 + 10, 32, 22))

        self.solids.append(pygame.Rect(200, TILE_SIZE * 2 + 10, 32, 22))
        self.interactables.append(Interactable(
            200, TILE_SIZE * 2 + 10, 32, 32, "INFO",
            "Bebedouro Escolar",
            "Bebedouro: água fresca e gelada! Hidrate-se antes dos desafios."
        ))

        self.interactables.append(Interactable(
            384, 52, 48, 40, "INFO",
            "Mural de Avisos",
            "Mural Escolar: 'Todas as salas estão abertas! Enfrente os desafios de Matemática, História, Geografia e Biologia.'\nDica: se errar uma questão, um Espírito da Dúvida pode aparecer para um duelo de conhecimento!"
        ))

        for px in [40, 980]:
            self.solids.append(pygame.Rect(px, TILE_SIZE * 2 + 10, 32, 22))

        bench_y = self.zone_h - TILE_SIZE - 26
        for bx in self.BENCH_XS:
            self.solids.append(pygame.Rect(bx + 2, bench_y + 12, 60, 16))
            self.interactables.append(Interactable(
                bx, bench_y, 64, 30, "INFO",
                "Banco do Corredor",
                "Banco de madeira: um ótimo lugar para revisar a matéria antes da avaliação."
            ))

        for px in self.SOUTH_PLANT_XS:
            self.solids.append(pygame.Rect(px, self.zone_h - TILE_SIZE - 24, 30, 20))

        # Alunos conversando e andando no corredor
        hall_area = pygame.Rect(48, 140, self.zone_w - 96, self.zone_h - 220)
        self.students = [
            StudentNPC(180, 260, name="Ana",   style="ana",   wander_rect=hall_area),
            StudentNPC(260, 300, name="Bruno", style="bruno", wander_rect=hall_area),
            StudentNPC(520, 250, name="Clara", style="clara", wander_rect=hall_area),
            StudentNPC(760, 320, name="Diego", style="diego", wander_rect=hall_area),
            StudentNPC(900, 260, name="Eva",   style="eva",   wander_rect=hall_area),
        ]

    def _build_classroom(self):
        sid = self.current_subject or SUBJECT_MATH
        cfg = SUBJECTS[sid]

        cols = 30
        rows = 17
        self.zone_w = cols * TILE_SIZE
        self.zone_h = rows * TILE_SIZE

        self.solids.append(pygame.Rect(0, 0, self.zone_w, TILE_SIZE * 3))
        self.solids.append(pygame.Rect(0, self.zone_h - TILE_SIZE, self.zone_w, TILE_SIZE))
        self.solids.append(pygame.Rect(0, 0, TILE_SIZE, self.zone_h))
        self.solids.append(pygame.Rect(self.zone_w - TILE_SIZE, 0, TILE_SIZE, self.zone_h))

        self.interactables.append(Interactable(
            self.BOARD_X, TILE_SIZE, 128, 64, "INFO",
            cfg["board_title"],
            cfg["board_text"]
        ))

        desk_x, desk_y = self.TEACHER_DESK
        self.solids.append(pygame.Rect(desk_x, desk_y + 10, 64, 28))

        self.teacher.x = 264
        self.teacher.y = 100
        self.teacher.name = cfg["teacher"]
        self.teacher.subject_label = cfg["name"]
        self.teacher.subject_id = sid
        self.solids.append(self.teacher.hitbox)
        self.interactables.append(Interactable(
            int(self.teacher.x - 10), int(self.teacher.y - 10), 52, 68, "TEACHER",
            f"Falar com {cfg['teacher']}",
            f"Diálogo com {cfg['teacher']} de {cfg['name']}",
            subject=sid
        ))

        door_exit_x = self.CLASS_DOOR_X
        door_exit_y = self.zone_h - TILE_SIZE * 2
        self.interactables.append(Interactable(
            door_exit_x, door_exit_y, 64, 32, "DOOR_EXIT",
            "Sair para o Corredor",
            "Voltando para o corredor escolar..."
        ))

        for col_i, cx in enumerate(self.DESK_COLS_X):
            for row_i, cy in enumerate(self.DESK_ROWS_Y):
                self.solids.append(pygame.Rect(cx + 2, cy + 12, 28, 24))
                if col_i == 1 and row_i == 1:
                    self.interactables.append(Interactable(
                        cx, cy, 32, 36, "INFO",
                        "Sua Carteira Escolar",
                        f"Seu caderno de {cfg['name']} está aberto com anotações e exercícios."
                    ))

        self.solids.append(pygame.Rect(self.BOOKSHELF_X, 200, 32, 28))
        self.interactables.append(Interactable(
            self.BOOKSHELF_X, 180, 32, 48, "INFO",
            "Estante de Livros",
            f"Livros e materiais de {cfg['name']} para estudo e consulta."
        ))

        for px in self.CLASS_PLANT_XS:
            self.solids.append(pygame.Rect(px + 8, self.zone_h - TILE_SIZE * 2 - 24, 16, 17))

        # Alunos na sala (conversando/andando entre carteiras)
        class_area = pygame.Rect(64, 180, self.zone_w - 128, self.zone_h - 280)
        self.students = [
            StudentNPC(300, 330, name="Léo", style="leo", wander_rect=class_area),
            StudentNPC(520, 360, name="Mia", style="mia", wander_rect=class_area),
        ]

    def check_collision(self, rect):
        for solid in self.solids:
            if rect.colliderect(solid):
                return True
        return False

    def get_nearby_interactable(self, player_rect):
        nearest = None
        min_dist = 999999
        for item in self.interactables:
            if item.is_near(player_rect):
                dist = (item.rect.centerx - player_rect.centerx) ** 2 + (item.rect.centery - player_rect.centery) ** 2
                if dist < min_dist:
                    min_dist = dist
                    nearest = item
        return nearest

    def draw_background(self, gl, assets):
        if self.current_zone == ZONE_HALLWAY:
            self._draw_hallway_tiles(gl, assets)
        else:
            self._draw_classroom_tiles(gl, assets)

    def update_students(self, dt):
        for s in self.students:
            s.update(dt, self)
        # interações de conversa entre alunos próximos
        for i in range(len(self.students)):
            for j in range(i + 1, len(self.students)):
                self.students[i].maybe_chat_with(self.students[j])

    def draw_students(self, gl, assets):
        # desenha por y para profundidade simples
        for s in sorted(self.students, key=lambda st: st.y):
            s.draw(gl, assets)

    @staticmethod
    def _floor_variant(x, y):
        v = (x * 7 + y * 13) % 11
        if v == 3:
            return 1
        if v == 8:
            return 2
        return 0

    def _draw_room_tiles(self, gl, assets, floor_prefix):
        wall_tex = assets.textures["wall"]
        base_tex = assets.textures["wall_base"]
        cols = self.zone_w // TILE_SIZE
        rows = self.zone_h // TILE_SIZE

        for y in range(rows):
            for x in range(cols):
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                is_wall = (y < 3 or y == rows - 1 or x == 0 or x == cols - 1)
                if is_wall:
                    tex = base_tex if (y == 2 and 0 < x < cols - 1) else wall_tex
                    gl.draw_texture(tex, px, py, TILE_SIZE, TILE_SIZE)
                else:
                    variant = self._floor_variant(x, y)
                    gl.draw_texture(assets.textures[f"{floor_prefix}_{variant}"], px, py, TILE_SIZE, TILE_SIZE)

        gl.draw_rect(TILE_SIZE, TILE_SIZE * 3, self.zone_w - TILE_SIZE * 2, 7, (26, 18, 30, 55))
        gl.draw_rect(TILE_SIZE, TILE_SIZE * 3, 6, self.zone_h - TILE_SIZE * 4, (26, 18, 30, 40))
        gl.draw_rect(self.zone_w - TILE_SIZE - 6, TILE_SIZE * 3, 6, self.zone_h - TILE_SIZE * 4, (26, 18, 30, 40))
        # detalhes de parede e luz ambiente
        for lx in range(TILE_SIZE * 2, self.zone_w - TILE_SIZE * 2, 160):
            gl.draw_rect(lx, TILE_SIZE * 3 + 10, 22, 3, (255, 244, 210, 40))
            gl.draw_rect(lx + 2, TILE_SIZE * 3 + 10, 18, 1, (255, 250, 230, 60))
        for y in range(TILE_SIZE * 4 + 12, self.zone_h - TILE_SIZE - 12, 96):
            gl.draw_rect(TILE_SIZE + 10, y, 2, 18, (255, 255, 255, 18))
            gl.draw_rect(self.zone_w - TILE_SIZE - 12, y, 2, 18, (255, 255, 255, 18))

    @staticmethod
    def _draw_prop(gl, assets, tex_key, x, y, w, h, shadow_w=None, shadow_h=9):
        if shadow_w is None:
            shadow_w = w
        gl.draw_texture(assets.textures["shadow"], x + (w - shadow_w) / 2, y + h - shadow_h / 2 - 2, shadow_w, shadow_h)
        gl.draw_texture(assets.textures[tex_key], x, y, w, h)

    def _draw_hallway_tiles(self, gl, assets):
        self._draw_room_tiles(gl, assets, "floor_hallway")

        rug_tex = assets.textures["rug_runner"]
        for rx in range(self.RUG_X0, self.RUG_X1, 32):
            gl.draw_texture(rug_tex, rx, self.RUG_Y, 32, 96)

        for wx in (176, 560, 900):
            gl.draw_texture(assets.textures["window"], wx, TILE_SIZE + 4, 64, 44)
            gl.draw_rect(wx + 8, TILE_SIZE + 52, 48, 4, (255, 255, 255, 22))
        gl.draw_texture(assets.textures["bulletin"], 384, 52, 48, 40)
        gl.draw_texture(assets.textures["clock"], 660, TILE_SIZE + 10, 28, 28)
        gl.draw_texture(assets.textures["decal_trophy"], 720, 58, 20, 22)
        gl.draw_texture(assets.textures["decal_map"], 120, 56, 24, 18)

        for sid, cfg in SUBJECTS.items():
            gl.draw_texture(assets.textures[cfg["door_texture"]], cfg["hall_x"], TILE_SIZE, 64, 64)
            gl.draw_rect(cfg["hall_x"] + 6, TILE_SIZE + 68, 52, 3, (255, 255, 255, 20))

        for lx in [600, 632, 800, 832, 864]:
            self._draw_prop(gl, assets, "lockers", lx, TILE_SIZE * 2 - 16, 32, 48, shadow_w=30)
        # pequenos detalhes nos armarios
        gl.draw_texture(assets.textures["decal_note"], 608, TILE_SIZE * 2 - 2, 12, 14)
        gl.draw_texture(assets.textures["decal_paper"], 846, TILE_SIZE * 2 + 2, 14, 12)

        self._draw_prop(gl, assets, "water_cooler", 200, TILE_SIZE * 2 - 2, 32, 34, shadow_w=24)
        for px in [40, 980]:
            self._draw_prop(gl, assets, "plant", px, TILE_SIZE * 2 - 8, 32, 40, shadow_w=26)
        self._draw_prop(gl, assets, "plant", 350, TILE_SIZE * 2 - 10, 32, 40, shadow_w=24)

        bench_y = self.zone_h - TILE_SIZE - 26
        for bx in self.BENCH_XS:
            self._draw_prop(gl, assets, "bench", bx, bench_y, 64, 30, shadow_w=58)
        for px in self.SOUTH_PLANT_XS:
            self._draw_prop(gl, assets, "plant", px, self.zone_h - TILE_SIZE - 42, 32, 40, shadow_w=26)
        self._draw_prop(gl, assets, "plant", 500, self.zone_h - TILE_SIZE - 44, 32, 40, shadow_w=24)

        # detalhes de chao/ambiente
        for (dx, dy, key, w, h) in [
            (262, 208, "decal_shine", 22, 9), (736, 430, "decal_shine", 22, 9), (420, 420, "decal_shine", 22, 9),
            (470, 240, "decal_paper", 14, 12), (690, 250, "decal_note", 12, 14), (150, 410, "decal_leaf", 10, 8),
            (890, 214, "decal_pencil", 12, 5), (540, 445, "decal_pencil", 12, 5), (820, 350, "decal_paper", 14, 12),
        ]:
            gl.draw_texture(assets.textures[key], dx, dy, w, h)

    def _draw_classroom_tiles(self, gl, assets):
        self._draw_room_tiles(gl, assets, "floor_classroom")
        sid = self.current_subject or SUBJECT_MATH
        cfg = SUBJECTS[sid]

        gl.draw_texture(assets.textures["blackboard"], self.BOARD_X, TILE_SIZE, 128, 64)
        for wx in (64, 600, 800):
            gl.draw_texture(assets.textures["window"], wx, TILE_SIZE + 4, 64, 44)
            gl.draw_rect(wx + 10, TILE_SIZE + 52, 44, 4, (255, 255, 255, 20))

        # posters e relogio (mais ricos e tematicos)
        poster_key = f"poster_{sid}" if f"poster_{sid}" in assets.textures else "poster_math"
        gl.draw_texture(assets.textures[poster_key], 500, TILE_SIZE + 6, 32, 40)
        gl.draw_texture(assets.textures["poster_math"], 540, TILE_SIZE + 8, 28, 36)
        gl.draw_texture(assets.textures["clock"], 440, TILE_SIZE + 8, 28, 28)
        gl.draw_texture(assets.textures["bulletin"], 700, TILE_SIZE + 6, 40, 34)
        gl.draw_texture(assets.textures["decal_trophy"], 748, TILE_SIZE + 10, 18, 20)

        self._draw_prop(gl, assets, "teacher_desk", *self.TEACHER_DESK, 64, 40, shadow_w=58)
        self._draw_prop(gl, assets, "bookshelf", self.BOOKSHELF_X, 180, 32, 48, shadow_w=30)
        # livros/objetos decorativos na estante e mesa
        gl.draw_texture(assets.textures["decal_note"], self.TEACHER_DESK[0] + 38, self.TEACHER_DESK[1] - 2, 10, 12)
        gl.draw_texture(assets.textures["decal_paper"], self.BOOKSHELF_X + 4, 176, 12, 10)

        for cx in self.DESK_COLS_X:
            for cy in self.DESK_ROWS_Y:
                self._draw_prop(gl, assets, "student_desk", cx, cy, 32, 36, shadow_w=26)
        # cadernos/itens sobre algumas carteiras
        for (dx, dy, key) in [(166, 226, "decal_note"), (358, 302, "decal_pencil"), (550, 378, "decal_paper"), (742, 228, "decal_note")]:
            gl.draw_texture(assets.textures[key], dx, dy, 12 if key!="decal_pencil" else 12, 12 if key!="decal_pencil" else 5)

        for px in self.CLASS_PLANT_XS:
            self._draw_prop(gl, assets, "plant", px, self.zone_h - TILE_SIZE * 2 - 48, 32, 40, shadow_w=26)
        self._draw_prop(gl, assets, "plant", 120, self.zone_h - TILE_SIZE * 2 - 46, 32, 40, shadow_w=24)
        gl.draw_texture(assets.textures["door_exit"], self.CLASS_DOOR_X, self.zone_h - TILE_SIZE * 2, 64, 64)

        # detalhes tematicos por materia
        self._draw_classroom_subject_details(gl, assets, sid)

        # detalhes gerais de chao
        for (dx, dy, key, w, h) in [
            (300, 460, "decal_paper", 14, 12), (620, 200, "decal_pencil", 12, 5), (220, 430, "decal_shine", 22, 9),
            (520, 470, "decal_shine", 22, 9), (760, 300, "decal_leaf", 10, 8), (420, 180, "decal_note", 12, 14),
        ]:
            if key in assets.textures:
                gl.draw_texture(assets.textures[key], dx, dy, w, h)

    def _draw_classroom_subject_details(self, gl, assets, sid):
        # detalhes visuais extras por materia (sem colisao/logica)
        if sid == "math":
            gl.draw_texture(assets.textures.get("poster_math", assets.textures["poster_math"]), 120, TILE_SIZE + 8, 30, 38)
            gl.draw_texture(assets.textures["decal_note"], 250, TILE_SIZE + 18, 12, 14)
            gl.draw_rect(310, TILE_SIZE + 22, 40, 20, (255,255,255,18))
        elif sid == "history":
            gl.draw_texture(assets.textures.get("poster_history", assets.textures["poster_math"]), 120, TILE_SIZE + 8, 30, 38)
            gl.draw_texture(assets.textures["decal_scroll"], 430, 140, 14, 16)
            gl.draw_texture(assets.textures["decal_map"], 820, 58, 24, 18)
            gl.draw_texture(assets.textures["decal_trophy"], 96, 168, 18, 20)
        elif sid == "geography":
            gl.draw_texture(assets.textures.get("poster_geo", assets.textures["poster_math"]), 120, TILE_SIZE + 8, 30, 38)
            gl.draw_texture(assets.textures["decal_globe"], 248, 126, 18, 18)
            gl.draw_texture(assets.textures["decal_map"], 560, 50, 24, 18)
            gl.draw_texture(assets.textures["decal_leaf"], 700, 420, 10, 8)
        elif sid == "biology":
            gl.draw_texture(assets.textures.get("poster_bio", assets.textures["poster_math"]), 120, TILE_SIZE + 8, 30, 38)
            gl.draw_texture(assets.textures["decal_tube"], 248, 126, 10, 18)
            gl.draw_texture(assets.textures["decal_leaf"], 420, 150, 10, 8)
            gl.draw_texture(assets.textures["decal_leaf"], 760, 430, 10, 8)
            gl.draw_texture(assets.textures["plant"], 808, 120, 28, 34)
