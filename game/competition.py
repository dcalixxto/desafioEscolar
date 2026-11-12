"""
Modo Competição — 'O Desafio Escolar'.

Regras implementadas (definidas pela equipe organizadora do evento):
- Duas equipes competem; cada equipe tem 5 representantes.
- Participa um representante por vez; os representantes se revezam:
  a rodada de um representante termina quando ele perde os 3 corações
  ou conclui todos os níveis; então entra um representante da outra equipe.
- Cada nível de desafio tem 5 perguntas de 4 alternativas, sempre da matéria
  do professor visitado (cada professor pergunta só o tema dele); o
  representante só avança para o próximo nível após concluir as 5 perguntas.
- Há a opção "Responder depois": a pergunta é adiada e volta ao fim do nível.
- Errar diminui os corações da rodada e o representante pode tentar a MESMA
  pergunta de novo, com a ajuda da dica; acertar soma pontos (10/15/20/30 por nível).
- Vence a equipe que avançar mais longe; em empate de nível, a pontuação desempata.
"""

from game.config import (
    DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL, DIFF_DESAFIO,
    DIFFICULTY_LABELS, COMP_MAX_LIVES, COMP_MAX_REPS,
    SUBJECT_MATH, SUBJECT_HISTORY, SUBJECT_GEOGRAPHY, SUBJECT_BIOLOGY,
)
from game.competition_data import COMPETITION_QUESTIONS, SUBJECT_NAMES


class CompetitionManager:
    """Estado e regras do Modo Competição."""

    LEVELS = [DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL, DIFF_DESAFIO]
    POINTS_PER_LEVEL = {
        DIFF_FACIL: 10,
        DIFF_MEDIO: 15,
        DIFF_DIFICIL: 20,
        DIFF_DESAFIO: 30,
    }

    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # Ciclo de vida da competição
    # ------------------------------------------------------------------
    def reset(self):
        """Zera a competição (antes do cadastro ou ao recomeçar)."""
        self.team_names = ["", ""]
        self.team_points = [0, 0]        # pontos totais acumulados por equipe
        self.team_correct = [0, 0]       # acertos acumulados
        self.team_wrong = [0, 0]         # erros acumulados
        self.team_max_level = [-1, -1]   # índice do nível mais longe alcançado
        self.reps_used = [0, 0]          # representantes que já jogaram
        self.history = []                # tabela de rodadas disputadas
        self.turn_team = 0               # equipe da rodada atual
        self.quiz_subject = SUBJECT_MATH # matéria do professor visitado
        self.run = None                  # estado da rodada em andamento
        self.last_run = None             # rodada finalizada (resumo na tela)

    def set_subject(self, subject):
        """Define a matéria do quiz: o professor só pergunta o tema dele.

        Chamada quando o representante conversa com um professor; cada
        professor (Matemática, História, Geografia ou Biologia) faz apenas
        perguntas do tema pelo qual é responsável.
        """
        if subject in COMPETITION_QUESTIONS:
            self.quiz_subject = subject

    def current_subject_name(self):
        """Nome da matéria em andamento (para exibir na interface)."""
        return SUBJECT_NAMES.get(self.quiz_subject, "Matemática")

    def setup_teams(self, name1, name2):
        """Define os nomes das duas equipes e inicia a competição."""
        self.reset()
        self.team_names = [
            (name1 or "").strip() or "Equipe 1",
            (name2 or "").strip() or "Equipe 2",
        ]

    def competition_over(self):
        """A competição termina quando os 5 representantes de cada equipe jogaram."""
        return all(self.reps_used[i] >= COMP_MAX_REPS for i in (0, 1))

    def teams_configured(self):
        return all(bool(name) for name in self.team_names)

    # ------------------------------------------------------------------
    # Revezamento de representantes
    # ------------------------------------------------------------------
    def start_turn(self):
        """Inicia a rodada de um novo representante da equipe da vez."""
        team = self.turn_team
        self.reps_used[team] += 1
        self.run = {
            "team": team,                       # equipe do representante em jogo
            "rep": self.reps_used[team],        # número do representante (1..5)
            "name": None,                       # nome digitado do representante
            "lives": COMP_MAX_LIVES,
            "level_idx": 0,                     # índice dentro de LEVELS
            "q_idx": 0,                         # pergunta atual do nível
            "answered": [],                     # índices de perguntas já respondidas no nível
            "deferred": [],                     # índices de perguntas adiadas
            "deferred_replay": False,           # pergunta atual voltou do adiamento?
            "points": 0,
            "correct": 0,
            "wrong": 0,
            "last_correct": None,               # resultado da última resposta
            "finished": None,                   # None | "derrota" | "vitoria"
        }
        return self.run

    def end_turn(self):
        """Encerra a rodada, acumula os resultados e define a próxima equipe."""
        if self.run is None:
            return
        team = self.turn_team
        self.team_points[team] += self.run["points"]
        self.team_correct[team] += self.run["correct"]
        self.team_wrong[team] += self.run["wrong"]
        # nível alcançado: o nível em que o representante estava ao terminar
        self.team_max_level[team] = max(self.team_max_level[team], self.run["level_idx"])
        self.last_run = self.run
        # registra a rodada na tabela de andamento do jogo
        self.history.append({
            "team": team,
            "rep": self.run["rep"],
            "name": self.run.get("name"),
            "level_label": self.level_label_by_index(self.run["level_idx"]),
            "points": self.run["points"],
            "correct": self.run["correct"],
            "wrong": self.run["wrong"],
            "finished": self.run["finished"],
        })

        other = 1 - team
        if self.reps_used[other] < COMP_MAX_REPS:
            self.turn_team = other
        # caso contrário, a mesma equipe joga novamente (adversário sem representantes)

    def next_up(self):
        """Informação de quem joga na próxima rodada (para a interface)."""
        if self.competition_over():
            return None
        team = self.turn_team
        return {
            "team": team,
            "team_name": self.team_names[team],
            "rep": self.reps_used[team] + 1,
        }

    # ------------------------------------------------------------------
    # Perguntas da rodada em andamento
    # ------------------------------------------------------------------
    def current_level_key(self):
        if self.run is None:
            return DIFF_FACIL
        return self.LEVELS[self.run["level_idx"]]

    def current_level_label(self):
        return DIFFICULTY_LABELS.get(self.current_level_key(), "")

    def current_questions(self):
        """Perguntas do nível atual, sempre da matéria do professor visitado."""
        return COMPETITION_QUESTIONS[self.quiz_subject][self.current_level_key()]

    def current_question(self):
        """Pergunta atual da rodada (ou None se o nível acabou)."""
        if self.run is None:
            return None
        questions = self.current_questions()
        if 0 <= self.run["q_idx"] < len(questions):
            return questions[self.run["q_idx"]]
        return None

    def current_points_value(self):
        return self.POINTS_PER_LEVEL[self.current_level_key()]

    def answer(self, option_index):
        """Registra a resposta do representante. Retorna (acertou, explicação)."""
        question = self.current_question()
        if question is None:
            return False, ""
        is_correct = (option_index == question["correct_index"])
        self.run["last_correct"] = is_correct
        if is_correct:
            self.run["points"] += self.current_points_value()
            self.run["correct"] += 1
            # acerto: reforço com a explicação completa
            return True, question["explanation"]
        else:
            self.run["lives"] -= 1
            self.run["wrong"] += 1
            # erro: apenas uma dica, para ajudar a chegar à resposta sem
            # entregá-la (a explicação completa só aparece no acerto)
            return False, question.get("hint", question["explanation"])

    def defer_question(self):
        """'Responder depois': adia a pergunta atual e pula para a próxima.

        Perguntas adiadas voltam ao fim do nível e, quando voltam,
        devem ser respondidas (não podem ser adiadas de novo).
        """
        if self.run is None or self.run["deferred_replay"]:
            return False
        self.run["deferred"].append(self.run["q_idx"])
        nxt = self._next_unanswered(self.run["q_idx"] + 1)
        if nxt is not None:
            self.run["q_idx"] = nxt
        else:
            # não restam perguntas normais: a pergunta adiada volta na hora
            self.run["q_idx"] = self.run["deferred"].pop(0)
            self.run["deferred_replay"] = True
        return True

    # ------------------------------------------------------------------
    # Avanço após o feedback de cada resposta
    # ------------------------------------------------------------------
    def confirm_after_feedback(self):
        """Chamado quando o representante confirma o feedback da resposta.

        Retorna um dos eventos:
        - "QUESTION": próxima pergunta (ou pergunta adiada que voltou)
        - "QUESTION_RETRY": errou e pode responder NOVAMENTE a mesma
          pergunta, agora com a ajuda da dica
        - "LEVEL_COMPLETE": nível concluído, avançou de dificuldade
        - "TURN_END": rodada do representante terminou (derrota ou vitória)
        """
        if self.run is None:
            return "TURN_END"

        # sem corações: fim da rodada por derrota
        if self.run["lives"] <= 0:
            self.run["finished"] = "derrota"
            return "TURN_END"

        # errou: fica na MESMA pergunta para tentar de novo (a dica serve
        # exatamente para isso); o erro continua custando 1 coração
        if self.run.get("last_correct") is False:
            self.run["last_correct"] = None
            return "QUESTION_RETRY"

        return self._advance()

    def _next_unanswered(self, start):
        """Próximo índice de pergunta do nível ainda não respondida/adiada."""
        skip = set(self.run["answered"]) | set(self.run["deferred"])
        for i in range(start, len(self.current_questions())):
            if i not in skip:
                return i
        return None

    def _advance(self):
        """Avança para a próxima pergunta/nível. Retorna o evento correspondente."""
        run = self.run
        run["answered"].append(run["q_idx"])
        run["deferred_replay"] = False

        # próxima pergunta normal deste nível que ainda não foi respondida
        nxt = self._next_unanswered(run["q_idx"] + 1)
        if nxt is not None:
            run["q_idx"] = nxt
            return "QUESTION"

        # perguntas adiadas voltam ao fim do nível
        if run["deferred"]:
            run["q_idx"] = run["deferred"].pop(0)
            run["deferred_replay"] = True
            return "QUESTION"

        # nível concluído
        if run["level_idx"] < len(self.LEVELS) - 1:
            run["level_idx"] += 1
            run["q_idx"] = 0
            run["deferred"] = []
            run["answered"] = []
            return "LEVEL_COMPLETE"

        # concluiu o último nível: vitória do representante
        run["finished"] = "vitoria"
        return "TURN_END"

    # ------------------------------------------------------------------
    # Resultados
    # ------------------------------------------------------------------
    def level_label_by_index(self, level_idx):
        if 0 <= level_idx < len(self.LEVELS):
            return DIFFICULTY_LABELS[self.LEVELS[level_idx]]
        return "—"

    def winner(self):
        """Equipe vencedora (0 ou 1) ou None em caso de empate.

        Critérios: nível mais longe alcançado; em caso de igualdade,
        pontuação; persistindo o empate, menos erros.
        """
        a_lvl, b_lvl = self.team_max_level
        a_pts, b_pts = self.team_points
        a_err, b_err = self.team_wrong

        if a_lvl != b_lvl:
            return 0 if a_lvl > b_lvl else 1
        if a_pts != b_pts:
            return 0 if a_pts > b_pts else 1
        if a_err != b_err:
            return 0 if a_err < b_err else 1
        return None
