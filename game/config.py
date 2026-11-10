"""
Configurações globais e constantes do jogo 'O Desafio Escolar'.
"""

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
FPS = 60
TITLE = "O Desafio Escolar - PyGame & OpenGL"

TILE_SIZE = 32

COLOR_BG = (22, 25, 38)
COLOR_BG_TOP = (24, 28, 46)
COLOR_BG_BOTTOM = (14, 16, 26)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_PRIMARY = (64, 158, 224)
COLOR_PRIMARY_DARK = (42, 110, 165)
COLOR_ACCENT = (247, 201, 72)
COLOR_ACCENT_DARK = (196, 148, 24)
COLOR_SUCCESS = (63, 201, 128)
COLOR_DANGER = (235, 87, 87)
COLOR_PANEL_BG = (23, 28, 42, 235)
COLOR_PANEL_BORDER = (82, 104, 145)
COLOR_TEXT = (235, 238, 245)
COLOR_TEXT_MUTED = (150, 162, 185)

STATE_NAME_INPUT = "NAME_INPUT"
STATE_EXPLORE = "EXPLORE"
STATE_DIALOG = "DIALOG"
STATE_QUIZ = "QUIZ"
STATE_VICTORY = "VICTORY"
STATE_GAME_OVER = "GAME_OVER"
STATE_LEADERBOARD = "LEADERBOARD"

DIFF_FACIL = "facil"
DIFF_MEDIO = "medio"
DIFF_DIFICIL = "dificil"
DIFF_DESAFIO = "desafio"

DIFFICULTY_LABELS = {
    DIFF_FACIL: "Fácil",
    DIFF_MEDIO: "Médio",
    DIFF_DIFICIL: "Difícil",
    DIFF_DESAFIO: "Desafio"
}

# Matérias
SUBJECT_MATH = "math"
SUBJECT_HISTORY = "history"
SUBJECT_GEOGRAPHY = "geography"
SUBJECT_BIOLOGY = "biology"

SUBJECTS = {
    SUBJECT_MATH: {
        "name": "Matemática",
        "teacher": "Prof. Roberto",
        "teacher_label": "Prof. Roberto (Matemática)",
        "zone": "CLASSROOM_MATH",
        "door_type": "DOOR_MATH",
        "door_texture": "door_math",
        "door_label": "Entrar na Sala de Matemática",
        "hall_x": 704,
        "board_title": "Quadro-Negro de Matemática",
        "board_text": "Quadro com anotações do Prof. Roberto: Álgebra, Geometria e Teorema de Pitágoras!",
    },
    SUBJECT_HISTORY: {
        "name": "História",
        "teacher": "Profa. Helena",
        "teacher_label": "Profa. Helena (História)",
        "zone": "CLASSROOM_HISTORY",
        "door_type": "DOOR_HISTORY",
        "door_texture": "door_history",
        "door_label": "Entrar na Sala de História",
        "hall_x": 96,
        "board_title": "Quadro-Negro de História",
        "board_text": "Linha do tempo com eventos importantes do Brasil e do mundo.",
    },
    SUBJECT_GEOGRAPHY: {
        "name": "Geografia",
        "teacher": "Prof. Carlos",
        "teacher_label": "Prof. Carlos (Geografia)",
        "zone": "CLASSROOM_GEOGRAPHY",
        "door_type": "DOOR_GEOGRAPHY",
        "door_texture": "door_geo",
        "door_label": "Entrar na Sala de Geografia",
        "hall_x": 288,
        "board_title": "Quadro-Negro de Geografia",
        "board_text": "Mapas, relevo, clima e regiões do planeta em destaque.",
    },
    SUBJECT_BIOLOGY: {
        "name": "Biologia",
        "teacher": "Profa. Marina",
        "teacher_label": "Profa. Marina (Biologia)",
        "zone": "CLASSROOM_BIOLOGY",
        "door_type": "DOOR_BIOLOGY",
        "door_texture": "door_bio",
        "door_label": "Entrar na Sala de Biologia",
        "hall_x": 480,
        "board_title": "Quadro-Negro de Biologia",
        "board_text": "Esquemas de células, ecossistemas e corpo humano.",
    },
}

SUBJECTS_BY_DOOR = {cfg["door_type"]: sid for sid, cfg in SUBJECTS.items()}
SUBJECTS_BY_ZONE = {cfg["zone"]: sid for sid, cfg in SUBJECTS.items()}
