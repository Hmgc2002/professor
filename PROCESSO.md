# PROCESSO

Como se faz um curso aqui. Herdado do método do `compendio` (repositório privado,
não publicado) e adaptado de «documentar» para «ensinar».

---

## As quatro fases

Por ordem. Cada uma produz algo antes de a seguinte começar. Saltar a Fase 0 porque
«o repositório é pequeno» é exatamente como se cria o segundo tópico que repete o primeiro.

### Fase 0 — Verificar

Antes de escrever uma linha:

1. **Procurar o termo** no repositório: `grep -ri "<termo>" docs/ topicos/`.
2. **Procurar o que a coisa serve para fazer**, não só o nome. Quem procura «B-tree»
   não encontra a lição que se chama «porque é que a tua query está lenta». Procurar
   por sintoma, por verbo, por sinónimo.
3. `grep "<termo>" INDICE.md` — o índice tem uma linha por cabeçalho com `id` de todas as páginas.
4. `git log -S "<termo>" --oneline` — apanha o que foi escrito e depois removido, e diz **porquê**.
5. Identificar **pré-requisitos** (tópicos que têm de vir antes) e **vizinhos**
   (tópicos que tocam neste e onde é preciso declarar a fronteira).
6. Localizar **fontes primárias**: documentação oficial, especificação, artigo original,
   código-fonte. Um blogue é fonte secundária e diz-se que é.

**Produz:** a secção «Fase 0» da nota das fases, com o que se procurou e o que se encontrou.
Se não se encontrou nada, escreve-se *o que se procurou* — «não existe» sem lista de
pesquisas não é uma verificação, é um palpite.

### Fase 1 — Criar

O curso completo segundo a secção «O que um curso tem de ter», abaixo.

### Fase 2 — Aprofundar

Reler **como aluno que não sabe a matéria**, não como autor que já a escreveu. Perguntar:

- Que lição explica *o quê* mas não o *porquê*?
- Que passo do exemplo trabalhado dá um salto que só faz sentido para quem já sabe?
- Que exercício se resolve sem perceber nada (copiar o padrão do exemplo acima)?
- Que erro comum é mesmo comum, e qual é que eu inventei por simetria?
- Que afirmação eu escrevi de memória sem abrir a fonte?

**Produz:** as correções **e a lista do que a Fase 1 errou**, escrita na nota das fases.
Uma Fase 2 que não encontrou nada não correu — voltar a correr.

### Fase 3 — Validar

1. **Resolver todos os exercícios e o teste** sem olhar para as soluções, e comparar.
   Uma solução que não bate é um bug na solução até prova em contrário.
2. **Correr todo o código.** Todo. Os exemplos, os exercícios, as soluções, os comandos.
3. **Conferir cada afirmação factual** contra a fonte aberta nesse momento.
4. **Cruzar com os outros tópicos**: contradições (uma tem de ceder e a outra regista-se),
   sobreposições (remissão com fronteira declarada).
5. `./validar.sh` limpo.

**Produz:** a secção «Fase 3» da nota das fases, com o que se correu e o que falhou.

---

## O que um curso tem de ter

### `docs/<slug>/index.html` — a entrada do tópico

- **O que vais conseguir fazer no fim** — objetivos verificáveis: «implementar X»,
  «explicar porque Y», «resolver Z sem consultar». Nunca «compreender X»: não se verifica.
- **O que este curso não é** — a fronteira. Se outro tópico já é dono de uma parte,
  remete-se para lá em vez de repetir.
- **O que assumi** — cada pressuposto do diagnóstico, sinalizado, com **o que muda se
  estiver errado**. Um pressuposto sem consequência declarada não é um pressuposto, é decoração.
- **O mapa** — pré-requisitos e ordem das lições, como diagrama. SVG inline (ou
  `<pre class="mermaid">` só se funcionar sem CDN, o que hoje não acontece → **SVG**).
  🔴 Um pré-requisito que o aluno não tem vira **lição 0**, não nota de rodapé.
- **O plano no tempo** — lições distribuídas pelas semanas que ele disse ter.
- **Nota das fases** — o que cada fase encontrou e corrigiu.

### `docs/<slug>/NN-<nome>.html` — cada lição

Por esta ordem e com estes títulos:

| # | Secção | O que é, e o erro que se comete |
|---|---|---|
| 1 | **Objetivo** | Uma frase verificável. Não «introdução a X» |
| 2 | **Recuperar** | 2–3 perguntas sobre lições anteriores, **respondidas antes de ler**. É prática de recuperação: o esforço de puxar da memória é o que consolida, e por isso as respostas ficam escondidas |
| 3 | **O mecanismo** | A explicação. **Porquê antes de como.** Diagrama quando a coisa tem partes que se movem |
| 4 | **Exemplo trabalhado** | Um problema resolvido passo a passo com **o raciocínio de cada passo à vista** — não só o que se fez, o porquê de ter sido esse |
| 5 | **Exemplo com lacunas** | O mesmo tipo de problema com passos em branco (desvanecimento do exemplo trabalhado) |
| 6 | **Erros comuns** | As conceções erradas típicas **deste** assunto e como se reconhecem |
| 7 | **Praticar** | Do mais fácil ao mais difícil. Soluções em `<details>` **fechado por defeito**. Se o tópico é técnico, pelo menos um exercício é código que corre |
| 8 | **Quiz** | 5–10 perguntas, correção imediata, e explicação de **cada** opção errada — não só da certa |
| 9 | **Explica por palavras tuas** | Pergunta aberta (técnica de Feynman). Vai para a entrega |
| 10 | **Resumo** | O mínimo a reter, em 5 linhas |
| 11 | **Fontes** | 🌐 *Verificado a AAAA-MM-DD*. Primárias sempre que existam. Livros/cursos/vídeos com o **porquê** de cada um e **o que saltar** |

### No fim do tópico

- **`folha.html`** — imprimível (A4, `@media print`), só o que se consulta.
- **`teste.html`** — teste de domínio **intercalado** (perguntas fora da ordem das lições),
  sem soluções à vista; a entrega vai para correção.
- **`flashcards.csv`** — `frente;verso;etiqueta`, importável no Anki.
- **`revisao.ics`** — eventos a **+1, +3, +7, +21 e +60 dias** da conclusão, cada um com a
  lista do que rever e o caminho da página. `VALARM`, `DESCRIPTION` com passos, `UID` estável.
- **Projeto** — quando o tópico o permitir: uma coisa real que obriga a usar tudo.

### A pedagogia é evidência, não gosto

As escolhas acima estão justificadas e citadas em `docs/metodo.html`: prática de recuperação,
repetição espaçada, intercalação, efeito do exemplo trabalhado e o seu desvanecimento,
dificuldades desejáveis, elaboração.

🔴 **Não usar o que não tem evidência** — «estilos de aprendizagem» (visual/auditivo/cinestésico)
é a mais popular e está refutada; não aparece aqui.
Se uma escolha for **convenção** e não evidência (a ordem das secções, os intervalos exatos
do `.ics`), **dizer que é convenção**.

---

## As regras de casa

### 🔴 Correr o que está escrito, em vez de o julgar

Código, comandos, contas e soluções. Ler um `SELECT` e concluir que está certo não é
verificar. No `compendio`, **seis de sete** erros de uma sessão só foram apanhados a correr.

### 🔴 Nunca escrever «isto não existe» sem procurar

E nunca apresentar como novidade o que já está noutro tópico. Ver Fase 0.

### Abrir a fonte antes de repetir uma afirmação

Se não conseguires verificar, **escreve que não verificaste** — é informação, não vergonha.
🔴 Não inventes fontes, DOIs, números de página nem citações. Um número que não vem da
fonte aberta é um número que não se escreve.

### Corrigir num sítio é corrigir em todos

Uma definição que muda procura-se no repositório inteiro: `grep -ri` em `docs/` e `topicos/`,
mais os flashcards e a folha.

### Correções à vista

Quando uma lição publicada estava errada, a correção **fica marcada**:

> ⚠️ **Corrigido a 2026-09-15** — dizia «um índice sobre `(a, b)` serve uma query que filtra só por `b`»,
> está «não serve»; porque a B-tree ordena primeiro por `a` e sem `a` não há intervalo contíguo para percorrer.

Não se apaga em silêncio. O aluno que leu a versão errada precisa de saber que leu.

### Antes de uma edição destrutiva em massa

Cópia em `arquivo/AAAA-MM-DD-motivo/` com um `LEIA-ME.txt` que diz o que se arquivou e porquê.

### O validador é para correr

Um validador com falsos positivos não se volta a correr. **Se der ruído, corrige o
validador primeiro** — nunca acrescentes uma exceção para calar um aviso verdadeiro.

---

## A validação (`./validar.sh`)

Corre antes de cada commit que toca em `docs/`.

| # | Verificação | Armadilha já conhecida |
|---|---|---|
| 1 | Âncoras órfãs e `id` duplicados | **Ignorar** o que está dentro de `<pre>`, `<code>` e comentários. O validador do `compendio` acusou-se a si próprio três vezes antes de aprender isto |
| 2 | Ligações entre páginas | Ficheiro **e** âncora têm de existir do outro lado |
| 3 | HTML mal formado | `tidy` do Homebrew (`/opt/homebrew/bin/tidy`), **não** o `/usr/bin/tidy` — esse é de 2006 e não conhece HTML5 |
| 4 | Acessibilidade | `axe-core` nos **dois temas**, lendo só `violations` (nunca `incomplete`, que é ruído) |
| 5 | Pedagogia | Todos os `<details>` de solução fechados por defeito; nenhuma opção de quiz sem explicação |
| 6 | `INDICE.md` | Regenerado |

---

## Registo de falhas

Uma linha por erro de **processo** apanhado — não por erro de conteúdo. É o que impede
a quinta repetição do mesmo padrão. Acrescenta-se no fim, nunca se reescreve o que está acima.

| Data | Tópico | O que falhou | O que mudou |
|---|---|---|---|
| 2026-09-15 | (infraestrutura) | O primeiro `validar.py` marcou como âncora órfã o texto `#id` que aparecia dentro de um `<code>` num exemplo do próprio modelo — a armadilha que o `compendio` já tinha documentado e que eu reescrevi na mesma | O extrator passou a remover `<pre>`, `<code>` e comentários **antes** de procurar, e o modelo ficou com um exemplo dessa forma lá dentro, de propósito, para o caso não voltar a passar despercebido |
| 2026-09-15 | indices-btree-sql | A Fase 1 escreveu «o Postgres não usa o índice quando a query devolve mais de ~20% das linhas» com um número redondo que eu não tirei de lado nenhum | A Fase 3 substituiu o número por uma explicação do mecanismo (custo relativo, `random_page_cost`) e por uma demonstração que o aluno corre para encontrar **o limiar da máquina dele**. Regra reforçada: número redondo sem fonte é sinal de invenção |
