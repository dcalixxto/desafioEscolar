"""
Script de Teste Automatizado e Validação do Jogo 'O Desafio Escolar'.
Simula a jornada completa do jogador sem requerer entrada manual.
"""

import os
import sys
import pygame

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    STATE_NAME_INPUT, STATE_EXPLORE, STATE_DIALOG, STATE_QUIZ, STATE_VICTORY,
    DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL
)
from game.gl_renderer import GLRenderer
from game.audio import sound_manager
from game.assets import AssetManager
from game.entities import Player
from game.world import SchoolWorld, ZONE_HALLWAY, ZONE_CLASSROOM
from game.quiz_data import QuizManager, QUIZ_QUESTIONS
from game.ui import UIManager
from game.competition import CompetitionManager
from game.ui_competition import CompetitionUI
from game.competition_data import COMPETITION_QUESTIONS, questions_per_level
from game.config import COMP_MAX_REPS, SUBJECT_MATH, SUBJECT_BIOLOGY


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

    # 5. Derrota: 3 erros drenam os corações e encerram a rodada
    comp.answer(1 - comp.current_question()["correct_index"])
    comp.confirm_after_feedback()
    assert comp.run["lives"] == 2, "1º erro deve deixar 2 corações!"
    comp.answer(1 - comp.current_question()["correct_index"])
    comp.confirm_after_feedback()
    assert comp.run["lives"] == 1, "2º erro deve deixar 1 coração!"
    comp.answer(1 - comp.current_question()["correct_index"])
    event = comp.confirm_after_feedback()
    assert comp.run["lives"] == 0, "3º erro deve zerar os corações!"
    assert event == "TURN_END" and comp.run["finished"] == "derrota", "Sem corações a rodada deve terminar em derrota!"
    comp.end_turn()
    assert comp.team_points[0] == 125, "Pontos das rodadas devem ser acumulados na equipe (50+75 da progressão)!"
    assert comp.turn_team == 1, "Após a derrota da Equipe 1, a vez é da Equipe 2!"
    assert comp.next_up()["rep"] == 1, "Equipe 2 deve começar com o representante 1!"
    assert len(comp.history) == 1, "A rodada disputada deve estar registrada na tabela de andamento!"
    entry = comp.history[0]
    assert entry["team"] == 0 and entry["rep"] == 1 and entry["points"] == 125, "Registro da tabela deve guardar equipe, representante e pontos!"
    assert entry["finished"] == "derrota", "Registro da tabela deve guardar o resultado da rodada!"
    print("[OK] Sistema de vida: 3 erros encerram a rodada e a vez passa para a Equipe 2.")
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
    assert quiz.is_game_completed() == True, "Jogo deveria estar marcado como completado!"
    print("[OK] Nível Difícil concluído! Condição de vitória alcançada!")

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

    # 5. Renderiza a Tela de Vitória
    gl.clear()
    ui.draw_victory_screen(player.name)
    pygame.display.flip()
    print("[OK] Certificado e Tela de Vitória renderizados perfeitamente!")

    # 6. Modo Competição (lógica e telas)
    comp_ui = CompetitionUI(gl, assets, sound_manager)
    run_competition_tests(gl, comp_ui)

    # 7. Tela cheia: a troca de modo recria o subsistema de vídeo, o pipeline
    #    GL, o viewport e as texturas (correção do crash e da proporção)
    dw, dh = pygame.display.get_desktop_sizes()[0]
    pygame.display.quit()
    pygame.display.init()
    pygame.display.set_mode((dw, dh), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN)
    assert (dw, dh) == pygame.display.get_surface().get_size(), "Tela cheia deveria usar a resolução nativa!"
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
    pygame.display.quit()
    pygame.display.init()
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    gl.reinit()
    gl.refresh_viewport()
    assets.rebuild()
    gl.clear()
    comp_ui.draw_menu(0.016)
    pygame.display.flip()
    print("[OK] Retorno para modo janela renderizado sem crash.")

    pygame.quit()
    print("\n=== TODOS OS TESTES PASSARAM COM 100% DE SUCESSO! ===")

if __name__ == "__main__":
    run_automated_test()
