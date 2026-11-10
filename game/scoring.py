"""Sistema de pontuação e vidas (corações) para O Desafio Escolar."""
from datetime import datetime

class ScoreManager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.correct = 0
        self.wrong = 0
        self.hearts = 3
        self.max_hearts = 3
        self.started_at = datetime.now().isoformat()

    def add_correct(self, points=10):
        self.correct += 1
        self.score += points

    def add_wrong(self, heart_damage=1):
        self.wrong += 1
        # perde coracao a cada erro conforme solicitado
        self.hearts = max(0, self.hearts - heart_damage)
        return self.hearts <= 0

    def is_game_over(self):
        return self.hearts <= 0

    def snapshot(self, player_name="", subject="", gender="masculino"):
        total = self.correct + self.wrong
        nota = round((self.correct / total) * 10.0, 1) if total > 0 else 0.0
        status = "aprovado" if nota >= 6.0 else "reprovado"
        return {
            "nome_jogador": player_name,
            "materia": subject,
            "pontuacao": int(self.score),
            "acertos": int(self.correct),
            "erros": int(self.wrong),
            "coracoes_restantes": int(self.hearts),
            "nota_final": nota,
            "status_final": status,
            "genero": gender,
            "data": datetime.now().isoformat(),
        }
