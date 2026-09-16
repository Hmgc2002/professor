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
6. **Ver as figuras a 400 px, nos dois temas.** O axe mede contraste, não texto cortado ou
   sobreposto num SVG. ✅ Desde 2026-09-16 há um passo automático — `validar_figuras.mjs`,
   dentro do `validar.sh` — que apanha texto fora do `viewBox`, texto por cima de texto,
   figuras vazias e marcadores de substituição não substituídos.
   ⚠️ **Não substitui olhar.** Ao criar o tópico `almanaque`, três figuras passaram esse passo
   e estavam visualmente más. Corre `CAPTURAS=/tmp/fig ./validar.sh` e **vê os PNG**.
7. **Contagens com atributo.** Toda a amostra que afirma «N palavras» ou «N caracteres» leva `data-palavras` / `data-caracteres`, e o `validar.py` confere — um número que se pode contar não se escreve à mão.

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
| 11 | **Fontes** | 🌐 *Verificado a AAAA-MM-DD*. Primárias sempre que existam. 🔴 **Pelo menos uma fonte que não seja documentação** — livro, artigo original, curso, **documentário, filme, série, palestra, vídeo ou podcast**: qualquer media serve, desde que responda ao *porque é assim* em vez do *o que faz* — com o **porquê** e **o que saltar**. Se o tópico não tiver nenhuma, escreve-se *que se procurou e não se encontrou*, que é informação diferente de silêncio |

### No fim do tópico

- **`bibliografia.html`** — o percurso, ordenado por **por onde começar** e não por autor. **Não é só leitura:** um documentário, uma série, uma palestra ou um canal de vídeo entram aqui como qualquer livro, com o mesmo rigor (o que é, o porquê, o que ver, e se foi mesmo visto). Cada
  entrada com o **porquê**, **o que saltar**, e a distinção primária/secundária. 🔴 Uma referência que não
  abriste não se escreve, e um ISBN que não confirmaste **não se cita** — diz-se que não se confirmou.
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
| 6 | **Geometria das figuras** | `validar_figuras.mjs`, a 400 px nos dois temas: texto fora do `viewBox`, texto sobreposto, figuras vazias, chaves por substituir. O limiar de sobreposição exige cruzamento **vertical e horizontal** — só por área, acusava rótulos empilhados, que estão bem |
| 7 | `INDICE.md` | Regenerado |

---

## Registo de falhas

Uma linha por erro de **processo** apanhado — não por erro de conteúdo. É o que impede
a quinta repetição do mesmo padrão. Acrescenta-se no fim, nunca se reescreve o que está acima.

| Data | Tópico | O que falhou | O que mudou |
|---|---|---|---|
| 2026-09-15 | (infraestrutura) | O primeiro `validar.py` marcou como âncora órfã o texto `#id` que aparecia dentro de um `<code>` num exemplo do próprio modelo — a armadilha que o `compendio` já tinha documentado e que eu reescrevi na mesma | O extrator passou a remover `<pre>`, `<code>` e comentários **antes** de procurar, e o modelo ficou com um exemplo dessa forma lá dentro, de propósito, para o caso não voltar a passar despercebido |
| 2026-09-15 | indices-btree-sql | A Fase 1 escreveu «o Postgres não usa o índice quando a query devolve mais de ~20% das linhas» com um número redondo que eu não tirei de lado nenhum | A Fase 3 substituiu o número por uma explicação do mecanismo (custo relativo, `random_page_cost`) e por uma demonstração que o aluno corre para encontrar **o limiar da máquina dele**. Regra reforçada: número redondo sem fonte é sinal de invenção |
| 2026-09-15 | (infraestrutura) | Dei como correção do `axe-core` um `codesign --force --deep --sign -` sobre o Chrome do puppeteer. **Não funciona** — falha com «main executable failed strict validation», porque o bundle do Chrome tem frameworks aninhados que o `--deep` assina pela ordem errada. Eu não tinha corrido o comando (foi bloqueado por enfraquecer a segurança do sistema) e mesmo assim escrevi-o como se fosse a solução | A regra «correr o que está escrito em vez de o julgar» **também se aplica aos comandos que dou a outra pessoa para correr**. Quando não posso correr um comando, digo que não o corri, em vez de o apresentar como verificado. O `validar_a11y.mjs` passou a procurar um Chrome já assinado (`/Applications/...`, ou `CHROME_PARA_VALIDAR`) e a mensagem de erro passou a dar a correção que funciona |
| 2026-09-15 | abstracts-e-resumos | Escrevi à mão as contagens das amostras («58 palavras», «43 caracteres»); 5 de 17 estavam erradas — num curso sobre escrever dentro de um limite | O `validar.py` passou a contar (`ver_amostras`): a amostra leva `data-palavras` e o validador confere. Testado com uma contagem errada de propósito. Regra: um número que se pode contar não se escreve à mão |
| 2026-09-15 | abstracts-e-resumos | Afirmei o que uma fonte **não** diz («a Wikipédia não diz de onde tirou o número») sem abrir essa parte. Diz: cita Finkelstein (2004) | «Abrir a fonte antes de repetir uma afirmação» vale também para afirmações de ausência — dizer que uma fonte não cita, não justifica ou não fala de algo exige tê-la aberto nessa parte |
| 2026-09-15 | abstracts-e-resumos | Parafraseei a definição de post-mortem do livro de SRE e acrescentei-lhe uma ideia («reduzir a probabilidade ou o impacto») que não está lá; a resposta certa do quiz repetia-a | Paráfrases de definições conferem-se contra a frase exata, não contra a lembrança dela |
| 2026-09-15 | (infraestrutura) | Dois flashcards com `;` no texto ficaram com quatro colunas e o `validar.sh` não viu — o passo 4 só verificava que o ficheiro existia | O passo 4 passou a contar as colunas de cada `flashcards.csv` |
| 2026-09-15 | (infraestrutura) | O tidy 5.8 acusou `<ol type="a">` como inválido. É válido (especificação WHATWG, «The ol element») | Filtro no `validar.sh` com a razão e a fonte escritas ao lado, como o do `<title>` em SVG. Não se tirou o atributo das páginas para calar o aviso |
| 2026-09-15 | abstracts-e-resumos | O axe passou a 400 px, mas quatro diagramas tinham texto cortado, sobreposto ou desatualizado — coisa que o axe não mede | Tirei capturas das figuras a 400 px nos dois temas (puppeteer) e corrigi. ⚠️ Não há passo do validador que o faça: por agora é um passo manual da Fase 3, e fica por decidir se entra no `validar.sh` |
| 2026-09-15 | abstracts-e-resumos | Nos quizzes, a opção certa estava na b em 31 de 54 perguntas | Posições redistribuídas. ⚠️ Nenhum validador conta posições; o tópico piloto não foi verificado quanto a isto |
| 2026-09-15 | indices-btree-sql | O curso foi publicado com a secção «Fontes» a cumprir metade do que o processo exige: 18 entradas de documentação, 2 sítios, 1 ferramenta — e **zero livros, zero artigos originais**. A Fase 2 não apanhou porque a lista de perguntas dela olhava para o *conteúdo* («que afirmação escrevi de memória?») e nunca para o *processo*. Um segundo tópico, criado noutra sessão, tinha bibliografia muito melhor — portanto a falha foi de execução, não do método, e é exatamente por isso que tinha de passar a ser uma verificação explícita em vez de depender de quem executa | A Fase 2 ganhou a pergunta «**que exigência do `PROCESSO.md` é que eu não cumpri?**», com uma lista de verificação a percorrer. A secção 11 passou a exigir 🔴 pelo menos uma fonte que não seja documentação, ou a declaração de que se procurou e não há. Os tópicos passaram a ter `bibliografia.html` |
| 2026-09-16 | cassete-dados | Escrevi as saídas dos exemplos e exercícios **antes** de correr o código. Ao correr, nenhuma batia — algumas em pormenores (2209 amostras e não 2205), outras no essencial (uma subida monótona que afinal tinha um máximo; um filtro com um zero que afinal tinha dois) | Todas substituídas pela saída real. Regra reforçada: uma saída de código numa lição **cola-se** de uma execução, nunca se escreve. Escrever primeiro e correr depois produz confirmação, não verificação |
| 2026-09-16 | cassete-dados | Apresentei uma curva medida (distorção em função do bias) como propriedade da fita, quando era do meu modelo simplificado | Quando uma simulação dá um resultado, varre-se com passo fino e troca-se o modelo antes de o afirmar. O que só aparece num modelo é do modelo |
| 2026-09-16 | cassete-dados | Numa pergunta de quiz marquei a opção errada como certa, e 42 de 48 certas estavam na opção b — a mesma falha já registada para abstracts-e-resumos | A posição passou a ser rodada na geração e o `validar.py` passou a contar posições (`ver_posicoes_certas`). Ao ligar a verificação, apanhou `indices-btree-sql` com 34 de 37 na b, por corrigir |
| 2026-09-16 | (infraestrutura) | O `validar.py` usava `str(Path)`. No Windows isso deu oito erros falsos e **regenerou o `INDICE.md` vazio**, apagando 295 linhas sem nenhum aviso — o passo «INDICE.md regenerado» parecia um sucesso | `as_posix()` em todos os caminhos relativos. Lição: um validador nunca tinha corrido fora do macOS, e «correu sem erros» não é o mesmo que «fez o que devia» — só o `git diff` o mostrou |
| 2026-09-16 | cassete-dados | O axe passou limpo, mas cinco de nove figuras estavam mal a 400 px, e uma contradizia o texto (zona morta desenhada onde a curva é mais inclinada) | Mesmo passo manual do registo anterior, e o mesmo resultado: continua a ser preciso. Os traçados passaram a ser calculados. ⚠️ Continua sem passo automático no `validar.sh` |
| 2026-09-16 | cassete-captura | Voltei a escrever números na prosa **antes** de correr o código — a mesma falha da sessão anterior, já registada acima. Aconteceu em três lições e nenhum dos números estava certo | Regra reforçada e agora com um mecanismo: as lições deste tópico são geradas por um script que **corre** cada bloco numa pasta temporária e cola a saída. Escrever primeiro e correr depois produz confirmação, não verificação |
| 2026-09-16 | cassete-captura | A rotação da posição da resposta certa nos quizzes usava `(n · 3 + len(chave)) % len(opcoes)`. Com três opções, `n · 3` é sempre 0: **42 de 42** respostas certas ficaram na «c». É a terceira ocorrência desta família de falhas (duas por escrita à mão) | Passou a usar um digest, que não tem período. E a lição de fundo: **a verificação automática que a ocorrência anterior deixou no `validar.py` foi o que apanhou esta**. Uma falha que se repete paga-se com um teste, não com atenção |
| 2026-09-16 | (infraestrutura) | O `validar.py` rebentava com `UnicodeEncodeError` ao imprimir o «✓» final numa consola de Windows com a saída redirecionada — ou seja, **só falhava quando estava tudo bem** | Força UTF-8 na saída. Um validador que só rebenta no caminho do sucesso é indistinguível de um validador partido: ninguém vê o caminho do sucesso até ser tarde |
| 2026-09-16 | cassete-captura | Afirmei que `simular_azimute()` «dá o mesmo que a fórmula» sem o ter conferido. Não dava: a média discreta errava 2 dB perto dos zeros | Conferir uma afirmação já escrita apanhou o erro. Regra: uma frase do tipo «X e Y concordam» é uma medição por fazer, não uma observação |
| 2026-09-16 | cassete-captura | Uma figura nova saiu **vazia** (chaves duplicadas numa f-string: o SVG ficou com `{x0}`), e o axe passou na mesma | O axe não vê figuras vazias. A captura das figuras a 400 px continua a ser o único passo que apanha isto, e continua manual |
| 2026-09-16 | cassete-dados | O arnês de limites da lição 6 importava cinco funções que o `fita.py` publicado na lição 5 não tinha: o exercício mais importante do tópico **não corria** para quem seguisse as lições pela ordem. Só apareceu ao reconstruir os ficheiros a partir das páginas, num tópico seguinte | Publicado o `fita.py` completo, com a correção à vista. Regra que fica: quando uma lição publica código por pedaços, reconstruir os ficheiros **a partir da página** e corrê-los — o que está no disco de quem escreve não é o que o aluno tem |
| 2026-09-16 | almanaque | `gha()` usava o tempo sidéreo **médio** quando o *Nautical Almanac* publica o **aparente**. Erro sistemático de −0,09′ no GHA de Áries. O código estava consistente **consigo próprio**, e nenhum teste interno o apanharia | Só apareceu ao comparar com o livro. Regra que fica: um erro **sistemático e pequeno** é a assinatura de um termo em falta, e a única maneira de o ver é uma referência **externa**. Ficou fixado em `ensaio.py` §7 |
| 2026-09-16 | almanaque | Escrevi cinco números de estimativa e todos estavam errados: «0,29′» para a equação dos equinócios (é 0,263′), «centenas de vezes» para a razão tabela/código (é 30), «alguns segundos» para o erro da fórmula fechada (é 76 s), «menos de um milésimo de milha» para a fixação (é 0,264), e «8° 59,6′» numa figura (é 59,7′) | Todos apanhados a correr ou a capturar. O gerador das lições **executa** cada bloco e cola a saída, por isso os números dentro dos blocos estavam certos — os errados foram os que escrevi **na prosa à volta**. A prosa precisa da mesma disciplina que o código |
| 2026-09-16 | almanaque | Um exercício media uma **tautologia**: aplicar 60 min de incremento mais o «v» cai exatamente no valor tabelado seguinte, porque o «v» **é definido** como essa diferença. Parecia validação e confirmava uma definição | Reescrito para medir o que o método realmente assume — a velocidade constante *dentro* da hora — comparando a reta com a parábola por três pontos tabelados: 0,006′. Regra: antes de escrever um teste, perguntar **que resultado o faria falhar** |
| 2026-09-16 | almanaque | O gerador etiquetava 25 dias do ano em Lisboa como «sempre-acima» (circumpolar). A Lua em Lisboa não é circumpolar: eram dias em que ela **saltou o nascer**, por atrasar ~50 min/dia | A exceção passou a distinguir **três** causas e a trazer as alturas mínima e máxima do dia. Regra: um resultado negativo tem de dizer **qual** dos negativos é — dois casos opostos com o mesmo sintoma é o erro de classificação mais fácil de cometer |
| 2026-09-16 | (infraestrutura) | O `ensaio.py` rebentou com `UnicodeEncodeError` num «Δ», em consola `cp1252` — **a mesma falha que este registo já tinha** para o `validar.py`, na sessão anterior. Reescrevi o mesmo bug | O registo de falhas só funciona se for **lido antes** de escrever, não depois de falhar. Ficou a correção no ficheiro novo, e fica esta linha a dizer que a anterior não chegou |
| 2026-09-16 | almanaque | Três figuras erradas que **passaram todas as verificações automáticas**: o mapa com o `viewBox` escrito à mão e quatro lições fora dele; a figura da reta de altura com rótulos sobrepostos e, à segunda tentativa, com geometria cortada; um rótulo truncado a meio de uma palavra | O verificador de figuras ganhou: `viewBox` calculado do envelope da geometria, rótulos em coluna fixa ordenados pelo alvo, e um detetor de sobreposição que exige cruzamento **vertical e horizontal** (o primeiro limiar, só por área, acusava rótulos empilhados). ⚠️ Continua a ser um passo **manual** da Fase 3: olhar para a imagem apanhou o que o detetor geométrico não apanhava |
| 2026-09-16 | almanaque | O `round()` do Python arredonda **ao par** e o livro arredonda metade para cima. A reconstrução da tabela de incrementos dava 0,1 onde a página imprime 0,2, e eu comecei a duvidar da fórmula | Regra: um desacordo de **uma décima** contra uma tabela impressa é, quase sempre, convenção de arredondamento e não método. Verifica-se isso **antes** de mexer na fórmula |
| 2026-09-16 | (infraestrutura) | A verificação das figuras a 400 px estava no registo **três vezes** como «continua a ser um passo manual» — e à quarta voltou a apanhar quatro erros, no tópico `almanaque` | Passou a ser o passo 4 do `validar.sh` (`validar_figuras.mjs`). A lição de fundo é a mesma de 2026-09-16 (cassete-captura): **uma falha que se repete paga-se com um teste, não com atenção**. Três registos a dizer «é manual» eram três avisos de que ninguém ia fazer manualmente |
| 2026-09-16 | almanaque | Regenerei páginas **duas vezes** sem voltar a correr o `sincronizar.py`: ficaram sem CSS, e a 400 px transbordavam centenas de píxeis. Das duas vezes quem apanhou foi o validador (o passo das figuras e o do axe a 400 px), não eu | O gerador de páginas escreve os marcadores de estilo vazios, por desenho (D-005). Regra: **gerar e sincronizar são um só passo** — quem gera corre os dois, sempre, pela ordem |
