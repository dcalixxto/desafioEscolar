"""
Banco de Questões e Lógica de Progressão/Combate para 'O Desafio Escolar'.
Inclui múltiplas matérias e combate simples ao errar respostas.
"""

from copy import deepcopy
from game.config import (
    DIFF_FACIL, DIFF_MEDIO, DIFF_DIFICIL, DIFF_DESAFIO,
    SUBJECT_MATH, SUBJECT_HISTORY, SUBJECT_GEOGRAPHY, SUBJECT_BIOLOGY, SUBJECTS
)

MATH_QUESTIONS = {
    DIFF_FACIL: [
        {"id": 1, "title": "Álgebra Básica (Equação do 1º Grau)", "question": "Um aluno comprou 3 cadernos iguais e uma régua que custou R$ 4,00. No total, ele pagou R$ 28,00. Qual o preço de cada caderno?", "options": ["R$ 6,00", "R$ 8,00", "R$ 7,50", "R$ 9,00"], "correct_index": 1, "explanation": "3x + 4 = 28 -> 3x = 24 -> x = R$ 8,00."},
        {"id": 2, "title": "Porcentagem do Cotidiano", "question": "Uma mochila escolar custa R$ 120,00, mas está com desconto de 25%. Qual o valor final?", "options": ["R$ 90,00", "R$ 95,00", "R$ 85,00", "R$ 100,00"], "correct_index": 0, "explanation": "25% de 120 = 30. Valor final: 120 - 30 = R$ 90,00."},
        {"id": 3, "title": "Geometria Básica (Perímetro)", "question": "Uma quadra retangular tem 15 m de largura e 25 m de comprimento. Qual é o perímetro?", "options": ["60 metros", "75 metros", "80 metros", "90 metros"], "correct_index": 2, "explanation": "Perímetro = 2 * (15 + 25) = 80 metros."},
        {"id": 4, "title": "Raciocínio com Frações", "question": "Em uma turma de 30 alunos, 2/5 participam do clube de matemática. Quantos participam?", "options": ["10 alunos", "12 alunos", "14 alunos", "15 alunos"], "correct_index": 1, "explanation": "2/5 de 30 = 12 alunos."},
        {"id": 5, "title": "Sequência Numérica", "question": "Observe a sequência: 3, 7, 11, 15, ... Qual é o próximo número?", "options": ["17", "18", "19", "21"], "correct_index": 2, "explanation": "A sequência aumenta de 4 em 4: 15 + 4 = 19."},
    ],
    DIFF_MEDIO: [
        {"id": 1, "title": "Geometria Plana (Área)", "question": "Um canteiro triangular tem base 8 m e altura 6 m. Qual é a área?", "options": ["48 m²", "24 m²", "14 m²", "28 m²"], "correct_index": 1, "explanation": "Área = (base * altura) / 2 = (8 * 6) / 2 = 24 m²."},
        {"id": 2, "title": "Equação do 2º Grau", "question": "Dada a equação x² - 49 = 0, quais são as raízes reais?", "options": ["x = 7 e x = -7", "x = 49 e x = -49", "Apenas x = 7", "x = 0 e x = 7"], "correct_index": 0, "explanation": "x² = 49 -> x = ±7."},
        {"id": 3, "title": "Regra de Três", "question": "Uma impressora imprime 180 páginas em 6 minutos. Quantas páginas em 15 minutos?", "options": ["360 páginas", "420 páginas", "450 páginas", "500 páginas"], "correct_index": 2, "explanation": "30 páginas/min * 15 min = 450 páginas."},
        {"id": 4, "title": "Média Aritmética", "question": "Notas: 6,0; 7,5; 8,5 e 8,0. Qual é a média?", "options": ["7,0", "7,5", "8,0", "8,5"], "correct_index": 1, "explanation": "Média = (6,0 + 7,5 + 8,5 + 8,0) / 4 = 7,5."},
        {"id": 5, "title": "Potenciação", "question": "Qual é o valor de 2⁵ + 3²?", "options": ["37", "41", "43", "45"], "correct_index": 1, "explanation": "2⁵ = 32 e 3² = 9. Soma = 41."},
    ],
    DIFF_DIFICIL: [
        {"id": 1, "title": "Teorema de Pitágoras", "question": "Uma rampa tem altura 3 m e base 4 m. Qual o comprimento da rampa?", "options": ["6 metros", "5 metros", "7 metros", "4,5 metros"], "correct_index": 1, "explanation": "c² = 3² + 4² = 25 -> c = 5 metros."},
        {"id": 2, "title": "Função Afim", "question": "Para f(x) = 4x - 7, qual é o valor de f(5)?", "options": ["13", "15", "20", "27"], "correct_index": 0, "explanation": "f(5) = 20 - 7 = 13."},
        {"id": 3, "title": "Probabilidade", "question": "Ao sortear um número de 1 a 20, qual a probabilidade de ser primo?", "options": ["25% (5/20)", "35% (7/20)", "40% (8/20)", "50% (10/20)"], "correct_index": 2, "explanation": "Primos: 2,3,5,7,11,13,17,19 (8 números) = 40%."},
        {"id": 4, "title": "Sistemas Lineares", "question": "No sistema {x + y = 10; x - y = 2}, qual é o valor de x?", "options": ["4", "5", "6", "8"], "correct_index": 2, "explanation": "Somando: 2x = 12 -> x = 6."},
        {"id": 5, "title": "Juros Simples", "question": "R$ 500,00 a 2% ao mês por 6 meses (juros simples). Qual o montante?", "options": ["R$ 540,00", "R$ 560,00", "R$ 580,00", "R$ 600,00"], "correct_index": 1, "explanation": "Juros = 500*0,02*6 = 60. Montante = R$ 560,00."},
    ],
    DIFF_DESAFIO: [
        {"id": 1, "title": "Equacao do 2o Grau (Bhaskara)", "question": "Resolva x^2 - 5x + 6 = 0. Quais sao as raizes?", "options": ["x = 1 e x = 6", "x = 2 e x = 3", "x = -2 e x = -3", "x = 1 e x = 5"], "correct_index": 1, "explanation": "Soma 5 e produto 6: raizes 2 e 3 (ou por Bhaskara: delta=1)."},
        {"id": 2, "title": "Funcao Quadratica", "question": "Para f(x) = x^2 - 4x + 3, qual e o valor minimo de f(x)?", "options": ["-1", "0", "1", "3"], "correct_index": 0, "explanation": "Vertice em xv=2: f(2)=4-8+3=-1 (minimo, pois a>0)."},
        {"id": 3, "title": "Trigonometria Basica", "question": "Em um triangulo retangulo, se sen(A)=3/5 e a hipotenusa mede 10, quanto mede o cateto oposto a A?", "options": ["4", "5", "6", "8"], "correct_index": 2, "explanation": "sen(A)=oposto/hipotenusa => oposto = 10*(3/5)=6."},
        {"id": 4, "title": "PA e PG (Raciocinio)", "question": "Uma PA tem primeiro termo 2 e razao 3. Qual e a soma dos 5 primeiros termos?", "options": ["30", "35", "40", "45"], "correct_index": 2, "explanation": "Termos: 2,5,8,11,14. Soma = 40 (ou S5 = 5/2*(2*2 + 4*3)=40)."},
        {"id": 5, "title": "Probabilidade e Contagem", "question": "De um grupo com 3 meninos e 2 meninas, escolhem-se 2 alunos ao acaso. Qual a probabilidade de escolher 1 menino e 1 menina?", "options": ["3/10", "2/5", "3/5", "1/2"], "correct_index": 2, "explanation": "Total C(5,2)=10. Favoraveis C(3,1)*C(2,1)=6. Probabilidade 6/10=3/5."},
    ],
}

HISTORY_QUESTIONS = {
    DIFF_FACIL: [
        {"id": 1, "title": "Independência do Brasil", "question": "Em que ano ocorreu a Independência do Brasil?", "options": ["1808", "1822", "1889", "1500"], "correct_index": 1, "explanation": "A Independência foi proclamada em 7 de setembro de 1822."},
        {"id": 2, "title": "Descobrimento", "question": "Quem comandou a expedição portuguesa que chegou ao Brasil em 1500?", "options": ["Dom Pedro I", "Cristóvão Colombo", "Pedro Álvares Cabral", "Tiradentes"], "correct_index": 2, "explanation": "Pedro Álvares Cabral liderou a chegada dos portugueses em 1500."},
        {"id": 3, "title": "Proclamação da República", "question": "Em que ano foi proclamada a República no Brasil?", "options": ["1822", "1888", "1889", "1930"], "correct_index": 2, "explanation": "A Proclamação da República ocorreu em 15 de novembro de 1889."},
    ],
    DIFF_MEDIO: [
        {"id": 1, "title": "Abolição da Escravidão", "question": "Qual lei aboliu oficialmente a escravidão no Brasil?", "options": ["Lei Eusébio de Queirós", "Lei do Ventre Livre", "Lei Áurea", "Lei dos Sexagenários"], "correct_index": 2, "explanation": "A Lei Áurea foi assinada em 1888."},
        {"id": 2, "title": "Era Vargas", "question": "Quem foi o presidente do Brasil associado ao Estado Novo (1937-1945)?", "options": ["Juscelino Kubitschek", "Getúlio Vargas", "João Goulart", "Washington Luís"], "correct_index": 1, "explanation": "Getúlio Vargas governou durante o período do Estado Novo."},
        {"id": 3, "title": "Revolução Francesa", "question": "Qual evento é considerado o marco inicial da Revolução Francesa em 1789?", "options": ["Queda do Muro de Berlim", "Tomada da Bastilha", "Independência dos EUA", "Congresso de Viena"], "correct_index": 1, "explanation": "A Tomada da Bastilha ocorreu em 14 de julho de 1789."},
    ],
    DIFF_DIFICIL: [
        {"id": 1, "title": "Guerra Fria", "question": "A Guerra Fria foi marcada principalmente pela rivalidade entre quais blocos?", "options": ["Brasil e Argentina", "EUA e URSS", "Alemanha e França", "China e Japão"], "correct_index": 1, "explanation": "A Guerra Fria envolveu a disputa geopolítica entre EUA e URSS."},
        {"id": 2, "title": "Constituição de 1988", "question": "A Constituição Brasileira de 1988 é conhecida como:", "options": ["Constituição Polaca", "Constituição Cidadã", "Constituição do Império", "Constituição outorgada"], "correct_index": 1, "explanation": "Ela é chamada de Constituição Cidadã pelo foco em direitos."},
        {"id": 3, "title": "Roma Antiga", "question": "Qual instituição política teve grande importância na República Romana?", "options": ["Senado", "Assembleia da ONU", "Parlamento Inglês", "Cortes Portuguesas"], "correct_index": 0, "explanation": "O Senado foi uma das principais instituições da República Romana."},
    ],
    DIFF_DESAFIO: [
        {"id": 1, "title": "Brasil Colonial e Economia", "question": "Qual atividade economica foi central no inicio da colonizacao do Brasil e impulsionou a ocupacao do litoral?", "options": ["Mineracao de ouro", "Extracao do pau-brasil", "Cultivo do cafe", "Industria siderurgica"], "correct_index": 1, "explanation": "No seculo XVI, a exploracao do pau-brasil foi a principal atividade economica inicial."},
        {"id": 2, "title": "Iluminismo e Revolucoes", "question": "Qual ideia iluminista influenciou fortemente movimentos por independencia nas Americas?", "options": ["Direito divino dos reis", "Soberania popular e direitos individuais", "Isolamento comercial", "Servidao como base social"], "correct_index": 1, "explanation": "O Iluminismo defendeu razao, liberdade e direitos, influenciando processos de independencia."},
        {"id": 3, "title": "Segunda Guerra Mundial", "question": "Qual foi uma consequencia direta do fim da Segunda Guerra Mundial (1945)?", "options": ["Criacao da ONU e inicio da Guerra Fria", "Unificacao imediata da Alemanha", "Fim de todos os conflitos mundiais", "Queda do Imperio Romano"], "correct_index": 0, "explanation": "Apos 1945, criou-se a ONU para cooperacao internacional e emergiu a rivalidade EUA-URSS."},
    ],
}

GEOGRAPHY_QUESTIONS = {
    DIFF_FACIL: [
        {"id": 1, "title": "Continentes", "question": "Quantos continentes existem na Terra (considerando o modelo de 6 continentes)?", "options": ["5", "6", "7", "4"], "correct_index": 1, "explanation": "No modelo mais usado no Brasil, são 6 continentes."},
        {"id": 2, "title": "Capital do Brasil", "question": "Qual é a capital do Brasil?", "options": ["Rio de Janeiro", "São Paulo", "Brasília", "Salvador"], "correct_index": 2, "explanation": "Brasília é a capital federal desde 1960."},
        {"id": 3, "title": "Pontos Cardeais", "question": "Qual ponto cardeal é oposto ao Norte?", "options": ["Leste", "Oeste", "Sul", "Nordeste"], "correct_index": 2, "explanation": "O ponto oposto ao Norte é o Sul."},
    ],
    DIFF_MEDIO: [
        {"id": 1, "title": "Biomas do Brasil", "question": "Qual bioma brasileiro é conhecido pela maior biodiversidade do planeta?", "options": ["Caatinga", "Pampa", "Amazônia", "Pantanal"], "correct_index": 2, "explanation": "A Amazônia possui enorme biodiversidade e a maior floresta tropical."},
        {"id": 2, "title": "Clima", "question": "O clima predominante na região Norte do Brasil é:", "options": ["Semiárido", "Equatorial", "Subtropical", "Temperado"], "correct_index": 1, "explanation": "A região Norte apresenta clima predominantemente equatorial, quente e úmido."},
        {"id": 3, "title": "Relevo", "question": "Planaltos, planícies e depressões são formas de:", "options": ["Clima", "Relevo", "Vegetação", "Hidrografia"], "correct_index": 1, "explanation": "Essas são classificações das formas do relevo terrestre."},
    ],
    DIFF_DIFICIL: [
        {"id": 1, "title": "Placas Tectônicas", "question": "Terremotos e vulcões estão frequentemente associados a:", "options": ["Zonas de fronteira agrícola", "Limites de placas tectônicas", "Áreas de clima polar", "Desertos arenosos"], "correct_index": 1, "explanation": "A atividade sísmica e vulcânica é comum nos limites das placas tectônicas."},
        {"id": 2, "title": "Fusos Horários", "question": "O sistema de fusos horários tem como referência principal o:", "options": ["Trópico de Câncer", "Meridiano de Greenwich", "Equador", "Círculo Polar Ártico"], "correct_index": 1, "explanation": "O Meridiano de Greenwich é a referência inicial dos fusos horários."},
        {"id": 3, "title": "Globalização", "question": "Um efeito marcante da globalização é:", "options": ["Isolamento total dos países", "Maior integração econômica e cultural", "Fim das tecnologias de comunicação", "Redução completa das trocas comerciais"], "correct_index": 1, "explanation": "A globalização intensifica fluxos econômicos, culturais e informacionais."},
    ],
    DIFF_DESAFIO: [
        {"id": 1, "title": "Demografia", "question": "Se um pais apresenta queda na taxa de natalidade e aumento da expectativa de vida, qual tendencia demografica e mais provavel?", "options": ["Populacao totalmente rural", "Envelhecimento da populacao", "Crescimento acelerado infantil", "Reducao da idade media"], "correct_index": 1, "explanation": "Menos nascimentos e maior longevidade elevam a proporcao de idosos (envelhecimento)."},
        {"id": 2, "title": "Clima e Correntes Maritimas", "question": "Correntes maritimas frias proximas ao litoral tendem a:", "options": ["Aumentar a umidade e chuvas intensas sempre", "Reduzir a evaporacao e favorecer menor pluviosidade", "Eliminar ventos costeiros", "Tornar o clima equatorial"], "correct_index": 1, "explanation": "Aguas frias diminuem a evaporacao, podendo contribuir para menor umidade e chuvas em algumas regioes."},
        {"id": 3, "title": "Urbanizacao e Problemas Ambientais", "question": "A impermeabilizacao do solo em grandes cidades (asfalto/concreto) esta mais diretamente associada a:", "options": ["Aumento da infiltracao da agua", "Reducao de enchentes", "Aumento do escoamento superficial e risco de alagamentos", "Formacao de novos rios"], "correct_index": 2, "explanation": "Com menos solo exposto, a agua escoa mais rapido pela superficie, elevando riscos de enchentes."},
    ],
}

BIOLOGY_QUESTIONS = {
    DIFF_FACIL: [
        {"id": 1, "title": "Células", "question": "Qual é a unidade básica da vida?", "options": ["Tecido", "Órgão", "Célula", "Sistema"], "correct_index": 2, "explanation": "A célula é a unidade estrutural e funcional básica dos seres vivos."},
        {"id": 2, "title": "Fotossíntese", "question": "Qual gás as plantas absorvem principalmente durante a fotossíntese?", "options": ["Oxigênio", "Gás carbônico (CO₂)", "Nitrogênio", "Hidrogênio"], "correct_index": 1, "explanation": "Na fotossíntese, as plantas utilizam CO₂, água e luz para produzir energia."},
        {"id": 3, "title": "Cinco Sentidos", "question": "Qual órgão é responsável principalmente pela visão?", "options": ["Ouvido", "Pele", "Olhos", "Nariz"], "correct_index": 2, "explanation": "Os olhos captam estímulos luminosos para a visão."},
    ],
    DIFF_MEDIO: [
        {"id": 1, "title": "Cadeia Alimentar", "question": "Organismos que produzem seu próprio alimento, como plantas, são chamados de:", "options": ["Consumidores", "Decompositores", "Produtores", "Parasitas"], "correct_index": 2, "explanation": "Produtores (autótrofos) produzem matéria orgânica, geralmente por fotossíntese."},
        {"id": 2, "title": "Sistema Circulatório", "question": "Qual órgão bombeia o sangue pelo corpo humano?", "options": ["Pulmão", "Coração", "Fígado", "Rim"], "correct_index": 1, "explanation": "O coração é responsável por bombear o sangue na circulação."},
        {"id": 3, "title": "Vacinação", "question": "As vacinas atuam principalmente:", "options": ["Substituindo órgãos", "Estimulando o sistema imunológico", "Causando doenças graves", "Parando a digestão"], "correct_index": 1, "explanation": "Vacinas estimulam defesas do organismo contra agentes infecciosos."},
    ],
    DIFF_DIFICIL: [
        {"id": 1, "title": "DNA", "question": "O DNA é a molécula responsável principalmente por:", "options": ["Produzir ossos diretamente", "Armazenar informação genética", "Filtrar o sangue", "Regular a temperatura ambiente"], "correct_index": 1, "explanation": "O DNA armazena e transmite informações genéticas."},
        {"id": 2, "title": "Ecossistemas", "question": "Relação ecológica em que ambos os organismos se beneficiam é chamada de:", "options": ["Competição", "Predação", "Mutualismo", "Parasitismo"], "correct_index": 2, "explanation": "No mutualismo, as duas espécies envolvidas obtêm benefícios."},
        {"id": 3, "title": "Mitose", "question": "A mitose tem como uma de suas funções principais:", "options": ["Formar gametas", "Crescimento e renovação celular", "Reduzir pela metade os cromossomos", "Produzir anticorpos"], "correct_index": 1, "explanation": "A mitose gera células geneticamente semelhantes, importante para crescimento e reparo."},
    ],
    DIFF_DESAFIO: [
        {"id": 1, "title": "Genetica Basica", "question": "No cruzamento Aa x Aa (A dominante, a recessivo), qual a proporcao esperada de individuos com fenotipo dominante?", "options": ["25%", "50%", "75%", "100%"], "correct_index": 2, "explanation": "Genotipos: AA, Aa, Aa, aa. Tres em quatro apresentam fenotipo dominante (75%)."},
        {"id": 2, "title": "Fisiologia Humana", "question": "Durante exercicio intenso, a frequencia respiratoria aumenta principalmente para:", "options": ["Reduzir a temperatura do sangue", "Fornecer mais O2 e eliminar mais CO2", "Produzir glicose nos pulmoes", "Parar a circulacao"], "correct_index": 1, "explanation": "Musculos ativos demandam mais oxigenio e geram mais CO2, exigindo maior ventilacao."},
        {"id": 3, "title": "Ecologia e Energia", "question": "Em uma cadeia alimentar, por que a energia disponivel diminui a cada nivel trofico?", "options": ["Porque a energia e criada nos consumidores", "Porque parte da energia e dissipada como calor e usada no metabolismo", "Porque produtores nao fazem fotossintese", "Porque decompositores geram toda energia"], "correct_index": 1, "explanation": "A cada transferencia, ha perdas (calor, metabolismo), restando menos energia para o nivel seguinte."},
    ],
}

ALL_QUESTIONS = {
    SUBJECT_MATH: MATH_QUESTIONS,
    SUBJECT_HISTORY: HISTORY_QUESTIONS,
    SUBJECT_GEOGRAPHY: GEOGRAPHY_QUESTIONS,
    SUBJECT_BIOLOGY: BIOLOGY_QUESTIONS,
}

# Compatibilidade com testes/código legado (matemática)
QUIZ_QUESTIONS = ALL_QUESTIONS[SUBJECT_MATH]

class QuizManager:
    def __init__(self, subject=SUBJECT_MATH):
        self.progress = {}
        self._init_progress()
        self.current_subject = subject if subject in ALL_QUESTIONS else SUBJECT_MATH
        self.current_difficulty = DIFF_FACIL
        self.current_question_idx = 0
        self.in_quiz = False
        self.last_answer_correct = None
        self.selected_option = None
        # marca se a pergunta atual já foi pontuada (impede pontos duplicados)
        self.current_question_scored = False
        # Combate ao errar
        self.in_combat = False
        self.player_hp = 3
        self.player_max_hp = 3
        self.enemy_hp = 2
        self.enemy_max_hp = 2
        self.combat_message = ""

    def _init_progress(self):
        for sid in ALL_QUESTIONS.keys():
            self.progress[sid] = {
                "unlocked": {DIFF_FACIL: True, DIFF_MEDIO: False, DIFF_DIFICIL: False, DIFF_DESAFIO: False},
                "completed": {DIFF_FACIL: False, DIFF_MEDIO: False, DIFF_DIFICIL: False, DIFF_DESAFIO: False},
            }

    @property
    def unlocked_levels(self):
        return self.progress[self.current_subject]["unlocked"]

    @unlocked_levels.setter
    def unlocked_levels(self, value):
        self.progress[self.current_subject]["unlocked"] = value

    @property
    def completed_levels(self):
        return self.progress[self.current_subject]["completed"]

    @completed_levels.setter
    def completed_levels(self, value):
        self.progress[self.current_subject]["completed"] = value

    def set_subject(self, subject):
        if subject in ALL_QUESTIONS:
            self.current_subject = subject
            self.current_question_idx = 0
            self.current_question_scored = False
            self.in_quiz = False
            self.end_combat()

    def subject_name(self):
        return SUBJECTS[self.current_subject]["name"]

    def teacher_name(self):
        return SUBJECTS[self.current_subject]["teacher"]

    def get_questions(self):
        return ALL_QUESTIONS[self.current_subject]

    def start_level(self, difficulty):
        if not self.unlocked_levels.get(difficulty, False):
            return False
        self.current_difficulty = difficulty
        self.current_question_idx = 0
        self.in_quiz = True
        self.last_answer_correct = None
        self.selected_option = None
        self.current_question_scored = False
        self.end_combat()
        return True

    def get_current_question(self):
        questions = self.get_questions().get(self.current_difficulty, [])
        if 0 <= self.current_question_idx < len(questions):
            return questions[self.current_question_idx]
        return None

    def total_questions_in_level(self):
        return len(self.get_questions().get(self.current_difficulty, []))

    def begin_combat(self):
        self.in_combat = True
        self.player_hp = self.player_max_hp
        self.enemy_hp = self.enemy_max_hp
        self.combat_message = "Um Espírito da Dúvida apareceu! Acerte para atacar."

    def end_combat(self):
        self.in_combat = False
        self.player_hp = self.player_max_hp
        self.enemy_hp = self.enemy_max_hp
        self.combat_message = ""

    def answer_question(self, option_index):
        """Registra a resposta da pergunta atual.

        A pontuação de uma pergunta é concedida uma única vez: o marcador
        current_question_scored impede novas pontuações/pontuações duplicadas
        na mesma pergunta, mesmo após o uso de dicas e novas tentativas.
        Um acerto (mesmo vindo após dica/combate) é reconhecido de imediato
        e a interface avança para a próxima pergunta.
        """
        q = self.get_current_question()
        if not q:
            return False, ""

        # pergunta já concluída (pontuada): ignora novas respostas
        if self.current_question_scored:
            return False, ""

        self.selected_option = option_index
        is_correct = (option_index == q["correct_index"])
        self.last_answer_correct = is_correct

        if is_correct:
            self.current_question_scored = True
            if self.in_combat:
                # o acerto vence o Espírito da Dúvida de imediato
                self.enemy_hp = 0
                self.combat_message = "Você venceu o Espírito da Dúvida!"
            return True, q["explanation"]
        else:
            if not self.in_combat:
                self.begin_combat()
            self.player_hp = max(0, self.player_hp - 1)
            if self.player_hp <= 0:
                self.combat_message = "Você ficou sem energia! Revise e tente novamente."
            else:
                self.combat_message = "Resposta errada! O Espírito da Dúvida atacou você."
            return False, q["explanation"]

    def advance_question(self):
        """Avança para a próxima questão ou conclui o nível."""
        self.last_answer_correct = None
        self.selected_option = None
        self.current_question_scored = False
        self.current_question_idx += 1
        self.end_combat()

        if self.current_question_idx >= self.total_questions_in_level():
            self.completed_levels[self.current_difficulty] = True
            if self.current_difficulty == DIFF_FACIL:
                self.unlocked_levels[DIFF_MEDIO] = True
            elif self.current_difficulty == DIFF_MEDIO:
                self.unlocked_levels[DIFF_DIFICIL] = True
            elif self.current_difficulty == DIFF_DIFICIL:
                self.unlocked_levels[DIFF_DESAFIO] = True
            self.in_quiz = False
            return True
        return False

    def retry_question(self):
        self.last_answer_correct = None
        self.selected_option = None
        # mantém combate ativo se já estiver em combate e ambos vivos

    def is_subject_completed(self, subject=None):
        sid = subject or self.current_subject
        prog = self.progress[sid]["completed"]
        return bool(prog.get(DIFF_DIFICIL, False) or prog.get(DIFF_DESAFIO, False))

    def is_game_completed(self):
        """Compatibilidade: considera matemática concluída como vitória principal."""
        return self.is_subject_completed(SUBJECT_MATH)

    def all_subjects_completed(self):
        return all(self.is_subject_completed(sid) for sid in ALL_QUESTIONS.keys())
