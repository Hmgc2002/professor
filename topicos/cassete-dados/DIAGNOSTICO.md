# Diagnóstico — A cassete como memória de computador

**Data:** 2026-09-16 · **Slug:** `cassete-dados` · **Curso:** [docs/cassete-dados/](../../docs/cassete-dados/index.html)

> 🔴 Este ficheiro é público. Só tem aqui informação técnica sobre o ponto de partida e o ritmo.
> Nada pessoal foi pedido nem é preciso para ensinar isto. Se algum tópico futuro precisar de
> contexto pessoal, esse contexto vai para `topicos/<slug>/PRIVADO.md`, que está no `.gitignore`.

---

## O pedido

O tópico entrou como um URL: `https://en.wikipedia.org/wiki/Cassette_tape`. Um artigo de
enciclopédia não é um curso — é uma lista de factos sobre um objeto. A primeira pergunta do
diagnóstico serviu para escolher **por que porta** se entra no objeto, porque a resposta muda
tudo o que vem a seguir.

---

## As perguntas e as respostas

### 1. Para que precisas disto?

**Armazenamento de dados** — a cassete como periférico de computador.

**O que isso decide:** o curso não é sobre música, nem sobre restauro, nem sobre história do
formato. É sobre um problema de engenharia: *como é que se põem bytes num meio analógico que não
grava corrente contínua, tem ruído de fundo, corta os agudos e nem sequer anda sempre à mesma
velocidade* — e como é que se voltam a tirar de lá.

A física entra toda, mas entra **ao serviço disso**. Cada facto sobre magnetismo que está no curso
está lá porque explica uma decisão do formato de dados. O que não explica nada ficou de fora, e a
fronteira diz onde.

### 2. De onde partes?

**Zero em todas as frentes que perguntei**, e foi respondido sem amaciar:

| Perguntei | Resposta |
|---|---|
| Histerese magnética, domínio, coercividade | Não |
| SNR, resposta em frequência, distorção harmónica | Não |
| Filtro passa-alto/passa-baixo, companding | Não |
| Amostragem, Nyquist, quantização, FSK | Não |
| Prática com cassetes (gravar, alinhar, limpar) | Não |

**O que isso decide:** 🔴 **há duas lições 0**, e nenhuma é opcional.

- A **lição 0** é sobre som, amostragem e o ficheiro `.wav`. Vem primeiro por ser a que está mais
  perto do que já sabes: a entrada do projeto é um ficheiro, e um ficheiro é uma coisa que sabes
  abrir. Começar pela física seria começar pelo mais longe.
- A **lição 1** é sobre magnetismo. Sem ela, «bias», «saturação» e «ruído da fita» são palavras
  decoradas.

Em contrapartida, **não há lição nenhuma sobre programar**: assume-se Python lido e escrito,
terminal, ficheiros binários, deslocamentos de bits e XOR. Se algum destes falhar, diz.

### 3. Que ritmo?

**Até 1h por dia, «o que for necessário».**

**O que isso decide:** lições que cabem numa sessão de ~1h incluindo os exercícios, e 8 lições
distribuídas por ~4 semanas a duas por semana. Há folga — e a folga vai para o projeto, que é
onde se percebe se aprendeste.

⚠️ «O que for necessário» é generoso mas não é infinito, e um curso longo perde-se por volta da
quinta semana. Por isso o curso tem **núcleo e extensão** (ver abaixo): há um ponto de chegada
honesto antes do fim.

### 4. Até quando?

**Sem prazo.**

**O que isso decide:** a revisão espaçada deixa de ser acessório. Sem prazo, nada obriga a voltar,
e o que não se revê perde-se. O `revisao.ics` é a peça do curso que menos parece importar e mais
importa.

### 5. Como saberemos que aprendeste?

**Código que corre**, escolhido de entre quatro opções:

> Escreves um programa que lê um `.wav` de uma fita de ZX Spectrum e devolve **os bytes certos** —
> verificável contra o ficheiro original, byte a byte.

**O que isso decide:** é o critério mais duro dos quatro, porque não há como te enganares a ti
próprio: ou os bytes batem ou não batem. Decide também o `teste.html` (que tem de medir
diagnóstico, não recordação) e o exercício final de cada lição a partir da 4.

---

## A tensão que as respostas criam, e como a resolvi

**Partir de zero em física e em sinal** com um **projeto de programação no fim** é um vão grande.
A tentação é encurtar a física para chegar depressa ao código. Isso produz um descodificador que
funciona e um aluno que não sabe porquê — exatamente o que este repositório existe para não fazer.

**Resolução — núcleo e extensão:**

| | Lições | Semanas | O que tens no fim |
|---|---|---|---|
| **Núcleo** | 0 · 1 · 2 · 3 · 4 | ~2–3 | Sabes o que a fita faz ao sinal e porque é que *nenhum* esquema ingénuo de gravar bits funciona. Já consegues explicar o formato de qualquer fita de computador que te apareça à frente |
| **Extensão** | 5 · 6 · 7 | ~1–2 | O formato do Spectrum ao pormenor, o descodificador a funcionar, e porque é que a fita morreu |

Parar no fim do núcleo deixa-te a saber a matéria. É a extensão que produz o **critério de
sucesso que escolheste**, por isso não é dispensável — é adiável.

---

## O que assumi (e o que muda se estiver errado)

| Assumi | Porquê | Se estiver errado |
|---|---|---|
| **Python 3**, lido e escrito | Perfil declarado: programador full-stack. Todo o código do curso é só biblioteca padrão, sem `pip install` | Se preferires outra linguagem, o curso mantém-se: o algoritmo está escrito em prosa antes de estar em código. Só as soluções mudavam |
| **Não tens leitor de cassetes nem cassetes** | Disseste que nunca lhes mexeste | Nada muda no curso, mas ganhavas um exercício extra a sério. O áudio das fitas é **gerado pelo curso** a partir de um `.tap`, precisamente para não depender de hardware |
| **Windows** como máquina principal | O repositório está em `C:\Users\…` | Pouco: o código é portável. O que muda são detalhes de consola (a lição 6 traz a armadilha da codificação `cp1252`, que apanhei a correr) |
| Queres saber **porquê**, não só fazer funcionar | É o que este repositório assume de todos os tópicos | Se só quisesses o descodificador, as lições 1 a 3 seriam um apêndice em vez do núcleo |
| **ZX Spectrum** e não C64 ou Kansas City como formato do projeto | É o formato melhor documentado, com a ROM desmontada e publicada, e o mais fácil de verificar byte a byte | O mecanismo é o mesmo. A lição 4 ensina o Kansas City **por contraste**, por isso terias a base para atacar outro formato sozinho |
| Não precisas de **teoria de códigos corretores de erros** | O formato do Spectrum tem só um XOR de paridade: deteta, não corrige | Passava a faltar um tópico inteiro, não uma lição. Ficaria `deteccao-e-correccao-de-erros`, com fronteira declarada |

---

## Estado

| | |
|---|---|
| Diagnóstico | ✅ 2026-09-16 |
| Curso publicado | ✅ 2026-09-16 (passou a Fase 3) |
| Primeira entrega em `respostas/` | ⬜ ainda nenhuma |

A última linha é a que conta. Enquanto estiver vazia, isto é um site — não é aprendizagem.
