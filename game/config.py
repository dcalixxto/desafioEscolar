"""
Configurações globais e constantes do jogo 'O Desafio Escolar'.
"""

# Resolução da janela e taxa de quadros
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
FPS = 60
TITLE = "O Desafio Escolar - PyGame & OpenGL"

# Tamanho do grid/tiles
TILE_SIZE = 32

# Paleta de Cores (RGB de 0 a 255 e normalizado para OpenGL)
COLOR_BG = (22, 25, 38)
COLOR_BG_TOP = (24, 28, 46)          # Topo do degradê de fundo
COLOR_BG_BOTTOM = (14, 16, 26)       # Base do degradê de fundo
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_PRIMARY = (64, 158, 224)       # Azul educacional
COLOR_PRIMARY_DARK = (42, 110, 165)
COLOR_ACCENT = (247, 201, 72)        # Dourado / Amarelo
COLOR_ACCENT_DARK = (196, 148, 24)
COLOR_SUCCESS = (63, 201, 128)       # Verde acerto
COLOR_DANGER = (235, 87, 87)         # Vermelho erro amigável
COLOR_PANEL_BG = (23, 28, 42, 235)   # Painel translúcido
COLOR_PANEL_BORDER = (82, 104, 145)
COLOR_TEXT = (235, 238, 245)
COLOR_TEXT_MUTED = (150, 162, 185)

# Estados do Jogo
STATE_NAME_INPUT = "NAME_INPUT"
STATE_EXPLORE = "EXPLORE"
STATE_DIALOG = "DIALOG"
STATE_QUIZ = "QUIZ"
STATE_VICTORY = "VICTORY"

# Níveis de Dificuldade
DIFF_FACIL = "facil"
DIFF_MEDIO = "medio"
DIFF_DIFICIL = "dificil"

DIFFICULTY_LABELS = {
    DIFF_FACIL: "Fácil",
    DIFF_MEDIO: "Médio",
    DIFF_DIFICIL: "Difícil"
}
