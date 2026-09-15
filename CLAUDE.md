# professor — instruções para qualquer sessão

Este repositório é um **curso por tópico**, não uma coleção de resumos. O produto
não é o site: é o dono do repositório saber a matéria. Tudo o que se segue existe
para manter essa diferença visível.

## Quem lê isto e como escreve

- **Português europeu.** Tratamento por **tu**. Sem «você», sem gerúndio brasileiro.
- O aluno é **programador full-stack**: terminal, Git e código não precisam de explicação.
- Ele aprende por **mecanismos**, não por listas. Uma lição que enumera factos sem
  explicar o que se move por baixo está errada, mesmo que esteja correta.
- Nunca escrever «é simples», «basta» ou «obviamente». Se fosse óbvio não havia lição.

## O ciclo (cinco momentos, nenhum opcional)

| # | Momento | Produz | Onde |
|---|---|---|---|
| ① | Diagnóstico | Até 5 perguntas **antes** de escrever: para quê · o que já sabe · tempo/semana · prazo · como saberemos que aprendeu. Se ele disser «avança», assume e **declara** o que assumiste | `topicos/<slug>/DIAGNOSTICO.md` |
| ② | Curso | Mapa de pré-requisitos + lições | `docs/<slug>/` |
| ③ | Prática | Exercícios graduados, quiz autocorrigido, perguntas abertas | dentro de cada lição |
| ④ | Correção | Corriges resposta a resposta, dizes **que conceção errada** cada erro revela, e ajustas as lições seguintes | `topicos/<slug>/respostas/` e `correcoes/` |
| ⑤ | Revisão | `.ics` de revisão espaçada, flashcards, teste de domínio | `docs/<slug>/revisao.ics`, `flashcards.csv` |

**Como as respostas chegam.** O site não tem backend e tu não lês o `localStorage`
do browser dele. Cada lição tem um botão **«Copiar as minhas respostas»** que gera
Markdown para ele colar em `topicos/<slug>/respostas/AAAA-MM-DD.md`. É esse ficheiro
que corriges — não perguntes «o que respondeste?», lê o ficheiro.

**O progresso vive no repositório, não no browser.** `topicos/<slug>/PROGRESSO.md`:
uma linha por sessão — data · lição · resultado · o que falhou · o que muda no plano.

## As quatro fases

Cada tópico passa pelas quatro, **por ordem**, e cada uma produz algo antes de a
seguinte começar. O que cada fase encontrou fica escrito na «nota das fases» do
`index.html` do tópico — é o que prova que o processo correu.

| Fase | Nome | Tem de produzir |
|---|---|---|
| **0** | Verificar | O que já existe no repositório sobre isto — procura o **termo** *e* o que a coisa **serve para fazer**, não só o título (`INDICE.md`, `git log -S`). Que tópicos são pré-requisito ou vizinhos. Que fontes primárias existem |
| **1** | Criar | O curso completo segundo `PROCESSO.md` §«O que um curso tem de ter» |
| **2** | Aprofundar | Reler **como aluno**: que lição é rasa, que exemplo falta, que exercício é trivial, que salto não está explicado. Corrigir e **listar o que a Fase 1 errou** |
| **3** | Validar | Resolver **todos** os exercícios e o teste sem olhar para as soluções; **correr todo o código**; conferir cada afirmação contra a fonte; cruzar com os outros tópicos; correr o `validar.sh` |

🔴 **Não publicar um curso que não passou a Fase 3.** Um curso a meio leva a etiqueta
*🚧 em construção* no catálogo `docs/index.html`.

## As regras de casa

Estão inteiras em `PROCESSO.md`. As que mais falham:

- 🔴 **Correr o que está escrito, em vez de o julgar.** Código, comandos, contas e soluções.
- 🔴 **Nunca escrever «isto não existe» sem procurar**, nem apresentar como novidade o que já está noutro tópico.
- **Abrir a fonte antes de repetir uma afirmação.** Se não conseguires verificar, escreve
  que não verificaste. Não inventes fontes, DOIs, páginas nem citações.
- **Corrigir num sítio é corrigir em todos.**
- **Correções à vista**: ⚠️ *corrigido a AAAA-MM-DD — dizia X, está Y, porque Z*. Nunca em silêncio.
- **Antes de uma edição destrutiva em massa**, cópia em `arquivo/AAAA-MM-DD-motivo/` com `LEIA-ME.txt`.
- **Registo de falhas** no fim do `PROCESSO.md`: uma linha por erro de processo apanhado.

## Antes de cada commit que toca em `docs/`

```bash
./validar.sh
```

Falha = não se faz commit. Um validador com falsos positivos não se volta a correr:
**se der ruído, corrige o validador primeiro**, não silencies o aviso.

## As páginas

- **HTML autocontido**: cada página abre sozinha do disco, sem build, sem rede, sem CDN.
  CSS e JS inline. Ver `DECISOES.md` D-003 e D-005 (como o CSS se mantém sincronizado
  sem deixar de ser inline).
- Tema claro/escuro, barra lateral colapsável, tabelas roláveis por teclado, caixas
  ⚠️ / 🔴 / ✅ / ⭐ com significado fixo.
- `localStorage` só para conveniência, sempre em `try/catch`, e a página funciona sem ele.
- **Tem de funcionar a 400 px** — é no telemóvel que ele estuda.
- WCAG AA nos dois temas; links sublinhados no corpo do texto; `<summary>` sem `<a>` dentro.
- Partir sempre de `modelo/`, nunca de uma página de outro tópico (copia-se o erro junto).

## A pedagogia é evidência, não gosto

Prática de recuperação · repetição espaçada · intercalação · exemplo trabalhado e o seu
desvanecimento · dificuldades desejáveis · elaboração. Estão citadas em `docs/metodo.html`.

🔴 **Não usar o que não tem evidência** — «estilos de aprendizagem» incluídos.
Se uma escolha for convenção e não evidência, **dizer que é convenção**.

## Restrições

- 🔴 **O repositório é público.** Nada de morada, terra, idade, empregador, inventário,
  finanças ou saúde — nem em `topicos/`, que também é público. Se um tópico precisar de
  contexto pessoal, **perguntar** se vai para um ficheiro no `.gitignore`
  (`topicos/<slug>/PRIVADO.md` já está ignorado).
- Não copiar material com direitos de autor (capítulos, exercícios de livros, transcrições).
  Resumir por palavras próprias e remeter para a fonte.
- 🔴 **Pedir antes de**: criar repositório remoto, ativar o Pages, criar segredos,
  instalar Actions que chamem APIs pagas, ou `push --force`.

## Commits

Em português. O título diz **o que se descobriu**, não o que se mexeu:

> `Recursão ganhou tópico próprio — e o exemplo do factorial escondia o caso base que é o erro mais comum`

O corpo lista *Ficheiros novos* e *Ficheiros alterados*, uma linha cada.

## Os comandos

`.claude/commands/`: `aprender` · `corrigir` · `rever` · `aprofundar`.
Cada um está escrito para uma sessão que não sabe nada desta conversa. Se mudares o
processo, **atualiza-os** — são eles que o executam.
