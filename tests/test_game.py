"""
Script de Teste Automatizado e Validação do Jogo 'O Desafio Escolar'.
Simula a jornada completa do jogador sem requerer entrada manual.
"""

import os
import sys
import tempfile
import pygame

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    STATE_NAME_INPUT, STATE_EXPLORE, STATE_DIALOG, STATE_QUIZ, STATE_VICTORY,
    DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL, DIFF_DESAFIO
)
from game.gl_renderer import GLRenderer
from game.display import create_display
from game.audio import sound_manager
from game.assets import AssetManager
from game.entities import Player
from game.world import SchoolWorld, ZONE_HALLWAY, ZONE_CLASSROOM
from game.quiz_data import QuizManager, QUIZ_QUESTIONS, ALL_QUESTIONS
from game.ui import UIManager
from game.competition import CompetitionManager
from game.ui_competition import CompetitionUI
from game.competition_data import COMPETITION_QUESTIONS, questions_per_level
from game.config import COMP_MAX_REPS, SUBJECT_MATH, SUBJECT_BIOLOGY, SUBJECT_HISTORY, TITLE
from game.leaderboard import Leaderboard
from game.scoring import ScoreManager


def play_competition_run(comp, always_correct):
    """Simula uma rodada completa de um representante.

    Repete o ciclo resposta -> feedback -> confirmacao ate o fim da rodada
    (derrota por falta de coracoes ou vitoria ao concluir todos os niveis).
    """
    for _ in range(100):
        q = comp.current_question()
        if q is None:
            break
        chosen = q["correct_index"] if always_correct else 1 - q["correct_index"]
        is_correct, _ = comp.answer(chosen)
        assert is_correct == always_correct, "Resposta simulada deve conferir com o gabarito!"
        if comp.confirm_after_feedback() == "TURN_END":
            break
    comp.end_turn()


def run_competition_tests(gl, comp_ui):
    """Testes do Modo Competição (lógica de jogo e telas)."""
    print("\n--- Testando o Modo Competição ---")

    # 1. Formato do evento: cada matéria tem 5 perguntas de 4 alternativas por nível
    subjects_count = questions_per_level()
    assert subjects_count == 4, f"Devem existir 4 matérias com banco completo (tem {subjects_count})!"
    for subject, levels in COMPETITION_QUESTIONS.items():
        for diff, questions in levels.items():
            assert len(questions) == 5, f"'{subject}/{diff}' deve ter exatamente 5 perguntas!"
            for q in questions:
                assert len(q["options"]) == 4, f"'{q['title']}' deve ter 4 alternativas!"
    print("[OK] Banco de questões da competição: 4 matérias x 4 níveis x 5 perguntas x 4 alternativas.")

    comp = CompetitionManager()
    comp.setup_teams("Time Azul", "Time Vermelho")
    assert comp.teams_configured(), "Equipes deveriam estar cadastradas!"
    print(f"[OK] Equipes cadastradas: {comp.team_names[0]} x {comp.team_names[1]}")

    # 2. Primeira rodada: representante 1 da Equipe 1 com 3 corações
    comp.start_turn()
    assert comp.run["rep"] == 1 and comp.turn_team == 0, "Primeira rodada deve ser do representante 1 da Equipe 1!"
    assert comp.run["lives"] == 3, "Representante deve começar com 3 corações!"
    assert comp.current_level_label() == "Fácil", "Competição deve começar no nível Fácil!"
    print("[OK] Rodada inicial: Representante 1 da Equipe 1, nível Fácil, 3 corações.")

    # 2b. Cada professor pergunta apenas o tema pelo qual é responsável
    comp.set_subject(SUBJECT_BIOLOGY)
    assert comp.current_subject_name() == "Biologia", "Matéria ativa deveria ser Biologia!"
    q = comp.current_question()
    assert q["subject"] == "Biologia", "Professor de Biologia deve perguntar apenas Biologia!"
    for level_questions in COMPETITION_QUESTIONS[SUBJECT_BIOLOGY].values():
        for item in level_questions:
            assert item["subject"] == "Biologia", "Banco de Biologia contém pergunta de outra matéria!"
    # voltando ao professor de Matemática, as perguntas voltam a ser de matemática
    comp.set_subject(SUBJECT_MATH)
    assert comp.current_question()["subject"] == "Matemática", "Professor de Matemática deve perguntar Matemática!"
    print("[OK] Tema por professor: rodada de Biologia só traz Biologia; Matemática só traz Matemática.")

    # 3. Acerta as 5 perguntas do Fácil e só então avança para o Médio
    for i in range(5):
        comp.answer(comp.current_question()["correct_index"])
        event = comp.confirm_after_feedback()
        if i < 4:
            assert event == "QUESTION", f"Após a {i + 1}ª pergunta deve vir a próxima (não o nível completo)!"
        else:
            assert event == "LEVEL_COMPLETE", "Ao concluir a 5ª pergunta do Fácil o nível deve ser concluído!"
    assert comp.current_level_label() == "Médio", "Após concluir o Fácil (5 perguntas) deve avançar ao Médio!"
    assert comp.run["points"] == 50, "5 acertos no Fácil (10 pts) devem somar 50!"
    print("[OK] Progressão de nível: Fácil concluído com 5 acertos -> Médio desbloqueado na competição.")

    # 4. "Responder depois": adia a 2ª pergunta; ela só volta ao fim do nível
    comp.answer(comp.current_question()["correct_index"])   # acerta 1ª do Médio
    event = comp.confirm_after_feedback()
    assert event == "QUESTION"
    assert comp.defer_question(), "Deveria ser possível adiar a 2ª pergunta do nível!"
    # no jogo, adiar exibe a próxima pergunta sem precisar confirmar feedback
    assert comp.run["q_idx"] == 2, "Após adiar a 2ª, deve vir a 3ª pergunta!"
    # responde as 3 perguntas restantes (3ª, 4ª e 5ª)
    for i in range(3):
        comp.answer(comp.current_question()["correct_index"])
        event = comp.confirm_after_feedback()
        assert event == "QUESTION", f"Pergunta {i + 3} do Médio deveria ser seguida pela próxima!"
    # esgotadas as perguntas normais, a pergunta adiada já voltou
    assert comp.run["deferred_replay"], "Pergunta adiada deve voltar ao fim do nível!"
    assert comp.run["q_idx"] == 1, "A pergunta que voltou deve ser a 2ª (adiada)!"
    assert not comp.defer_question(), "Pergunta adiada que voltou não pode ser adiada de novo!"
    comp.answer(comp.current_question()["correct_index"])
    event = comp.confirm_after_feedback()
    assert event == "LEVEL_COMPLETE", "Nível Médio deve concluir após responder a pergunta adiada!"
    assert comp.run["points"] == 125, "Rodada deve somar 50 (Fácil) + 75 (Médio, 5 acertos de 15)!"
    print("[OK] 'Responder depois': pergunta adiada voltou ao fim do nível e o nível foi concluído.")

    # 5. Errar permite responder NOVAMENTE a mesma pergunta (a dica ajuda)
    q0 = comp.current_question()
    idx0 = comp.run["q_idx"]
    is_correct, help_text = comp.answer(1 - q0["correct_index"])
    assert not is_correct, "Resposta propositalmente errada!"
    assert help_text != q0["explanation"], "Ao errar deve receber a DICA, não a explicação com a resposta!"
    event = comp.confirm_after_feedback()
    assert event == "QUESTION_RETRY", "Após errar, deve poder responder a mesma pergunta de novo!"
    assert comp.run["q_idx"] == idx0, "A pergunta deve continuar a mesma após o erro!"
    assert comp.run["lives"] == 2, "O erro custa 1 coração!"
    # acerta na 2ª tentativa: avança normalmente e pontua
    is_correct, _ = comp.answer(q0["correct_index"])
    assert is_correct, "Acerto na 2ª tentativa!"
    event = comp.confirm_after_feedback()
    assert event == "QUESTION" and comp.run["q_idx"] == idx0 + 1, "Após acertar na 2ª tentativa, avança para a próxima pergunta!"
    assert comp.run["points"] == 145, "Rodada deve somar 125 + 20 do acerto no Difícil!"
    print("[OK] Tentativa com dica: errar mantém a MESMA pergunta; acertar depois avança e pontua.")

    # 6. Derrota: os 2 erros restantes drenam os corações e encerram a rodada
    comp.answer(1 - comp.current_question()["correct_index"])
    comp.confirm_after_feedback()
    assert comp.run["lives"] == 1, "Próximo erro deve deixar 1 coração!"
    comp.answer(1 - comp.current_question()["correct_index"])
    event = comp.confirm_after_feedback()
    assert comp.run["lives"] == 0, "Último erro deve zerar os corações!"
    assert event == "TURN_END" and comp.run["finished"] == "derrota", "Sem corações a rodada deve terminar em derrota!"
    comp.end_turn()
    assert comp.team_points[0] == 145, "Pontos das rodadas devem ser acumulados na equipe (50+75+20 da progressão)!"
    assert comp.turn_team == 1, "Após a derrota da Equipe 1, a vez é da Equipe 2!"
    assert comp.next_up()["rep"] == 1, "Equipe 2 deve começar com o representante 1!"
    assert len(comp.history) == 1, "A rodada disputada deve estar registrada na tabela de andamento!"
    entry = comp.history[0]
    assert entry["team"] == 0 and entry["rep"] == 1 and entry["points"] == 145, "Registro da tabela deve guardar equipe, representante e pontos!"
    assert entry["finished"] == "derrota", "Registro da tabela deve guardar o resultado da rodada!"
    print("[OK] Sistema de vida: erros drenam os corações e, sem corações, a vez passa para a Equipe 2.")
    print("[OK] Tabela de andamento: a rodada concluída foi registrada com equipe, rep, pontos e resultado.")

    # 6. Competição completa: revezamento até os 5 representantes de cada equipe
    # (a 1ª rodada da Equipe 1 já foi disputada no teste de derrota acima)
    turn_number = 1
    while not comp.competition_over() and turn_number < 100:
        comp.start_turn()
        always_correct = (turn_number % 2 == 0)   # alterna rodadas perfeitas/imperfeitas
        play_competition_run(comp, always_correct)
        turn_number += 1
    assert turn_number == 2 * COMP_MAX_REPS, f"Devem ser 10 rodadas no total (foram {turn_number})!"
    winner = comp.winner()
    assert winner in (0, 1), "Deve haver uma equipe vencedora (ou None em empate exato)!"
    print(f"[OK] Competição completa: {turn_number} rodadas disputadas. Placar final: "
          f"{comp.team_names[0]} {comp.team_points[0]} pts x {comp.team_names[1]} {comp.team_points[1]} pts.")

    # 6b. Destaques do resultado: os 2 alunos que mais acertaram
    top2 = comp_ui._top_students(comp, 2)
    assert len(top2) == 2, "Devem existir 2 alunos em destaque (os que mais acertaram)!"
    assert top2[0]["correct"] >= top2[1]["correct"], "O ranking de destaques deve ordenar pelos acertos!"
    assert top2[0]["correct"] > 0, "O aluno em 1º lugar deve ter acertos registrados!"
    print("[OK] Destaques do resultado: os 2 alunos com mais acertos foram identificados "
          f"({top2[0]['correct']} e {top2[1]['correct']} acertos).")

    # 7. Renderização das telas da competição
    comp_view = CompetitionManager()
    comp_view.setup_teams("Time Azul", "Time Vermelho")
    comp_view.start_turn()
    gl.clear()
    comp_ui.draw_menu(0.016)
    pygame.display.flip()
    gl.clear()
    comp_ui.draw_setup(0.016, 0)
    pygame.display.flip()
    print("[OK] Menu inicial e tela de cadastro das equipes renderizados.")

    gl.clear()
    comp_ui.draw_quiz(0.016, comp_view)
    pygame.display.flip()
    print("[OK] Tela de quiz da competição (placar, vida, nível e alternativas) renderizada.")

    gl.clear()
    comp_ui.draw_competition_hud(comp_view, "Corredor Principal", None)
    pygame.display.flip()
    print("[OK] HUD de exploração da competição renderizado.")

    gl.clear()
    comp_ui.draw_rep_name_screen(0.016, comp_view)
    pygame.display.flip()
    print("[OK] Tela de nome do representante renderizada.")

    comp_view.answer(0)
    comp_view.confirm_after_feedback()
    comp_view.end_turn()
    gl.clear()
    comp_ui.draw_turn_end(0.016, comp_view)
    pygame.display.flip()
    print("[OK] Tela de fim de rodada com placar renderizada.")

    gl.clear()
    comp_ui.draw_result(0.016, comp_view)
    pygame.display.flip()
    print("[OK] Tela de resultado final renderizada.")


def run_ranking_tests(gl, ui, comp_ui):
    """Ranking geral do menu: soma por participante sem contar a mesma partida duas vezes."""
    print("\n--- Testando o Ranking Geral ---")
    tmp_dir = tempfile.mkdtemp()
    lb = Leaderboard(os.path.join(tmp_dir, "ranking.json"))

    # partida clássica com dois registros acumulados (vitória e depois sem corações)
    score = ScoreManager()
    score.add_correct(10)
    lb.add_entry(score.snapshot("Ana", "Matemática"))
    score.add_correct(20)
    score.add_wrong()
    lb.add_entry(score.snapshot("Ana", "História"))
    # segunda partida da mesma pessoa (nome digitado com outra caixa)
    score.reset()
    score.add_correct(15)
    lb.add_entry(score.snapshot("ana ", "Geografia"))
    # registros antigos, sem "sessao": dois acumulados de uma partida + outra pessoa
    lb.add_entry({"nome_jogador": "Bia", "pontuacao": 40, "acertos": 4, "erros": 0, "data": "2026-11-25T10:00:00"})
    lb.add_entry({"nome_jogador": "Bia", "pontuacao": 55, "acertos": 5, "erros": 1, "data": "2026-11-25T10:05:00"})
    # rodada da competição
    lb.add_entry({"nome_jogador": "Ana", "modo": "competicao", "pontuacao": 100, "acertos": 7,
                  "erros": 3, "data": "2026-11-25T11:00:00", "sessao": "competicao-1"})

    totals = {p["nome"].casefold().strip(): p for p in lb.totals()}
    ana, bia = totals["ana"], totals["bia"]
    assert ana["pontuacao"] == 30 + 15 + 100, f"Ana deveria somar 145 pontos, somou {ana['pontuacao']}!"
    assert ana["partidas"] == 3 and ana["modos"] == "Clássico e Competição"
    assert bia["pontuacao"] == 55 and bia["partidas"] == 1, "Registros antigos acumulados contaram em dobro!"
    assert lb.totals()[0]["pontuacao"] == 145, "Ranking deveria estar ordenado pela pontuação total!"
    assert all(e.get("modo") != "competicao" for e in lb.top(10)), \
        "O ranking de sessões (por nota) não deveria listar rodadas da competição!"
    print("[OK] Ranking geral: pontuação total por participante, sem contar a mesma partida duas vezes.")

    # menu com 3 opções: Clássico, Competição e Ranking
    key = lambda k: pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="")
    assert comp_ui.handle_menu_event(key(pygame.K_3)) == "RANKING", "Atalho [3] deveria abrir o ranking!"
    comp_ui.menu_selected = 0
    comp_ui.handle_menu_event(key(pygame.K_UP))
    assert comp_ui.menu_selected == 2, "Seta para cima na 1ª opção deveria ir para a última!"
    gl.clear()
    comp_ui.draw_menu(0.016)
    pygame.display.flip()
    print("[OK] Menu inicial com a opção Ranking Geral.")

    # botão "Jogar" da tela de nome é clicável (além do ENTER)
    ui.player_name_input = "Carla"
    # janela 960x540: posição física = lógica
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=ui._play_button_rect().center)
    assert ui.handle_name_input_event(click) == ("Carla", ui.selected_gender), \
        "Clicar no botão Jogar deveria confirmar o nome!"
    ui.player_name_input = ""
    print("[OK] Botão 'Jogar' da tela de nome aceita clique do mouse.")

    # tela do ranking com mais participantes que as linhas visíveis + rolagem
    players = [{"nome": f"Aluno {i}", "pontuacao": 300 - i, "partidas": 1, "acertos": 10,
                "erros": 1, "modos": "Clássico", "data": ""} for i in range(25)]
    ui.ranking_offset = 0
    ui.handle_ranking_event(key(pygame.K_PAGEDOWN), len(players))
    ui.handle_ranking_event(key(pygame.K_PAGEDOWN), len(players))
    assert ui.ranking_offset == 15, "A rolagem deveria parar na última página!"
    assert ui.handle_ranking_event(key(pygame.K_ESCAPE), len(players)) == "BACK"
    gl.clear()
    ui.draw_ranking_screen(players)
    pygame.display.flip()
    gl.clear()
    ui.draw_ranking_screen([])
    pygame.display.flip()
    print("[OK] Tela do Ranking Geral renderizada (com rolagem e vazia).")


def run_main_flow_tests():
    """Joga o Modo Clássico pelo main.py real, enviando teclas como o jogador:
    em todas as matérias e níveis, erra uma vez e acerta cada pergunta até
    concluir o nível. Pega erros que só aparecem no fluxo do main.py (ex.:
    o crash ao concluir o último nível de História)."""
    print("\n--- Testando o fluxo real do Modo Clássico (main.py) ---")
    import main as game_main

    game = game_main.DesafioEscolarGame()
    game.leaderboard = Leaderboard(os.path.join(tempfile.mkdtemp(), "ranking.json"))

    def press(k):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0))
        game.handle_events()
        game.update(1 / 60)
        game.render(1 / 60)

    answer_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
    for subject, levels in ALL_QUESTIONS.items():
        game.quiz = QuizManager(subject)
        for level, questions in levels.items():
            game.score.reset()   # corações cheios a cada nível
            game.last_dialog_subject = subject
            game.quiz.unlocked_levels[level] = True
            game.quiz.start_level(level)
            game.ui.feedback_active = False
            game.state = STATE_QUIZ
            for i, q in enumerate(questions):
                if i == 0:   # um erro por nível: dica + nova tentativa
                    press(answer_keys[(q["correct_index"] + 1) % 4])
                    press(pygame.K_RETURN)
                press(answer_keys[q["correct_index"]])
                press(pygame.K_RETURN)
            assert game.quiz.completed_levels[level], f"{subject}/{level} deveria estar concluído!"
            assert game.state in (STATE_DIALOG, STATE_VICTORY), \
                f"{subject}/{level}: fim do nível deveria abrir diálogo ou vitória, ficou em {game.state}"
    print("[OK] 4 matérias x 4 níveis jogados pelo main.py: erro, dica, acertos e fim de nível sem crash.")


def run_automated_test():
    print("=== INICIANDO TESTE DO JOGO 'O DESAFIO ESCOLAR' ===")
    
    # Inicializa Pygame e OpenGL
    pygame.init()
    pygame.display.set_caption("Teste Automatizado - O Desafio Escolar")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    
    gl = GLRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)
    assets = AssetManager(gl)
    world = SchoolWorld()
    player = Player(736, 200, name="Daniel")
    quiz = QuizManager()
    ui = UIManager(gl, assets, sound_manager)

    print("[OK] Engine OpenGL, Assets e Mundo inicializados com sucesso!")

    # 1. Teste de Renderização dos Estados
    gl.clear()
    ui.draw_name_input_screen(0.016)
    pygame.display.flip()
    print("[OK] Tela de Entrada de Nome renderizada.")

    gl.clear()
    gl.apply_camera()
    world.draw_background(gl, assets)
    player.draw(gl, assets)
    gl.reset_camera()
    ui.draw_exploration_hud(player.name, "Corredor Principal", quiz, None)
    pygame.display.flip()
    print("[OK] Corredor Principal e HUD renderizados.")

    # 2. Teste de Transição para Sala de Matemática
    world.set_zone(ZONE_CLASSROOM, player)
    assert world.current_zone == ZONE_CLASSROOM, "Falha ao entrar na sala de aula!"
    assert player.x == SchoolWorld.CLASS_DOOR_X and player.y == 440, \
        "Posição inicial do jogador na sala inválida!"
    assert not world.check_collision(player.hitbox), \
        "O jogador nasceu dentro de um objeto sólido na sala de aula!"
    print(f"[OK] Entrou na Sala de Matemática! Posição do jogador: ({player.x}, {player.y})")

    # Renderiza sala de aula com professor
    gl.clear()
    gl.apply_camera()
    world.draw_background(gl, assets)
    world.teacher.draw(gl, assets)
    player.draw(gl, assets)
    gl.reset_camera()
    ui.draw_exploration_hud(player.name, "Sala de Matemática", quiz, None)
    pygame.display.flip()
    print("[OK] Interior da Sala de Matemática e Professor Roberto renderizados.")

    # 3. Teste de Colisão
    # Testa colisão com a parede norte
    wall_rect = pygame.Rect(100, 10, 20, 20)
    assert world.check_collision(wall_rect) == True, "Colisão com parede norte deveria ser detectada!"
    # Testa espaço livre no corredor entre carteiras
    free_rect = pygame.Rect(100, 300, 20, 20)
    assert world.check_collision(free_rect) == False, "Espaço livre não deveria acusar colisão!"
    print("[OK] Sistema de detecção de colisões funcionando perfeitamente.")

    # 4. Teste de Quiz e Progressão
    print("\n--- Testando Progressão do Quiz (Fácil -> Médio -> Difícil) ---")
    assert quiz.unlocked_levels[DIFF_FACIL] == True, "Fácil deve começar desbloqueado!"
    assert quiz.unlocked_levels[DIFF_MEDIO] == False, "Médio deve começar bloqueado!"
    assert quiz.unlocked_levels[DIFF_DIFICIL] == False, "Difícil deve começar bloqueado!"
    print("[OK] Bloqueios iniciais verificados (Fácil desbloqueado, Médio e Difícil bloqueados).")

    # Inicia nível Fácil
    quiz.start_level(DIFF_FACIL)
    
    # Responde questões do nível Fácil
    while quiz.in_quiz:
        q = quiz.get_current_question()
        correct_idx = q["correct_index"]
        is_correct, exp = quiz.answer_question(correct_idx)
        assert is_correct == True
        print(f"  [Acerto Fácil] Q{quiz.current_question_idx + 1}: {q['title']}")
        quiz.advance_question()

    assert quiz.completed_levels[DIFF_FACIL] == True, "Nível Fácil deveria estar concluído!"
    assert quiz.unlocked_levels[DIFF_MEDIO] == True, "Nível Médio deveria ter sido desbloqueado!"
    print("[OK] Nível Fácil concluído! Nível Médio desbloqueado com sucesso! 🔓")

    # Inicia nível Médio
    quiz.start_level(DIFF_MEDIO)
    # Testa erro proposital na primeira questão
    q = quiz.get_current_question()
    wrong_idx = (q["correct_index"] + 1) % 4
    is_correct, exp = quiz.answer_question(wrong_idx)
    assert is_correct == False, "Resposta propositalmente incorreta não detectada!"
    print(f"  [Teste de Erro Amigável Médio] Respondeu incorretamente. Mensagem pedagógica: {exp}")
    quiz.retry_question()

    # Agora acerta todas as do Médio
    while quiz.in_quiz:
        q = quiz.get_current_question()
        correct_idx = q["correct_index"]
        is_correct, exp = quiz.answer_question(correct_idx)
        assert is_correct == True
        print(f"  [Acerto Médio] Q{quiz.current_question_idx + 1}: {q['title']}")
        quiz.advance_question()

    assert quiz.completed_levels[DIFF_MEDIO] == True, "Nível Médio deveria estar concluído!"
    assert quiz.unlocked_levels[DIFF_DIFICIL] == True, "Nível Difícil deveria ter sido desbloqueado!"
    print("[OK] Nível Médio concluído! Nível Difícil desbloqueado com sucesso! 🔓")

    # Inicia nível Difícil
    quiz.start_level(DIFF_DIFICIL)
    while quiz.in_quiz:
        q = quiz.get_current_question()
        correct_idx = q["correct_index"]
        is_correct, exp = quiz.answer_question(correct_idx)
        assert is_correct == True
        print(f"  [Acerto Difícil] Q{quiz.current_question_idx + 1}: {q['title']}")
        quiz.advance_question()

    assert quiz.completed_levels[DIFF_DIFICIL] == True, "Nível Difícil deveria estar concluído!"
    assert quiz.unlocked_levels[DIFF_DESAFIO] == True, "Nível Desafio deveria ter sido desbloqueado!"
    assert quiz.is_game_completed() == False, "A vitória só deveria vir após o nível Desafio!"
    print("[OK] Nível Difícil concluído! Nível Desafio desbloqueado com sucesso! 🔓")

    # Inicia nível Desafio (último nível da progressão no modo clássico)
    quiz.start_level(DIFF_DESAFIO)
    while quiz.in_quiz:
        q = quiz.get_current_question()
        is_correct, exp = quiz.answer_question(q["correct_index"])
        assert is_correct == True
        print(f"  [Acerto Desafio] Q{quiz.current_question_idx + 1}: {q['title']}")
        quiz.advance_question()

    assert quiz.completed_levels[DIFF_DESAFIO] == True, "Nível Desafio deveria estar concluído!"
    assert quiz.is_game_completed() == True, "Jogo deveria estar marcado como completado!"
    print("[OK] Nível Desafio concluído! Condição de vitória alcançada!")

    # Regressão: com Matemática já vencida, concluir um nível de OUTRA matéria
    # não pode reabrir a tela de vitória de Matemática
    quiz.set_subject(SUBJECT_HISTORY)
    quiz.start_level(DIFF_FACIL)
    while quiz.current_question_idx < quiz.total_questions_in_level() - 1:
        quiz.answer_question(quiz.get_current_question()["correct_index"])
        quiz.advance_question()
    quiz.answer_question(quiz.get_current_question()["correct_index"])
    ui.feedback_active, ui.feedback_correct = True, True
    enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    result = ui.handle_quiz_event(enter, quiz)
    assert result == "LEVEL_COMPLETE", f"Nível de História deveria dar LEVEL_COMPLETE, deu {result}!"
    quiz.set_subject(SUBJECT_MATH)
    print("[OK] Concluir nível de outra matéria após vencer Matemática não reabre a vitória.")

    # 4b. Regressão do bug de dicas/pontos duplicados: errar -> dica -> acertar
    #     deve avançar de vez, com pontuação concedida UMA única vez.
    print("\n--- Testando correção: errar -> dica -> acertar (sem pontos duplicados) ---")
    quiz.start_level(DIFF_FACIL)
    awarded = 0   # simula a pontuação concedida pelo main.py
    q = quiz.get_current_question()

    # 1ª tentativa: erra de propósito (entra em combate ao Espírito da Dúvida)
    already = quiz.current_question_scored
    is_correct, _ = quiz.answer_question((q["correct_index"] + 1) % 4)
    assert not is_correct and quiz.in_combat, "Errar deve iniciar o combate ao Espírito da Dúvida!"
    if is_correct and not already:
        awarded += 1

    # dica/retry: mantém a MESMA pergunta e não reinicia o estado pontuado
    quiz.retry_question()
    assert quiz.get_current_question()["id"] == q["id"], "A dica deve manter a mesma pergunta!"

    # 2ª tentativa: acerta com a ajuda da dica
    already = quiz.current_question_scored
    is_correct, _ = quiz.answer_question(q["correct_index"])
    assert is_correct, "Acerto após a dica deve ser reconhecido de imediato!"
    assert quiz.current_question_scored, "Pergunta acertada deve ficar marcada como concluída!"
    if is_correct and not already:
        awarded += 1

    # responder de novo NÃO repontua (pergunta respondida fica bloqueada)
    already = quiz.current_question_scored
    is_correct2, _ = quiz.answer_question(q["correct_index"])
    assert not is_correct2 and already, "Pergunta concluída deve recusar novas respostas!"

    # confirmar o feedback avança de vez (sem exigir nova seleção correta)
    quiz.advance_question()
    assert quiz.current_question_idx == 1, "Após acertar e confirmar, deve avançar para a 2ª pergunta!"
    assert not quiz.current_question_scored, "Nova pergunta começa sem marca de pontuação!"
    assert awarded == 1, f"A pergunta deve pontuar exatamente uma vez (pontuou {awarded})!"
    quiz.in_quiz = False
    quiz.end_combat()
    print("[OK] Errar -> dica -> acertar avança de vez e pontua UMA única vez (bug corrigido).")

    # 4c. Dicas pedagógicas: todas as perguntas têm dica própria e nenhuma
    #     dica entrega a resposta (não contém o texto da alternativa correta)
    for bank in list(ALL_QUESTIONS.values()) + list(COMPETITION_QUESTIONS.values()):
        for diff, questions in bank.items():
            for q in questions:
                hint = q.get("hint", "")
                assert hint and hint != q["explanation"], f"'{q['title']}' precisa de uma dica própria!"
                assert q["options"][q["correct_index"]].lower() not in hint.lower(), \
                    f"A dica de '{q['title']}' está entregando a resposta!"
    print("[OK] Dicas de todas as perguntas: ajudam a chegar à resposta sem entregá-la.")

    # 5. Renderiza a Tela de Vitória
    gl.clear()
    ui.draw_victory_screen(player.name)
    pygame.display.flip()
    print("[OK] Certificado e Tela de Vitória renderizados perfeitamente!")

    # 6. Modo Competição (lógica e telas)
    comp_ui = CompetitionUI(gl, assets, sound_manager)
    run_competition_tests(gl, comp_ui)
    run_ranking_tests(gl, ui, comp_ui)

    # 7. Tela cheia: a troca de modo recria o subsistema de vídeo, o pipeline
    #    GL, o viewport e as texturas (correção do crash e da proporção)
    dw, dh = pygame.display.get_desktop_sizes()[0]
    surf = create_display(True)
    # 1 linha a mais que o monitor: evita o congelamento da captura no OBS
    assert (dw, dh + 1) == surf.get_size(), "Tela cheia deveria ter a resolução nativa + 1 linha!"
    assert gl.logical_mouse_pos((0, 0)) == (0, 0), "Imagem deveria ficar colada no topo da tela!"
    # sem bordas (NOFRAME) e não exclusiva (FULLSCREEN): capturável pelo OBS
    assert surf.get_flags() & pygame.NOFRAME, "Tela cheia deveria ser uma janela sem bordas!"
    assert not surf.get_flags() & pygame.FULLSCREEN, "Tela cheia não deveria ser exclusiva!"
    assert pygame.display.get_caption()[0] == TITLE, "A janela recriada deveria manter o título!"
    gl.reinit()
    gl.refresh_viewport()
    assets.rebuild()
    comp_view = CompetitionManager()
    comp_view.setup_teams("Time Azul", "Time Vermelho")
    comp_view.start_turn()
    gl.clear()
    comp_ui.draw_quiz(0.016, comp_view)
    pygame.display.flip()
    print(f"[OK] Tela cheia na resolução nativa do monitor ({dw}x{dh}) renderizada sem crash.")

    # volta para modo janela
    surf = create_display(False)
    assert surf.get_size() == (WINDOW_WIDTH, WINDOW_HEIGHT), "Modo janela deveria voltar a 960x540!"
    gl.reinit()
    gl.refresh_viewport()
    assets.rebuild()
    gl.clear()
    comp_ui.draw_menu(0.016)
    pygame.display.flip()
    print("[OK] Retorno para modo janela renderizado sem crash.")

    # por último: cria o jogo completo (nova janela e contexto OpenGL)
    run_main_flow_tests()

    pygame.quit()
    print("\n=== TODOS OS TESTES PASSARAM COM 100% DE SUCESSO! ===")

if __name__ == "__main__":
    run_automated_test()
