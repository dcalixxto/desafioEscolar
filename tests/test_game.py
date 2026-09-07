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

    # 5. Renderiza a Tela de Vitória
    gl.clear()
    ui.draw_victory_screen(player.name)
    pygame.display.flip()
    print("[OK] Certificado e Tela de Vitória renderizados perfeitamente!")

    pygame.quit()
    print("\n=== TODOS OS TESTES PASSARAM COM 100% DE SUCESSO! ===")

if __name__ == "__main__":
    run_automated_test()
