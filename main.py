"""
O Desafio Escolar - Jogo Educativo 2D com PyGame e OpenGL.
Desenvolvido para FUPAC/UNIPAC - Ciência da Computação / Programação Para Jogos.
Equipe Pecê Gamer.
"""

import sys
import pygame
from OpenGL.GL import *

from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    STATE_NAME_INPUT, STATE_EXPLORE, STATE_DIALOG, STATE_QUIZ, STATE_VICTORY,
    DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL
)
from game.gl_renderer import GLRenderer
from game.audio import sound_manager
from game.assets import AssetManager
from game.entities import Player
from game.world import SchoolWorld, ZONE_HALLWAY, ZONE_CLASSROOM
from game.quiz_data import QuizManager
from game.ui import UIManager

class DesafioEscolarGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)

        # Configura contexto OpenGL com Duplo Buffer
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        # Módulos principais
        self.gl = GLRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.assets = AssetManager(self.gl)
        self.world = SchoolWorld()
        self.player = Player(736, 200, name="Estudante")
        self.quiz = QuizManager()
        self.ui = UIManager(self.gl, self.assets, sound_manager)

        # Estado inicial
        self.state = STATE_NAME_INPUT
        self.running = True

    def run(self):
        """Loop principal do jogo."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0 # Delta time em segundos

            self.handle_events()
            self.update(dt)
            self.render(dt)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Distribui os eventos de acordo com o estado atual."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == STATE_NAME_INPUT:
                chosen_name = self.ui.handle_name_input_event(event)
                if chosen_name is not None:
                    self.player.name = chosen_name
                    self.state = STATE_EXPLORE

            elif self.state == STATE_EXPLORE:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_e, pygame.K_SPACE]:
                        self.try_interact()

            elif self.state == STATE_DIALOG:
                action = self.ui.handle_dialog_event(event)
                if action == "CLOSE":
                    self.state = STATE_EXPLORE
                elif action == "SHOW_CERT":
                    self.ui.close_dialog()
                    self.state = STATE_VICTORY
                elif action == "START_QUIZ":
                    self.ui.close_dialog()
                    # Seleciona o nível mais alto desbloqueado que ainda não foi concluído
                    if not self.quiz.completed_levels[DIFF_FACIL]:
                        self.quiz.start_level(DIFF_FACIL)
                    elif not self.quiz.completed_levels[DIFF_MEDIO]:
                        self.quiz.start_level(DIFF_MEDIO)
                    else:
                        self.quiz.start_level(DIFF_DIFICIL)
                    self.state = STATE_QUIZ
                elif action == "INFO_RULES":
                    self.ui.show_dialog(
                        "Prof. Roberto",
                        [
                            "O nosso desafio matemático funciona por progressão:",
                            "- Você começa no nível FÁCIL (operações e porcentagens).",
                            "- Ao acertar as questões, desbloqueia o nível MÉDIO.",
                            "- Ao vencer o nível Médio, o nível DIFÍCIL é liberado!",
                            "Se errar, não desanime: revise os conceitos e tente de novo!"
                        ],
                        options=[
                            ("Vamos começar os exercícios!", "START_QUIZ"),
                            ("Obrigado pela explicação.", "CLOSE")
                        ]
                    )

            elif self.state == STATE_QUIZ:
                result = self.ui.handle_quiz_event(event, self.quiz)
                if result is not None:
                    if result.startswith("SWITCH_DIFF_"):
                        d_key = result.split("SWITCH_DIFF_")[1]
                        self.quiz.start_level(d_key)
                    elif result.startswith("ANSWER_"):
                        opt_idx = int(result.split("_")[1])
                        is_correct, explanation = self.quiz.answer_question(opt_idx)
                        self.ui.start_quiz_feedback(is_correct, explanation)
                    elif result == "LEVEL_COMPLETE":
                        # Acabou um nível intermediário
                        next_diff = DIFF_MEDIO if self.quiz.unlocked_levels[DIFF_MEDIO] and not self.quiz.completed_levels[DIFF_MEDIO] else DIFF_DIFICIL
                        self.ui.show_dialog(
                            "Prof. Roberto",
                            [
                                f"Excelente trabalho, {self.player.name}!",
                                f"Você concluiu a bateria de exercícios e desbloqueou o próximo nível!",
                                f"Novo desafio disponível na sala de aula!"
                            ],
                            options=[
                                ("Continuar para o próximo nível", "START_QUIZ"),
                                ("Voltar a explorar a sala", "CLOSE")
                            ]
                        )
                        self.state = STATE_DIALOG
                    elif result == "VICTORY":
                        self.state = STATE_VICTORY
                    elif result == "EXIT_QUIZ":
                        self.state = STATE_EXPLORE

            elif self.state == STATE_VICTORY:
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                    sound_manager.play("blip")
                    self.state = STATE_EXPLORE

    def try_interact(self):
        """Trata a interação com o objeto mais próximo do jogador."""
        interactable = self.world.get_nearby_interactable(self.player.hitbox)
        if not interactable:
            return

        sound_manager.play("blip")

        if interactable.itype == "DOOR_MATH":
            sound_manager.play("door")
            self.world.set_zone(ZONE_CLASSROOM, self.player)

        elif interactable.itype == "DOOR_EXIT":
            sound_manager.play("door")
            self.world.set_zone(ZONE_HALLWAY, self.player)

        elif interactable.itype == "DOOR_LOCKED":
            self.ui.show_dialog(
                interactable.label,
                interactable.message.split("\n"),
                is_notice=True
            )
            self.state = STATE_DIALOG

        elif interactable.itype == "INFO":
            self.ui.show_dialog(
                interactable.label,
                interactable.message.split("\n"),
                is_notice=True
            )
            self.state = STATE_DIALOG

        elif interactable.itype == "TEACHER":
            # Diálogo interativo com o Professor Roberto
            if self.quiz.is_game_completed():
                self.ui.show_dialog(
                    "Prof. Roberto",
                    [
                        f"Incrível, {self.player.name}!",
                        "Você já dominou todos os níveis da Sala de Matemática!",
                        "Você já é o melhor estudante da turma. Deseja praticar mais?"
                    ],
                    options=[
                        ("Revisar exercícios do nível Difícil", "START_QUIZ"),
                        ("Rever meu Certificado de Vitória", "SHOW_CERT"),
                        ("Apenas passeando pela sala", "CLOSE")
                    ]
                )
            else:
                self.ui.show_dialog(
                    "Prof. Roberto",
                    [
                        f"Olá, {self.player.name}! Seja muito bem-vindo à aula de Matemática.",
                        "Aqui você irá desafiar sua mente e subir de nível acadêmico.",
                        "Está pronto para responder aos exercícios?"
                    ],
                    options=[
                        ("Sim! Iniciar exercícios matemáticos", "START_QUIZ"),
                        ("Como funciona o sistema de progressão?", "INFO_RULES"),
                        ("Agora não, vou me preparar primeiro.", "CLOSE")
                    ]
                )
            self.state = STATE_DIALOG

    def update(self, dt):
        """Atualização da lógica e física."""
        if self.state == STATE_EXPLORE:
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1

            self.player.update(dt, dx, dy, self.world, sound_manager)

            if self.world.current_zone == ZONE_CLASSROOM:
                self.world.teacher.update(dt)

            # Câmera acompanha o jogador suavemente
            self.gl.set_camera(self.player.x + 16, self.player.y + 24, self.world.zone_w, self.world.zone_h)

    def render(self, dt):
        """Renderização via PyOpenGL."""
        if self.state == STATE_NAME_INPUT:
            self.ui.draw_name_input_screen(dt)

        elif self.state == STATE_EXPLORE or self.state == STATE_DIALOG:
            self.gl.clear((20, 24, 34))

            # 1. Desenha o mundo com a Câmera 2D ativada
            self.gl.apply_camera()
            self.world.draw_background(self.gl, self.assets)

            # Professor (na sala de aula)
            if self.world.current_zone == ZONE_CLASSROOM:
                self.world.teacher.draw(self.gl, self.assets)

            # Jogador
            self.player.draw(self.gl, self.assets)
            self.gl.reset_camera()

            # 2. HUD e Diálogo sobrepostos na tela (em coordenadas fixas de tela)
            loc_name = "Sala de Matemática" if self.world.current_zone == ZONE_CLASSROOM else "Corredor Principal"
            nearby = self.world.get_nearby_interactable(self.player.hitbox)
            self.ui.draw_exploration_hud(self.player.name, loc_name, self.quiz, nearby)

            if self.state == STATE_DIALOG:
                self.ui.draw_dialog()

        elif self.state == STATE_QUIZ:
            self.ui.draw_quiz(self.quiz, self.player.name)

        elif self.state == STATE_VICTORY:
            self.ui.draw_victory_screen(self.player.name)

if __name__ == "__main__":
    game = DesafioEscolarGame()
    game.run()
