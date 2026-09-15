# Registo de alterações

O formato é uma entrada por sessão de trabalho, com data. O que muda o que eu
consigo aprender fica no topo da entrada; o que muda só a mecânica fica no fim.

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
