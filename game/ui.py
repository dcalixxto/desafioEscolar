"""
Módulo de Interface do Usuário (UI) para 'O Desafio Escolar'.
Renderiza menus, caixas de diálogo, telas de quiz e tela de vitória via PyOpenGL.
"""

import pygame
from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_WHITE, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_BG_TOP, COLOR_BG_BOTTOM,
    DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL, DIFFICULTY_LABELS
)

class UIManager:
    def __init__(self, gl_renderer, assets, sound_manager):
        self.gl = gl_renderer
        self.assets = assets
        self.sound = sound_manager

        # Estado da tela de Nome
        self.player_name_input = ""
        self.cursor_timer = 0.0

        # Estado do Diálogo
        self.dialog_active = False
        self.dialog_title = ""
        self.dialog_lines = []
        self.dialog_options = [] # Lista de tuplas (texto, callback)
        self.dialog_selected_opt = 0
        self.dialog_is_notice = False

        # Estado do Quiz
        self.quiz_buttons = [] # Lista de rects para mouse hover/click
        self.hovered_option = -1
        self.feedback_active = False
        self.feedback_correct = False
        self.feedback_text = ""

    # =========================================================================
    # 1. TELA DE CRIAÇÃO / NOME DO ESTUDANTE
    # =========================================================================
    def handle_name_input_event(self, event):
        """Gerencia digitação do nome do jogador."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                name = self.player_name_input.strip()
                if not name:
                    name = "Estudante"
                self.sound.play("blip")
                return name
            elif event.key == pygame.K_BACKSPACE:
                if len(self.player_name_input) > 0:
                    self.player_name_input = self.player_name_input[:-1]
                    self.sound.play("blip")
            else:
                # Permite letras, números e espaços até 16 caracteres
                if len(self.player_name_input) < 16 and (event.unicode.isalnum() or event.unicode in " _-"):
                    self.player_name_input += event.unicode
                    self.sound.play("blip")
        return None

    def draw_name_input_screen(self, dt):
        """Renderiza a tela inicial de boas-vindas e inserção do nome."""
        self.cursor_timer += dt

        # Fundo com degradê suave
        self.gl.clear(COLOR_BG_BOTTOM)
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG_TOP, COLOR_BG_BOTTOM)

        # Painel central principal
        pw, ph = 640, 380
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2

        self.gl.draw_panel(px, py, pw, ph, (26, 32, 48, 245), border_color=(70, 96, 138), border_width=3, radius=18)
        self.gl.draw_panel(px + 5, py + 5, pw - 10, ph - 10, (0, 0, 0, 0), border_color=(48, 68, 100), border_width=1, radius=14, shadow=False)

        # Faixa dourada decorativa no topo do painel
        self.gl.draw_rounded_rect(px + 40, py - 3, pw - 80, 6, COLOR_ACCENT, radius=3)

        # Cabeçalho da Faculdade e Matéria
        self.gl.draw_text("FUPAC / UNIPAC - FUNDAÇÃO PRESIDENTE ANTÔNIO CARLOS", WINDOW_WIDTH / 2, py + 22, color=(160, 185, 220), size=14, center_x=True)
        self.gl.draw_text("Ciência da Computação | Programação Para Jogos", WINDOW_WIDTH / 2, py + 40, color=(120, 145, 180), size=12, center_x=True)

        # Título do Jogo
        self.gl.draw_text("O DESAFIO ESCOLAR", WINDOW_WIDTH / 2, py + 72, color=COLOR_ACCENT, size=32, bold=True, center_x=True)
        self.gl.draw_text("Equipe Pecê Gamer", WINDOW_WIDTH / 2, py + 108, color=(180, 200, 225), size=14, center_x=True)

        # Linha divisória
        self.gl.draw_rect(px + 40, py + 130, pw - 80, 2, (50, 70, 100, 160))

        # Instrução
        self.gl.draw_text("Boas-vindas à escola!", WINDOW_WIDTH / 2, py + 150, color=COLOR_WHITE, size=20, bold=True, center_x=True)
        self.gl.draw_text("Digite seu nome de estudante para iniciar sua jornada acadêmica:", WINDOW_WIDTH / 2, py + 180, color=COLOR_TEXT_MUTED, size=15, center_x=True)

        # Campo de Texto para o Nome
        bx, by, bw, bh = px + 120, py + 215, 400, 48
        self.gl.draw_panel(bx, by, bw, bh, (16, 19, 30), border_color=COLOR_PRIMARY, border_width=2, radius=10, shadow=False)

        # Texto digitado + Cursor piscante
        display_text = self.player_name_input
        show_cursor = (int(self.cursor_timer * 2.5) % 2 == 0)
        cursor_str = "|" if show_cursor else " "

        if not display_text and not show_cursor:
            self.gl.draw_text("Ex: Lucas, Daniel, Matheus...", bx + 16, by + 14, color=(90, 105, 130), size=18)
        else:
            self.gl.draw_text(display_text + cursor_str, bx + 16, by + 14, color=COLOR_WHITE, size=20, bold=True)

        # Dica de tecla Enter
        self.gl.draw_panel(px + 170, py + 295, 300, 36, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=1, radius=8, shadow_offset=(2, 3))
        self.gl.draw_text("Pressione [ENTER] para Jogar", WINDOW_WIDTH / 2, py + 304, color=COLOR_WHITE, size=15, bold=True, center_x=True)

        # Rodapé com créditos
        self.gl.draw_text("Autores: Angelo, Daniel, Hamilton, João Alberto, Lucas E., Lucas N., Matheus | Prof. Rodrigo Fernandes", WINDOW_WIDTH / 2, WINDOW_HEIGHT - 24, color=(100, 115, 140), size=12, center_x=True)

    # =========================================================================
    # 2. HUD DE EXPLORAÇÃO
    # =========================================================================
    def draw_exploration_hud(self, player_name, location_name, quiz_mgr, interactable):
        """Renderiza crachá do aluno, status das salas e indicador de interação."""
        # 1. Crachá do Estudante (Canto Superior Esquerdo)
        self.gl.draw_panel(16, 16, 260, 52, (20, 26, 40, 235), border_color=(64, 86, 118), border_width=2, radius=14, shadow_offset=(3, 4))
        # Avatar circular com iniciais
        self.gl.draw_circle(42, 42, 19, (36, 48, 70))
        self.gl.draw_circle(42, 42, 19, COLOR_PRIMARY, filled=False, border_width=2)
        self.gl.draw_text(player_name[:1].upper() if player_name else "A", 42, 32, color=COLOR_ACCENT, size=20, bold=True, center_x=True)
        # Nome e Sala atual
        self.gl.draw_text(f"Estudante: {player_name}", 70, 22, color=COLOR_WHITE, size=15, bold=True)
        self.gl.draw_text(f"Local: {location_name}", 70, 42, color=(150, 200, 255), size=13)

        # 2. Status de Desafio em Matemática (Canto Superior Direito)
        self.gl.draw_panel(WINDOW_WIDTH - 280, 16, 264, 52, (20, 26, 40, 235), border_color=(64, 86, 118), border_width=2, radius=14, shadow_offset=(3, 4))
        self.gl.draw_text("Matemática:", WINDOW_WIDTH - 270, 22, color=COLOR_ACCENT, size=14, bold=True)

        # Indicadores dos 3 níveis: Fácil, Médio, Difícil
        diffs = [
            (DIFF_FACIL, "Fácil", 0),
            (DIFF_MEDIO, "Médio", 56),
            (DIFF_DIFICIL, "Difícil", 116)
        ]
        base_x = WINDOW_WIDTH - 180
        for d_key, label, offset_x in diffs:
            completed = quiz_mgr.completed_levels.get(d_key, False)
            unlocked = quiz_mgr.unlocked_levels.get(d_key, False)

            icon_key = "star" if completed else ("lock_open" if unlocked else "lock_closed")
            color_text = COLOR_SUCCESS if completed else (COLOR_WHITE if unlocked else COLOR_TEXT_MUTED)

            self.gl.draw_texture(self.assets.textures[icon_key], base_x + offset_x, 20, 18, 18)
            self.gl.draw_text(label, base_x + offset_x + 9, 41, color=color_text, size=11, bold=True, center_x=True)

        # 3. Balão flutuante de interação no rodapé/centro
        if interactable is not None:
            bw, bh = 340, 36
            bx = (WINDOW_WIDTH - bw) / 2
            by = WINDOW_HEIGHT - 60
            self.gl.draw_panel(bx, by, bw, bh, (255, 245, 180, 245), border_color=COLOR_ACCENT_DARK, border_width=2, radius=18, shadow_offset=(2, 4))
            self.gl.draw_text(f"[E ou ESPAÇO] {interactable.label}", WINDOW_WIDTH / 2, by + 8, color=(30, 35, 45), size=15, bold=True, center_x=True)

    # =========================================================================
    # 3. SISTEMA DE DIÁLOGO E AVISOS
    # =========================================================================
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

        # Painel inferior de diálogo estilo RPG
        pw = 740
        ph = 160 if not self.dialog_options else 200
        px = (WINDOW_WIDTH - pw) / 2
        py = WINDOW_HEIGHT - ph - 24

        self.gl.draw_panel(px, py, pw, ph, (20, 26, 42, 248), border_color=COLOR_PRIMARY, border_width=3, radius=16, shadow_offset=(4, 5))
        self.gl.draw_panel(px + 5, py + 5, pw - 10, ph - 10, (0, 0, 0, 0), border_color=(62, 92, 140), border_width=1, radius=12, shadow=False)

        # Título / Nome do Interlocutor
        self.gl.draw_panel(px + 20, py - 14, 240, 28, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=1, radius=8, shadow_offset=(2, 3))
        self.gl.draw_text(self.dialog_title, px + 30, py - 8, color=COLOR_WHITE, size=14, bold=True)

        # Linhas de Texto do Diálogo
        for i, line in enumerate(self.dialog_lines):
            self.gl.draw_text(line, px + 30, py + 26 + i * 22, color=COLOR_TEXT, size=15)

        # Opções de Resposta
        if self.dialog_options:
            start_y = py + 34 + len(self.dialog_lines) * 22
            for idx, (opt_text, _) in enumerate(self.dialog_options):
                is_selected = (idx == self.dialog_selected_opt)
                opt_color = COLOR_ACCENT if is_selected else COLOR_WHITE
                prefix = "> " if is_selected else "  "

                # Destaque de linha selecionada
                if is_selected:
                    self.gl.draw_panel(px + 26, start_y + idx * 26 - 2, pw - 52, 24, (45, 65, 100, 210), border_color=COLOR_ACCENT, border_width=1, radius=6, shadow=False)

                self.gl.draw_text(prefix + opt_text, px + 30, start_y + idx * 26 + 1, color=opt_color, size=14, bold=is_selected)
        elif self.dialog_is_notice:
            # Instrução de fechar
            self.gl.draw_text("[Pressione E ou ESPAÇO para fechar]", px + pw - 250, py + ph - 26, color=COLOR_ACCENT, size=13)

    # =========================================================================
    # 4. SISTEMA DE QUIZ PROGRESSIVO
    # =========================================================================
    def start_quiz_feedback(self, is_correct, explanation):
        self.feedback_active = True
        self.feedback_correct = is_correct
        self.feedback_text = explanation
        if is_correct:
            self.sound.play("correct")
        else:
            self.sound.play("wrong")

    def handle_quiz_event(self, event, quiz_mgr):
        """Gerencia seleção de alternativas por teclado ou mouse."""
        if self.feedback_active:
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e]:
                self.feedback_active = False
                if self.feedback_correct:
                    # Acertou: avança
                    finished_level = quiz_mgr.advance_question()
                    if finished_level:
                        self.sound.play("fanfare")
                        if quiz_mgr.is_game_completed():
                            return "VICTORY"
                        return "LEVEL_COMPLETE"
                else:
                    # Errou: "estudar mais um pouco" e tentar de novo
                    quiz_mgr.retry_question()
                return "REFRESH"
            return None

        # Teclado para opções 1, 2, 3, 4 ou A, B, C, D
        if event.type == pygame.KEYDOWN:
            key_map = {
                pygame.K_1: 0, pygame.K_a: 0,
                pygame.K_2: 1, pygame.K_b: 1,
                pygame.K_3: 2, pygame.K_c: 2,
                pygame.K_4: 3, pygame.K_d: 3
            }
            if event.key in key_map:
                opt_idx = key_map[event.key]
                return f"ANSWER_{opt_idx}"
            elif event.key == pygame.K_ESCAPE:
                return "EXIT_QUIZ"

        # Clique do Mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            # Checa clique nas abas de dificuldade
            for rect, d_key in getattr(self, "diff_buttons", []):
                if rect.collidepoint(mx, my) and quiz_mgr.unlocked_levels.get(d_key, False):
                    self.sound.play("blip")
                    return f"SWITCH_DIFF_{d_key}"

            # Checa clique nas alternativas
            for idx, rect in enumerate(self.quiz_buttons):
                if rect.collidepoint(mx, my):
                    return f"ANSWER_{idx}"

        # Movimento do Mouse (Hover)
        if event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            self.hovered_option = -1
            for idx, rect in enumerate(self.quiz_buttons):
                if rect.collidepoint(mx, my):
                    self.hovered_option = idx
                    break

        return None

    def draw_quiz(self, quiz_mgr, student_name):
        """Renderiza a interface do quiz de matemática."""
        self.gl.clear((16, 20, 32))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (26, 33, 50), (16, 20, 32))

        # Painel Superior: Seletor e Status das Dificuldades
        self.gl.draw_panel(20, 16, WINDOW_WIDTH - 40, 56, (28, 36, 54), border_color=(64, 86, 122), border_width=2, radius=14, shadow_offset=(3, 4))
        self.gl.draw_text("SALA DE MATEMÁTICA - AVALIAÇÃO PROGRESSIVA", 40, 26, color=COLOR_WHITE, size=18, bold=True)
        self.gl.draw_text(f"Estudante: {student_name}", 40, 48, color=(160, 200, 255), size=13)

        # Botões das 3 Dificuldades
        self.diff_buttons = []
        diff_info = [
            (DIFF_FACIL, "1. Fácil", 480),
            (DIFF_MEDIO, "2. Médio", 630),
            (DIFF_DIFICIL, "3. Difícil", 780)
        ]
        for d_key, label, bx in diff_info:
            is_cur = (quiz_mgr.current_difficulty == d_key)
            unlocked = quiz_mgr.unlocked_levels.get(d_key, False)
            completed = quiz_mgr.completed_levels.get(d_key, False)

            bg_col = COLOR_PRIMARY_DARK if is_cur else ((35, 48, 70) if unlocked else (25, 30, 42))
            border_col = COLOR_ACCENT if is_cur else (COLOR_PRIMARY if unlocked else (50, 60, 75))

            btn_rect = pygame.Rect(bx, 24, 130, 40)
            self.diff_buttons.append((btn_rect, d_key))

            self.gl.draw_panel(bx, 24, 130, 40, bg_col, border_color=border_col, border_width=2 if is_cur else 1, radius=10, shadow_offset=(2, 3))

            icon = "star" if completed else ("lock_open" if unlocked else "lock_closed")
            self.gl.draw_texture(self.assets.textures[icon], bx + 8, 32, 22, 22)
            self.gl.draw_text(label, bx + 36, 35, color=COLOR_WHITE if unlocked else COLOR_TEXT_MUTED, size=14, bold=is_cur)

        # Questão Atual
        q = quiz_mgr.get_current_question()
        if not q:
            return

        # Caixa Central da Pergunta
        qw, qh = WINDOW_WIDTH - 80, 120
        qx, qy = 40, 92
        self.gl.draw_panel(qx, qy, qw, qh, (30, 40, 60), border_color=(74, 100, 145), border_width=2, radius=14, shadow_offset=(3, 4))

        # Título da Questão e Progresso
        total_q = quiz_mgr.total_questions_in_level()
        cur_q = quiz_mgr.current_question_idx + 1
        diff_label = DIFFICULTY_LABELS.get(quiz_mgr.current_difficulty, "")

        self.gl.draw_panel(qx + 16, qy + 12, 160, 24, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=1, radius=7, shadow=False)
        self.gl.draw_text(f"Nível {diff_label} • Questão {cur_q}/{total_q}", qx + 24, qy + 16, color=COLOR_WHITE, size=13, bold=True)
        self.gl.draw_text(q["title"], qx + 190, qy + 16, color=COLOR_ACCENT, size=14, bold=True)

        # Pontos de progresso das questões do nível
        dot_r = 5
        dot_gap = 16
        dots_start_x = qx + qw - 20 - (total_q - 1) * dot_gap
        for i in range(total_q):
            dcx = dots_start_x + i * dot_gap
            dcy = qy + 22
            if i < cur_q - 1:
                self.gl.draw_circle(dcx, dcy, dot_r, COLOR_SUCCESS)
            elif i == cur_q - 1:
                self.gl.draw_circle(dcx, dcy, dot_r + 1, COLOR_ACCENT)
            else:
                self.gl.draw_circle(dcx, dcy, dot_r, (70, 80, 100))

        # Enunciado da questão (suporta quebra em 2 linhas se longo)
        words = q["question"].split()
        line1, line2 = "", ""
        for w in words:
            if len(line1) + len(w) + 1 < 75:
                line1 += (" " if line1 else "") + w
            else:
                line2 += (" " if line2 else "") + w

        self.gl.draw_text(line1, qx + 20, qy + 50, color=COLOR_WHITE, size=16, bold=True)
        if line2:
            self.gl.draw_text(line2, qx + 20, qy + 76, color=COLOR_WHITE, size=16, bold=True)

        # Alternativas de Múltipla Escolha (2 colunas x 2 linhas)
        self.quiz_buttons.clear()
        letters = ["A", "B", "C", "D"]
        card_w = (WINDOW_WIDTH - 110) // 2
        card_h = 58
        base_opt_y = 230

        for idx, opt_text in enumerate(q["options"]):
            col = idx % 2
            row = idx // 2
            cx = 40 + col * (card_w + 30)
            cy = base_opt_y + row * (card_h + 16)

            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            self.quiz_buttons.append(card_rect)

            is_hovered = (self.hovered_option == idx)
            bg_c = (44, 63, 94) if is_hovered else (28, 38, 58)
            border_c = COLOR_ACCENT if is_hovered else COLOR_PRIMARY

            self.gl.draw_panel(cx, cy, card_w, card_h, bg_c, border_color=border_c, border_width=2 if is_hovered else 1,
                                radius=12, shadow_offset=(3, 4) if is_hovered else (2, 3))

            # Letra da alternativa (A, B, C, D)
            badge_bg = COLOR_ACCENT if is_hovered else COLOR_PRIMARY_DARK
            self.gl.draw_circle(cx + 29, cy + 29, 17, badge_bg)
            self.gl.draw_circle(cx + 29, cy + 29, 17, border_c, filled=False, border_width=1)
            self.gl.draw_text(letters[idx], cx + 29, cy + 19, color=COLOR_WHITE if not is_hovered else (30, 30, 40), size=18, bold=True, center_x=True)

            # Texto da alternativa
            self.gl.draw_text(opt_text, cx + 58, cy + 19, color=COLOR_WHITE, size=16, bold=is_hovered)

        # Dica de navegação
        self.gl.draw_text("Clique na resposta ou use as teclas [1, 2, 3, 4] / [A, B, C, D] | [ESC] Sair", WINDOW_WIDTH / 2, WINDOW_HEIGHT - 22, color=COLOR_TEXT_MUTED, size=13, center_x=True)

        # Painel de Feedback (Acerto ou Erro Pedagógico)
        if self.feedback_active:
            fb_w, fb_h = 680, 160
            fb_x = (WINDOW_WIDTH - fb_w) / 2
            fb_y = 360

            if self.feedback_correct:
                bg_col = (20, 55, 35, 250)
                bdr_col = COLOR_SUCCESS
                title_txt = "PARABÉNS! RESPOSTA CORRETA!"
                title_col = COLOR_SUCCESS
                action_txt = "Pressione [ENTER] para Continuar"
            else:
                bg_col = (55, 25, 25, 250)
                bdr_col = COLOR_DANGER
                title_txt = "OPS! QUE TAL ESTUDAR MAIS UM POUCO?"
                title_col = (255, 140, 130)
                action_txt = "Pressione [ENTER] para Tentar Novamente"

            self.gl.draw_panel(fb_x, fb_y, fb_w, fb_h, bg_col, border_color=bdr_col, border_width=3, radius=16, shadow_offset=(4, 5))
            self.gl.draw_text(title_txt, WINDOW_WIDTH / 2, fb_y + 16, color=title_col, size=18, bold=True, center_x=True)

            # Explicação pedagógica
            self.gl.draw_text("Explicação:", fb_x + 24, fb_y + 48, color=COLOR_ACCENT, size=14, bold=True)
            self.gl.draw_text(self.feedback_text, fb_x + 24, fb_y + 72, color=COLOR_WHITE, size=14)

            # Botão de Ação
            self.gl.draw_panel(WINDOW_WIDTH / 2 - 160, fb_y + 112, 320, 32, (30, 40, 60), border_color=bdr_col, border_width=1, radius=8, shadow=False)
            self.gl.draw_text(action_txt, WINDOW_WIDTH / 2, fb_y + 119, color=COLOR_WHITE, size=14, bold=True, center_x=True)

    # =========================================================================
    # 5. TELA DE VITÓRIA FINAL
    # =========================================================================
    def draw_victory_screen(self, student_name):
        """Renderiza o certificado de superação acadêmica ao vencer o nível Difícil."""
        self.gl.clear((14, 17, 28))
        self.gl.draw_vertical_gradient(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, (24, 28, 44), (12, 14, 22))

        pw, ph = 720, 450
        px = (WINDOW_WIDTH - pw) / 2
        py = (WINDOW_HEIGHT - ph) / 2

        # Moldura dourada com certificado
        self.gl.draw_panel(px, py, pw, ph, (26, 34, 52, 250), border_color=COLOR_ACCENT, border_width=4, radius=18, shadow_offset=(5, 6))
        self.gl.draw_panel(px + 8, py + 8, pw - 16, ph - 16, (0, 0, 0, 0), border_color=COLOR_ACCENT_DARK, border_width=1, radius=14, shadow=False)

        # Título
        self.gl.draw_text("CERTIFICADO DE EXCELÊNCIA ACADÊMICA", WINDOW_WIDTH / 2, py + 30, color=COLOR_ACCENT, size=24, bold=True, center_x=True)
        self.gl.draw_text("O DESAFIO ESCOLAR - DISCIPLINA DE MATEMÁTICA", WINDOW_WIDTH / 2, py + 62, color=(180, 210, 245), size=14, bold=True, center_x=True)

        # 3 Estrelas douradas
        for i, sx in enumerate([-40, 0, 40]):
            self.gl.draw_texture(self.assets.textures["star"], WINDOW_WIDTH / 2 + sx - 12, py + 92, 24, 24)

        # Certificação
        self.gl.draw_text("Certificamos que o(a) estudante:", WINDOW_WIDTH / 2, py + 135, color=COLOR_TEXT_MUTED, size=15, center_x=True)
        self.gl.draw_text(f"{student_name}", WINDOW_WIDTH / 2, py + 165, color=COLOR_WHITE, size=30, bold=True, center_x=True)

        msg1 = "Concluiu com êxito todas as baterias de exercícios: FÁCIL, MÉDIO e DIFÍCIL,"
        msg2 = "provando dedicação, raciocínio lógico e superação contínua do conhecimento!"
        self.gl.draw_text(msg1, WINDOW_WIDTH / 2, py + 215, color=(215, 230, 250), size=15, center_x=True)
        self.gl.draw_text(msg2, WINDOW_WIDTH / 2, py + 240, color=(215, 230, 250), size=15, center_x=True)

        # Mensagem sobre as outras salas
        msg_rooms = "As demais salas temáticas (História, Geografia e Biologia) serão inauguradas em breve!"
        self.gl.draw_text(msg_rooms, WINDOW_WIDTH / 2, py + 285, color=COLOR_ACCENT, size=14, bold=True, center_x=True)

        # Assinaturas
        line_y = py + 345
        self.gl.draw_rect(px + 80, line_y, 220, 1, (100, 120, 150))
        self.gl.draw_rect(px + pw - 300, line_y, 220, 1, (100, 120, 150))
        self.gl.draw_text("Prof. Roberto (Matemática)", px + 190, line_y + 8, color=(160, 180, 210), size=12, center_x=True)
        self.gl.draw_text("Equipe Pecê Gamer / FUPAC", px + pw - 190, line_y + 8, color=(160, 180, 210), size=12, center_x=True)

        # Botão para voltar ao jogo
        self.gl.draw_panel(WINDOW_WIDTH / 2 - 160, py + ph - 55, 320, 36, COLOR_PRIMARY_DARK, border_color=COLOR_PRIMARY, border_width=2, radius=10, shadow_offset=(2, 3))
        self.gl.draw_text("Pressione [ESPAÇO] para Continuar Explorando", WINDOW_WIDTH / 2, py + ph - 45, color=COLOR_WHITE, size=14, bold=True, center_x=True)
