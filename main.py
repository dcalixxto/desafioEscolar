"""
O Desafio Escolar - Jogo Educativo 2D com PyGame e OpenGL.
Desenvolvido para FUPAC/UNIPAC - Ciência da Computação / Programação Para Jogos.
Equipe Pecê Gamer.
"""

import os
import sys
import ctypes
import pygame
from OpenGL.GL import *


def _enable_high_dpi():
    """Ativa DPI-awareness no Windows.

    Sem isso, em monitores com escala (ex.: 125%), o sistema operacional
    estica a janela do jogo e os textos/gráficos ficam "borrados". Com o
    jogo DPI-aware, o pygame enxerga a resolução física real do monitor e
    a tela cheia usa os pixels nativos.
    """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)   # PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


_enable_high_dpi()

from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    STATE_MENU, STATE_NAME_INPUT, STATE_EXPLORE, STATE_DIALOG, STATE_QUIZ, STATE_VICTORY, STATE_GAME_OVER, STATE_LEADERBOARD,
    STATE_COMP_SETUP, STATE_COMP_REP_NAME, STATE_COMP_EXPLORE, STATE_COMP_DIALOG, STATE_COMP_QUIZ, STATE_COMP_TURN_END, STATE_COMP_RESULT,
    DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL, DIFF_DESAFIO,
    SUBJECTS, SUBJECTS_BY_DOOR, SUBJECT_MATH,
    COMP_MAX_REPS,
)
from game.gl_renderer import GLRenderer
from game.audio import sound_manager
from game.assets import AssetManager
from game.entities import Player
from game.world import SchoolWorld, ZONE_HALLWAY
from game.quiz_data import QuizManager
from game.ui import UIManager
from game.scoring import ScoreManager
from game.leaderboard import Leaderboard
from game.competition import CompetitionManager
from game.ui_competition import CompetitionUI

class DesafioEscolarGame:
    MUSIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music", "tema.mp3")

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        self.gl = GLRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.assets = AssetManager(self.gl)
        self.world = SchoolWorld()
        self.player = Player(736, 200, name="Estudante", gender="masculino")
        self.quiz = QuizManager(SUBJECT_MATH)
        self.ui = UIManager(self.gl, self.assets, sound_manager)
        self.score = ScoreManager()
        self.leaderboard = Leaderboard()
        self.last_saved_session = None

        # Modo Competição (duas equipes, um representante por vez)
        self.comp = CompetitionManager()
        self.comp_ui = CompetitionUI(self.gl, self.assets, sound_manager)

        self.state = STATE_MENU
        self.running = True
        self.last_dialog_subject = SUBJECT_MATH
        self.music_enabled = True
        self.start_background_music()

    # ------------------------------------------------------------------
    # Música de fundo (toca durante o jogo inteiro; [M] pausa/retoma)
    # ------------------------------------------------------------------
    def start_background_music(self):
        try:
            if os.path.exists(self.MUSIC_PATH):
                pygame.mixer.music.load(self.MUSIC_PATH)
                pygame.mixer.music.set_volume(0.55)
                pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def toggle_background_music(self):
        try:
            if self.music_enabled:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            self.music_enabled = not self.music_enabled
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Tela cheia (requisito do Modo Competição; disponível a qualquer momento)
    # ------------------------------------------------------------------
    def is_fullscreen(self):
        return bool(self.screen.get_flags() & pygame.FULLSCREEN)

    def set_fullscreen(self, enabled):
        try:
            # recria o subsistema de vídeo: sem isso o SDL reaproveita a
            # janela antiga e ignora o tamanho pedido (causa da proporção
            # distorcida ao alternar janela <-> tela cheia)
            pygame.display.quit()
            pygame.display.init()

            if enabled:
                # usa a resolução nativa do monitor: evita modos de vídeo
                # exóticos (ex.: 960x540) que distorcem em alguns monitores
                desktop_w, desktop_h = pygame.display.get_desktop_sizes()[0]
                flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN
                self.screen = pygame.display.set_mode((desktop_w, desktop_h), flags)
            else:
                flags = pygame.OPENGL | pygame.DOUBLEBUF
                self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)

            # a troca de modo recria o contexto GL: reconfigura o pipeline,
            # o viewport (letterbox 16:9) e regenera as texturas
            self.gl.reinit()
            self.gl.refresh_viewport()
            self.assets.rebuild()
            return True
        except Exception:
            return False

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.is_fullscreen())

    def ensure_fullscreen(self):
        if not self.is_fullscreen():
            self.set_fullscreen(True)

    def reset_for_next_student(self):
        self.score.reset()
        self.last_saved_session = None
        self.quiz = QuizManager(SUBJECT_MATH)
        self.world = SchoolWorld()
        self.player = Player(736, 200, name="Estudante", gender=self.ui.selected_gender)
        self.state = STATE_MENU
        self.ui.player_name_input = ""
        # keep selected gender

    def reset_exploration_for_turn(self):
        """Posiciona o representante da vez no corredor, como um novo aluno.

        Alternna o gênero do sprite entre representantes para diferenciar
        visualmente cada rodada.
        """
        rep = self.comp.run["rep"] if self.comp.run else 1
        gender = "masculino" if rep % 2 == 1 else "feminino"
        team_name = self.comp.team_names[self.comp.turn_team]
        rep_name = self.comp.run.get("name") if self.comp.run else None
        display_name = rep_name or f"{team_name} - Rep {rep}"
        self.world = SchoolWorld()
        self.player = Player(736, 200, name=display_name, gender=gender)

    def save_current_score(self, reason="fim"):
        try:
            snap = self.score.snapshot(self.player.name, self.quiz.subject_name() if hasattr(self.quiz, 'subject_name') else '', self.player.gender)
            snap["motivo"] = reason
            self.leaderboard.add_entry(snap)
            self.last_saved_session = snap
        except Exception:
            pass

    def handle_student_game_over(self):
        # salva pontuacao e mostra opcoes para proximo aluno
        self.save_current_score("sem_coracoes")
        self.state = STATE_GAME_OVER


    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render(dt)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def start_quiz_for_subject(self, subject_id):
        self.quiz.set_subject(subject_id)
        if not self.quiz.completed_levels.get(DIFF_FACIL, False):
            self.quiz.start_level(DIFF_FACIL)
        elif not self.quiz.completed_levels.get(DIFF_MEDIO, False):
            self.quiz.start_level(DIFF_MEDIO)
        elif not self.quiz.completed_levels.get(DIFF_DIFICIL, False):
            self.quiz.start_level(DIFF_DIFICIL)
        elif not self.quiz.completed_levels.get(DIFF_DESAFIO, False):
            self.quiz.start_level(DIFF_DESAFIO)
        else:
            self.quiz.start_level(DIFF_DESAFIO)
        self.state = STATE_QUIZ

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # [F11] alterna tela cheia em qualquer estado
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue

            # [M] pausa/retoma a música (exceto em telas de digitação)
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_m
                    and self.state not in (STATE_NAME_INPUT, STATE_COMP_SETUP, STATE_COMP_REP_NAME)):
                self.toggle_background_music()
                continue

            if self.state == STATE_MENU:
                action = self.comp_ui.handle_menu_event(event)
                if action == "CLASSIC":
                    sound_manager.play("blip")
                    self.state = STATE_NAME_INPUT
                elif action == "COMPETITION":
                    sound_manager.play("door")
                    self.ensure_fullscreen()
                    self.comp.reset()
                    self.comp_ui.setup_team_idx = 0
                    self.comp_ui.team_name_input = ""
                    self.comp_ui._clear_overlays()
                    self.state = STATE_COMP_SETUP
                elif action == "QUIT":
                    self.running = False
                    return

            elif self.state == STATE_COMP_SETUP:
                result = self.comp_ui.handle_setup_event(event)
                if result == "BACK":
                    sound_manager.play("blip")
                    self.comp.reset()
                    self.state = STATE_MENU
                elif result is not None:
                    tag, name = result
                    if tag == "TEAM1":
                        self.comp.team_names[0] = name.strip() or "Equipe 1"
                    else:  # TEAM2
                        name2 = name.strip() or "Equipe 2"
                        self.comp.setup_teams(self.comp.team_names[0], name2)
                        self.comp.start_turn()
                        self.comp_ui.rep_name_input = ""
                        sound_manager.play("levelup")
                        self.state = STATE_COMP_REP_NAME

            elif self.state == STATE_COMP_REP_NAME:
                result = self.comp_ui.handle_rep_name_event(event)
                if result is not None:
                    _, rep_name = result
                    self.comp.run["name"] = rep_name or None
                    self.comp_ui.rep_name_input = ""
                    self.reset_exploration_for_turn()
                    self.state = STATE_COMP_EXPLORE

            elif self.state == STATE_COMP_EXPLORE:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_e, pygame.K_SPACE]:
                        self.try_interact()
                    elif event.key == pygame.K_ESCAPE:
                        self.ui.show_dialog(
                            "Encerrar Competição?",
                            [
                                "Deseja abandonar a competição e voltar ao menu?",
                                "O progresso das rodadas atuais será perdido."
                            ],
                            options=[
                                ("Sim, encerrar", "END_COMP"),
                                ("Não, continuar jogando", "CLOSE")
                            ]
                        )
                        self.state = STATE_COMP_DIALOG

            elif self.state == STATE_COMP_DIALOG:
                action = self.ui.handle_dialog_event(event)
                if action == "CLOSE":
                    self.state = STATE_COMP_EXPLORE
                elif action == "START_COMP_QUIZ":
                    self.ui.close_dialog()
                    self.state = STATE_COMP_QUIZ
                elif action == "INFO_COMP":
                    self.ui.show_dialog(
                        "Regras da Competição",
                        [
                            "- Cada nível tem 5 perguntas de 4 alternativas, da matéria do professor visitado.",
                            "- Acertar soma pontos (10/15/20/30); errar custa 1 coração.",
                            "- 'Responder depois' guarda a pergunta para o fim do nível.",
                            "- Ao perder os 3 corações, entra um representante da outra equipe."
                        ],
                        options=[
                            ("Entendi, vamos começar!", "START_COMP_QUIZ"),
                            ("Voltar", "CLOSE")
                        ]
                    )
                elif action == "END_COMP":
                    self.ui.close_dialog()
                    self.comp.reset()
                    self.state = STATE_MENU

            elif self.state == STATE_COMP_QUIZ:
                action = self.comp_ui.handle_quiz_event(event, self.comp)
                if action is None:
                    continue
                if action == "EXIT":
                    sound_manager.play("blip")
                    self.state = STATE_COMP_EXPLORE
                elif action.startswith("ANSWER_"):
                    opt_idx = int(action.split("_")[1])
                    is_correct, explanation = self.comp.answer(opt_idx)
                    self.comp_ui.show_feedback(is_correct, explanation)
                elif action == "DEFER":
                    self.comp.defer_question()
                elif action == "CONFIRM":
                    flow = self.comp.confirm_after_feedback()
                    if flow == "LEVEL_COMPLETE":
                        self.comp_ui.show_level_complete(self.comp)
                    elif flow == "TURN_END":
                        self.comp.end_turn()
                        self.comp_ui._clear_overlays()
                        self.comp_ui.continue_button = None
                        self.state = STATE_COMP_TURN_END

            elif self.state == STATE_COMP_TURN_END:
                action = self.comp_ui.handle_turn_end_event(event)
                if action == "NEXT":
                    if self.comp.competition_over():
                        sound_manager.play("fanfare")
                        self.state = STATE_COMP_RESULT
                    else:
                        self.comp.start_turn()
                        self.comp_ui.rep_name_input = ""
                        self.state = STATE_COMP_REP_NAME
                elif action == "END_COMPETITION":
                    sound_manager.play("fanfare")
                    self.state = STATE_COMP_RESULT

            elif self.state == STATE_COMP_RESULT:
                action = self.comp_ui.handle_result_event(event)
                if action == "MENU":
                    sound_manager.play("blip")
                    self.comp.reset()
                    self.comp_ui._result_seeded = False
                    self.comp_ui._result_particles = []
                    self.state = STATE_MENU

            elif self.state == STATE_NAME_INPUT:
                chosen = self.ui.handle_name_input_event(event)
                if chosen is not None:
                    if isinstance(chosen, tuple):
                        chosen_name, chosen_gender = chosen
                    else:
                        chosen_name, chosen_gender = chosen, "masculino"
                    self.player.name = chosen_name
                    self.player.gender = chosen_gender
                    self.score.reset()
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
                    self.start_quiz_for_subject(self.last_dialog_subject)
                elif action == "INFO_RULES":
                    subj = self.last_dialog_subject
                    cfg = SUBJECTS[subj]
                    self.ui.show_dialog(
                        cfg["teacher"],
                        [
                            f"Sala de {cfg['name']}: desafios com progressão de dificuldade.",
                            "- Comece no nível FÁCIL e desbloqueie MÉDIO e DIFÍCIL.",
                            "- Ao errar, pode surgir um combate contra o Espírito da Dúvida.",
                            "- Acerte para causar dano; se sua energia acabar, revise e tente novamente."
                        ],
                        options=[
                            ("Vamos começar os exercícios!", "START_QUIZ"),
                            ("Obrigado pela explicação.", "CLOSE")
                        ]
                    )

            elif self.state == STATE_QUIZ:
                result = self.ui.handle_quiz_event(event, self.quiz)
                if result is not None:
                    # checa perda de todos os coracoes
                    if self.score.is_game_over():
                        self.ui.feedback_active = False
                        self.quiz.end_combat()
                        self.quiz.in_quiz = False
                        self.handle_student_game_over()
                        continue
                    if result.startswith("SWITCH_DIFF_"):
                        d_key = result.split("SWITCH_DIFF_")[1]
                        self.quiz.start_level(d_key)
                    elif result.startswith("ANSWER_"):
                        opt_idx = int(result.split("_")[1])
                        # pergunta já pontuada (defesa contra pontos duplicados
                        # em novas tentativas após dica/combate)
                        already_scored = getattr(self.quiz, "current_question_scored", False)
                        is_correct, explanation = self.quiz.answer_question(opt_idx)
                        # pontuacao e vidas: acerto ganha pontos UMA vez por pergunta; erro perde 1 coracao
                        if already_scored:
                            # pergunta concluida: nenhuma pontuacao ou penalidade nova
                            pass
                        elif is_correct:
                            pts = 10
                            if hasattr(self.quiz, 'current_difficulty'):
                                from game.config import DIFF_MEDIO, DIFF_DIFICIL, DIFF_DESAFIO
                                if self.quiz.current_difficulty == DIFF_MEDIO: pts = 15
                                elif self.quiz.current_difficulty == DIFF_DIFICIL: pts = 20
                                elif self.quiz.current_difficulty == DIFF_DESAFIO: pts = 30
                            self.score.add_correct(pts)
                        else:
                            self.score.add_wrong(1)
                        self.ui.start_quiz_feedback(is_correct, explanation)
                    elif result == "LEVEL_COMPLETE":
                        cfg = SUBJECTS[self.quiz.current_subject]
                        self.ui.show_dialog(
                            cfg["teacher"],
                            [
                                f"Excelente trabalho, {self.player.name}!",
                                f"Você concluiu um nível em {cfg['name']} e desbloqueou o próximo desafio.",
                                "Continue praticando para dominar todas as matérias!"
                            ],
                            options=[
                                ("Continuar para o próximo nível", "START_QUIZ"),
                                ("Voltar a explorar a sala", "CLOSE")
                            ]
                        )
                        self.last_dialog_subject = self.quiz.current_subject
                        self.state = STATE_DIALOG
                    elif result == "SUBJECT_COMPLETE":
                        cfg = SUBJECTS[self.quiz.current_subject]
                        self.ui.show_dialog(
                            cfg["teacher"],
                            [
                                f"Parabéns, {self.player.name}!",
                                f"Você concluiu todos os níveis de {cfg['name']}!",
                                "Explore outras salas ou revise os exercícios quando quiser."
                            ],
                            options=[
                                ("Revisar nível Difícil", "START_QUIZ"),
                                ("Voltar a explorar", "CLOSE")
                            ]
                        )
                        self.last_dialog_subject = self.quiz.current_subject
                        self.state = STATE_DIALOG
                    elif result == "COMBAT_DEFEAT":
                        cfg = SUBJECTS[self.quiz.current_subject]
                        self.quiz.end_combat()
                        self.quiz.in_quiz = False
                        self.ui.show_dialog(
                            cfg["teacher"],
                            [
                                "O Espírito da Dúvida venceu desta vez...",
                                "Respire fundo, revise a explicação e volte com mais energia!",
                                "Você pode tentar o desafio novamente quando estiver pronto."
                            ],
                            is_notice=True
                        )
                        self.last_dialog_subject = self.quiz.current_subject
                        self.state = STATE_DIALOG
                    elif result == "VICTORY":
                        self.save_current_score("vitoria_matematica")
                        self.state = STATE_VICTORY
                    elif result == "EXIT_QUIZ":
                        self.quiz.end_combat()
                        self.quiz.in_quiz = False
                        self.state = STATE_EXPLORE

            elif self.state == STATE_VICTORY:
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                    sound_manager.stop_music()
                    sound_manager.play("blip")
                    self.state = STATE_EXPLORE
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    sound_manager.stop_music()
                    self.state = STATE_LEADERBOARD

            elif self.state == STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        self.reset_for_next_student()
                    elif event.key == pygame.K_t:
                        self.state = STATE_LEADERBOARD
                    elif event.key == pygame.K_ESCAPE:
                        self.reset_for_next_student()

            elif self.state == STATE_LEADERBOARD:
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_v]:
                    if self.last_saved_session is not None and self.score.is_game_over():
                        self.state = STATE_GAME_OVER
                    else:
                        self.state = STATE_NAME_INPUT if self.last_saved_session is None else STATE_EXPLORE

    def try_interact(self):
        interactable = self.world.get_nearby_interactable(self.player.hitbox)
        if not interactable:
            return

        competition = (self.state == STATE_COMP_EXPLORE)
        sound_manager.play("blip")

        if interactable.itype in SUBJECTS_BY_DOOR:
            sid = SUBJECTS_BY_DOOR[interactable.itype]
            sound_manager.play("door")
            self.world.set_zone(SUBJECTS[sid]["zone"], self.player, subject_id=sid)

        elif interactable.itype == "DOOR_EXIT":
            sound_manager.play("door")
            # volta para o corredor em frente à porta da matéria atual
            sid = self.world.current_subject or SUBJECT_MATH
            self.world.set_zone(ZONE_HALLWAY, self.player, subject_id=sid)

        elif interactable.itype == "DOOR_LOCKED":
            self.ui.show_dialog(
                interactable.label,
                interactable.message.split("\n"),
                is_notice=True
            )
            self.state = STATE_COMP_DIALOG if competition else STATE_DIALOG

        elif interactable.itype == "INFO":
            self.ui.show_dialog(
                interactable.label,
                interactable.message.split("\n"),
                is_notice=True
            )
            self.state = STATE_COMP_DIALOG if competition else STATE_DIALOG

        elif interactable.itype == "TEACHER":
            if competition:
                # Modo Competição: o professor conduz o representante da vez
                # e só pergunta sobre o tema pelo qual é responsável
                sid = interactable.subject or self.world.current_subject or SUBJECT_MATH
                self.comp.set_subject(sid)
                subject_name = SUBJECTS[sid]["name"]
                team_name = self.comp.team_names[self.comp.turn_team]
                rep = self.comp.run["rep"]
                self.ui.show_dialog(
                    interactable.label,
                    [
                        f"Olá, Representante {rep}/{COMP_MAX_REPS} da {team_name}!",
                        f"Pronto para os desafios de {subject_name}? Avance pelos níveis para a sua equipe!",
                        f"Cada nível tem 5 perguntas de {subject_name}; errar custa 1 coração."
                    ],
                    options=[
                        ("Iniciar desafios da competição", "START_COMP_QUIZ"),
                        ("Como funciona?", "INFO_COMP"),
                        ("Agora não, vou dar uma volta.", "CLOSE")
                    ]
                )
                self.state = STATE_COMP_DIALOG
                return

            sid = interactable.subject or self.world.current_subject or SUBJECT_MATH
            self.last_dialog_subject = sid
            self.quiz.set_subject(sid)
            cfg = SUBJECTS[sid]
            if self.quiz.is_subject_completed(sid):
                self.ui.show_dialog(
                    cfg["teacher"],
                    [
                        f"Incrível, {self.player.name}!",
                        f"Você dominou todos os níveis de {cfg['name']}!",
                        "Deseja revisar os exercícios ou explorar outras salas?"
                    ],
                    options=[
                        ("Revisar exercícios do nível Difícil", "START_QUIZ"),
                        ("Ver certificado da escola", "SHOW_CERT"),
                        ("Apenas passeando pela sala", "CLOSE")
                    ]
                )
            else:
                self.ui.show_dialog(
                    cfg["teacher"],
                    [
                        f"Olá, {self.player.name}! Bem-vindo à aula de {cfg['name']}.",
                        "Aqui você enfrentará desafios de conhecimento e poderá evoluir de nível.",
                        "Se errar, prepare-se: o Espírito da Dúvida pode desafiar você em combate!"
                    ],
                    options=[
                        (f"Iniciar desafios de {cfg['name']}", "START_QUIZ"),
                        ("Como funciona?", "INFO_RULES"),
                        ("Agora não, vou me preparar primeiro.", "CLOSE")
                    ]
                )
            self.state = STATE_DIALOG

    def update(self, dt):
        if self.state == STATE_EXPLORE or self.state == STATE_COMP_EXPLORE:
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
            self.world.update_students(dt)

            if self.world.current_zone != ZONE_HALLWAY:
                self.world.teacher.update(dt)

            self.gl.set_camera(self.player.x + 16, self.player.y + 24, self.world.zone_w, self.world.zone_h)

    def render(self, dt):
        if self.state == STATE_MENU:
            self.comp_ui.draw_menu(dt)

        elif self.state == STATE_COMP_SETUP:
            first_name = self.comp.team_names[0] if self.comp_ui.setup_team_idx == 1 else ""
            self.comp_ui.draw_setup(dt, self.comp_ui.setup_team_idx, first_name)

        elif self.state == STATE_COMP_REP_NAME:
            self.comp_ui.draw_rep_name_screen(dt, self.comp)

        elif self.state == STATE_COMP_QUIZ:
            self.comp_ui.draw_quiz(dt, self.comp)

        elif self.state == STATE_COMP_TURN_END:
            self.comp_ui.draw_turn_end(dt, self.comp)

        elif self.state == STATE_COMP_RESULT:
            self.comp_ui.draw_result(dt, self.comp)

        elif self.state == STATE_COMP_EXPLORE or self.state == STATE_COMP_DIALOG:
            # exploração clássica: o representante anda pela escola normalmente
            self.gl.clear((20, 24, 34))

            self.gl.apply_camera()
            self.world.draw_background(self.gl, self.assets)
            self.world.draw_students(self.gl, self.assets)
            if self.world.current_zone != ZONE_HALLWAY:
                self.world.teacher.draw(self.gl, self.assets)
            self.player.draw(self.gl, self.assets)
            self.gl.reset_camera()

            if self.world.current_zone == ZONE_HALLWAY:
                loc_name = "Corredor Principal"
            else:
                sid = self.world.current_subject or SUBJECT_MATH
                loc_name = f"Sala de {SUBJECTS[sid]['name']}"
            nearby = self.world.get_nearby_interactable(self.player.hitbox)
            self.comp_ui.draw_competition_hud(self.comp, loc_name, nearby)
            self.gl.draw_vignette(45)

            if self.state == STATE_COMP_DIALOG:
                self.ui.draw_dialog()

        elif self.state == STATE_NAME_INPUT:
            self.ui.draw_name_input_screen(dt)

        elif self.state == STATE_EXPLORE or self.state == STATE_DIALOG:
            self.gl.clear((20, 24, 34))

            self.gl.apply_camera()
            self.world.draw_background(self.gl, self.assets)
            self.world.draw_students(self.gl, self.assets)
            if self.world.current_zone != ZONE_HALLWAY:
                self.world.teacher.draw(self.gl, self.assets)
            self.player.draw(self.gl, self.assets)
            self.gl.reset_camera()

            if self.world.current_zone == ZONE_HALLWAY:
                loc_name = "Corredor Principal"
            else:
                sid = self.world.current_subject or SUBJECT_MATH
                loc_name = f"Sala de {SUBJECTS[sid]['name']}"
            nearby = self.world.get_nearby_interactable(self.player.hitbox)
            self.ui.draw_exploration_hud(self.player.name, loc_name, self.quiz, nearby, self.score)
            self.gl.draw_vignette(45)

            if self.state == STATE_DIALOG:
                self.ui.draw_dialog()

        elif self.state == STATE_QUIZ:
            self.ui.draw_quiz(self.quiz, self.player.name, self.score)

        elif self.state == STATE_VICTORY:
            self.ui.draw_victory_screen(self.player.name, self.quiz)

        elif self.state == STATE_GAME_OVER:
            entries = self.leaderboard.top(10)
            self.ui.draw_game_over_student(self.player.name, self.score, entries)

        elif self.state == STATE_LEADERBOARD:
            entries = self.leaderboard.top(10)
            self.ui.draw_leaderboard_screen(entries)

if __name__ == "__main__":
    game = DesafioEscolarGame()
    game.run()
