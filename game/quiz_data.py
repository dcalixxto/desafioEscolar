"""
Banco de Questões Matemáticas e Lógica de Progressão para 'O Desafio Escolar'.
Baseado no GDD do projeto (público de 14 a 17 anos).
"""

from game.config import DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL

QUIZ_QUESTIONS = {
    DIFF_FACIL: [
        {
            "id": 1,
            "title": "Álgebra Básica (Equação do 1º Grau)",
            "question": "Um aluno comprou 3 cadernos iguais e uma régua que custou R$ 4,00. No total, ele pagou R$ 28,00. Qual o preço de cada caderno?",
            "options": [
                "R$ 6,00",
                "R$ 8,00",
                "R$ 7,50",
                "R$ 9,00"
            ],
            "correct_index": 1, # R$ 8,00
            "explanation": "Montando a equação: 3x + 4 = 28 -> 3x = 24 -> x = 24 / 3 = R$ 8,00."
        },
        {
            "id": 2,
            "title": "Porcentagem do Cotidiano",
            "question": "Uma mochila escolar custa R$ 120,00, mas está com um desconto especial de 25% para estudantes. Qual o valor final da mochila com desconto?",
            "options": [
                "R$ 90,00",
                "R$ 95,00",
                "R$ 85,00",
                "R$ 100,00"
            ],
            "correct_index": 0, # R$ 90,00
            "explanation": "25% de 120 é 120 * 0,25 = 30. Subtraindo o desconto: 120 - 30 = R$ 90,00."
        },
        {
            "id": 3,
            "title": "Geometria Básica (Perímetro)",
            "question": "A quadra esportiva da escola possui formato retangular com 15 metros de largura e 25 metros de comprimento. Qual é o perímetro dessa quadra?",
            "options": [
                "60 metros",
                "75 metros",
                "80 metros",
                "90 metros"
            ],
            "correct_index": 2, # 80 metros
            "explanation": "O perímetro de um retângulo é a soma de todos os lados: 2 * (15 + 25) = 2 * 40 = 80 metros."
        }
    ],

    DIFF_MEDIO: [
        {
            "id": 1,
            "title": "Geometria Plana (Área de Triângulo)",
            "question": "Um canteiro de flores triangular na entrada da escola tem base medindo 8 metros e altura relativa de 6 metros. Qual é a área desse canteiro?",
            "options": [
                "48 m²",
                "24 m²",
                "14 m²",
                "28 m²"
            ],
            "correct_index": 1, # 24 m²
            "explanation": "A área do triângulo é dada por (base * altura) / 2 = (8 * 6) / 2 = 48 / 2 = 24 m²."
        },
        {
            "id": 2,
            "title": "Equações do 2º Grau",
            "question": "Dada a equação x² - 49 = 0, quais são as raízes reais que tornam a igualdade verdadeira?",
            "options": [
                "x = 7 e x = -7",
                "x = 49 e x = -49",
                "Apenas x = 7",
                "x = 0 e x = 7"
            ],
            "correct_index": 0, # x = 7 e x = -7
            "explanation": "x² = 49 -> x = ±√49 -> x = 7 ou x = -7."
        },
        {
            "id": 3,
            "title": "Regra de Três & Proporcionalidade",
            "question": "Uma impressora da biblioteca imprime 180 páginas em 6 minutos no ritmo normal. Quantas páginas ela imprimirá em 15 minutos mantendo a mesma velocidade?",
            "options": [
                "360 páginas",
                "420 páginas",
                "450 páginas",
                "500 páginas"
            ],
            "correct_index": 2, # 450 páginas
            "explanation": "Velocidade = 180 / 6 = 30 páginas por minuto. Em 15 minutos: 30 * 15 = 450 páginas."
        }
    ],

    DIFF_DIFICIL: [
        {
            "id": 1,
            "title": "Teorema de Pitágoras",
            "question": "Uma rampa de acessibilidade tem altura vertical de 3 metros e sua base horizontal no chão mede 4 metros. Qual é o comprimento total da rampa inclinada?",
            "options": [
                "6 metros",
                "5 metros",
                "7 metros",
                "4,5 metros"
            ],
            "correct_index": 1, # 5 metros
            "explanation": "Pelo Teorema de Pitágoras: a² + b² = c² -> 3² + 4² = 9 + 16 = 25 -> c = √25 = 5 metros."
        },
        {
            "id": 2,
            "title": "Funções do 1º Grau (Função Afim)",
            "question": "Considere a função afim f(x) = 4x - 7. Qual é o valor numérico de f(5)?",
            "options": [
                "13",
                "15",
                "20",
                "27"
            ],
            "correct_index": 0, # 13
            "explanation": "Substituindo x = 5 na função: f(5) = 4 * 5 - 7 = 20 - 7 = 13."
        },
        {
            "id": 3,
            "title": "Probabilidade Básica",
            "question": "Em um sorteio da gincana escolar com fichas numeradas de 1 a 20 dentro de uma urna, qual a probabilidade de se retirar um número primo?",
            "options": [
                "25% (5/20)",
                "35% (7/20)",
                "40% (8/20)",
                "50% (10/20)"
            ],
            "correct_index": 2, # 40% (8/20)
            "explanation": "Os números primos entre 1 e 20 são: 2, 3, 5, 7, 11, 13, 17 e 19 (total de 8 números). Probabilidade = 8 / 20 = 2 / 5 = 40%."
        }
    ]
}

class QuizManager:
    def __init__(self):
        self.unlocked_levels = {
            DIFF_FACIL: True,
            DIFF_MEDIO: False,
            DIFF_DIFICIL: False
        }
        self.completed_levels = {
            DIFF_FACIL: False,
            DIFF_MEDIO: False,
            DIFF_DIFICIL: False
        }
        self.current_difficulty = DIFF_FACIL
        self.current_question_idx = 0
        self.in_quiz = False
        self.last_answer_correct = None
        self.selected_option = None

    def start_level(self, difficulty):
        if not self.unlocked_levels.get(difficulty, False):
            return False
        self.current_difficulty = difficulty
        self.current_question_idx = 0
        self.in_quiz = True
        self.last_answer_correct = None
        self.selected_option = None
        return True

    def get_current_question(self):
        questions = QUIZ_QUESTIONS.get(self.current_difficulty, [])
        if 0 <= self.current_question_idx < len(questions):
            return questions[self.current_question_idx]
        return None

    def total_questions_in_level(self):
        return len(QUIZ_QUESTIONS.get(self.current_difficulty, []))

    def answer_question(self, option_index):
        q = self.get_current_question()
        if not q:
            return False, ""

        self.selected_option = option_index
        is_correct = (option_index == q["correct_index"])
        self.last_answer_correct = is_correct

        if is_correct:
            return True, q["explanation"]
        else:
            return False, q["explanation"]

    def advance_question(self):
        """Avança para a próxima questão ou conclui o nível."""
        self.last_answer_correct = None
        self.selected_option = None
        self.current_question_idx += 1
        
        # Verifica se concluiu o nível
        if self.current_question_idx >= self.total_questions_in_level():
            self.completed_levels[self.current_difficulty] = True
            
            # Desbloqueia o próximo nível conforme o GDD
            if self.current_difficulty == DIFF_FACIL:
                self.unlocked_levels[DIFF_MEDIO] = True
            elif self.current_difficulty == DIFF_MEDIO:
                self.unlocked_levels[DIFF_DIFICIL] = True
                
            self.in_quiz = False
            return True # Nível concluído com sucesso!
        return False # Ainda há questões

    def retry_question(self):
        """Reinicia o estado para tentar responder a mesma questão novamente."""
        self.last_answer_correct = None
        self.selected_option = None

    def is_game_completed(self):
        """Condição de vitória final: concluir o nível Difícil."""
        return self.completed_levels[DIFF_DIFICIL]
