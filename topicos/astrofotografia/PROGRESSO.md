# Progresso — Astrofotografia

Uma linha por sessão. Preenche-se com `/corrigir astrofotografia` depois de cada entrega,
nunca à mão a partir da memória.

| Data | Lição | Resultado | O que falhou | O que muda no plano |
|---|---|---|---|---|
| 2026-09-18 | — | curso criado e validado (passou as quatro fases) | — | Começar pela lição 0. 🔴 **Antes da lição 4** é preciso uma noite de poses tuas — e antes disso, uma tarde a confirmar que a câmara grava RAW e que sabes pô-la em manual. Importar o `revisao.ics` antes da primeira sessão: as datas assumem o núcleo concluído a 2026-11-27 |

## A ordem

O mapa está em [`docs/astrofotografia/index.html`](../../docs/astrofotografia/index.html#mapa).
Marca aqui o que está feito:

| # | Lição | Precisa de céu? | Estado | Feito |
|---|---|---|---|---|
| 0 | A luz como contagem | não | núcleo | ⬜ |
| 1 | O ruído | não | núcleo | ⬜ |
| 2 | A Terra roda | não (mas melhora com) | núcleo | ⬜ |
| 3 | Do céu ao píxel | não | núcleo | ⬜ |
| 4 | Calibrar | 🔴 **sim** | núcleo | ⬜ |
| 5 | Alinhar e empilhar | 🔴 **sim** | núcleo | ⬜ |
| 6 | Esticar | não | núcleo | ⬜ |
| 7 | O céu que atrapalha | 🔴 **sim** | núcleo | ⬜ |
| 8 | Planear a sessão | não | **extensão** | ⬜ |
| 9 | A tua imagem (projeto) | 🔴 **sim** | núcleo | ⬜ |
| — | Teste de domínio | não | — | ⬜ |

⚠️ **As lições que precisam de céu podem ser feitas com o campo sintético** que o teu próprio
código gera (`campo.py`), e **devem** ser, na primeira passagem: assim o *pipeline* já está a
funcionar quando a noite boa aparecer. O que não se pode simular é a surpresa — e é por isso que
nenhuma delas se dá por concluída sem dados teus.

## O que é preciso arranjar

| | Estado | Quando é preciso |
|---|---|---|
| Python 3 e `numpy` | ⬜ confirmar | Lição 0 |
| Câmara em **manual**, a gravar **RAW** | ⬜ confirmar | 🔴 **Lição 4** — antes disso não faz falta |
| Conversor de RAW para PGM de 16 bits (`dcraw`, `LibRaw`, `darktable-cli`…) | ⬜ | 🔴 **Lição 4**. A lição diz o que cada opção faz e porque é que **não** se deixa o conversor interpolar a cor |
| Tripé e disparador (ou temporizador da câmara) | ⬜ | Lição 4 |
| Uma noite sem Lua e sem nuvens | ⬜ | Lições 4, 5, 7 e 9 |
| `PREVISOES.md` escrito e commitado | ⬜ | 🔴 **Antes** de correr `projeto.py`, na lição 9 — ele recusa-se a correr sem isso |
| Siril ou DeepSkyStacker (opcional) | ⬜ | Lição 9, e só como terceira testemunha |

## O critério de sucesso

Do [diagnóstico](DIAGNOSTICO.md): *«produzo uma imagem empilhada e explico-a por números — SNR
ganho, escala em segundos de arco por píxel, largura das estrelas, brilho do céu, e o que
limitou»*.

Marca-o como cumprido quando tiveres os cinco:

| | Feito |
|---|---|
| Uma pilha de pelo menos 30 poses tuas, calibrada com *bias*, *darks* e *flats* teus | ⬜ |
| `PREVISOES.md` commitado **antes** da medição (confere a data do *commit*) | ⬜ |
| `projeto.py` a correr sobre as tuas poses, sem avisos por resolver, com a tabela toda | ⬜ |
| A previsão do ganho de SNR comparada com o ganho medido, **com a diferença explicada** | ⬜ |
| Relatório com **o que limitou à cabeça** — e não a imagem à cabeça | ⬜ |

⚠️ **O que já se sabe que vai acontecer**, e não é problema teu. Em simulação, com poses iguais
e alinhamento ao píxel inteiro, a pilha chega ao √N a menos de 1 %. Numa noite tua isso **não** vai
acontecer, e há três desvios já medidos na
[lição 5](../../docs/astrofotografia/05-alinhar-e-empilhar.html#mecanismo):

- a **transparência a variar** puxa o ganho para baixo (com 30 % de perda média, ×4,4 em vez de ×5,7);
- a **mediana** como método de combinação custa ≈10 %;
- 🔴 o **alinhamento por interpolação** faz o número sair **acima** de √N — o que é impossível, e é
  o sinal de uma medição contaminada, não de um bom resultado.

O projeto não é fazer o número bater com √N. É saber de que lado falhou, por quanto, e qual dos três
o explica.

## Revisões

As datas saem de [`docs/astrofotografia/revisao.ics`](../../docs/astrofotografia/revisao.ics),
contadas a partir do dia em que o **núcleo** ficar concluído. O `.ics` publicado assume 2026-11-27;
se acabares noutro dia, desloca o primeiro evento e os outros seguem.

| Marco | Quando | Feito |
|---|---|---|
| Núcleo concluído (lições 0–7 e 9) | ⬜ por marcar | |
| Revisão +1 dia | — | ⬜ |
| Revisão +3 dias | — | ⬜ |
| Revisão +7 dias | — | ⬜ |
| Revisão +21 dias | — | ⬜ |
| Revisão +60 dias | — | ⬜ |
