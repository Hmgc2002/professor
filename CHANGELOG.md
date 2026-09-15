# Registo de alterações

O formato é uma entrada por sessão de trabalho, com data. O que muda o que eu
consigo aprender fica no topo da entrada; o que muda só a mecânica fica no fim.

## 2026-09-15 — A pesquisa passou a procurar dentro das lições

**Corrigido**

- A pesquisa do catálogo filtrava cartões com uma lista de palavras-chave escrita à mão.
  Testada com 21 termos reais, falhava em **8**: `bitmap`, `vacuum`, `heap fetches`,
  `work_mem`, `visibility map`, `prefixo`, `correlação`, `estatísticas`.
- Passa a usar um índice **gerado do conteúdo** das páginas pelo `sincronizar.py`
  (111 secções, ~85 kB inline), com relevância por **onde** o termo aparece e resultados
  agrupados por página, com ligação direta à secção.
- Limite declarado em D-015: acima de ~40 páginas indexadas, o índice inline deixa de caber
  e a decisão tem de ser revista.

## 2026-09-15 — Repositório criado e publicado

**No ar:** <https://hmgc2002.github.io/professor/> (GitHub Pages, `main:/docs`)

Confirmado, não assumido: as 15 páginas e ficheiros respondem 200, com os tipos certos
(`text/calendar` para o `.ics`, `text/csv` para os flashcards). O quiz corrige no site publicado,
as soluções estão fechadas, e a página não carrega **nenhum** recurso externo — zero pedidos fora
da própria origem, que é o que a decisão D-003 exige.

**Novo**

- Esqueleto completo: `CLAUDE.md`, `PROCESSO.md`, `DECISOES.md`, `INDICE.md`.
- `modelo/` com as três páginas-modelo (tópico, lição, folha), tema claro/escuro,
  barra lateral colapsável e quiz funcional sem rede.
- Validadores: `validar.py` (âncoras, ligações, `<details>`, quiz, índice),
  `validar_a11y.mjs` (axe-core nos dois temas), `validar.sh` (orquestra e inclui `tidy`).
- Quatro comandos em `.claude/commands/`: `aprender`, `corrigir`, `rever`, `aprofundar`.
- Tópico piloto **Índices B-tree em SQL**: diagnóstico, 7 lições, folha imprimível,
  teste de domínio, 40 flashcards e calendário de revisão espaçada.
