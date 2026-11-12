# O Desafio Escolar 🎓📐

> **FUPAC / UNIPAC - Fundação Presidente Antônio Carlos**  
> **Curso:** Ciência da Computação  
> **Disciplina:** Programação Para Jogos  
> **Professor:** Rodrigo Fernandes  
> **Equipe Pecê Gamer:**  
> - Angelo Teixeira  
> - Daniel Calixto Lima  
> - Hamilton Ferreira  
> - João Alberto  
> - Lucas Eduardo  
> - Lucas Nogueira  
> - Matheus Souza Lima  

---

## 🎮 Sobre o Jogo

**O Desafio Escolar** é um jogo 2D educativo com elementos de RPG e aventura em visão *Top-Down*. O jogador controla um novo estudante recém-matriculado cujo grande sonho é ser o melhor aluno da escola.

Para isso, ele deve explorar os corredores e salas da instituição. Neste momento inicial, a **Sala de Matemática** está aberta e o professor aguarda para aplicar avaliações progressivas de conhecimento. As demais salas temáticas (**História**, **Geografia** e **Biologia**) exibem placas indicando que serão inauguradas em breve.

### 🌟 Mecânica de Progressão de Quiz
O jogador inicia obrigatoriamente no nível **Fácil**. Ao responder corretamente aos problemas matemáticos propostos pelo professor, o cadeado do nível **Médio** se abre; completando o Médio, o nível **Difícil** é desbloqueado. Ao vencer o nível Difícil, o jogador alcança a condição de vitória e recebe seu **Certificado de Excelência Acadêmica**!

Errar uma questão não impõe *Game Over* punitivo: o professor apresenta uma explicação didática e convida o estudante a *"Estudar mais um pouco"* e tentar novamente.

---

## 🎨 Direção de Arte

O visual segue o estilo **pixel-art vibrante** dos RPGs top-down clássicos. Todos os
sprites e cenários são **gerados proceduralmente em tempo de execução** (nenhum arquivo
de imagem é carregado do disco), seguindo três regras de estilo:

- **Contorno escuro** de 1px em personagens e objetos, destacando as silhuetas do fundo
- **Sombreamento em três tons** (luz / base / sombra) para dar volume a móveis e cenário
- **Sombra elíptica projetada** no chão sob personagens e mobiliário, criando profundidade

O ambiente escolar usa uma paleta quente e saturada: piso cerâmico creme com passadeira
terracota no corredor, tacos de madeira na sala, paredes claras com lambril verde-água e
janelas com vista para o exterior.

---

## 🏆 Modo Competição

No menu inicial, escolha **Modo Competição** para o formato de evento entre duas equipes:

- Cada equipe cadastra um nome no jogo e tem **5 representantes** (escolhidos presencialmente, sem cadastro de integrantes)
- Os representantes **andam pela escola como no modo clássico**: antes de cada rodada digita-se o nome do representante; fale com o professor (`E`/`Espaço`) para iniciar os desafios
- Participa **um representante por vez**, que joga com **3 corações** (painel de vida no **canto inferior esquerdo**, sempre visível); ao perder a vida ou concluir todos os níveis, entra um representante da **outra equipe**
- Cada nível tem **5 perguntas com 4 alternativas** (A-D / 1-4) e cada professor **pergunta apenas o tema pelo qual é responsável** (Matemática, História, Geografia ou Biologia); o nível só é concluído **após responder as 5 perguntas**; há a opção **"Responder depois"** (a pergunta volta ao fim do nível)
- Errar drena os corações; acertar soma pontos (10/15/20/30 conforme o nível), concedidos **uma única vez por pergunta** — mesmo após usar a dica, o acerto avança imediatamente
- Ao fim de cada rodada, uma **tabela de andamento** mostra todas as rodadas disputadas (equipe, representante, nível, pontos e resultado)
- O jogo entra em **tela cheia** automaticamente (alterne a qualquer momento com `F11`)
- **Placar comparativo** durante todo o evento; vence a equipe que **avançar mais longe**, com a **pontuação como desempate**

---

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3.13+
- **Game Engine & Loop:** [Pygame 2.6.1](https://www.pygame.org/) (janela, áudio, inputs e fontes)
- **Pipeline Gráfico:** [PyOpenGL 3.1.10](https://pyopengl.sourceforge.net/) (renderização 2D acelerada por hardware via projeção ortográfica, blending e texturas)
- **Efeitos Sonoros:** Sintetizador procedural com `pygame.mixer` (sem dependência de arquivos externos)

---

## 🕹️ Controles do Jogo

| Ação | Tecla(s) / Controle |
|---|---|
| **Movimentação** | `W`, `A`, `S`, `D` ou `Setas Direcionais` |
| **Interagir / Ação** | `E` ou `Barra de Espaço` |
| **Opções de Diálogo** | `W` / `S` ou `Setas Cima / Baixo` e `Enter` / `E` |
| **Alternativas do Quiz** | `1`, `2`, `3`, `4` ou `A`, `B`, `C`, `D` ou **Clique do Mouse** |
| **Responder depois (Competição)** | `R` ou **Clique do Mouse** |
| **Música (pausar/retomar)** | `M` |
| **Tela Cheia** | `F11` |
| **Avançar / Tentar Novamente** | `Enter` ou `Espaço` |
| **Fechar / Voltar** | `ESC` |

---

## 📂 Estrutura do Projeto

```text
desafioEscolar/
│
├── main.py                # Ponto de entrada do jogo e máquina de estados
├── requirements.txt       # Dependências do projeto (Pygame, PyOpenGL)
├── music/tema.mp3         # Música de fundo do jogo (toca em loop)
│
├── game/                  # Pacote principal com toda a lógica e engine do jogo
│   ├── config.py          # Resolução (960x540), paleta de cores, constantes e dificuldades
│   ├── gl_renderer.py     # Engine gráfica 2D em PyOpenGL (viewport, orto, texturas, texto,
│   │                      #   painéis arredondados com sombra, gradientes e círculos)
│   ├── assets.py          # Gerador procedural de sprites, tiles e ícones em pixel-art
│   ├── world.py           # Mapa escolar (corredor, sala de aula, colisões AABB)
│   ├── entities.py        # Entidades: Jogador (Player), Professor Roberto (NPC) e Objetos
│   ├── quiz_data.py       # Banco de questões matemáticas (Fácil, Médio, Difícil)
│   ├── ui.py              # Interface gráfica (tela de nome, HUD, diálogos, quiz e vitória)
│   ├── audio.py           # Efeitos sonoros sintetizados (passos, diálogos, acertos, fanfarra)
│   ├── competition.py     # Modo Competição (equipes, revezamento, vidas e níveis)
│   ├── competition_data.py# Banco de questões da competição (5 perguntas/4 alternativas por nível)
│   └── ui_competition.py  # Telas do Modo Competição (menu, cadastro, quiz, placar e resultado)
│
└── tests/
    └── test_game.py       # Suíte de testes automatizados
```

---

## ⚡ Como Executar

### 1. Pré-requisitos
Certifique-se de ter o Python instalado. Caso ainda não tenha as dependências:

```bash
pip install -r requirements.txt
```

### 2. Iniciar o Jogo
Execute:

```bash
python main.py
```

### 3. Executar os Testes Automatizados
Para validar todos os estados, colisões e a progressão das questões matematicamente:

```bash
python tests/test_game.py
```