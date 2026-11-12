"""
Interface do Modo Competição — 'O Desafio Escolar'.

Telas:
- Menu inicial (Modo Clássico / Modo Competição)
- Cadastro das equipes (nome da Equipe 1 e Equipe 2)
- Quiz da competição (placar, vida, nível, perguntas de 2 alternativas e
  a opção "Responder depois")
- Fim de rodada (resumo do representante + placar)
- Resultado final (equipe vencedora)

Reutiliza o renderer OpenGL e os componentes visuais do jogo original.
"""

import random
import pygame
from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_WHITE, COLOR_TEXT_MUTED,
    COLOR_BG_TOP, COLOR_BG_BOTTOM,
    COMP_MAX_REPS, COMP_MAX_LIVES, COMP_TEAM_COLORS, COMP_TEAM_COLORS_DARK,
)

LETTERS = ["A", "B", "C", "D"]


class CompetitionUI:
    """Telas e entradas do Modo Competição."""

    def __init__(self, gl_renderer, assets, sound_manager):
        self.gl = gl_renderer
        self.assets = assets
        self.sound = sound_manager

        # Menu
        self.menu_selected = 0  # 0 = Clássico, 1 = Competição

        # Cadastro das equipes
        self.setup_team_idx = 0       # 0 = Equipe 1, 1 = Equipe 2
        self.team_name_input = ""
        self.rep_name_input = ""      # nome do representante da rodada
        self.cursor_timer = 0.0

        # Quiz da competição
        self.quiz_buttons = []        # rects das alternativas
        self.defer_button = None
        self.continue_button = None
        self.hovered_option = -1

        # Feedback e overlays
        self.feedback_active = False
        self.feedback_correct = False
        self.feedback_text = ""
        self.level_overlay_active = False
        self.level_overlay_title = ""
        self.level_overlay_msg = ""

        # Partículas da tela de resultado
        self._result_particles = []
        self._result_seeded = False

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _mouse_pos(self, event=None):
        """Posição do mouse em coordenadas lógicas (960x540).

        Em tela cheia a superfície usa a resolução nativa do monitor com
        letterbox; o renderer converte para as coordenadas da interface.
        """
        pos = event.pos if (event is not None and hasattr(event, "pos")) else None
        return self.gl.logical_mouse_pos(pos)

    def _wrap_text(self, text, max_chars):
        words = str(text).split()
        lines = [""]
        for w in words:
            if len(lines[-1]) + len(w) + 1 <= max_chars:
                lines[-1] = (lines[-1] + " " + w).strip()
            else:
                lines.append(w)
        return [l for l in lines if l]

    def _clear_overlays(self):
        self.feedback_active = False
        self.level_overlay_active = False
        self.feedback_text = ""
        self.level_overlay_title = ""
        self.level_overlay_msg = ""

    # ------------------------------------------------------------------
    # Menu inicial
    # ------------------------------------------------------------------
    def handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a,
                             pygame.K_TAB]:
                self.menu_selected = 1 - self.menu_selected
                self.sound.play("blip")
            elif event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d]:
                self.menu_selected = 1 - self.menu_selected
                self.sound.play("blip")
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e]:
                self.sound.play("select")
                return "COMPETITION" if self.menu_selected == 1 else "CLASSIC"
            elif event.key == pygame.K_1:
                self.sound.play("select")
                return "CLASSIC"
            elif event.key == pygame.K_2:
                self.sound.play("select")
                return "COMPETITION"
            elif event.key == pygame.K_ESCAPE:
                return "QUIT"
        elif event.type == pygame.MOUSEMOTION:
            mx, my = self._mouse_pos()
            for i, rect in enumerate(self._menu_rects()):
                if rect.collidepoint(mx, my) and i != self.menu_selected:
                    self.menu_selected = i
                    self.sound.play("blip")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._mouse_pos(event)
            for i, rect in enumerate(self._menu_rects()):
                if rect.collidepoint(mx, my):
                    self.sound.play("select")
                    return "COMPETITION" if i == 1 else "CLASSIC"
        return None

    def _menu_rects(self):
        bw, bh = 480, 76
        bx = (WINDOW_WIDTH - bw) / 2
        return [
            pygame.Rect(bx, 250, bw, bh),
            pygame.Rect(bx, 352, bw, bh),
        ]

    def draw_menu(self, dt):
        self.cursor_timer += dt
        self.gl.clear(COLOR_BG_BOTTOM)
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG_TOP, COLOR_BG_BOTTOM)
        self.gl.draw_vignette(60)

        self.gl.draw_text("O DESAFIO ESCOLAR", WINDOW_WIDTH / 2, 100, color=COLOR_ACCENT, size=42, bold=True, center_x=True)
        self.gl.draw_text("Equipe Pecê Gamer - FUPAC / UNIPAC", WINDOW_WIDTH / 2, 148, color=(180, 210, 245), size=17, center_x=True)

        labels = [
            ("MODO CLÁSSICO", "Explore a escola, converse com os professores e evolua de nível."),
            ("MODO COMPETIÇÃO", "Duas equipes, um representante por vez. Quem avançar mais longe vence!"),
        ]
        rects = self._menu_rects()
        for i, (title, desc) in enumerate(labels):
            rect = rects[i]
            selected = (i == self.menu_selected)
            if selected:
                self.gl.draw_glow_rect(rect.x, rect.y, rect.w, rect.h, (247, 201, 72, 55), layers=3, spread=5)
            bg = COLOR_PRIMARY_DARK if selected else (28, 36, 54)
            border = COLOR_ACCENT if selected else COLOR_PRIMARY
            self.gl.draw_panel(rect.x, rect.y, rect.w, rect.h, bg, border_color=border,
                               border_width=3 if selected else 2, radius=14, shadow_offset=(3, 5))
            self.gl.draw_text(title, rect.centerx, rect.y + 18, color=COLOR_WHITE, size=24, bold=True, center_x=True)
            self.gl.draw_text(desc, rect.centerx, rect.y + 50, color=(170, 200, 235) if selected else COLOR_TEXT_MUTED, size=14, center_x=True)

        self.gl.draw_text("[W/S] ou [Setas] escolher  •  [ENTER] selecionar  •  [1/2] atalho", WINDOW_WIDTH / 2, 468, color=COLOR_TEXT_MUTED, size=14, center_x=True)
        self.gl.draw_text("[F11] alterna tela cheia", WINDOW_WIDTH / 2, 494, color=COLOR_TEXT_MUTED, size=13, center_x=True)

    # ------------------------------------------------------------------
    # Cadastro das equipes
    # ------------------------------------------------------------------
    def handle_setup_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.sound.play("blip")
                return "BACK"
            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                name = self.team_name_input.strip()
                self.sound.play("select")
                if self.setup_team_idx == 0:
                    self.team_name_input = ""
                    self.setup_team_idx = 1
                    return ("TEAM1", name)
                else:
                    return ("TEAM2", name)
            elif event.key == pygame.K_BACKSPACE:
                if self.team_name_input:
                    self.team_name_input = self.team_name_input[:-1]
                    self.sound.play("blip")
            else:
                if len(event.unicode) > 0 and event.unicode.isprintable() and len(self.team_name_input) < 18:
                    self.team_name_input += event.unicode
                    self.sound.play("blip")
        return None

    def draw_setup(self, dt, current_team_idx, first_team_name=""):
        self.cursor_timer += dt
        self.gl.clear(COLOR_BG_BOTTOM)
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG_TOP, COLOR_BG_BOTTOM)
        self.gl.draw_vignette(60)

        pw, ph = 720, 420
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2

        team_color = COMP_TEAM_COLORS[current_team_idx]
        team_color_dark = COMP_TEAM_COLORS_DARK[current_team_idx]

        self.gl.draw_panel(px, py, pw, ph, (26, 32, 48, 245), border_color=team_color, border_width=3, radius=18, shadow_offset=(4, 5))
        self.gl.draw_rounded_rect(px + 40, py - 3, pw - 80, 6, team_color, radius=3)

        self.gl.draw_text("MODO COMPETIÇÃO", WINDOW_WIDTH / 2, py + 40, color=team_color, size=26, bold=True, center_x=True)
        self.gl.draw_text(f"Cadastro das equipes — Equipe {current_team_idx + 1} de 2", WINDOW_WIDTH / 2, py + 78, color=(180, 210, 245), size=17, center_x=True)

        self.gl.draw_text(f"Digite o nome da EQUIPE {current_team_idx + 1}:", WINDOW_WIDTH / 2, py + 128, color=COLOR_WHITE, size=20, bold=True, center_x=True)

        bx, by, bw, bh = px + 110, py + 160, 500, 56
        self.gl.draw_panel(bx, by, bw, bh, (16, 19, 30), border_color=team_color, border_width=2, radius=10, shadow=False)
        show_cursor = (int(self.cursor_timer * 2.5) % 2 == 0)
        cursor_str = "|" if show_cursor else " "
        if self.team_name_input:
            self.gl.draw_text(self.team_name_input + cursor_str, bx + 18, by + 16, color=COLOR_WHITE, size=24, bold=True)
        elif show_cursor:
            placeholder = f"Equipe {current_team_idx + 1}..."
            self.gl.draw_text(placeholder + cursor_str, bx + 18, by + 16, color=(90, 105, 130), size=22)

        self.gl.draw_text("Cada equipe possui 5 representantes (escolhidos presencialmente).", px + pw / 2, py + 252, color=(200, 215, 240), size=15, center_x=True)
        self.gl.draw_text("Cada representante joga com 3 corações; erros drenam a vida da rodada.", px + pw / 2, py + 276, color=(200, 215, 240), size=15, center_x=True)

        if current_team_idx == 1 and first_team_name:
            self.gl.draw_text(f"Equipe 1: {first_team_name}", px + pw / 2, py + 308, color=COMP_TEAM_COLORS[0], size=16, bold=True, center_x=True)

        btn_w, btn_h = 340, 44
        btn_x = (WINDOW_WIDTH - btn_w) / 2
        self.gl.draw_panel(btn_x, py + 330, btn_w, btn_h, team_color_dark, border_color=team_color, border_width=2, radius=10, shadow_offset=(2, 3))
        self.gl.draw_text("[ENTER] Confirmar", WINDOW_WIDTH / 2, py + 340, color=COLOR_WHITE, size=18, bold=True, center_x=True)
        self.gl.draw_text("[ESC] Voltar ao menu", WINDOW_WIDTH / 2, py + ph - 32, color=COLOR_TEXT_MUTED, size=13, center_x=True)

    # ------------------------------------------------------------------
    # HUD de exploração da competição (representante andando pela escola)
    # ------------------------------------------------------------------
    def draw_competition_hud(self, comp, location_name, nearby=None):
        """HUD de exploração sem nada na parte superior (para não cobrir as
        placas com os nomes das salas): nome + vida do representante no canto
        inferior esquerdo, pontuação das equipes no canto inferior direito."""
        # nome + vida do representante, no canto inferior esquerdo
        self._draw_lives_panel(comp, WINDOW_HEIGHT - 78 - 12, show_team=True)

        # pontuação das equipes, no canto inferior direito
        self._draw_score_panel(comp, WINDOW_HEIGHT - 78 - 12)

        # local atual, ao lado do painel de vida
        self.gl.draw_text(f"Local: {location_name}", 278, WINDOW_HEIGHT - 78 - 12 + 14, color=(200, 215, 240), size=13)
        self.gl.draw_text("[ESC] Encerrar  •  [F11] Tela cheia  •  [M] Música", WINDOW_WIDTH / 2, WINDOW_HEIGHT - 20, color=COLOR_TEXT_MUTED, size=12, center_x=True)

        if nearby is not None:
            pulse = 2 if (pygame.time.get_ticks() // 350) % 2 == 0 else 0
            bw, bh = 460 + pulse * 2, 40
            bx = (WINDOW_WIDTH - bw) / 2
            by = WINDOW_HEIGHT - 130
            self.gl.draw_glow_rect(bx, by, bw, bh, (247, 201, 72, 60), layers=3, spread=4)
            self.gl.draw_panel(bx, by, bw, bh, (255, 245, 180, 245), border_color=COLOR_ACCENT_DARK, border_width=2, radius=18, shadow_offset=(2, 4))
            self.gl.draw_text(f"[E / ESPAÇO] {nearby.label}", WINDOW_WIDTH / 2, by + 10, color=(30, 35, 45), size=15, bold=True, center_x=True)

    def _draw_score_panel(self, comp, y):
        """Painel de pontuação das equipes, no canto inferior direito."""
        pw, ph = 250, 78
        px = WINDOW_WIDTH - pw - 14
        self.gl.draw_panel(px, y, pw, ph, (24, 30, 46, 235), border_color=(70, 92, 128), border_width=2, radius=12, shadow_offset=(2, 3))
        self.gl.draw_text("PONTUAÇÃO", px + 12, y + 6, color=COLOR_ACCENT, size=10, bold=True)
        if comp.run is not None:
            level_label = comp.level_label_by_index(comp.team_max_level[comp.run["team"]])
            self.gl.draw_text(f"Nível: {level_label}", px + pw - 90, y + 6, color=COLOR_TEXT_MUTED, size=10, bold=True)

        for i in (0, 1):
            ry = y + 24 + i * 26
            color = COMP_TEAM_COLORS[i]
            active = (comp.turn_team == i and comp.run is not None)
            name = comp.team_names[i]
            if len(name) > 13:
                name = name[:12] + "…"
            self.gl.draw_text(name, px + 12, ry, color=color, size=13, bold=active)
            self.gl.draw_text(f"{comp.team_points[i]} pts", px + pw - 74, ry + 1,
                              color=COLOR_ACCENT if active else COLOR_TEXT_MUTED, size=13, bold=True)

    def _draw_lives_panel(self, comp, y, show_team=False):
        """Painel fixo do canto inferior esquerdo: nome do representante em
        jogo e seus corações, sem interferir nas perguntas e alternativas."""
        hw, hh = 250, 78
        hx = 14
        team = comp.run["team"] if comp.run is not None else comp.turn_team
        team_color = COMP_TEAM_COLORS[team]

        self.gl.draw_panel(hx, y, hw, hh, (24, 30, 46, 235), border_color=(120, 70, 80), border_width=2, radius=12, shadow_offset=(2, 3))

        label = "REPRESENTANTE"
        if show_team:
            label += "  •  " + comp.team_names[team]
        self.gl.draw_text(label, hx + 10, y + 6, color=team_color, size=10, bold=True)

        if comp.run is None:
            self.gl.draw_text("Aguardando rodada...", hx + 10, y + 34, color=COLOR_TEXT_MUTED, size=12)
            return

        name = (comp.run.get("name") or "").strip() or f"Representante {comp.run['rep']}"
        if len(name) > 18:
            name = name[:17] + "…"
        self.gl.draw_text(f"Rep {comp.run['rep']}/{COMP_MAX_REPS}", hx + hw - 82, y + 18, color=(150, 175, 210), size=10, bold=True)
        self.gl.draw_text(name, hx + 10, y + 28, color=(200, 225, 250), size=15, bold=True)

        lives = comp.run["lives"]
        for h in range(COMP_MAX_LIVES):
            heart_color = COLOR_DANGER if h < lives else (70, 78, 92)
            self.gl.draw_text("♥", hx + 12 + h * 26, y + 52, color=heart_color, size=20, bold=True)
        self.gl.draw_text(f"{lives}/{COMP_MAX_LIVES}", hx + hw - 44, y + 56, color=COLOR_WHITE, size=13, bold=True)

    # ------------------------------------------------------------------
    # Nome do representante da rodada
    # ------------------------------------------------------------------
    def handle_rep_name_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                self.sound.play("select")
                return ("CONFIRM", self.rep_name_input.strip())
            elif event.key == pygame.K_ESCAPE:
                self.sound.play("blip")
                return ("CONFIRM", "")   # ESC usa o nome padrão
            elif event.key == pygame.K_BACKSPACE:
                if self.rep_name_input:
                    self.rep_name_input = self.rep_name_input[:-1]
                    self.sound.play("blip")
            else:
                if len(event.unicode) > 0 and event.unicode.isprintable() and len(self.rep_name_input) < 16:
                    self.rep_name_input += event.unicode
                    self.sound.play("blip")
        return None

    def draw_rep_name_screen(self, dt, comp):
        """Tela rápida de cadastro do representante antes da rodada dele."""
        self.cursor_timer += dt
        self.gl.clear(COLOR_BG_BOTTOM)
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG_TOP, COLOR_BG_BOTTOM)
        self.gl.draw_vignette(60)

        team = comp.turn_team
        run = comp.run
        team_color = COMP_TEAM_COLORS[team]
        team_color_dark = COMP_TEAM_COLORS_DARK[team]

        pw, ph = 660, 360
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2

        self.gl.draw_panel(px, py, pw, ph, (26, 32, 48, 245), border_color=team_color, border_width=3, radius=18, shadow_offset=(4, 5))
        self.gl.draw_rounded_rect(px + 40, py - 3, pw - 80, 6, team_color, radius=3)

        self.gl.draw_text(f"RODADA {run['rep']}/{COMP_MAX_REPS}", WINDOW_WIDTH / 2, py + 42, color=team_color, size=26, bold=True, center_x=True)
        self.gl.draw_text(f"Equipe: {comp.team_names[team]}", WINDOW_WIDTH / 2, py + 78, color=(180, 210, 245), size=17, center_x=True)
        self.gl.draw_text("Digite o nome do representante:", WINDOW_WIDTH / 2, py + 122, color=COLOR_WHITE, size=18, bold=True, center_x=True)

        bx, by, bw, bh = px + 90, py + 148, 480, 52
        self.gl.draw_panel(bx, by, bw, bh, (16, 19, 30), border_color=team_color, border_width=2, radius=10, shadow=False)
        show_cursor = (int(self.cursor_timer * 2.5) % 2 == 0)
        cursor_str = "|" if show_cursor else " "
        default_name = f"Representante {run['rep']}"
        if self.rep_name_input:
            self.gl.draw_text(self.rep_name_input + cursor_str, bx + 16, by + 15, color=COLOR_WHITE, size=22, bold=True)
        elif show_cursor:
            self.gl.draw_text(default_name + cursor_str, bx + 16, by + 15, color=(90, 105, 130), size=20)

        self.gl.draw_text("3 corações nesta rodada. Boa sorte!", WINDOW_WIDTH / 2, py + 236, color=(200, 215, 240), size=15, center_x=True)
        self.gl.draw_text("[ENTER] Confirmar  •  [ESC] Usar nome padrão", WINDOW_WIDTH / 2, py + 272, color=COLOR_TEXT_MUTED, size=14, center_x=True)

    # ------------------------------------------------------------------
    # Quiz da competição
    # ------------------------------------------------------------------
    def show_feedback(self, is_correct, explanation):
        self.feedback_active = True
        self.feedback_correct = is_correct
        self.feedback_text = explanation
        self.sound.play("correct" if is_correct else "wrong")

    def show_level_complete(self, comp):
        team_name = comp.team_names[comp.turn_team]
        self.level_overlay_active = True
        self.level_overlay_title = "NÍVEL CONCLUÍDO!"
        self.level_overlay_msg = f"A {team_name} avançou para o nível {comp.current_level_label()}! Dificuldade maior, mais pontos."
        self.sound.play("levelup")

    def handle_quiz_event(self, event, comp):
        # overlays (feedback / nível concluído) capturam as entradas primeiro
        if self.feedback_active or self.level_overlay_active:
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e]:
                self.sound.play("blip")
                if self.level_overlay_active:
                    self.level_overlay_active = False
                    return "CONFIRM"
                self.feedback_active = False
                return "CONFIRM"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.continue_button and self.continue_button.collidepoint(*self._mouse_pos(event)):
                    self.sound.play("blip")
                    if self.level_overlay_active:
                        self.level_overlay_active = False
                    else:
                        self.feedback_active = False
                    return "CONFIRM"
            return None

        if event.type == pygame.KEYDOWN:
            key_map = {
                pygame.K_1: 0, pygame.K_a: 0,
                pygame.K_2: 1, pygame.K_b: 1,
                pygame.K_3: 2, pygame.K_c: 2,
                pygame.K_4: 3, pygame.K_d: 3,
            }
            if event.key in key_map:
                self.sound.play("select")
                return f"ANSWER_{key_map[event.key]}"
            elif event.key == pygame.K_r:
                self.sound.play("blip")
                return "DEFER"
            elif event.key == pygame.K_ESCAPE:
                return "EXIT"

        elif event.type == pygame.MOUSEMOTION:
            mx, my = self._mouse_pos()
            prev = self.hovered_option
            self.hovered_option = -1
            for idx, rect in enumerate(self.quiz_buttons):
                if rect.collidepoint(mx, my):
                    self.hovered_option = idx
                    break
            if self.hovered_option != -1 and self.hovered_option != prev:
                self.sound.play("blip")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._mouse_pos(event)
            for idx, rect in enumerate(self.quiz_buttons):
                if rect.collidepoint(mx, my):
                    self.sound.play("select")
                    return f"ANSWER_{idx}"
            if self.defer_button and self.defer_button.collidepoint(mx, my):
                self.sound.play("blip")
                return "DEFER"
        return None

    def draw_quiz(self, dt, comp):
        self.gl.clear((16, 20, 32))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (30, 40, 64), (14, 18, 30))
        self.gl.draw_vignette(70)

        self._draw_scoreboard(comp)
        self._draw_question_panel(comp)
        self._draw_option_buttons(comp)
        # nome + vida do representante, no canto inferior esquerdo
        self._draw_lives_panel(comp, WINDOW_HEIGHT - 78 - 12)
        # pontuação das equipes, no canto inferior direito
        self._draw_score_panel(comp, WINDOW_HEIGHT - 78 - 12)
        self._draw_footer_hint(comp)

        if self.feedback_active:
            self._draw_feedback_overlay(comp)
        elif self.level_overlay_active:
            self._draw_level_overlay(comp)

    def _draw_scoreboard(self, comp):
        """Placar superior: equipe 1 x equipe 2, com vidas e nível alcançado."""
        pw, ph = WINDOW_WIDTH - 32, 104
        px, py = 16, 12
        self.gl.draw_panel(px, py, pw, ph, (24, 30, 46, 248), border_color=(70, 92, 128), border_width=2, radius=14, shadow_offset=(3, 4))

        block_w = 380
        blocks = [
            (px + 12, 0, comp.team_names[0]),
            (px + pw - block_w - 12, 1, comp.team_names[1]),
        ]
        for bx, team_idx, team_name in blocks:
            color = COMP_TEAM_COLORS[team_idx]
            color_dark = COMP_TEAM_COLORS_DARK[team_idx]
            active = (comp.turn_team == team_idx and comp.run is not None)
            border = color if active else (52, 66, 92)
            self.gl.draw_panel(bx, py + 8, block_w, ph - 16, (26, 34, 50, 245) if active else (22, 28, 42, 245),
                               border_color=border, border_width=3 if active else 1, radius=10, shadow=False)

            self.gl.draw_text(team_name, bx + 14, py + 16, color=color, size=21, bold=True)

            # nível mais longe alcançado pela equipe
            level_label = comp.level_label_by_index(comp.team_max_level[team_idx])
            self.gl.draw_text(f"Nível alcançado: {level_label}", bx + 14, py + 46, color=(170, 200, 240), size=14)

            self.gl.draw_text(f"Pontos: {comp.team_points[team_idx]}", bx + block_w - 130, py + 46, color=COLOR_ACCENT, size=15, bold=True)

            if active:
                # nome e corações do representante em jogo ficam no painel do
                # canto inferior esquerdo (ver _draw_lives_panel)
                self.gl.draw_text("Vez desta equipe!", bx + 14, py + 72, color=color, size=13, bold=True)
            else:
                nxt = comp.reps_used[team_idx] + 1 if comp.reps_used[team_idx] < COMP_MAX_REPS else None
                msg = f"Próximo: Rep {nxt}/{COMP_MAX_REPS}" if nxt else "Todos os reps jogaram"
                self.gl.draw_text(msg, bx + 14, py + 72, color=COLOR_TEXT_MUTED, size=13)

        # "VS" central
        self.gl.draw_text("VS", WINDOW_WIDTH / 2, py + 40, color=COLOR_ACCENT, size=28, bold=True, center_x=True)

    def _draw_question_panel(self, comp):
        q = comp.current_question()
        if q is None:
            return
        qx, qy, qw, qh = 40, 132, WINDOW_WIDTH - 80, 148
        self.gl.draw_panel(qx, qy, qw, qh, (30, 40, 60, 248), border_color=(74, 100, 145), border_width=2, radius=14, shadow_offset=(3, 4))

        # faixa: nível + questão + matéria
        q_total = len(comp.current_questions())
        badge_text = f"Nível {comp.current_level_label()}  •  Questão {comp.run['q_idx'] + 1}/{q_total}  •  {q['subject']}"
        self.gl.draw_panel(qx + 16, qy + 12, 360, 26, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=1, radius=7, shadow=False)
        self.gl.draw_text(badge_text, qx + 24, qy + 17, color=COLOR_WHITE, size=14, bold=True)
        self.gl.draw_text(q["title"], qx + 386, qy + 16, color=COLOR_ACCENT, size=17, bold=True)

        # aviso de pergunta adiada que voltou
        if comp.run["deferred_replay"]:
            self.gl.draw_text("Pergunta adiada - Responda agora!", qx + qw - 260, qy + 18, color=COLOR_DANGER, size=13, bold=True)

        lines = self._wrap_text(q["question"], 62)[:3]
        for i, line in enumerate(lines):
            self.gl.draw_text(line, qx + 20, qy + 52 + i * 28, color=COLOR_WHITE, size=21, bold=True)

        # progresso do nível (5 perguntas)
        bar_x, bar_y, bar_w, bar_h = qx + 20, qy + qh - 22, qw - 40, 10
        self.gl.draw_rounded_rect(bar_x, bar_y, bar_w, bar_h, (45, 58, 82), radius=5)
        prog = max(0.0, min(1.0, comp.run["q_idx"] / q_total))
        if self.feedback_active and self.feedback_correct:
            prog = max(prog, (comp.run["q_idx"] + 1) / q_total)
        self.gl.draw_rounded_rect(bar_x, bar_y, int(bar_w * prog), bar_h, COLOR_SUCCESS, radius=5)

    def _draw_option_buttons(self, comp):
        q = comp.current_question()
        if q is None:
            return
        self.quiz_buttons = []
        card_w, card_h = 430, 64
        xs = [40, WINDOW_WIDTH - 40 - card_w]
        ys = [296, 368]

        for idx, opt_text in enumerate(q["options"]):
            cx = xs[idx % 2]
            cy = ys[idx // 2]
            rect = pygame.Rect(cx, cy, card_w, card_h)
            self.quiz_buttons.append(rect)

            hovered = (self.hovered_option == idx)
            bg = (52, 74, 110) if hovered else (28, 38, 58)
            border = COLOR_ACCENT if hovered else COLOR_PRIMARY
            if hovered:
                self.gl.draw_glow_rect(cx, cy, card_w, card_h, (247, 201, 72, 55), layers=2, spread=4)
            self.gl.draw_panel(cx, cy, card_w, card_h, bg, border_color=border,
                               border_width=3 if hovered else 2, radius=14,
                               shadow_offset=(4, 5) if hovered else (3, 4))

            badge_bg = COLOR_ACCENT if hovered else COLOR_PRIMARY_DARK
            badge_cx, badge_cy = cx + 32, cy + card_h / 2
            self.gl.draw_circle(badge_cx, badge_cy, 20, badge_bg)
            self.gl.draw_circle(badge_cx, badge_cy, 20, border, filled=False, border_width=2)
            self.gl.draw_text(LETTERS[idx], badge_cx, badge_cy - 11, color=(30, 30, 40) if hovered else COLOR_WHITE, size=20, bold=True, center_x=True)
            self.gl.draw_text(opt_text, cx + 62, cy + card_h / 2 - 10, color=COLOR_WHITE, size=17, bold=hovered)

        # botão "Responder depois" (perguntas adiadas que voltaram devem ser respondidas)
        self.defer_button = None
        if not comp.run["deferred_replay"]:
            bw, bh = 300, 40
            bx = (WINDOW_WIDTH - bw) / 2
            by = 444
            self.defer_button = pygame.Rect(bx, by, bw, bh)
            self.gl.draw_panel(bx, by, bw, bh, (38, 46, 66), border_color=COLOR_TEXT_MUTED, border_width=2, radius=10, shadow_offset=(2, 3))
            self.gl.draw_text("Responder depois  [R]", WINDOW_WIDTH / 2, by + 9, color=(225, 232, 245), size=16, bold=True, center_x=True)

    def _draw_footer_hint(self, comp):
        hints = "[1-4] / [A-D] ou clique  •  [R] Adiar  •  [ESC] Explorar"
        self.gl.draw_text(hints, 280, WINDOW_HEIGHT - 14, color=COLOR_TEXT_MUTED, size=12)

    def _draw_feedback_overlay(self, comp):
        fb_w, fb_h = 800, 208
        fb_x = (WINDOW_WIDTH - fb_w) / 2
        fb_y = 288
        if self.feedback_correct:
            bg = (20, 55, 35, 250)
            border = COLOR_SUCCESS
            title = "RESPOSTA CORRETA!"
            title_col = COLOR_SUCCESS
            pts = comp.current_points_value()
            sub = f"A Equipe marcou +{pts} pontos!"
        else:
            bg = (55, 25, 25, 250)
            border = COLOR_DANGER
            if comp.run["lives"] <= 0:
                title = "SEM CORAÇÕES!"
                sub = "A rodada deste representante chegou ao fim."
            else:
                title = "RESPOSTA ERRADA!"
                sub = f"Perdeu 1 coração ({comp.run['lives']} restante(s))."
            title_col = (255, 160, 150)

        self.gl.draw_panel(fb_x, fb_y, fb_w, fb_h, bg, border_color=border, border_width=3, radius=16, shadow_offset=(4, 5))
        self.gl.draw_text(title, WINDOW_WIDTH / 2, fb_y + 18, color=title_col, size=26, bold=True, center_x=True)
        self.gl.draw_text(sub, WINDOW_WIDTH / 2, fb_y + 52, color=(220, 232, 245), size=15, center_x=True)

        self.gl.draw_text("Explicação:", fb_x + 28, fb_y + 84, color=COLOR_ACCENT, size=16, bold=True)
        for i, line in enumerate(self._wrap_text(self.feedback_text, 92)[:2]):
            self.gl.draw_text(line, fb_x + 28, fb_y + 108 + i * 24, color=COLOR_WHITE, size=16)

        btn_w, btn_h = 380, 40
        btn_x = (WINDOW_WIDTH - btn_w) / 2
        btn_y = fb_y + fb_h - 52
        self.continue_button = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.gl.draw_panel(btn_x, btn_y, btn_w, btn_h, (30, 40, 60), border_color=border, border_width=1, radius=8, shadow=False)
        self.gl.draw_text("[ENTER] Continuar", WINDOW_WIDTH / 2, btn_y + 10, color=COLOR_WHITE, size=16, bold=True, center_x=True)

    def _draw_level_overlay(self, comp):
        ov_w, ov_h = 780, 190
        ov_x = (WINDOW_WIDTH - ov_w) / 2
        ov_y = 296
        self.gl.draw_panel(ov_x, ov_y, ov_w, ov_h, (24, 48, 38, 250), border_color=COLOR_SUCCESS, border_width=3, radius=16, shadow_offset=(4, 5))
        self.gl.draw_text(self.level_overlay_title, WINDOW_WIDTH / 2, ov_y + 26, color=COLOR_SUCCESS, size=28, bold=True, center_x=True)
        for i, line in enumerate(self._wrap_text(self.level_overlay_msg, 70)[:2]):
            self.gl.draw_text(line, WINDOW_WIDTH / 2, ov_y + 68 + i * 26, color=(215, 235, 220), size=18, center_x=True)

        btn_w, btn_h = 380, 40
        btn_x = (WINDOW_WIDTH - btn_w) / 2
        btn_y = ov_y + ov_h - 56
        self.continue_button = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.gl.draw_panel(btn_x, btn_y, btn_w, btn_h, (30, 40, 60), border_color=COLOR_SUCCESS, border_width=1, radius=8, shadow=False)
        self.gl.draw_text("[ENTER] Ir para o próximo nível", WINDOW_WIDTH / 2, btn_y + 10, color=COLOR_WHITE, size=16, bold=True, center_x=True)

    # ------------------------------------------------------------------
    # Fim de rodada
    # ------------------------------------------------------------------
    def handle_turn_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e]:
                self.sound.play("select")
                return "NEXT"
            elif event.key == pygame.K_ESCAPE:
                self.sound.play("blip")
                return "END_COMPETITION"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._mouse_pos(event)
            if self.continue_button and self.continue_button.collidepoint(mx, my):
                self.sound.play("select")
                return "NEXT"
        return None

    def draw_turn_end(self, dt, comp):
        self.gl.clear((14, 17, 28))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (24, 28, 44), (12, 14, 22))
        self.gl.draw_vignette(70)

        run = comp.last_run
        if run is None:
            return
        team = run.get("team", 0)

        pw, ph = 900, 500
        px = (WINDOW_WIDTH - pw) / 2
        py = 20
        team_color = COMP_TEAM_COLORS[team]

        won = (run["finished"] == "vitoria")
        border = COLOR_ACCENT if won else COLOR_DANGER
        self.gl.draw_panel(px, py, pw, ph, (26, 32, 48, 250), border_color=border, border_width=3, radius=18, shadow_offset=(4, 5))
        self.gl.draw_rounded_rect(px + 40, py - 3, pw - 80, 6, team_color, radius=3)

        if won:
            self.gl.draw_text("TODOS OS NÍVEIS CONCLUÍDOS!", WINDOW_WIDTH / 2, py + 24, color=COLOR_ACCENT, size=24, bold=True, center_x=True)
            for sx in [-60, 0, 60]:
                self.gl.draw_texture(self.assets.textures["star"], WINDOW_WIDTH / 2 + sx - 12, py + 44, 24, 24)
        else:
            self.gl.draw_text("SEM CORAÇÕES - FIM DA RODADA", WINDOW_WIDTH / 2, py + 24, color=COLOR_DANGER, size=24, bold=True, center_x=True)

        rep_line = f"Representante {run['rep']}/{COMP_MAX_REPS} da {comp.team_names[team]}"
        if run.get("name"):
            rep_line += f"  -  \"{run['name']}\""
        self.gl.draw_text(rep_line, WINDOW_WIDTH / 2, py + 82, color=team_color, size=17, bold=True, center_x=True)
        self.gl.draw_text(f"Pontos da rodada: {run['points']}   •   Acertos: {run['correct']}   •   Erros: {run['wrong']}",
                          WINDOW_WIDTH / 2, py + 106, color=(220, 232, 245), size=15, center_x=True)

        # placar atual (compacto, lado a lado)
        leader = comp.winner()
        col_w, col_h = 400, 66
        for i in (0, 1):
            cx = px + 30 if i == 0 else px + pw - 30 - col_w
            cy = py + 128
            color = COMP_TEAM_COLORS[i]
            is_leader = (leader == i)
            self.gl.draw_panel(cx, cy, col_w, col_h, (28, 36, 54, 245), border_color=COLOR_ACCENT if is_leader else color,
                               border_width=3 if is_leader else 2, radius=10, shadow_offset=(2, 3))
            self.gl.draw_text(comp.team_names[i], cx + 14, cy + 10, color=color, size=16, bold=True)
            level_label = comp.level_label_by_index(comp.team_max_level[i])
            self.gl.draw_text(f"Nível: {level_label}", cx + 14, cy + 38, color=COLOR_WHITE, size=14)
            self.gl.draw_text(f"{comp.team_points[i]} pts", cx + col_w - 100, cy + 24, color=COLOR_ACCENT, size=18, bold=True, center_x=True)
            if is_leader:
                self.gl.draw_text("LÍDER", cx + col_w - 100, cy + 46, color=COLOR_ACCENT, size=11, bold=True, center_x=True)

        # tabela de andamento: todas as rodadas disputadas até aqui
        self.gl.draw_text("ANDAMENTO DA COMPETIÇÃO - RODADAS DISPUTADAS", px + 30, py + 212, color=COLOR_ACCENT, size=15, bold=True)
        col_x = {
            "equipe": px + 30,
            "rep": px + 240,
            "nome": px + 300,
            "nivel": px + 470,
            "pts": px + 580,
            "status": px + 660,
        }
        self.gl.draw_text("Equipe", col_x["equipe"], py + 238, color=(180, 210, 255), size=13, bold=True)
        self.gl.draw_text("Rep", col_x["rep"], py + 238, color=(180, 210, 255), size=13, bold=True)
        self.gl.draw_text("Nome", col_x["nome"], py + 238, color=(180, 210, 255), size=13, bold=True)
        self.gl.draw_text("Nível", col_x["nivel"], py + 238, color=(180, 210, 255), size=13, bold=True)
        self.gl.draw_text("Pts", col_x["pts"], py + 238, color=(180, 210, 255), size=13, bold=True)
        self.gl.draw_text("Resultado", col_x["status"], py + 238, color=(180, 210, 255), size=13, bold=True)
        self.gl.draw_rect(px + 24, py + 258, pw - 48, 2, (70, 90, 120))

        max_rows = 7
        recent = comp.history[-max_rows:]
        row_y = py + 268
        for entry in recent:
            e_color = COMP_TEAM_COLORS[entry["team"]]
            name = entry.get("name") or f"Rep {entry['rep']}"
            self.gl.draw_text(comp.team_names[entry["team"]][:14], col_x["equipe"], row_y, color=e_color, size=13, bold=True)
            self.gl.draw_text(f"{entry['rep']}/{COMP_MAX_REPS}", col_x["rep"], row_y, color=COLOR_WHITE, size=13)
            self.gl.draw_text(str(name)[:16], col_x["nome"], row_y, color=COLOR_WHITE, size=13)
            self.gl.draw_text(entry["level_label"], col_x["nivel"], row_y, color=COLOR_WHITE, size=13)
            self.gl.draw_text(str(entry["points"]), col_x["pts"], row_y, color=COLOR_ACCENT, size=13, bold=True)
            status_txt = "Vitória" if entry["finished"] == "vitoria" else "Derrota"
            status_col = COLOR_SUCCESS if entry["finished"] == "vitoria" else COLOR_DANGER
            self.gl.draw_text(status_txt, col_x["status"], row_y, color=status_col, size=13, bold=True)
            row_y += 20
        if not recent:
            self.gl.draw_text("Nenhuma rodada disputada ainda.", px + 30, row_y, color=COLOR_TEXT_MUTED, size=13)

        # próxima rodada
        nxt = comp.next_up()
        if nxt:
            nxt_color = COMP_TEAM_COLORS[nxt["team"]]
            self.gl.draw_text("Próximo a jogar:", WINDOW_WIDTH / 2, py + 418, color=COLOR_TEXT_MUTED, size=13, center_x=True)
            self.gl.draw_text(f"Representante {nxt['rep']}/{COMP_MAX_REPS} da {nxt['team_name']}", WINDOW_WIDTH / 2, py + 438, color=nxt_color, size=19, bold=True, center_x=True)
        else:
            self.gl.draw_text("Todos os representantes jogaram!", WINDOW_WIDTH / 2, py + 424, color=COLOR_ACCENT, size=18, bold=True, center_x=True)

        btn_w, btn_h = 380, 40
        btn_x = (WINDOW_WIDTH - btn_w) / 2
        btn_y = py + ph - 52
        self.continue_button = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.gl.draw_panel(btn_x, btn_y, btn_w, btn_h, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=2, radius=10, shadow_offset=(2, 3))
        label = "[ENTER] Continuar" if nxt else "[ENTER] Ver resultado final"
        self.gl.draw_text(label, WINDOW_WIDTH / 2, btn_y + 10, color=COLOR_WHITE, size=16, bold=True, center_x=True)
        self.gl.draw_text("[ESC] Encerrar competição e ver o placar final", WINDOW_WIDTH / 2, py + ph - 10, color=COLOR_TEXT_MUTED, size=12, center_x=True)

    # ------------------------------------------------------------------
    # Resultado final
    # ------------------------------------------------------------------
    def handle_result_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
            self.sound.play("blip")
            return "MENU"
        return None

    def _seed_result_particles(self):
        if self._result_seeded:
            return
        self._result_seeded = True
        rnd = random.Random(7)
        colors = [COLOR_ACCENT, (120, 220, 255), (140, 255, 180), (255, 160, 200), COLOR_WHITE]
        for _ in range(40):
            self._result_particles.append({
                "x": rnd.uniform(0, WINDOW_WIDTH),
                "y": rnd.uniform(-80, WINDOW_HEIGHT),
                "s": rnd.uniform(2, 5),
                "v": rnd.uniform(18, 55),
                "c": rnd.choice(colors),
                "p": rnd.uniform(0, 6.28),
            })

    def _top_students(self, comp, n=2):
        """Os alunos (representantes) com mais acertos no evento.

        Ordena o histórico de rodadas por acertos e, em caso de empate,
        por pontos; retorna os n primeiros.
        """
        ranked = sorted(
            comp.history,
            key=lambda e: (e["correct"], e["points"]),
            reverse=True,
        )
        return ranked[:n]

    def _draw_top_students(self, comp, px, py, pw, ph):
        """Painel de destaques da tela de resultado: os 2 alunos que mais
        acertaram durante toda a competição."""
        self.gl.draw_text("DESTAQUES - ALUNOS QUE MAIS ACERTARAM", px + 40, py + 268, color=COLOR_ACCENT, size=14, bold=True)

        card_w, card_h = 386, 72
        cy = py + 288
        top = self._top_students(comp, 2)
        for idx, entry in enumerate(top):
            cx = px + 40 + idx * (card_w + 8)
            e_color = COMP_TEAM_COLORS[entry["team"]]
            name = entry.get("name") or f"Representante {entry['rep']}"
            if len(name) > 18:
                name = name[:17] + "…"

            medal = COLOR_ACCENT if idx == 0 else (170, 180, 195)
            self.gl.draw_panel(cx, cy, card_w, card_h, (24, 32, 48, 245), border_color=e_color,
                               border_width=3 if idx == 0 else 2, radius=12, shadow_offset=(2, 3))
            self.gl.draw_text(f"{idx + 1}º LUGAR", cx + 12, cy + 6, color=medal, size=11, bold=True)
            self.gl.draw_text(name, cx + 12, cy + 22, color=e_color, size=17, bold=True)
            self.gl.draw_text(f"{comp.team_names[entry['team']]}  •  Rep {entry['rep']}/{COMP_MAX_REPS}",
                              cx + 12, cy + 46, color=(200, 215, 240), size=12)
            self.gl.draw_text(f"{entry['correct']} acertos", cx + card_w - 118, cy + 22,
                              color=COLOR_ACCENT if idx == 0 else COLOR_WHITE, size=18, bold=True)
            self.gl.draw_texture(self.assets.textures["star"], cx + card_w - 30, cy + 8, 18, 18)

        if not top:
            self.gl.draw_text("Nenhuma rodada disputada na competição.", px + 40, cy + 20, color=COLOR_TEXT_MUTED, size=13)

    def draw_result(self, dt, comp):
        self._seed_result_particles()
        self.gl.clear((14, 17, 28))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (24, 28, 44), (12, 14, 22))

        t = pygame.time.get_ticks() / 1000.0
        for p in self._result_particles:
            y = (p["y"] + t * p["v"]) % (WINDOW_HEIGHT + 40) - 20
            x = p["x"] + (12 if p["p"] > 3.14 else -12) * abs(((t * 1.5 + p["p"]) % 6.28) - 3.14) / 3.14
            self.gl.draw_circle(x, y, p["s"], (*p["c"][:3], 180))

        pw, ph = 860, 460
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2

        winner = comp.winner()
        border = COMP_TEAM_COLORS[winner] if winner is not None else COLOR_ACCENT
        self.gl.draw_panel(px, py, pw, ph, (26, 34, 52, 250), border_color=border, border_width=4, radius=18, shadow_offset=(5, 6))

        self.gl.draw_text("COMPETIÇÃO ENCERRADA", WINDOW_WIDTH / 2, py + 30, color=(180, 210, 245), size=18, bold=True, center_x=True)

        if winner is not None:
            self.gl.draw_text("EQUIPE VENCEDORA!", WINDOW_WIDTH / 2, py + 68, color=COLOR_ACCENT, size=26, bold=True, center_x=True)
            self.gl.draw_text(comp.team_names[winner], WINDOW_WIDTH / 2, py + 106, color=COMP_TEAM_COLORS[winner], size=38, bold=True, center_x=True)
            for sx in [-50, 50]:
                self.gl.draw_texture(self.assets.textures["star"], WINDOW_WIDTH / 2 + sx - 12, py + 88, 24, 24)
        else:
            self.gl.draw_text("EMPATE ENTRE AS EQUIPES!", WINDOW_WIDTH / 2, py + 68, color=COLOR_ACCENT, size=26, bold=True, center_x=True)
            self.gl.draw_text("As duas equipes conquistaram o mesmo resultado.", WINDOW_WIDTH / 2, py + 106, color=COLOR_WHITE, size=20, center_x=True)

        # tabela comparativa
        self.gl.draw_text("Nível alcançado", px + 300, py + 156, color=COLOR_WHITE, size=15, bold=True)
        self.gl.draw_text("Pontos", px + 500, py + 156, color=COLOR_WHITE, size=15, bold=True)
        self.gl.draw_text("Acertos", px + 600, py + 156, color=COLOR_WHITE, size=15, bold=True)
        self.gl.draw_text("Erros", px + 700, py + 156, color=COLOR_WHITE, size=15, bold=True)
        self.gl.draw_rect(px + 40, py + 178, pw - 80, 2, (70, 90, 120))

        for i in (0, 1):
            y = py + 196 + i * 44
            color = COMP_TEAM_COLORS[i]
            self.gl.draw_text(f"{i + 1}.", px + 40, y, color=COLOR_TEXT_MUTED, size=18)
            self.gl.draw_text(comp.team_names[i], px + 64, y, color=color, size=18, bold=(winner == i))
            self.gl.draw_text(comp.level_label_by_index(comp.team_max_level[i]), px + 300, y, color=COLOR_WHITE, size=18)
            self.gl.draw_text(str(comp.team_points[i]), px + 500, y, color=COLOR_ACCENT, size=18, bold=True)
            self.gl.draw_text(str(comp.team_correct[i]), px + 600, y, color=COLOR_WHITE, size=18)
            self.gl.draw_text(str(comp.team_wrong[i]), px + 700, y, color=COLOR_WHITE, size=18)

        msg_y = py + ph - 92
        # destaque: os 2 alunos (representantes) que mais acertaram no evento
        self._draw_top_students(comp, px, py, pw, ph)

        self.gl.draw_text("Vence quem avança mais longe pelos níveis; a pontuação desempata.",
                          WINDOW_WIDTH / 2, msg_y, color=COLOR_TEXT_MUTED, size=14, center_x=True)

        btn_w, btn_h = 360, 44
        btn_x = (WINDOW_WIDTH - btn_w) / 2
        btn_y = py + ph - 62
        self.gl.draw_panel(btn_x, btn_y, btn_w, btn_h, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=2, radius=10, shadow_offset=(2, 3))
        self.gl.draw_text("[ENTER / ESC] Voltar ao Menu", WINDOW_WIDTH / 2, btn_y + 12, color=COLOR_WHITE, size=18, bold=True, center_x=True)
