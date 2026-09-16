# Progresso — O almanaque

Uma linha por sessão. Preenche-se com `/corrigir almanaque` depois de cada entrega,
nunca à mão a partir da memória.

| Data | Lição | Resultado | O que falhou | O que muda no plano |
|---|---|---|---|---|
| 2026-09-16 | — | curso criado e validado (passou as quatro fases) | — | Começar pela lição 0. Importar o `revisao.ics` antes da primeira sessão — as datas assumem o núcleo concluído a 2026-11-25. 🔴 Descarregar o PDF do *Nautical Almanac* de [thenauticalalmanac.com](https://thenauticalalmanac.com) antes da lição 6: a partir daí é preciso |

## A ordem

O mapa está em [`docs/almanaque/index.html`](../../docs/almanaque/index.html#mapa).
Marca aqui o que está feito:

| # | Lição | Estado | Feito |
|---|---|---|---|
| 0 | A esfera celeste | núcleo | ⬜ |
| 1 | O que é um almanaque | núcleo | ⬜ |
| 2 | O tempo | núcleo | ⬜ |
| 3 | O Sol | núcleo | ⬜ |
| 4 | Nascer, pôr e crepúsculos | núcleo | ⬜ |
| 5 | A Lua | núcleo | ⬜ |
| 6 | Ler as tábuas | núcleo | ⬜ |
| 7 | Reduzir uma altura | núcleo | ⬜ |
| 8 | As marés | **extensão** | ⬜ |
| 9 | O teu almanaque (projeto) | núcleo | ⬜ |
| — | Teste de domínio | — | ⬜ |

## O que é preciso arranjar

| | Estado | Quando é preciso |
|---|---|---|
| PDF do *Nautical Almanac* de um ano (grátis) | ⬜ | 🔴 **Lição 6** — sem ele não há E3 nas lições 6 e 9 |
| Python 3 (qualquer versão recente) | ⬜ confirmar | Lição 0 |
| `TOLERANCIA.md` escrito e commitado | ⬜ | 🔴 **Antes** de correr `comparar.py`, na lição 9 |
| `skyfield` (opcional, único `pip install` do curso) | ⬜ | Lição 9, e só como terceira testemunha |

## O critério de sucesso

Do [diagnóstico](DIAGNOSTICO.md): *«produzo um almanaque anual para uma posição dada, com
números que batem com fonte oficial dentro de tolerância declarada»*.

Marca-o como cumprido quando tiveres os três:

| | Feito |
|---|---|
| `almanaque-AAAA.csv` e `eventos-AAAA.csv` gerados para um ano | ⬜ |
| `TOLERANCIA.md` commitado **antes** da comparação (confere a data do commit) | ⬜ |
| Relatório com o que passou e o que falhou, **com as falhas à cabeça** | ⬜ |

⚠️ **O que já se sabe que vai falhar**, e não é problema teu: quatro das seis colunas
tabeladas não chegam aos 0,1′ do livro. Está medido na
[lição 9](../../docs/almanaque/09-o-teu-almanaque.html#mecanismo) e no
[index do tópico](../../docs/almanaque/index.html#fases). O projeto não é fazê-las passar —
é saber quais, por quanto, e porquê.

## Revisões

As datas saem de [`docs/almanaque/revisao.ics`](../../docs/almanaque/revisao.ics), contadas a
partir do dia em que o **núcleo** ficar concluído. O `.ics` publicado assume 2026-11-25; se
acabares noutro dia, desloca o primeiro evento e os outros seguem.

| Marco | Quando | Feito |
|---|---|---|
| Núcleo concluído (lições 0–7 e 9) | ⬜ por marcar | |
| Revisão +1 dia | — | ⬜ |
| Revisão +3 dias | — | ⬜ |
| Revisão +7 dias | — | ⬜ |
| Revisão +21 dias | — | ⬜ |
| Revisão +60 dias | — | ⬜ |
