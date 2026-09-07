"""
Módulo de Criação de Sprites e Texturas Pixel Art para 'O Desafio Escolar'.

Direção de arte: pixel-art vibrante inspirada nos RPGs top-down clássicos.
Cada objeto recebe contorno escuro, sombreamento em três tons (luz / base /
sombra) e sombra projetada no chão, dando volume e leitura clara das formas.
"""

import pygame
from game.config import TILE_SIZE

# ---------------------------------------------------------------------------
# Paleta de arte (saturada e quente)
# ---------------------------------------------------------------------------
OUTLINE = (46, 32, 40)

# Madeira quente
WOOD_L = (222, 166, 100)
WOOD_M = (183, 124, 66)
WOOD_D = (124, 76, 40)

# Taco do piso: tons próximos entre si para o chão não competir com os móveis
FLOOR_W_L = (208, 154, 94)
FLOOR_W_M = (192, 138, 80)
FLOOR_W_S = (154, 102, 58)   # emenda entre tábuas
FLOOR_W_G = (174, 120, 68)   # veio discreto

# Tapete/passadeira do corredor (terracota quente)
RUG_M = (198, 106, 82)
RUG_L = (222, 132, 104)
RUG_D = (156, 72, 56)

# Piso cerâmico do corredor
TILE_L = (247, 236, 210)
TILE_M = (233, 217, 184)
TILE_D = (207, 186, 148)
GROUT = (190, 168, 132)

# Parede pintada e lambril verde-água
WALL_L = (250, 241, 216)
WALL_M = (236, 223, 192)
WAINS_L = (94, 208, 172)
WAINS_M = (52, 165, 132)
WAINS_D = (30, 118, 96)

# Folhagem
LEAF_L = (134, 222, 96)
LEAF_M = (78, 186, 111)
LEAF_D = (42, 132, 80)

# Azuis (armários, vidros, água)
BLUE_L = (126, 205, 244)
BLUE_M = (58, 148, 214)
BLUE_D = (32, 98, 156)

# Destaques
GOLD_L = (255, 216, 110)
GOLD_M = (240, 180, 48)
GOLD_D = (184, 130, 22)
RED_M = (226, 92, 82)
RED_D = (168, 54, 50)
CHALK = (232, 245, 236)
BOARD_M = (44, 112, 80)
BOARD_D = (28, 78, 56)
PAPER = (250, 246, 236)


# ---------------------------------------------------------------------------
# Helpers de desenho
# ---------------------------------------------------------------------------
def _rect(surf, x, y, w, h, color, radius=0):
    if w > 0 and h > 0:
        pygame.draw.rect(surf, color, (x, y, w, h), border_radius=radius)


def _block(surf, x, y, w, h, base, light=None, dark=None, radius=0, outline=OUTLINE):
    """Bloco com contorno escuro, topo iluminado e base sombreada."""
    if outline is not None and w > 2 and h > 2:
        _rect(surf, x, y, w, h, outline, radius)
        x, y, w, h = x + 1, y + 1, w - 2, h - 2
        radius = max(0, radius - 1)

    _rect(surf, x, y, w, h, base, radius)
    if light is not None and h >= 4:
        _rect(surf, x, y, w, max(1, h // 3), light)
    if dark is not None and h >= 4:
        dh = max(1, h // 4)
        _rect(surf, x, y + h - dh, w, dh, dark)


def _with_outline(surf, color=OUTLINE):
    """Aplica um contorno escuro de 1px ao redor da silhueta do sprite."""
    mask = pygame.mask.from_surface(surf)
    silhouette = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    mask.to_surface(silhouette, setcolor=color, unsetcolor=(0, 0, 0, 0))

    out = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(silhouette, (dx, dy))
    out.blit(surf, (0, 0))
    return out


def _fit_text(text, max_w, base_size=10, bold=True, color=OUTLINE):
    """Renderiza um texto reduzindo o corpo até caber na largura disponível."""
    for size in range(base_size, 5, -1):
        font = pygame.font.SysFont("Segoe UI", size, bold=bold)
        surf = font.render(text, True, color)
        if surf.get_width() <= max_w:
            return surf
    font = pygame.font.SysFont("Segoe UI", 6, bold=bold)
    surf = font.render(text, True, color)
    return pygame.transform.smoothscale(surf, (max_w, surf.get_height()))


class AssetManager:
    def __init__(self, gl_renderer):
        self.gl = gl_renderer
        self.textures = {}
        self.player_frames = {}   # {dir: [tex_id, ...]}
        self.teacher_frames = []  # [tex_id, ...]
        self._generate_all_assets()

    def _register(self, key, surf):
        self.textures[key] = self.gl.create_texture(surf)[0]

    def _generate_all_assets(self):
        """Gera todos os sprites, tiles e objetos do jogo."""
        self._generate_shadow()
        self._generate_floors_and_walls()
        self._generate_doors()
        self._generate_furniture()
        self._generate_wall_decor()
        self._generate_decals()
        self._generate_player_sprites()
        self._generate_teacher_sprites()
        self._generate_ui_icons()

    # =====================================================================
    # Sombra projetada
    # =====================================================================
    def _generate_shadow(self):
        """Elipse translúcida usada como sombra de personagens e móveis."""
        w, h = 32, 14
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (26, 18, 30, 45), (0, 0, w, h))
        pygame.draw.ellipse(surf, (26, 18, 30, 90), (3, 2, w - 6, h - 4))
        self._register("shadow", surf)

    # =====================================================================
    # Pisos e paredes
    # =====================================================================
    def _generate_floors_and_walls(self):
        # --- Piso do corredor: cerâmica creme em xadrez com rejunte ---
        for variant in (0, 1, 2):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            for j in range(2):
                for i in range(2):
                    tone = TILE_L if (i + j) % 2 == 0 else TILE_M
                    _rect(surf, i * 16, j * 16, 16, 16, tone)
            # Rejunte
            pygame.draw.line(surf, GROUT, (0, 0), (TILE_SIZE, 0))
            pygame.draw.line(surf, GROUT, (0, 16), (TILE_SIZE, 16))
            pygame.draw.line(surf, GROUT, (0, 0), (0, TILE_SIZE))
            pygame.draw.line(surf, GROUT, (16, 0), (16, TILE_SIZE))

            if variant == 1:
                for px, py in ((6, 9), (21, 5), (12, 25), (27, 20)):
                    surf.set_at((px, py), TILE_D)
            elif variant == 2:
                pygame.draw.line(surf, (255, 253, 244), (19, 21), (26, 21))
                pygame.draw.line(surf, (255, 253, 244), (21, 24), (27, 24))

            self._register(f"floor_hallway_{variant}", surf)
        self.textures["floor_hallway"] = self.textures["floor_hallway_0"]

        # --- Piso da sala: tacos de madeira (contraste suave para não virar tijolo) ---
        for variant in (0, 1, 2):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill(FLOOR_W_M)
            # O tom depende só da fileira (não da variação), para as tábuas
            # seguirem contínuas de um tile para o outro sem manchar o piso
            for row, py in enumerate((0, 8, 16, 24)):
                tone = FLOOR_W_L if row % 2 == 0 else FLOOR_W_M
                _rect(surf, 0, py, TILE_SIZE, 8, tone)
                pygame.draw.line(surf, FLOOR_W_S, (0, py), (TILE_SIZE, py))
            # Uma emenda vertical curta por fileira, deslocada entre variações
            for row, py in enumerate((0, 8, 16, 24)):
                seam_x = (9 + row * 11 + variant * 7) % TILE_SIZE
                pygame.draw.line(surf, FLOOR_W_S, (seam_x, py + 1), (seam_x, py + 7))
            if variant == 2:
                pygame.draw.line(surf, FLOOR_W_G, (5, 12), (15, 12))
                pygame.draw.line(surf, FLOOR_W_G, (18, 28), (27, 28))
            self._register(f"floor_classroom_{variant}", surf)
        self.textures["floor_classroom"] = self.textures["floor_classroom_0"]

        # --- Parede pintada (corpo) ---
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(WALL_L)
        for x in range(0, TILE_SIZE, 8):
            pygame.draw.line(surf, WALL_M, (x, 0), (x, TILE_SIZE))
        self._register("wall", surf)

        # --- Base da parede: moldura + lambril + rodapé ---
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(WALL_L)
        for x in range(0, TILE_SIZE, 8):
            pygame.draw.line(surf, WALL_M, (x, 0), (x, 11))
        # Moldura de madeira (chair rail)
        _rect(surf, 0, 10, TILE_SIZE, 3, WOOD_M)
        pygame.draw.line(surf, WOOD_L, (0, 10), (TILE_SIZE, 10))
        # Lambril verde-água
        _rect(surf, 0, 13, TILE_SIZE, 13, WAINS_M)
        pygame.draw.line(surf, WAINS_L, (0, 13), (TILE_SIZE, 13))
        for x in range(4, TILE_SIZE, 8):
            pygame.draw.line(surf, WAINS_D, (x, 15), (x, 24))
        # Rodapé
        _rect(surf, 0, 26, TILE_SIZE, 6, WOOD_D)
        pygame.draw.line(surf, WOOD_M, (0, 26), (TILE_SIZE, 26))
        pygame.draw.line(surf, OUTLINE, (0, 31), (TILE_SIZE, 31))
        self._register("wall_base", surf)

    # =====================================================================
    # Portas
    # =====================================================================
    def _make_door(self, label, placard_color):
        """Porta escolar 64x64 com placa identificadora da matéria."""
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)

        # Batente e folha da porta
        _block(surf, 6, 12, 52, 52, WOOD_D)
        _block(surf, 10, 16, 44, 48, WOOD_M, light=WOOD_L)
        # Almofadas da porta
        _block(surf, 15, 40, 34, 20, WOOD_M, light=None, dark=WOOD_D, outline=WOOD_D)
        # Janela de vidro
        _block(surf, 16, 20, 32, 16, BLUE_L, light=(196, 236, 255), outline=WOOD_D)
        pygame.draw.line(surf, (255, 255, 255), (20, 33), (30, 23))
        pygame.draw.line(surf, (255, 255, 255), (25, 33), (34, 24))
        # Maçaneta dourada
        pygame.draw.circle(surf, OUTLINE, (49, 44), 4)
        pygame.draw.circle(surf, GOLD_M, (49, 44), 3)
        pygame.draw.circle(surf, GOLD_L, (48, 43), 1)

        # Placa da matéria
        _block(surf, 3, 0, 58, 13, PAPER, outline=OUTLINE)
        _rect(surf, 5, 10, 54, 2, placard_color)
        text = _fit_text(label, 50, base_size=10)
        surf.blit(text, (32 - text.get_width() // 2, 1))
        return surf

    def _generate_doors(self):
        self._register("door_math", self._make_door("MATEMÁTICA", LEAF_M))
        self._register("door_history", self._make_door("HISTÓRIA", RED_M))
        self._register("door_geo", self._make_door("GEOGRAFIA", RED_M))
        self._register("door_bio", self._make_door("BIOLOGIA", RED_M))
        self._register("door_exit", self._make_door("SAÍDA", LEAF_M))

    # =====================================================================
    # Mobiliário
    # =====================================================================
    def _generate_furniture(self):
        # --- Mesa do Professor (64x40) ---
        surf = pygame.Surface((64, 40), pygame.SRCALPHA)
        _block(surf, 2, 6, 60, 30, WOOD_M, light=WOOD_L, dark=WOOD_D)
        # Gavetas laterais
        _block(surf, 6, 18, 16, 16, WOOD_D, outline=OUTLINE)
        pygame.draw.line(surf, GOLD_M, (10, 25), (18, 25), 2)
        # Notebook aberto
        _block(surf, 28, 8, 15, 12, (52, 58, 74), outline=OUTLINE)
        _rect(surf, 30, 10, 11, 8, BLUE_L)
        # Prova e maçã
        _block(surf, 45, 12, 12, 14, PAPER, outline=OUTLINE)
        pygame.draw.line(surf, (170, 178, 196), (47, 16), (55, 16))
        pygame.draw.line(surf, (170, 178, 196), (47, 19), (55, 19))
        pygame.draw.circle(surf, OUTLINE, (24, 12), 5)
        pygame.draw.circle(surf, RED_M, (24, 12), 4)
        pygame.draw.circle(surf, (255, 150, 140), (22, 10), 1)
        pygame.draw.line(surf, LEAF_D, (24, 8), (26, 6), 2)
        self._register("teacher_desk", surf)

        # --- Carteira do aluno (32x36) ---
        surf = pygame.Surface((32, 36), pygame.SRCALPHA)
        # Encosto da cadeira
        _block(surf, 8, 1, 16, 8, BLUE_M, light=BLUE_L, dark=BLUE_D)
        # Tampo
        _block(surf, 2, 11, 28, 16, WOOD_L, light=(238, 190, 132), dark=WOOD_M)
        # Caderno aberto
        _block(surf, 9, 15, 14, 9, PAPER, outline=WOOD_D)
        pygame.draw.line(surf, BLUE_M, (16, 16), (16, 23))
        pygame.draw.line(surf, (176, 186, 206), (11, 18), (14, 18))
        pygame.draw.line(surf, (176, 186, 206), (18, 20), (21, 20))
        # Pernas de metal
        _rect(surf, 5, 27, 3, 8, (96, 104, 120))
        _rect(surf, 24, 27, 3, 8, (96, 104, 120))
        pygame.draw.line(surf, OUTLINE, (5, 34), (7, 34))
        pygame.draw.line(surf, OUTLINE, (24, 34), (26, 34))
        self._register("student_desk", surf)

        # --- Armários escolares (32x48) ---
        surf = pygame.Surface((32, 48), pygame.SRCALPHA)
        _block(surf, 1, 0, 30, 46, BLUE_M, light=BLUE_L, dark=BLUE_D)
        pygame.draw.line(surf, BLUE_D, (16, 2), (16, 44))
        for ly in (10, 14, 18):
            pygame.draw.line(surf, BLUE_D, (5, ly), (12, ly))
            pygame.draw.line(surf, BLUE_D, (20, ly), (27, ly))
        # Fechaduras
        for lx in (12, 27):
            _rect(surf, lx, 26, 3, 5, (226, 232, 240))
            surf.set_at((lx + 1, 28), OUTLINE)
        # Base sombreada
        _rect(surf, 2, 43, 28, 3, BLUE_D)
        self._register("lockers", surf)

        # --- Bebedouro (32x34) ---
        surf = pygame.Surface((32, 34), pygame.SRCALPHA)
        _block(surf, 7, 13, 18, 21, (232, 238, 244), light=(255, 255, 255), dark=(190, 200, 212))
        # Galão de água
        _block(surf, 9, 1, 14, 13, BLUE_L, light=(178, 226, 250), dark=BLUE_M)
        _rect(surf, 13, 0, 6, 3, BLUE_D)
        # Torneiras
        pygame.draw.circle(surf, OUTLINE, (12, 20), 3)
        pygame.draw.circle(surf, BLUE_M, (12, 20), 2)
        pygame.draw.circle(surf, OUTLINE, (20, 20), 3)
        pygame.draw.circle(surf, RED_M, (20, 20), 2)
        _rect(surf, 11, 26, 10, 2, (190, 200, 212))
        self._register("water_cooler", surf)

        # --- Planta decorativa (32x40) ---
        surf = pygame.Surface((32, 40), pygame.SRCALPHA)
        # Folhagem
        for cx, cy, r, tone in ((16, 14, 9, LEAF_M), (9, 18, 6, LEAF_D),
                                (23, 18, 6, LEAF_D), (14, 9, 6, LEAF_L),
                                (21, 12, 5, LEAF_L)):
            pygame.draw.circle(surf, OUTLINE, (cx, cy), r + 1)
            pygame.draw.circle(surf, tone, (cx, cy), r)
        # Vaso de cerâmica
        pygame.draw.polygon(surf, OUTLINE, [(8, 24), (24, 24), (21, 39), (11, 39)])
        pygame.draw.polygon(surf, (206, 116, 72), [(9, 25), (23, 25), (20, 38), (12, 38)])
        pygame.draw.polygon(surf, (232, 148, 100), [(10, 26), (16, 26), (15, 37), (12, 37)])
        _rect(surf, 8, 24, 16, 3, (176, 92, 56))
        self._register("plant", surf)

        # --- Passadeira do corredor (32x96, ladrilhável na horizontal) ---
        surf = pygame.Surface((32, 96), pygame.SRCALPHA)
        _rect(surf, 0, 6, 32, 84, RUG_M)
        # Bordas mais escuras e miolo iluminado
        _rect(surf, 0, 6, 32, 5, RUG_D)
        _rect(surf, 0, 85, 32, 5, RUG_D)
        _rect(surf, 0, 30, 32, 36, RUG_L)
        _rect(surf, 0, 38, 32, 20, RUG_M)
        # Losangos decorativos
        for cy in (20, 48, 76):
            pygame.draw.polygon(surf, RUG_D, [(16, cy - 6), (23, cy), (16, cy + 6), (9, cy)])
            pygame.draw.polygon(surf, RUG_L, [(16, cy - 3), (20, cy), (16, cy + 3), (12, cy)])
        # Franjas
        for fx in range(1, 32, 4):
            pygame.draw.line(surf, (244, 232, 208), (fx, 1), (fx, 5))
            pygame.draw.line(surf, (244, 232, 208), (fx, 90), (fx, 94))
        self._register("rug_runner", surf)

        # --- Banco de madeira do corredor (64x30) ---
        surf = pygame.Surface((64, 30), pygame.SRCALPHA)
        _block(surf, 2, 2, 60, 9, WOOD_M, light=WOOD_L, dark=WOOD_D)      # encosto
        _block(surf, 0, 12, 64, 11, WOOD_L, light=(238, 190, 132), dark=WOOD_M)  # assento
        for lx in (5, 53):
            _rect(surf, lx, 23, 6, 6, WOOD_D)
        self._register("bench", surf)

        # --- Estante de livros (32x48) ---
        surf = pygame.Surface((32, 48), pygame.SRCALPHA)
        _block(surf, 1, 2, 30, 44, WOOD_D)
        for shelf_y in (6, 20, 34):
            _rect(surf, 3, shelf_y, 26, 12, (96, 60, 32))
            colors = [RED_M, BLUE_M, LEAF_M, GOLD_M, BLUE_D]
            bx = 4
            for i in range(5):
                bw = 4 if i % 2 == 0 else 5
                bh = 10 if i % 3 else 8
                _rect(surf, bx, shelf_y + 12 - bh, bw, bh, colors[(i + shelf_y) % 5])
                pygame.draw.line(surf, OUTLINE, (bx, shelf_y + 12 - bh),
                                 (bx, shelf_y + 11))
                bx += bw + 1
            pygame.draw.line(surf, WOOD_M, (3, shelf_y + 12), (28, shelf_y + 12))
        self._register("bookshelf", surf)

    # =====================================================================
    # Decoração de parede
    # =====================================================================
    def _generate_wall_decor(self):
        # --- Quadro-negro (128x64) ---
        surf = pygame.Surface((128, 64), pygame.SRCALPHA)
        _block(surf, 0, 0, 128, 60, WOOD_M, light=WOOD_L, dark=WOOD_D)
        _block(surf, 6, 6, 116, 44, BOARD_M, outline=OUTLINE)
        # Leve desgaste de giz
        _rect(surf, 10, 38, 40, 6, BOARD_D)
        # Fórmulas
        font = pygame.font.SysFont("Segoe UI", 13, bold=True)
        for i, txt in enumerate(("f(x) = ax + b", "a² + b² = c²")):
            surf.blit(font.render(txt, True, CHALK), (14, 11 + i * 16))
        small = pygame.font.SysFont("Segoe UI", 11)
        surf.blit(small.render("π = 3,1415...", True, (206, 232, 216)), (14, 43))
        # Suporte e giz
        _rect(surf, 12, 50, 104, 4, WOOD_D)
        _rect(surf, 20, 50, 8, 3, CHALK)
        _rect(surf, 34, 50, 6, 3, (250, 214, 160))
        _block(surf, 96, 48, 14, 6, (86, 96, 118), outline=OUTLINE)
        self._register("blackboard", surf)

        # --- Janela com vista externa (64x44) ---
        surf = pygame.Surface((64, 44), pygame.SRCALPHA)
        _block(surf, 0, 0, 64, 40, WOOD_M, light=WOOD_L, dark=WOOD_D)
        # Céu
        _rect(surf, 5, 5, 54, 30, (146, 214, 246))
        _rect(surf, 5, 5, 54, 12, (176, 228, 250))
        # Nuvens
        pygame.draw.circle(surf, (255, 255, 255), (18, 13), 5)
        pygame.draw.circle(surf, (255, 255, 255), (25, 13), 4)
        pygame.draw.circle(surf, (255, 255, 255), (46, 11), 4)
        # Colinas verdes
        pygame.draw.ellipse(surf, LEAF_D, (0, 22, 34, 20))
        pygame.draw.ellipse(surf, LEAF_M, (24, 24, 40, 18))
        _rect(surf, 5, 32, 54, 3, LEAF_M)
        # Caixilhos
        _rect(surf, 31, 5, 2, 30, WOOD_D)
        _rect(surf, 5, 18, 54, 2, WOOD_D)
        # Peitoril
        _block(surf, 0, 36, 64, 8, WOOD_L, dark=WOOD_M)
        self._register("window", surf)

        # --- Mural de avisos (48x40) ---
        surf = pygame.Surface((48, 40), pygame.SRCALPHA)
        _block(surf, 0, 0, 48, 40, WOOD_D)
        _rect(surf, 3, 3, 42, 34, (206, 158, 104))
        # Avisos coloridos com "texto"
        for px, py, pw, ph, col in ((6, 6, 16, 13, PAPER), (25, 8, 16, 12, (196, 232, 250)),
                                    (8, 22, 15, 12, (250, 226, 160)), (26, 23, 15, 11, PAPER)):
            _block(surf, px, py, pw, ph, col, outline=OUTLINE)
            for ly in range(py + 3, py + ph - 2, 3):
                pygame.draw.line(surf, (150, 150, 160), (px + 2, ly), (px + pw - 3, ly))
        # Tachinhas
        for tx, ty in ((13, 7), (32, 9), (14, 23), (33, 24)):
            pygame.draw.circle(surf, RED_D, (tx, ty), 2)
            pygame.draw.circle(surf, RED_M, (tx, ty), 1)
        self._register("bulletin", surf)

        # --- Cartaz de matemática (32x40) ---
        surf = pygame.Surface((32, 40), pygame.SRCALPHA)
        _block(surf, 0, 0, 32, 40, PAPER, outline=OUTLINE)
        _rect(surf, 2, 2, 28, 9, BLUE_M)
        font = pygame.font.SysFont("Segoe UI", 9, bold=True)
        surf.blit(font.render("MATH", True, (255, 255, 255)), (7, 2))
        # Triângulo com marcação de ângulo reto
        pygame.draw.polygon(surf, LEAF_M, [(7, 33), (25, 33), (7, 17)])
        pygame.draw.polygon(surf, OUTLINE, [(7, 33), (25, 33), (7, 17)], 1)
        _rect(surf, 8, 29, 4, 4, PAPER)
        pygame.draw.rect(surf, (120, 128, 145), (8, 29, 4, 4), 1)
        small = pygame.font.SysFont("Segoe UI", 8, bold=True)
        surf.blit(small.render("a²+b²", True, OUTLINE), (5, 34))
        self._register("poster_math", surf)

        # --- Relógio de parede (28x28) ---
        surf = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(surf, OUTLINE, (14, 14), 13)
        pygame.draw.circle(surf, (238, 242, 248), (14, 14), 11)
        pygame.draw.circle(surf, (210, 218, 230), (14, 14), 11, 1)
        for mx, my in ((14, 5), (23, 14), (14, 23), (5, 14)):
            surf.set_at((mx, my), OUTLINE)
        pygame.draw.line(surf, OUTLINE, (14, 14), (14, 8), 2)
        pygame.draw.line(surf, OUTLINE, (14, 14), (19, 15), 1)
        pygame.draw.circle(surf, RED_M, (14, 14), 2)
        self._register("clock", surf)

    # =====================================================================
    # Pequenos detalhes de chão
    # =====================================================================
    def _generate_decals(self):
        # Papel amassado
        surf = pygame.Surface((14, 12), pygame.SRCALPHA)
        pygame.draw.polygon(surf, OUTLINE, [(1, 9), (4, 1), (12, 3), (10, 11)])
        pygame.draw.polygon(surf, PAPER, [(3, 8), (5, 3), (10, 4), (9, 9)])
        pygame.draw.line(surf, (206, 202, 194), (5, 6), (9, 5))
        pygame.draw.line(surf, (206, 202, 194), (5, 8), (8, 8))
        self._register("decal_paper", surf)

        # Brilho / reflexo no piso
        surf = pygame.Surface((22, 9), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (255, 255, 255, 40), (0, 0, 22, 9))
        pygame.draw.ellipse(surf, (255, 255, 255, 70), (4, 2, 13, 5))
        self._register("decal_shine", surf)

        # Lápis caído
        surf = pygame.Surface((12, 5), pygame.SRCALPHA)
        _rect(surf, 0, 1, 9, 3, GOLD_M)
        _rect(surf, 0, 1, 9, 1, GOLD_L)
        pygame.draw.polygon(surf, (240, 208, 168), [(9, 1), (12, 2), (9, 4)])
        surf.set_at((11, 2), OUTLINE)
        _rect(surf, 0, 1, 2, 3, RED_M)
        self._register("decal_pencil", surf)

    # =====================================================================
    # Sprites do Jogador
    # =====================================================================
    def _generate_player_sprites(self):
        """Gera sprites do jogador (4 direções x 3 frames) com contorno."""
        SKIN = (255, 216, 174)
        SKIN_D = (222, 176, 132)
        HAIR = (104, 62, 32)
        HAIR_L = (140, 88, 46)
        EYES = (46, 34, 40)
        SHIRT = (252, 252, 255)
        SHIRT_D = (214, 222, 238)
        TIE = (58, 148, 214)
        PANTS = (60, 76, 112)
        PANTS_D = (42, 54, 84)
        SHOES = (62, 46, 54)
        BAG = (226, 124, 64)
        BAG_D = (176, 88, 44)

        directions = ["down", "up", "left", "right"]
        self.player_frames = {d: [] for d in directions}

        for d in directions:
            for step in (0, 1, 2):
                surf = pygame.Surface((32, 48), pygame.SRCALPHA)

                # Balanço vertical do corpo e passada dos pés
                bob = -1 if step else 0
                fx_l = -2 if step == 1 else (2 if step == 2 else 0)
                fx_r = -fx_l

                # --- Pernas e sapatos (sempre na base) ---
                _rect(surf, 11, 34 + bob, 5, 8 - bob, PANTS)
                _rect(surf, 17, 34 + bob, 5, 8 - bob, PANTS)
                _rect(surf, 11, 40, 5, 2, PANTS_D)
                _rect(surf, 17, 40, 5, 2, PANTS_D)
                _rect(surf, 10 + fx_l, 42, 6, 4, SHOES)
                _rect(surf, 17 + fx_r, 42, 6, 4, SHOES)

                if d == "down":
                    _rect(surf, 9, 21 + bob, 14, 14, SHIRT)
                    _rect(surf, 9, 31 + bob, 14, 4, SHIRT_D)
                    _rect(surf, 15, 21 + bob, 3, 9, TIE)
                    _rect(surf, 8, 21 + bob, 2, 12, BAG)
                    _rect(surf, 22, 21 + bob, 2, 12, BAG)
                    _rect(surf, 6, 23 + bob, 3, 10, SKIN)
                    _rect(surf, 23, 23 + bob, 3, 10, SKIN)
                    # Cabeça
                    _rect(surf, 9, 8 + bob, 14, 13, SKIN)
                    _rect(surf, 9, 18 + bob, 14, 3, SKIN_D)
                    _rect(surf, 8, 5 + bob, 16, 7, HAIR)
                    _rect(surf, 8, 5 + bob, 16, 3, HAIR_L)
                    _rect(surf, 8, 11 + bob, 3, 4, HAIR)
                    _rect(surf, 21, 11 + bob, 3, 4, HAIR)
                    _rect(surf, 12, 14 + bob, 2, 3, EYES)
                    _rect(surf, 18, 14 + bob, 2, 3, EYES)
                    _rect(surf, 11, 18 + bob, 2, 1, (245, 170, 160))
                    _rect(surf, 19, 18 + bob, 2, 1, (245, 170, 160))

                elif d == "up":
                    _rect(surf, 9, 21 + bob, 14, 14, BAG)
                    _rect(surf, 11, 24 + bob, 10, 7, BAG_D)
                    _rect(surf, 9, 31 + bob, 14, 4, BAG_D)
                    _rect(surf, 6, 22 + bob, 3, 11, SHIRT)
                    _rect(surf, 23, 22 + bob, 3, 11, SHIRT)
                    _rect(surf, 8, 5 + bob, 16, 16, HAIR)
                    _rect(surf, 8, 5 + bob, 16, 4, HAIR_L)

                elif d == "left":
                    _rect(surf, 10, 21 + bob, 12, 14, SHIRT)
                    _rect(surf, 10, 31 + bob, 12, 4, SHIRT_D)
                    _rect(surf, 19, 21 + bob, 5, 12, BAG)
                    _rect(surf, 11, 23 + bob, 4, 10, SKIN)
                    _rect(surf, 8, 8 + bob, 14, 13, SKIN)
                    _rect(surf, 8, 18 + bob, 12, 3, SKIN_D)
                    _rect(surf, 8, 5 + bob, 15, 7, HAIR)
                    _rect(surf, 8, 5 + bob, 15, 3, HAIR_L)
                    _rect(surf, 19, 10 + bob, 4, 7, HAIR)
                    _rect(surf, 9, 14 + bob, 2, 3, EYES)

                else:  # right
                    _rect(surf, 10, 21 + bob, 12, 14, SHIRT)
                    _rect(surf, 10, 31 + bob, 12, 4, SHIRT_D)
                    _rect(surf, 8, 21 + bob, 5, 12, BAG)
                    _rect(surf, 17, 23 + bob, 4, 10, SKIN)
                    _rect(surf, 10, 8 + bob, 14, 13, SKIN)
                    _rect(surf, 12, 18 + bob, 12, 3, SKIN_D)
                    _rect(surf, 9, 5 + bob, 15, 7, HAIR)
                    _rect(surf, 9, 5 + bob, 15, 3, HAIR_L)
                    _rect(surf, 9, 10 + bob, 4, 7, HAIR)
                    _rect(surf, 21, 14 + bob, 2, 3, EYES)

                tex_id, _, _ = self.gl.create_texture(_with_outline(surf))
                self.player_frames[d].append(tex_id)

    # =====================================================================
    # Sprites do Professor
    # =====================================================================
    def _generate_teacher_sprites(self):
        """Gera o Professor Roberto (pose formal, óculos e livro)."""
        SKIN = (255, 220, 182)
        SKIN_D = (224, 184, 142)
        HAIR = (128, 134, 146)
        HAIR_L = (166, 172, 184)
        GLASSES = (238, 244, 252)
        VEST = (62, 84, 116)
        VEST_D = (44, 60, 86)
        SHIRT = (250, 250, 252)
        TIE = (200, 62, 58)
        PANTS = (70, 92, 122)
        SHOES = (52, 40, 46)
        BOOK = (198, 68, 62)

        self.teacher_frames = []
        for frame in (0, 1):
            surf = pygame.Surface((32, 48), pygame.SRCALPHA)
            breathe = 1 if frame else 0

            # Pernas e sapatos
            _rect(surf, 11, 34, 5, 8, PANTS)
            _rect(surf, 17, 34, 5, 8, PANTS)
            _rect(surf, 10, 42, 6, 4, SHOES)
            _rect(surf, 17, 42, 6, 4, SHOES)

            # Tronco com colete
            _rect(surf, 8, 21 - breathe, 16, 14 + breathe, VEST)
            _rect(surf, 8, 31, 16, 4, VEST_D)
            _rect(surf, 13, 21 - breathe, 6, 12, SHIRT)
            _rect(surf, 15, 22 - breathe, 2, 9, TIE)

            # Braços
            _rect(surf, 5, 23 - breathe, 3, 10, VEST)
            _rect(surf, 24, 23 - breathe, 3, 10, VEST)

            # Livro didático na mão
            _rect(surf, 3, 27 - breathe, 6, 9, BOOK)
            _rect(surf, 4, 28 - breathe, 4, 7, PAPER)

            # Cabeça
            _rect(surf, 9, 8, 14, 13, SKIN)
            _rect(surf, 9, 18, 14, 3, SKIN_D)
            _rect(surf, 8, 4, 16, 6, HAIR)
            _rect(surf, 8, 4, 16, 3, HAIR_L)
            _rect(surf, 8, 9, 2, 5, HAIR)
            _rect(surf, 22, 9, 2, 5, HAIR)
            # Óculos
            pygame.draw.rect(surf, GLASSES, (10, 13, 5, 4), 1)
            pygame.draw.rect(surf, GLASSES, (17, 13, 5, 4), 1)
            pygame.draw.line(surf, GLASSES, (15, 14), (17, 14))
            surf.set_at((12, 15), (46, 34, 40))
            surf.set_at((19, 15), (46, 34, 40))
            # Bigode
            _rect(surf, 13, 18, 6, 2, HAIR)

            tex_id, _, _ = self.gl.create_texture(_with_outline(surf))
            self.teacher_frames.append(tex_id)

    # =====================================================================
    # Ícones de interface
    # =====================================================================
    def _generate_ui_icons(self):
        # --- Cadeado fechado ---
        surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.arc(surf, OUTLINE, (5, 1, 14, 14), 0, 3.1416, 4)
        pygame.draw.arc(surf, GOLD_D, (6, 2, 12, 12), 0, 3.1416, 3)
        _block(surf, 3, 10, 18, 13, GOLD_M, light=GOLD_L, dark=GOLD_D, radius=3)
        pygame.draw.circle(surf, (86, 58, 16), (12, 15), 2)
        pygame.draw.line(surf, (86, 58, 16), (12, 15), (12, 19), 2)
        self._register("lock_closed", surf)

        # --- Cadeado aberto ---
        surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.arc(surf, OUTLINE, (8, 0, 14, 14), 0.3, 3.1416, 4)
        pygame.draw.arc(surf, LEAF_D, (9, 1, 12, 12), 0.3, 3.1416, 3)
        _block(surf, 3, 10, 18, 13, LEAF_M, light=LEAF_L, dark=LEAF_D, radius=3)
        pygame.draw.circle(surf, (20, 62, 38), (12, 15), 2)
        pygame.draw.line(surf, (20, 62, 38), (12, 15), (12, 19), 2)
        self._register("lock_open", surf)

        # --- Estrela dourada ---
        surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        points = [(12, 1), (15, 9), (23, 9), (17, 14), (19, 22),
                  (12, 17), (5, 22), (7, 14), (1, 9), (9, 9)]
        pygame.draw.polygon(surf, OUTLINE, points)
        inner = [(12, 3), (14.6, 10), (21, 10), (16, 14), (17.6, 20),
                 (12, 15.6), (6.4, 20), (8, 14), (3, 10), (9.4, 10)]
        pygame.draw.polygon(surf, GOLD_M, inner)
        pygame.draw.polygon(surf, GOLD_L, [(12, 4), (13.8, 10), (12, 12), (10, 10)])
        self._register("star", surf)
