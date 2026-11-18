"""
Criação da janela do jogo (modo janela e tela cheia sem bordas).

A tela cheia usa uma janela SEM BORDAS do tamanho do monitor, em vez da tela
cheia exclusiva (pygame.FULLSCREEN). Na tela cheia exclusiva o OpenGL assume o
monitor e não passa pelo compositor do Windows, então programas de captura
(OBS, Discord, Xbox Game Bar) mostram tela preta. A janela sem bordas tem o
mesmo visual e continua visível para essas ferramentas.
"""

import os
import pygame
from game.config import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE

BASE_FLAGS = pygame.OPENGL | pygame.DOUBLEBUF


def create_display(fullscreen):
    """Recria o subsistema de vídeo e abre a janela no modo pedido.

    Recriar o subsistema é necessário: sem isso o SDL reaproveita a janela
    antiga e ignora o tamanho pedido (proporção distorcida ao alternar).
    O contexto OpenGL é recriado junto; quem chama deve reconfigurar o
    pipeline GL e regenerar as texturas.
    """
    pygame.display.quit()

    # a posição da janela só é lida pelo SDL na criação da janela
    if fullscreen:
        os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
        os.environ.pop("SDL_VIDEO_CENTERED", None)
    else:
        os.environ.pop("SDL_VIDEO_WINDOW_POS", None)
        os.environ["SDL_VIDEO_CENTERED"] = "1"

    pygame.display.init()
    # a janela recriada perde o título: o OBS usa o título para reencontrá-la
    pygame.display.set_caption(TITLE)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)

    if fullscreen:
        # resolução nativa do monitor + 1 linha. Uma janela que cobre o
        # monitor EXATAMENTE é promovida pelo Windows a apresentação direta
        # ("independent flip"): o compositor para de receber os quadros e o
        # OBS congela (só atualiza no Alt+Tab). Com 1 px a mais a promoção não
        # acontece. A linha extra fica fora da tela, abaixo da borda inferior;
        # o renderer cola a imagem no topo (ver GLRenderer.refresh_viewport).
        desktop_w, desktop_h = pygame.display.get_desktop_sizes()[0]
        return pygame.display.set_mode((desktop_w, desktop_h + 1), BASE_FLAGS | pygame.NOFRAME)
    return pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), BASE_FLAGS)
