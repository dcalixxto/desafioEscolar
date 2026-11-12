"""
Módulo de Interface do Usuário (UI) para 'O Desafio Escolar'.
Renderiza menus, diálogos, quiz com combate e telas de vitória via PyOpenGL.
"""

import math
import random
import pygame
from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_WHITE, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_BG_TOP, COLOR_BG_BOTTOM,
    DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL, DIFF_DESAFIO, DIFFICULTY_LABELS, SUBJECTS
)

def _to_logical(pos):
    """Converte a posição física do mouse para coordenadas lógicas (960x540),
    descontando o letterbox do viewport quando em tela cheia."""
    mx, my = pos
    surf = pygame.display.get_surface()
    if surf is None:
        return mx, my
    w, h = surf.get_size()
    if w == WINDOW_WIDTH and h == WINDOW_HEIGHT:
        return mx, my
    scale = min(w / float(WINDOW_WIDTH), h / float(WINDOW_HEIGHT))
    vx = (w - WINDOW_WIDTH * scale) / 2.0
    vy = (h - WINDOW_HEIGHT * scale) / 2.0
    return int((mx - vx) / scale), int((my - vy) / scale)


class UIManager:
    def __init__(self, gl_renderer, assets, sound_manager):
        self.gl = gl_renderer
        self.assets = assets
        self.sound = sound_manager

        self.player_name_input = ""
        self.selected_gender = "masculino"  # masculino/feminino
        self.cursor_timer = 0.0

        self.dialog_active = False
        self.dialog_title = ""
        self.dialog_lines = []
        self.dialog_options = []
        self.dialog_selected_opt = 0
        self.dialog_is_notice = False

        self.quiz_buttons = []
        self.hovered_option = -1
        self.feedback_active = False
        self.feedback_correct = False
        self.feedback_text = ""

        self._victory_particles = []
        self._victory_seeded = False

    def handle_name_input_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_TAB, pygame.K_LEFT, pygame.K_RIGHT):
                self.selected_gender = "feminino" if self.selected_gender == "masculino" else "masculino"
                self.sound.play("blip")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                name = self.player_name_input.strip()
                if not name:
                    name = "Estudante"
                self.sound.play("blip")
                return (name, self.selected_gender)
            elif event.key == pygame.K_BACKSPACE:
                if len(self.player_name_input) > 0:
                    self.player_name_input = self.player_name_input[:-1]
                    self.sound.play("blip")
            else:
                if len(event.unicode) > 0 and event.unicode.isprintable() and len(self.player_name_input) < 18:
                    self.player_name_input += event.unicode
                    self.sound.play("blip")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = _to_logical(pygame.mouse.get_pos())
            pw, ph = 680, 420
            px = (WINDOW_WIDTH - pw) / 2
            py = (WINDOW_HEIGHT - ph) / 2
            mrect = pygame.Rect(px + 170, py + 270, 150, 36)
            frect = pygame.Rect(px + 360, py + 270, 150, 36)
            if mrect.collidepoint(mx, my):
                self.selected_gender = "masculino"; self.sound.play("blip")
            elif frect.collidepoint(mx, my):
                self.selected_gender = "feminino"; self.sound.play("blip")
        return None

    def draw_name_input_screen(self, dt):
        self.cursor_timer += dt
        self.gl.clear(COLOR_BG_BOTTOM)
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG_TOP, COLOR_BG_BOTTOM)
        self.gl.draw_vignette(60)

        pw, ph = 680, 420
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2

        self.gl.draw_panel(px, py, pw, ph, (26, 32, 48, 245), border_color=(70, 96, 138), border_width=3, radius=18)
        self.gl.draw_panel(px + 5, py + 5, pw - 10, ph - 10, (0, 0, 0, 0), border_color=(48, 68, 100), border_width=1, radius=14, shadow=False)
        self.gl.draw_rounded_rect(px + 40, py - 3, pw - 80, 6, COLOR_ACCENT, radius=3)

        self.gl.draw_text("O DESAFIO ESCOLAR", WINDOW_WIDTH / 2, py + 40, color=COLOR_ACCENT, size=34, bold=True, center_x=True)
        self.gl.draw_text("Digite seu nome, escolha seu personagem e comece a jornada!", WINDOW_WIDTH / 2, py + 90, color=(180, 220, 255), size=15, center_x=True)

        bx, by, bw, bh = px + 140, py + 140, 400, 50
        self.gl.draw_panel(bx, by, bw, bh, (16, 19, 30), border_color=COLOR_PRIMARY, border_width=2, radius=10, shadow=False)

        display_text = self.player_name_input
        show_cursor = (int(self.cursor_timer * 2.5) % 2 == 0)
        cursor_str = "|" if show_cursor else " "
        if not display_text and not show_cursor:
            self.gl.draw_text("Digite seu nome...", bx + 16, by + 15, color=(90, 105, 130), size=18)
        else:
            self.gl.draw_text(display_text + cursor_str, bx + 16, by + 15, color=COLOR_WHITE, size=20, bold=True)

        self.gl.draw_text("Escolha seu personagem:", WINDOW_WIDTH / 2, py + 235, color=COLOR_WHITE, size=16, bold=True, center_x=True)
        msel = self.selected_gender == "masculino"
        fsel = self.selected_gender == "feminino"
        self.gl.draw_panel(px + 170, py + 270, 150, 36, COLOR_PRIMARY_DARK if msel else (35,45,60), border_color=COLOR_ACCENT if msel else (70,90,120), border_width=2 if msel else 1, radius=8, shadow_offset=(2,3))
        self.gl.draw_text("Homem", px + 245, py + 279, color=COLOR_WHITE, size=15, bold=True, center_x=True)
        self.gl.draw_panel(px + 360, py + 270, 150, 36, COLOR_PRIMARY_DARK if fsel else (35,45,60), border_color=COLOR_ACCENT if fsel else (70,90,120), border_width=2 if fsel else 1, radius=8, shadow_offset=(2,3))
        self.gl.draw_text("Mulher", px + 435, py + 279, color=COLOR_WHITE, size=15, bold=True, center_x=True)
        self.gl.draw_text("[TAB/<- ->] alterna | clique para escolher", WINDOW_WIDTH / 2, py + 318, color=COLOR_TEXT_MUTED, size=13, center_x=True)

        self.gl.draw_panel(px + 190, py + 340, 300, 36, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=1, radius=8, shadow_offset=(2, 3))
        self.gl.draw_text("Pressione [ENTER] para Jogar", WINDOW_WIDTH / 2, py + 349, color=COLOR_WHITE, size=15, bold=True, center_x=True)
        self.gl.draw_text("Você tem 3 corações. A cada erro, perde 1. Sem corações, sua pontuação é salva!", WINDOW_WIDTH / 2, py + 388, color=(255, 200, 200), size=13, center_x=True)

    def draw_exploration_hud(self, player_name, location_name, quiz_mgr, interactable, score_mgr=None):
        # painel do estudante, no canto inferior esquerdo (nada no topo, para
        # não cobrir as placas com os nomes das salas)
        py = WINDOW_HEIGHT - 78
        self.gl.draw_panel(16, py, 360, 66, (20, 26, 40, 235), border_color=(64, 86, 118), border_width=2, radius=14, shadow_offset=(3, 4))
        self.gl.draw_circle(44, py + 28, 20, (36, 48, 70))
        self.gl.draw_circle(44, py + 28, 20, COLOR_PRIMARY, filled=False, border_width=2)
        self.gl.draw_text(player_name[:1].upper() if player_name else "A", 44, py + 17, color=COLOR_ACCENT, size=20, bold=True, center_x=True)
        self.gl.draw_text(f"Estudante: {player_name}", 74, py + 6, color=COLOR_WHITE, size=15, bold=True)
        self.gl.draw_text(f"Local: {location_name}", 74, py + 27, color=(150, 200, 255), size=13)
        if score_mgr is not None:
            hearts = getattr(score_mgr, "hearts", 0)
            score = getattr(score_mgr, "score", 0)
            hx = 240
            for i in range(3):
                col = COLOR_DANGER if i < hearts else (80,80,90)
                self.gl.draw_text("♥", hx + i*18, py + 6, color=col, size=18, bold=True)
            self.gl.draw_text(f"Pts: {score}", 240, py + 29, color=COLOR_ACCENT, size=13, bold=True)

        # progresso dos níveis, no canto inferior direito
        py2 = WINDOW_HEIGHT - 68
        subj_name = quiz_mgr.subject_name() if hasattr(quiz_mgr, "subject_name") else "Matemática"
        self.gl.draw_panel(WINDOW_WIDTH - 325, py2, 309, 56, (20, 26, 40, 235), border_color=(64, 86, 118), border_width=2, radius=14, shadow_offset=(3, 4))
        self.gl.draw_text(f"Progresso: {subj_name}", WINDOW_WIDTH - 310, py2 + 6, color=COLOR_ACCENT, size=14, bold=True)

        diffs = [
            (DIFF_FACIL, "Fácil", 0),
            (DIFF_MEDIO, "Médio", 52),
            (DIFF_DIFICIL, "Difícil", 106),
            (DIFF_DESAFIO, "Desafio", 166)
        ]
        base_x = WINDOW_WIDTH - 306
        for d_key, label, offset_x in diffs:
            completed = quiz_mgr.completed_levels.get(d_key, False)
            unlocked = quiz_mgr.unlocked_levels.get(d_key, False)
            icon_key = "star" if completed else ("lock_open" if unlocked else "lock_closed")
            color_text = COLOR_SUCCESS if completed else (COLOR_WHITE if unlocked else COLOR_TEXT_MUTED)
            self.gl.draw_texture(self.assets.textures[icon_key], base_x + offset_x, py2 + 22, 18, 18)
            self.gl.draw_text(label, base_x + offset_x + 22, py2 + 25, color=color_text, size=11, bold=True)

        # dica de interação, flutuando acima dos painéis inferiores
        if interactable is not None:
            pulse = 2 if (pygame.time.get_ticks() // 350) % 2 == 0 else 0
            bw, bh = 420 + pulse * 2, 40
            bx = (WINDOW_WIDTH - bw) / 2
            by = WINDOW_HEIGHT - 130
            self.gl.draw_glow_rect(bx, by, bw, bh, (247, 201, 72, 60), layers=3, spread=4)
            self.gl.draw_panel(bx, by, bw, bh, (255, 245, 180, 245), border_color=COLOR_ACCENT_DARK, border_width=2, radius=18, shadow_offset=(2, 4))
            self.gl.draw_text(f"[E / ESPAÇO] {interactable.label}", WINDOW_WIDTH / 2, by + 10, color=(30, 35, 45), size=15, bold=True, center_x=True)

    def show_dialog(self, title, lines, options=None, is_notice=False):
        self.dialog_active = True
        self.dialog_title = title
        self.dialog_lines = lines if isinstance(lines, list) else [lines]
        self.dialog_options = options if options is not None else []
        self.dialog_selected_opt = 0
        self.dialog_is_notice = is_notice
        self.sound.play("dialog")

    def close_dialog(self):
        self.dialog_active = False

    def handle_dialog_event(self, event):
        if not self.dialog_active:
            return None

        if event.type == pygame.KEYDOWN:
            if self.dialog_is_notice or not self.dialog_options:
                if event.key in [pygame.K_e, pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                    self.sound.play("blip")
                    self.close_dialog()
                    return "CLOSE"
            else:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.dialog_selected_opt = max(0, self.dialog_selected_opt - 1)
                    self.sound.play("blip")
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.dialog_selected_opt = min(len(self.dialog_options) - 1, self.dialog_selected_opt + 1)
                    self.sound.play("blip")
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e]:
                    self.sound.play("blip")
                    opt_text, opt_action = self.dialog_options[self.dialog_selected_opt]
                    return opt_action
        return None

    def draw_dialog(self):
        if not self.dialog_active:
            return

        pw = 780
        ph = 165 if not self.dialog_options else 220
        px = (WINDOW_WIDTH - pw) / 2
        py = WINDOW_HEIGHT - ph - 24

        self.gl.draw_panel(px, py, pw, ph, (20, 26, 42, 248), border_color=COLOR_PRIMARY, border_width=3, radius=16, shadow_offset=(4, 5))
        self.gl.draw_panel(px + 5, py + 5, pw - 10, ph - 10, (0, 0, 0, 0), border_color=(62, 92, 140), border_width=1, radius=12, shadow=False)
        self.gl.draw_panel(px + 20, py - 14, 280, 28, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=1, radius=8, shadow_offset=(2, 3))
        self.gl.draw_text(self.dialog_title, px + 30, py - 8, color=COLOR_WHITE, size=14, bold=True)

        for i, line in enumerate(self.dialog_lines):
            self.gl.draw_text(line, px + 30, py + 26 + i * 22, color=COLOR_TEXT, size=15)

        if self.dialog_options:
            start_y = py + 36 + len(self.dialog_lines) * 22
            for idx, (opt_text, _) in enumerate(self.dialog_options):
                is_selected = (idx == self.dialog_selected_opt)
                opt_color = COLOR_ACCENT if is_selected else COLOR_WHITE
                prefix = "> " if is_selected else "  "
                if is_selected:
                    self.gl.draw_panel(px + 26, start_y + idx * 26 - 2, pw - 52, 24, (45, 65, 100, 210), border_color=COLOR_ACCENT, border_width=1, radius=6, shadow=False)
                self.gl.draw_text(prefix + opt_text, px + 30, start_y + idx * 26 + 1, color=opt_color, size=14, bold=is_selected)
        elif self.dialog_is_notice:
            self.gl.draw_text("[Pressione E ou ESPAÇO para fechar]", px + pw - 250, py + ph - 26, color=COLOR_ACCENT, size=13)

    def start_quiz_feedback(self, is_correct, explanation):
        self.feedback_active = True
        self.feedback_correct = is_correct
        self.feedback_text = explanation
        if is_correct:
            self.sound.play("correct")
        else:
            self.sound.play("wrong")

    def handle_quiz_event(self, event, quiz_mgr):
        if self.feedback_active:
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e]:
                self.feedback_active = False
                # Se errou e ficou sem energia, encerra a tentativa
                if (not self.feedback_correct) and getattr(quiz_mgr, "in_combat", False) and getattr(quiz_mgr, "player_hp", 1) <= 0:
                    quiz_mgr.end_combat()
                    return "COMBAT_DEFEAT"

                if self.feedback_correct:
                    # Acerto (mesmo após dica/combate) avança de imediato para
                    # a próxima pergunta; a pontuação já foi concedida uma
                    # única vez em answer_question.
                    finished_level = quiz_mgr.advance_question()
                    if finished_level:
                        self.sound.play("levelup")
                        # vitória geral de matemática abre certificado
                        if quiz_mgr.is_game_completed():
                            self.sound.play("fanfare")
                            return "VICTORY"
                        # se completou a matéria atual (nível difícil)
                        if quiz_mgr.is_subject_completed(quiz_mgr.current_subject):
                            return "SUBJECT_COMPLETE"
                        return "LEVEL_COMPLETE"
                else:
                    # errou: permanece em combate, tenta responder novamente
                    quiz_mgr.retry_question()
                return "REFRESH"
            return None

        if event.type == pygame.KEYDOWN:
            key_map = {
                pygame.K_1: 0, pygame.K_a: 0,
                pygame.K_2: 1, pygame.K_b: 1,
                pygame.K_3: 2, pygame.K_c: 2,
                pygame.K_4: 3, pygame.K_d: 3
            }
            if event.key in key_map:
                opt_idx = key_map[event.key]
                self.sound.play("select")
                return f"ANSWER_{opt_idx}"
            elif event.key == pygame.K_ESCAPE:
                return "EXIT_QUIZ"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = _to_logical(event.pos)
            for rect, d_key in getattr(self, "diff_buttons", []):
                if rect.collidepoint(mx, my) and quiz_mgr.unlocked_levels.get(d_key, False):
                    self.sound.play("blip")
                    return f"SWITCH_DIFF_{d_key}"
            for idx, rect in enumerate(self.quiz_buttons):
                if rect.collidepoint(mx, my):
                    self.sound.play("select")
                    return f"ANSWER_{idx}"

        if event.type == pygame.MOUSEMOTION:
            mx, my = _to_logical(event.pos)
            prev = self.hovered_option
            self.hovered_option = -1
            for idx, rect in enumerate(self.quiz_buttons):
                if rect.collidepoint(mx, my):
                    self.hovered_option = idx
                    break
            if self.hovered_option != -1 and self.hovered_option != prev:
                self.sound.play("blip")

        return None

    def _wrap_text(self, text, max_chars):
        words = str(text).split()
        lines = [""]
        for w in words:
            if len(lines[-1]) + len(w) + 1 <= max_chars:
                lines[-1] = (lines[-1] + " " + w).strip()
            else:
                lines.append(w)
        return [l for l in lines if l]

    def _draw_hp_bar(self, x, y, w, h, hp, max_hp, color, label):
        self.gl.draw_text(label, x, y - 16, color=COLOR_WHITE, size=12, bold=True)
        self.gl.draw_rounded_rect(x, y, w, h, (45, 50, 65), radius=6)
        ratio = 0 if max_hp <= 0 else max(0.0, min(1.0, hp / max_hp))
        if ratio > 0:
            self.gl.draw_rounded_rect(x, y, int(w * ratio), h, color, radius=6)
        self.gl.draw_rounded_rect(x, y, w, h, (90, 100, 120), radius=6, filled=False, border_width=1)
        self.gl.draw_text(f"{hp}/{max_hp}", x + w / 2, y - 1, color=COLOR_WHITE, size=12, bold=True, center_x=True)

    def draw_quiz(self, quiz_mgr, student_name, score_mgr=None):
        self.gl.clear((16, 20, 32))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (30, 40, 64), (14, 18, 30))
        self.gl.draw_vignette(70)

        subject_name = quiz_mgr.subject_name() if hasattr(quiz_mgr, "subject_name") else "Matemática"
        self.gl.draw_panel(20, 16, WINDOW_WIDTH - 40, 60, (28, 36, 54, 245), border_color=(64, 86, 122), border_width=2, radius=14, shadow_offset=(3, 4))
        self.gl.draw_text(f"SALA DE {subject_name.upper()} - DESAFIO PROGRESSIVO", 40, 26, color=COLOR_WHITE, size=18, bold=True)
        extra = ""
        if score_mgr is not None:
            hearts = "♥"*getattr(score_mgr,"hearts",0) + "♡"*(3-getattr(score_mgr,"hearts",0))
            extra = f"   Vidas: {hearts}   Pontos: {getattr(score_mgr,"score",0)}   Acertos: {getattr(score_mgr,"correct",0)}  Erros: {getattr(score_mgr,"wrong",0)}"
        self.gl.draw_text(f"Estudante: {student_name}{extra}", 40, 49, color=(160, 200, 255), size=13)

        self.diff_buttons = []
        diff_info = [
            (DIFF_FACIL, "1.Fácil", 430),
            (DIFF_MEDIO, "2.Médio", 548),
            (DIFF_DIFICIL, "3.Difícil", 666),
            (DIFF_DESAFIO, "4.Desafio", 784)
        ]
        for d_key, label, bx in diff_info:
            is_cur = (quiz_mgr.current_difficulty == d_key)
            unlocked = quiz_mgr.unlocked_levels.get(d_key, False)
            completed = quiz_mgr.completed_levels.get(d_key, False)
            bg_col = COLOR_PRIMARY_DARK if is_cur else ((35, 48, 70) if unlocked else (25, 30, 42))
            border_col = COLOR_ACCENT if is_cur else (COLOR_PRIMARY if unlocked else (50, 60, 75))
            btn_w = 110 if d_key != DIFF_DESAFIO else 132
            btn_rect = pygame.Rect(bx, 24, btn_w, 40)
            self.diff_buttons.append((btn_rect, d_key))
            self.gl.draw_panel(bx, 24, btn_w, 40, bg_col, border_color=border_col, border_width=2 if is_cur else 1, radius=10, shadow_offset=(2, 3))
            icon = "star" if completed else ("lock_open" if unlocked else "lock_closed")
            self.gl.draw_texture(self.assets.textures[icon], bx + 6, 32, 20, 20)
            self.gl.draw_text(label, bx + 30, 35, color=COLOR_WHITE if unlocked else COLOR_TEXT_MUTED, size=13, bold=is_cur)

        # Combate (se ativo)
        in_combat = getattr(quiz_mgr, "in_combat", False)
        qy_base = 96
        if in_combat:
            cy = 86
            self.gl.draw_panel(40, cy, WINDOW_WIDTH - 80, 54, (46, 26, 36, 245), border_color=(180, 90, 90), border_width=2, radius=12, shadow_offset=(3, 4))
            self.gl.draw_text("COMBATE DE CONHECIMENTO: Espírito da Dúvida", 60, cy + 8, color=(255, 210, 210), size=15, bold=True)
            msg = getattr(quiz_mgr, "combat_message", "") or "Acerte para causar dano e vencer o duelo!"
            self.gl.draw_text(msg, 60, cy + 30, color=COLOR_WHITE, size=13)
            self._draw_hp_bar(520, cy + 10, 150, 12, getattr(quiz_mgr, "player_hp", 0), getattr(quiz_mgr, "player_max_hp", 3), COLOR_SUCCESS, "Você")
            self._draw_hp_bar(700, cy + 10, 150, 12, getattr(quiz_mgr, "enemy_hp", 0), getattr(quiz_mgr, "enemy_max_hp", 2), COLOR_DANGER, "Dúvida")
            qy_base = 150

        q = quiz_mgr.get_current_question()
        if not q:
            return

        qw, qh = WINDOW_WIDTH - 80, 130
        qx, qy = 40, qy_base
        self.gl.draw_panel(qx, qy, qw, qh, (30, 40, 60, 248), border_color=(74, 100, 145), border_width=2, radius=14, shadow_offset=(3, 4))

        total_q = quiz_mgr.total_questions_in_level()
        cur_q = quiz_mgr.current_question_idx + 1
        diff_label = DIFFICULTY_LABELS.get(quiz_mgr.current_difficulty, "")

        self.gl.draw_panel(qx + 16, qy + 12, 210, 24, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=1, radius=7, shadow=False)
        self.gl.draw_text(f"Nível {diff_label} • Questão {cur_q}/{total_q}", qx + 24, qy + 16, color=COLOR_WHITE, size=13, bold=True)
        self.gl.draw_text(q["title"], qx + 236, qy + 16, color=COLOR_ACCENT, size=14, bold=True)

        bar_x, bar_y, bar_w, bar_h = qx + 20, qy + 104, qw - 40, 10
        self.gl.draw_rounded_rect(bar_x, bar_y, bar_w, bar_h, (45, 58, 82), radius=5)
        prog = max(0.0, min(1.0, (cur_q - 1) / max(1, total_q)))
        if self.feedback_active and self.feedback_correct and not (in_combat and getattr(quiz_mgr, "enemy_hp", 0) > 0):
            prog = max(prog, cur_q / max(1, total_q))
        self.gl.draw_rounded_rect(bar_x, bar_y, int(bar_w * prog), bar_h, COLOR_SUCCESS, radius=5)

        q_lines = self._wrap_text(q["question"], 78)
        for i, line in enumerate(q_lines[:3]):
            self.gl.draw_text(line, qx + 20, qy + 46 + i * 20, color=COLOR_WHITE, size=16 if i < 2 else 15, bold=True)

        self.quiz_buttons.clear()
        letters = ["A", "B", "C", "D"]
        card_w = (WINDOW_WIDTH - 110) // 2
        card_h = 62
        base_opt_y = qy_base + 154

        for idx, opt_text in enumerate(q["options"]):
            col = idx % 2
            row = idx // 2
            cx = 40 + col * (card_w + 30)
            cy = base_opt_y + row * (card_h + 16)
            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            self.quiz_buttons.append(card_rect)

            is_hovered = (self.hovered_option == idx)
            bg_c = (50, 72, 108) if is_hovered else (28, 38, 58)
            border_c = COLOR_ACCENT if is_hovered else COLOR_PRIMARY
            if is_hovered:
                self.gl.draw_glow_rect(cx, cy, card_w, card_h, (247, 201, 72, 55), layers=2, spread=4)
            self.gl.draw_panel(cx, cy, card_w, card_h, bg_c, border_color=border_c, border_width=2 if is_hovered else 1,
                                radius=12, shadow_offset=(3, 4) if is_hovered else (2, 3))

            badge_bg = COLOR_ACCENT if is_hovered else COLOR_PRIMARY_DARK
            self.gl.draw_circle(cx + 29, cy + 31, 17, badge_bg)
            self.gl.draw_circle(cx + 29, cy + 31, 17, border_c, filled=False, border_width=1)
            self.gl.draw_text(letters[idx], cx + 29, cy + 21, color=(30, 30, 40) if is_hovered else COLOR_WHITE, size=18, bold=True, center_x=True)
            self.gl.draw_text(opt_text, cx + 58, cy + 21, color=COLOR_WHITE, size=16, bold=is_hovered)

        self.gl.draw_text("Clique ou use [1-4]/[A-D] • Acerte para vencer o combate quando ele aparecer • [ESC] voltar", WINDOW_WIDTH / 2, WINDOW_HEIGHT - 22, color=COLOR_TEXT_MUTED, size=13, center_x=True)

        if self.feedback_active:
            fb_w, fb_h = 740, 172
            fb_x = (WINDOW_WIDTH - fb_w) / 2
            fb_y = 360 if not in_combat else 372
            if self.feedback_correct:
                bg_col = (20, 55, 35, 250)
                bdr_col = COLOR_SUCCESS
                title_txt = "PARABÉNS! RESPOSTA CORRETA!"
                action_txt = "Pressione [ENTER] para continuar"
                title_col = COLOR_SUCCESS
            else:
                bg_col = (55, 25, 25, 250)
                bdr_col = COLOR_DANGER
                if getattr(quiz_mgr, "player_hp", 1) <= 0:
                    title_txt = "A DÚVIDA VENCEU... MAS VOCÊ PODE TENTAR DE NOVO!"
                    action_txt = "Pressione [ENTER] para voltar e revisar"
                else:
                    title_txt = "RESPOSTA ERRADA! O ESPÍRITO DA DÚVIDA ATACOU!"
                    action_txt = "Pressione [ENTER] para contra-atacar respondendo"
                title_col = (255, 160, 150)

            self.gl.draw_panel(fb_x, fb_y, fb_w, fb_h, bg_col, border_color=bdr_col, border_width=3, radius=16, shadow_offset=(4, 5))
            self.gl.draw_text(title_txt, WINDOW_WIDTH / 2, fb_y + 16, color=title_col, size=17, bold=True, center_x=True)
            self.gl.draw_text("Dica:" if not self.feedback_correct else "Explicação:", fb_x + 24, fb_y + 50, color=COLOR_ACCENT, size=14, bold=True)
            for i, line in enumerate(self._wrap_text(self.feedback_text, 98)[:2]):
                self.gl.draw_text(line, fb_x + 24, fb_y + 74 + i * 22, color=COLOR_WHITE, size=14)
            self.gl.draw_panel(WINDOW_WIDTH / 2 - 190, fb_y + 122, 380, 32, (30, 40, 60), border_color=bdr_col, border_width=1, radius=8, shadow=False)
            self.gl.draw_text(action_txt, WINDOW_WIDTH / 2, fb_y + 129, color=COLOR_WHITE, size=14, bold=True, center_x=True)

    def _seed_victory_particles(self):
        if self._victory_seeded:
            return
        self._victory_seeded = True
        rnd = random.Random(42)
        colors = [COLOR_ACCENT, (120, 220, 255), (140, 255, 180), (255, 160, 200), COLOR_WHITE]
        for _ in range(40):
            self._victory_particles.append({
                "x": rnd.uniform(0, WINDOW_WIDTH),
                "y": rnd.uniform(-80, WINDOW_HEIGHT),
                "s": rnd.uniform(2, 5),
                "v": rnd.uniform(18, 55),
                "c": rnd.choice(colors),
                "p": rnd.uniform(0, 6.28),
            })

    def draw_victory_screen(self, student_name, quiz_mgr=None):
        self._seed_victory_particles()
        self.gl.clear((14, 17, 28))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (24, 28, 44), (12, 14, 22))

        t = pygame.time.get_ticks() / 1000.0
        for p in self._victory_particles:
            y = (p["y"] + t * p["v"]) % (WINDOW_HEIGHT + 40) - 20
            x = p["x"] + math.sin(t * 1.5 + p["p"]) * 12
            self.gl.draw_circle(x, y, p["s"], (*p["c"][:3], 180))

        pw, ph = 760, 470
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2

        self.gl.draw_panel(px, py, pw, ph, (26, 34, 52, 250), border_color=COLOR_ACCENT, border_width=4, radius=18, shadow_offset=(5, 6))
        self.gl.draw_panel(px + 8, py + 8, pw - 16, ph - 16, (0, 0, 0, 0), border_color=COLOR_ACCENT_DARK, border_width=1, radius=14, shadow=False)

        self.gl.draw_text("CERTIFICADO DE EXCELÊNCIA ACADÊMICA", WINDOW_WIDTH / 2, py + 28, color=COLOR_ACCENT, size=24, bold=True, center_x=True)
        self.gl.draw_text("O DESAFIO ESCOLAR - JORNADA DO CONHECIMENTO", WINDOW_WIDTH / 2, py + 60, color=(180, 210, 245), size=14, bold=True, center_x=True)

        for sx in [-40, 0, 40]:
            self.gl.draw_texture(self.assets.textures["star"], WINDOW_WIDTH / 2 + sx - 12, py + 90, 24, 24)

        self.gl.draw_text("Certificamos que o(a) estudante:", WINDOW_WIDTH / 2, py + 132, color=COLOR_TEXT_MUTED, size=15, center_x=True)
        self.gl.draw_text(f"{student_name}", WINDOW_WIDTH / 2, py + 160, color=COLOR_WHITE, size=30, bold=True, center_x=True)

        msg1 = "Demonstrou grande evolução ao enfrentar desafios e combates de conhecimento,"
        msg2 = "superando dúvidas e avançando em suas matérias com dedicação!"
        self.gl.draw_text(msg1, WINDOW_WIDTH / 2, py + 208, color=(215, 230, 250), size=15, center_x=True)
        self.gl.draw_text(msg2, WINDOW_WIDTH / 2, py + 232, color=(215, 230, 250), size=15, center_x=True)

        # Status das matérias
        y0 = py + 270
        self.gl.draw_text("Progresso por matéria:", px + 60, y0, color=COLOR_ACCENT, size=15, bold=True)
        if quiz_mgr is not None and hasattr(quiz_mgr, "is_subject_completed"):
            for i, (sid, cfg) in enumerate(SUBJECTS.items()):
                done = quiz_mgr.is_subject_completed(sid)
                txt = f"✓ {cfg['name']} - Concluída" if done else f"• {cfg['name']} - Em andamento"
                col = COLOR_SUCCESS if done else (210, 220, 235)
                self.gl.draw_text(txt, px + 80, y0 + 26 + i * 22, color=col, size=14, bold=done)
        else:
            self.gl.draw_text("Matemática concluída! Continue explorando as outras matérias.", px + 80, y0 + 30, color=(210, 220, 235), size=14)

        line_y = py + 388
        self.gl.draw_rect(px + 80, line_y, 220, 1, (100, 120, 150))
        self.gl.draw_rect(px + pw - 300, line_y, 220, 1, (100, 120, 150))
        self.gl.draw_text("Professores das Salas", px + 190, line_y + 8, color=(160, 180, 210), size=12, center_x=True)
        self.gl.draw_text("Equipe Pecê Gamer / FUPAC", px + pw - 190, line_y + 8, color=(160, 180, 210), size=12, center_x=True)

        self.gl.draw_panel(WINDOW_WIDTH / 2 - 170, py + ph - 52, 340, 36, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=2, radius=10, shadow_offset=(2, 3))
        self.gl.draw_text("Pressione [ESPAÇO] para Continuar Explorando", WINDOW_WIDTH / 2, py + ph - 42, color=COLOR_WHITE, size=14, bold=True, center_x=True)



    def draw_game_over_student(self, player_name, score_mgr, leaderboard_entries):
        self.gl.clear((30, 18, 22))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (50, 24, 30), (18, 12, 18))
        self.gl.draw_vignette(80)
        pw, ph = 760, 470
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2
        self.gl.draw_panel(px, py, pw, ph, (40, 28, 36, 248), border_color=COLOR_DANGER, border_width=3, radius=16, shadow_offset=(4,5))
        self.gl.draw_text("FIM DA TENTATIVA - SEM CORAÇÕES", WINDOW_WIDTH/2, py + 28, color=COLOR_DANGER, size=24, bold=True, center_x=True)
        self.gl.draw_text(f"Aluno: {player_name}", WINDOW_WIDTH/2, py + 62, color=COLOR_WHITE, size=18, bold=True, center_x=True)
        hearts = getattr(score_mgr, 'hearts', 0)
        score = getattr(score_mgr, 'score', 0)
        correct = getattr(score_mgr, 'correct', 0)
        wrong = getattr(score_mgr, 'wrong', 0)
        nota = round((correct/(correct+wrong))*10,1) if (correct+wrong)>0 else 0.0
        self.gl.draw_text(f"Pontuação: {score}   |   Acertos: {correct}   |   Erros: {wrong}   |   Nota: {nota}", WINDOW_WIDTH/2, py + 96, color=COLOR_ACCENT, size=16, bold=True, center_x=True)
        self.gl.draw_text("Sua pontuação foi salva na tabela de classificação!", WINDOW_WIDTH/2, py + 124, color=(220,230,245), size=14, center_x=True)

        self.gl.draw_text("Top 5 - Tabela de Pontuação", px + 40, py + 160, color=COLOR_WHITE, size=16, bold=True)
        y = py + 188
        for i, e in enumerate(leaderboard_entries[:5]):
            line = f"{i+1}. {e.get('nome_jogador','-')}  |  {e.get('pontuacao',0)} pts  |  Nota {e.get('nota_final',0)}  |  A:{e.get('acertos',0)} E:{e.get('erros',0)}"
            self.gl.draw_text(line, px + 50, y, color=(230,235,245), size=13)
            y += 24
        if not leaderboard_entries:
            self.gl.draw_text("Nenhum registro ainda.", px + 50, y, color=COLOR_TEXT_MUTED, size=13)

        self.gl.draw_panel(px + 80, py + ph - 90, 270, 40, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=2, radius=10, shadow_offset=(2,3))
        self.gl.draw_text("[N] Próximo Aluno", px + 215, py + ph - 80, color=COLOR_WHITE, size=15, bold=True, center_x=True)
        self.gl.draw_panel(px + 410, py + ph - 90, 270, 40, (60,50,40), border_color=COLOR_ACCENT, border_width=2, radius=10, shadow_offset=(2,3))
        self.gl.draw_text("[T] Ver Tabela Completa", px + 545, py + ph - 80, color=COLOR_WHITE, size=15, bold=True, center_x=True)
        self.gl.draw_text("[ESC] Voltar ao início", WINDOW_WIDTH/2, py + ph - 30, color=COLOR_TEXT_MUTED, size=13, center_x=True)

    def draw_leaderboard_screen(self, entries):
        self.gl.clear((18, 22, 34))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (28, 36, 54), (12, 16, 24))
        self.gl.draw_vignette(70)
        pw, ph = 840, 480
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2
        self.gl.draw_panel(px, py, pw, ph, (24, 30, 46, 248), border_color=COLOR_ACCENT, border_width=3, radius=16, shadow_offset=(4,5))
        self.gl.draw_text("TABELA DE PONTUAÇÃO - RANKING", WINDOW_WIDTH/2, py + 24, color=COLOR_ACCENT, size=26, bold=True, center_x=True)
        self.gl.draw_text("Pos  Nome            Gênero    Pontos  Acertos  Erros  Nota  Data", px + 30, py + 66, color=(180,210,255), size=14, bold=True)
        self.gl.draw_rect(px + 24, py + 86, pw - 48, 2, (70,90,120))
        y = py + 100
        for i, e in enumerate(entries[:10]):
            nome = str(e.get('nome_jogador','-'))[:14]
            gen = str(e.get('genero','-'))[:8]
            pts = e.get('pontuacao',0)
            ac = e.get('acertos',0)
            er = e.get('erros',0)
            nota = e.get('nota_final',0)
            data = str(e.get('data',''))[:10]
            line = f"{i+1:>2}.  {nome:<14} {gen:<8} {pts:>6}   {ac:>6}   {er:>5}  {nota:>4}  {data}"
            col = COLOR_WHITE if i < 3 else (220,225,235)
            self.gl.draw_text(line, px + 30, y, color=col, size=14, bold=(i<3))
            y += 28
        if not entries:
            self.gl.draw_text("Nenhuma pontuação salva ainda.", WINDOW_WIDTH/2, py + 180, color=COLOR_TEXT_MUTED, size=16, center_x=True)
        self.gl.draw_text("[ESC/ENTER] Voltar", WINDOW_WIDTH/2, py + ph - 28, color=COLOR_TEXT_MUTED, size=13, center_x=True)
