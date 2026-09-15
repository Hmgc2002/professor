# Diagnóstico — Índices B-tree em SQL

**Data:** 2026-09-15 · **Slug:** `indices-btree-sql` · **Curso:** [docs/indices-btree-sql/](../../docs/indices-btree-sql/index.html)

> 🔴 Este ficheiro é público. Está escrito sabendo disso: só há aqui informação técnica sobre o
> ponto de partida e o ritmo. Se algum tópico futuro precisar de contexto pessoal para ser bem
> ensinado, esse contexto vai para `topicos/<slug>/PRIVADO.md`, que está no `.gitignore`.

---

## As perguntas e as respostas

### 1. Para que precisas disto?

**«As três coisas»** — diagnosticar queries lentas, desenhar esquemas de raiz, e os fundamentos.

**O que isso decide:** o curso não pode ser só «como ler um EXPLAIN» nem só «como funciona uma
B-tree». Tem de ir do mecanismo (porque é logarítmico, o que é uma página) até ao diagnóstico
(este plano diz-me o quê) e ao desenho (que índices criar antes de haver problema, e o que eles
custam nas escritas).

### 2. Que base de dados vais ter à frente?

**Postgres como principal, SQLite como alternativa.**

**O que isso decide:** as explicações e os planos de execução são de Postgres, que tem a melhor
instrumentação para diagnóstico (`EXPLAIN (ANALYZE, BUFFERS)`). Cada exercício com código traz a
variante SQLite, porque o ritmo escolhido é de sessões curtas e nem sempre vais ter um servidor à
mão. Onde os dois divergem em mecanismo — e divergem em mais do que sintaxe — está dito.

### 3. De onde partes?

**«SQL sólido, índices quase zero»** — JOINs e agregações sem esforço; índice é caixa preta.

**O que isso decide:** 🔴 há **lição 0**, e não é opcional. Sem a noção de página, de I/O e do que
é que o planeador está a tentar minimizar, tudo o resto vira regras decoradas. Em contrapartida,
não há lição nenhuma sobre sintaxe de SQL: parte-se do princípio que escreves a query, o problema
é ela ser lenta.

### 4. Que ritmo?

**~1h/semana, sem prazo.**

**O que isso decide:** lições que cabem numa hora, incluindo os exercícios. E, sobretudo:
a **revisão espaçada passa a ser a peça central**, não um acessório. Num ritmo lento, o que
determina se aprendes não é a velocidade a que lês — é se revês. O `revisao.ics` é a parte do
curso que menos parece importar e mais importa.

### 5. Como saberemos que aprendeste?

⚠️ **Não perguntei — assumi.** Eram cinco perguntas e usei as quatro anteriores. O critério
assumido é este:

> Dado um esquema, uma query e o seu plano de execução, consegues dizer **que índice falta (ou
> qual está a mais), porquê, e o que esperas que mude no plano** — sem consultar as lições. E
> consegues **medir** que mudou.

Se este critério não é o teu, diz — é o que decide o `teste.html` e vários exercícios.

---

## A tensão que as respostas criam, e como a resolvi

**«As três coisas»** pede ~7 lições. **~1h/semana** torna isso ~8 semanas seguidas, e o abandono
em cursos longos não acontece no fim: acontece por volta da quinta semana, quando o fim ainda não
se vê.

**Resolução — núcleo e extensão** (registado como decisão D-011):

| | Lições | Semanas | O que tens no fim |
|---|---|---|---|
| **Núcleo** | 0 · 1 · 2 · 3 | ~4 | Já consegues diagnosticar: ler um plano, perceber porque é que um índice foi ou não usado, e corrigir o caso comum |
| **Extensão** | 4 · 5 · 6 | ~3–4 | Índices compostos, diagnóstico de casos difíceis, e o custo do outro lado (escritas, espaço, quando **não** indexar) |

O núcleo é um ponto de chegada honesto: parar aí deixa-te capaz de resolver o caso mais frequente.
A extensão é onde está o desenho de esquemas, que foi uma das três coisas que pediste — por isso
não é «opcional» no sentido de dispensável; é adiável.

---

## O que assumi (e o que muda se estiver errado)

| Assumi | Porquê | Se estiver errado |
|---|---|---|
| O critério de sucesso da pergunta 5 | Não cheguei a perguntar | Muda o `teste.html` e os exercícios de diagnóstico das lições 3 e 5 |
| Postgres 17 | É a versão que instalei para correr e conferir tudo | Quase nada: o mecanismo é o mesmo há muitas versões. O que pode mudar é a formatação do `EXPLAIN` e detalhes de `VACUUM`/visibility map |
| Sabes usar um terminal e criar uma base de dados de treino | Perfil declarado: programador full-stack | A lição 0 precisaria de uma secção de preparação do ambiente |
| Não precisas de índices que não sejam B-tree (GIN, GiST, BRIN, hash) | O diagnóstico não mencionou pesquisa textual, JSON nem geometria | Passa a faltar um tópico inteiro — não uma lição. Ficaria `indices-nao-btree-sql`, com fronteira declarada |
| Trabalhas com tabelas até alguns milhões de linhas | É onde os índices B-tree decidem quase tudo | Acima disso entram particionamento e outras estratégias, que este curso **não** cobre e diz que não cobre |

---

## Estado

| | |
|---|---|
| Diagnóstico | ✅ 2026-09-15 |
| Curso publicado | ✅ 2026-09-15 (passou a Fase 3) |
| Primeira entrega em `respostas/` | ⬜ ainda nenhuma |

A última linha é a que conta. Enquanto estiver vazia, isto é um site — não é aprendizagem.
