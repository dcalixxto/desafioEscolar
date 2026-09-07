"""
Módulo do Mundo Escolar (Corredores, Sala de Matemática e Colisões).
"""

import pygame
from game.config import TILE_SIZE
from game.entities import Interactable, Teacher

ZONE_HALLWAY = "HALLWAY"
ZONE_CLASSROOM = "CLASSROOM"

class SchoolWorld:
    # Posições compartilhadas entre a construção da zona e a renderização
    BENCH_XS = [160, 300, 640, 780]
    SOUTH_PLANT_XS = [96, 900]
    RUG_Y = 288
    RUG_X0 = 64
    RUG_X1 = 1024

    # Sala de aula: grade de carteiras e posições do mobiliário
    DESK_COLS_X = [160, 352, 544, 736]
    DESK_ROWS_Y = [220, 296, 372]
    CLASS_DOOR_X = 448
    TEACHER_DESK = (176, 112)
    BOOKSHELF_X = 864
    BOARD_X = 288
    CLASS_PLANT_XS = [40, 880]

    def __init__(self):
        self.current_zone = ZONE_HALLWAY
        self.teacher = Teacher(320, 110)
        self.solids = []
        self.interactables = []
        self.zone_w = 0
        self.zone_h = 0
        self._build_current_zone()

    def set_zone(self, zone_id, player=None):
        self.current_zone = zone_id
        self._build_current_zone()
        if player is not None:
            if zone_id == ZONE_CLASSROOM:
                # Surge próximo à porta de entrada da sala de aula
                player.x = self.CLASS_DOOR_X
                player.y = 440
                player.direction = "up"
            else:
                # Surge no corredor em frente à porta de matemática
                player.x = 736
                player.y = 200
                player.direction = "down"

    def _build_current_zone(self):
        self.solids.clear()
        self.interactables.clear()

        if self.current_zone == ZONE_HALLWAY:
            self._build_hallway()
        else:
            self._build_classroom()

    def _build_hallway(self):
        """Constrói o Corredor Principal com as 4 salas escolares."""
        # Dimensões do corredor: 34 tiles de largura x 17 tiles de altura
        # (17 fileiras preenchem a altura da janela, sem faixa vazia embaixo)
        cols = 34
        rows = 17
        self.zone_w = cols * TILE_SIZE # 1088 px
        self.zone_h = rows * TILE_SIZE # 544 px

        # Paredes limites (Norte, Sul, Oeste, Leste)
        self.solids.append(pygame.Rect(0, 0, self.zone_w, TILE_SIZE * 3)) # Parede norte
        self.solids.append(pygame.Rect(0, self.zone_h - TILE_SIZE, self.zone_w, TILE_SIZE)) # Parede sul
        self.solids.append(pygame.Rect(0, 0, TILE_SIZE, self.zone_h)) # Parede oeste
        self.solids.append(pygame.Rect(self.zone_w - TILE_SIZE, 0, TILE_SIZE, self.zone_h)) # Parede leste

        # Portas das 4 salas no topo do corredor (Y = TILE_SIZE)
        # 1. Sala de História (Bloqueada)
        hx = 96
        self.interactables.append(Interactable(
            hx, TILE_SIZE * 2, 64, 32, "DOOR_LOCKED",
            "Sala de História",
            "Sala de História: [EM BREVE!]\nEsta sala ainda será inaugurada na escola. Concentre-se na sala de Matemática!"
        ))
        self.solids.append(pygame.Rect(hx, TILE_SIZE * 2, 64, 32))

        # 2. Sala de Geografia (Bloqueada)
        gx = 288
        self.interactables.append(Interactable(
            gx, TILE_SIZE * 2, 64, 32, "DOOR_LOCKED",
            "Sala de Geografia",
            "Sala de Geografia: [EM BREVE!]\nEsta sala ainda será inaugurada na escola. Vá para a sala de Matemática!"
        ))
        self.solids.append(pygame.Rect(gx, TILE_SIZE * 2, 64, 32))

        # 3. Sala de Biologia (Bloqueada)
        bx = 480
        self.interactables.append(Interactable(
            bx, TILE_SIZE * 2, 64, 32, "DOOR_LOCKED",
            "Sala de Biologia",
            "Sala de Biologia: [EM BREVE!]\nEsta sala ainda será inaugurada na escola. Domine a sala de Matemática primeiro!"
        ))
        self.solids.append(pygame.Rect(bx, TILE_SIZE * 2, 64, 32))

        # 4. Sala de Matemática (ABERTA E ACESSÍVEL)
        mx = 704
        self.interactables.append(Interactable(
            mx, TILE_SIZE * 2, 64, 32, "DOOR_MATH",
            "Entrar na Sala de Matemática",
            "Entrando na Sala de Matemática..."
        ))

        # Armários escolares (Lockers) ao longo do corredor
        for lx in [600, 632, 800, 832, 864]:
            self.solids.append(pygame.Rect(lx, TILE_SIZE * 2 + 10, 32, 22))

        # Bebedouro
        self.solids.append(pygame.Rect(200, TILE_SIZE * 2 + 10, 32, 22))
        self.interactables.append(Interactable(
            200, TILE_SIZE * 2 + 10, 32, 32, "INFO",
            "Bebedouro Escolar",
            "Bebedouro: Água fresca e gelada! Mantenha-se hidratado para resolver os desafios matemáticos."
        ))

        # Mural de avisos da escola (alinhado ao mural desenhado na parede)
        self.interactables.append(Interactable(
            384, 52, 48, 40, "INFO",
            "Mural de Avisos",
            "Mural Escolar: 'Atenção alunos: O Professor Roberto está aplicando a avaliação progressiva de Matemática! Vença os 3 níveis para ser o melhor da escola!'"
        ))

        # Plantas decorativas no corredor
        for px in [40, 980]:
            self.solids.append(pygame.Rect(px, TILE_SIZE * 2 + 10, 32, 22))

        # Bancos encostados na parede sul (área de convivência)
        bench_y = self.zone_h - TILE_SIZE - 26
        for bx in self.BENCH_XS:
            self.solids.append(pygame.Rect(bx + 2, bench_y + 12, 60, 16))
            self.interactables.append(Interactable(
                bx, bench_y, 64, 30, "INFO",
                "Banco do Corredor",
                "Banco de madeira: um ótimo lugar para revisar a matéria antes da avaliação."
            ))

        # Plantas grandes junto à parede sul
        for px in self.SOUTH_PLANT_XS:
            self.solids.append(pygame.Rect(px, self.zone_h - TILE_SIZE - 24, 30, 20))

    def _build_classroom(self):
        """Constrói o interior da Sala de Matemática."""
        # 30 x 17 tiles preenchem exatamente a janela (960x544)
        cols = 30
        rows = 17
        self.zone_w = cols * TILE_SIZE # 960 px
        self.zone_h = rows * TILE_SIZE # 544 px

        # Paredes limites
        self.solids.append(pygame.Rect(0, 0, self.zone_w, TILE_SIZE * 3)) # Parede norte (lousa)
        self.solids.append(pygame.Rect(0, self.zone_h - TILE_SIZE, self.zone_w, TILE_SIZE)) # Parede sul
        self.solids.append(pygame.Rect(0, 0, TILE_SIZE, self.zone_h)) # Parede oeste
        self.solids.append(pygame.Rect(self.zone_w - TILE_SIZE, 0, TILE_SIZE, self.zone_h)) # Parede leste

        # Lousa / Quadro-Negro (parede norte)
        self.interactables.append(Interactable(
            self.BOARD_X, TILE_SIZE, 128, 64, "INFO",
            "Quadro-Negro de Matemática",
            "Quadro com anotações do Professor Roberto: Fórmulas de Álgebra, Geometria e Teorema de Pitágoras!"
        ))

        # Mesa do Professor (à esquerda da lousa)
        desk_x, desk_y = self.TEACHER_DESK
        self.solids.append(pygame.Rect(desk_x, desk_y + 10, 64, 28))

        # Posiciona o Professor Roberto ao lado da mesa e lousa
        self.teacher.x = 264
        self.teacher.y = 100
        self.solids.append(self.teacher.hitbox)
        self.interactables.append(Interactable(
            int(self.teacher.x - 10), int(self.teacher.y - 10), 52, 68, "TEACHER",
            "Falar com Prof. Roberto",
            "Diálogo com o Professor de Matemática"
        ))

        # Porta de Saída da sala (na parede sul, volta ao corredor)
        door_exit_x = self.CLASS_DOOR_X
        door_exit_y = self.zone_h - TILE_SIZE * 2
        self.interactables.append(Interactable(
            door_exit_x, door_exit_y, 64, 32, "DOOR_EXIT",
            "Sair para o Corredor",
            "Voltando para o corredor escolar..."
        ))

        # Fileiras de Carteiras Escolares dos Alunos (4 colunas x 3 fileiras)
        # Deixando corredores confortáveis para o estudante caminhar
        for col_i, cx in enumerate(self.DESK_COLS_X):
            for row_i, cy in enumerate(self.DESK_ROWS_Y):
                # Colisão sólida da carteira
                self.solids.append(pygame.Rect(cx + 2, cy + 12, 28, 24))
                # Interação opcional para ler anotações
                if col_i == 1 and row_i == 1:
                    self.interactables.append(Interactable(
                        cx, cy, 32, 36, "INFO",
                        "Sua Carteira Escolar",
                        "Aqui está sua carteira de estudos! Um caderno aberto com rascunhos de cálculos."
                    ))

        # Estante de livros encostada na parede leste
        self.solids.append(pygame.Rect(self.BOOKSHELF_X, 200, 32, 28))
        self.interactables.append(Interactable(
            self.BOOKSHELF_X, 180, 32, 48, "INFO",
            "Estante de Livros",
            "Estante da sala: apostilas de álgebra, geometria e um almanaque de curiosidades matemáticas."
        ))

        # Plantas nos cantos inferiores da sala
        for px in self.CLASS_PLANT_XS:
            self.solids.append(pygame.Rect(px + 8, self.zone_h - TILE_SIZE * 2 - 24, 16, 17))

    def check_collision(self, rect):
        """Verifica se um rect colide com qualquer obstáculo sólido da sala/corredor."""
        for solid in self.solids:
            if rect.colliderect(solid):
                return True
        return False

    def get_nearby_interactable(self, player_rect):
        """Retorna o objeto interativo mais próximo do jogador, se houver."""
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
        """Renderiza os pisos, paredes e elementos estáticos da zona atual."""
        if self.current_zone == ZONE_HALLWAY:
            self._draw_hallway_tiles(gl, assets)
        else:
            self._draw_classroom_tiles(gl, assets)

    @staticmethod
    def _floor_variant(x, y):
        """Escolhe deterministicamente uma variação de piso para quebrar a repetição."""
        v = (x * 7 + y * 13) % 11
        if v == 3:
            return 1
        if v == 8:
            return 2
        return 0

    def _draw_room_tiles(self, gl, assets, floor_prefix):
        """Desenha piso (com variações), paredes com rodapé e sombras de canto."""
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
                    # A terceira fileira encosta no piso: recebe lambril e rodapé
                    tex = base_tex if (y == 2 and 0 < x < cols - 1) else wall_tex
                    gl.draw_texture(tex, px, py, TILE_SIZE, TILE_SIZE)
                else:
                    variant = self._floor_variant(x, y)
                    gl.draw_texture(assets.textures[f"{floor_prefix}_{variant}"],
                                    px, py, TILE_SIZE, TILE_SIZE)

        # Sombra projetada das paredes sobre o piso (dá profundidade ao ambiente)
        gl.draw_rect(TILE_SIZE, TILE_SIZE * 3, self.zone_w - TILE_SIZE * 2, 7, (26, 18, 30, 55))
        gl.draw_rect(TILE_SIZE, TILE_SIZE * 3, 6, self.zone_h - TILE_SIZE * 4, (26, 18, 30, 40))
        gl.draw_rect(self.zone_w - TILE_SIZE - 6, TILE_SIZE * 3, 6,
                     self.zone_h - TILE_SIZE * 4, (26, 18, 30, 40))

    @staticmethod
    def _draw_prop(gl, assets, tex_key, x, y, w, h, shadow_w=None, shadow_h=9):
        """Desenha um objeto com sombra elíptica na base."""
        if shadow_w is None:
            shadow_w = w
        gl.draw_texture(assets.textures["shadow"],
                        x + (w - shadow_w) / 2, y + h - shadow_h / 2 - 2, shadow_w, shadow_h)
        gl.draw_texture(assets.textures[tex_key], x, y, w, h)

    def _draw_hallway_tiles(self, gl, assets):
        self._draw_room_tiles(gl, assets, "floor_hallway")

        # 0. Passadeira que percorre o corredor e quebra o vazio do piso
        rug_tex = assets.textures["rug_runner"]
        for rx in range(self.RUG_X0, self.RUG_X1, 32):
            gl.draw_texture(rug_tex, rx, self.RUG_Y, 32, 96)

        # 1. Janelas com vista externa e decoração de parede
        for wx in (176, 560, 900):
            gl.draw_texture(assets.textures["window"], wx, TILE_SIZE + 4, 64, 44)
        gl.draw_texture(assets.textures["bulletin"], 384, 52, 48, 40)
        gl.draw_texture(assets.textures["clock"], 660, TILE_SIZE + 10, 28, 28)

        # 2. Portas com placas das matérias
        gl.draw_texture(assets.textures["door_history"], 96, TILE_SIZE, 64, 64)
        gl.draw_texture(assets.textures["door_geo"], 288, TILE_SIZE, 64, 64)
        gl.draw_texture(assets.textures["door_bio"], 480, TILE_SIZE, 64, 64)
        gl.draw_texture(assets.textures["door_math"], 704, TILE_SIZE, 64, 64)

        # 3. Armários escolares
        for lx in [600, 632, 800, 832, 864]:
            self._draw_prop(gl, assets, "lockers", lx, TILE_SIZE * 2 - 16, 32, 48, shadow_w=30)

        # 4. Bebedouro e plantas
        self._draw_prop(gl, assets, "water_cooler", 200, TILE_SIZE * 2 - 2, 32, 34, shadow_w=24)
        for px in [40, 980]:
            self._draw_prop(gl, assets, "plant", px, TILE_SIZE * 2 - 8, 32, 40, shadow_w=26)

        # 5. Bancos e plantas da parede sul
        bench_y = self.zone_h - TILE_SIZE - 26
        for bx in self.BENCH_XS:
            self._draw_prop(gl, assets, "bench", bx, bench_y, 64, 30, shadow_w=58)
        for px in self.SOUTH_PLANT_XS:
            self._draw_prop(gl, assets, "plant", px, self.zone_h - TILE_SIZE - 42, 32, 40, shadow_w=26)

        # 6. Detalhes soltos no piso
        gl.draw_texture(assets.textures["decal_shine"], 262, 208, 22, 9)
        gl.draw_texture(assets.textures["decal_paper"], 470, 240, 14, 12)
        gl.draw_texture(assets.textures["decal_pencil"], 890, 214, 12, 5)
        gl.draw_texture(assets.textures["decal_shine"], 736, 430, 22, 9)

    def _draw_classroom_tiles(self, gl, assets):
        self._draw_room_tiles(gl, assets, "floor_classroom")

        # 1. Quadro-negro, janelas e cartaz
        gl.draw_texture(assets.textures["blackboard"], self.BOARD_X, TILE_SIZE, 128, 64)
        for wx in (64, 600, 800):
            gl.draw_texture(assets.textures["window"], wx, TILE_SIZE + 4, 64, 44)
        gl.draw_texture(assets.textures["poster_math"], 500, TILE_SIZE + 6, 32, 40)
        # Relógio à direita da lousa (fora da área coberta pela HUD)
        gl.draw_texture(assets.textures["clock"], 440, TILE_SIZE + 8, 28, 28)

        # 2. Mesa do professor e estante
        self._draw_prop(gl, assets, "teacher_desk", *self.TEACHER_DESK, 64, 40, shadow_w=58)
        self._draw_prop(gl, assets, "bookshelf", self.BOOKSHELF_X, 180, 32, 48, shadow_w=30)

        # 3. Carteiras dos alunos
        for cx in self.DESK_COLS_X:
            for cy in self.DESK_ROWS_Y:
                self._draw_prop(gl, assets, "student_desk", cx, cy, 32, 36, shadow_w=26)

        # 4. Plantas dos cantos e porta de saída
        for px in self.CLASS_PLANT_XS:
            self._draw_prop(gl, assets, "plant", px,
                            self.zone_h - TILE_SIZE * 2 - 48, 32, 40, shadow_w=26)
        gl.draw_texture(assets.textures["door_exit"], self.CLASS_DOOR_X,
                        self.zone_h - TILE_SIZE * 2, 64, 64)

        # 5. Detalhes soltos no piso
        gl.draw_texture(assets.textures["decal_paper"], 300, 460, 14, 12)
        gl.draw_texture(assets.textures["decal_pencil"], 620, 200, 12, 5)
        gl.draw_texture(assets.textures["decal_shine"], 220, 430, 22, 9)
