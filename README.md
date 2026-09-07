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
| **Avançar / Tentar Novamente** | `Enter` ou `Espaço` |
| **Fechar / Voltar** | `ESC` |

---

## 📂 Estrutura do Projeto

```text
desafioEscolar/
│
├── main.py                # Ponto de entrada do jogo e máquina de estados
├── requirements.txt       # Dependências do projeto (Pygame, PyOpenGL)
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
│   └── audio.py           # Efeitos sonoros sintetizados (passos, diálogos, acertos, fanfarra)
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