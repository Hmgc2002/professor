# Diagnóstico — Astrofotografia

**Data:** 2026-09-18 · **Slug:** `astrofotografia` · **Curso:** [docs/astrofotografia/](../../docs/astrofotografia/index.html)

> 🔴 Este ficheiro é público. Tem só o ponto de partida técnico, o ritmo e a **classe** de
> equipamento. Não se perguntou de onde observas, nem se registou aqui marca, modelo ou preço de
> nada — inventário não vai para ficheiro público.
> O curso precisa de **uma** posição para os exemplos de planeamento e usa a mesma que o tópico
> [`almanaque`](../almanaque/DIAGNOSTICO.md) já tinha fixado por esta razão: o Observatório
> Astronómico de Lisboa, na Tapada da Ajuda (38° 42,5′ N, 9° 11,2′ W), que é um sítio publicado
> num mapa. Se um dia quiseres o curso calibrado para o sítio de onde fotografas de facto, ou
> para os teus milímetros e micrómetros concretos, isso vai para
> `topicos/astrofotografia/PRIVADO.md`, que está no `.gitignore`.

---

## O pedido

> astrofotografia · <https://en.wikipedia.org/wiki/Astrophotography>

Um artigo, não uma pergunta. E um artigo que cobre desde o daguerreótipo da Lua de 1840 até
telescópios remotos alugados à hora — portanto a primeira coisa que o diagnóstico teve de fazer
foi **cortar**, e dizer com que critério cortou.

---

## As perguntas e as respostas

### 1. Para quê?

**As quatro opções**, sem exclusão:

| Objetivo | O que decide no curso |
|---|---|
| **Fotografar com o que tenho** | É o eixo. Sem seguimento, o tempo de pose é imposto pela rotação da Terra, e tudo o resto do curso é a consequência disso: muitas poses curtas, empilhadas |
| **Montar equipamento dedicado** | Entra como **extensão declarada**, não como núcleo — ver a tensão abaixo |
| **Processar e programar o pipeline** | Todas as lições têm código que corre. O *pipeline* (calibrar, alinhar, empilhar, esticar, medir) é escrito por ti, de raiz |
| **Perceber a física sem fotografar já** | É o que faz este curso ser de mecanismos: cada regra prática é derivada, e o número que ela dá é **medido** no fim |

⚠️ **A tensão, dita antes de morder.** «Montar equipamento dedicado» e «fotografar com o que tenho»
não pedem o mesmo curso. Um curso sobre montagens equatoriais gasta lições inteiras em alinhamento
polar, erro periódico e guiagem — coisas que **não se podem praticar** com câmara, objetiva e tripé, e
que não têm como ser verificadas por ti enquanto o material não existir. Um curso que as ensinasse à
mesma produzia leitura, não aprendizagem.

**A resolução:** o núcleo é o que se pratica esta semana com o que existe. O que o equipamento
dedicado muda entra onde a física o obriga a entrar — a lição 3 calcula a escala em segundos de arco
por píxel para **qualquer** ótica, e a lição 2 mostra o que acontece ao limite de pose quando a
velocidade angular residual deixa de ser 15″/s e passa a ser o erro da montagem. Assim, o dia em que
comprares a montagem, o que muda é **um número**, não o curso.

⚠️ **A segunda tensão.** «Perceber a física» e «ter uma imagem» puxam em sentidos opostos quando o
tempo é pouco. Com 6 h por semana não puxam: há tempo para derivar **e** para fotografar. É por isso
que a resposta 3 é a que autoriza este plano de 10 lições — com 2 h por semana o curso teria de ser
outro, e estaria dito aqui.

### 2. De onde partes?

Respondido sem amaciar: **nada disto a sério**.

| Perguntei | Resposta |
|---|---|
| Fotografia — abertura, tempo, ISO, distância focal, histograma | **Não.** São palavras novas |
| Astronomia de posição — declinação, ângulo horário, altura e azimute | **Não** (o tópico `almanaque` existe mas ainda não foi feito) |
| Sinal e ruído — SNR, quantização, estatística do ruído | **Não** (os tópicos `cassete-*` existem mas ainda não foram feitos) |

É programador full-stack: terminal, Git, Python e ler código não se explicam, e o `numpy` aprende-se
a usar enquanto se usa. O que falta é **a física da luz e do sensor**, e falta toda.

🔴 **Consequência imediata, e é a decisão mais importante deste diagnóstico:** há **dois**
pré-requisitos em falta, e por isso há **duas** lições de fundação com as onze secções, não uma caixa
de «recorda que» no início da lição 3.

- **Lição 0 — a luz como contagem.** Exposição construída de raiz a partir de fotões: área, tempo,
  eficiência, ganho. Sem isto, «abre mais o diafragma» é uma superstição.
- **Lição 1 — o ruído.** Poisson, leitura, térmico e céu. Sem isto, empilhar é um ritual: não há como
  prever o que 60 poses fazem, nem como reconhecer que não fizeram.

A astronomia de posição **não** vira lição: é do tópico [`almanaque`](../../docs/almanaque/index.html),
que já a ensina melhor do que uma lição de passagem a ensinaria. O curso remete para lá e declara a
fronteira — e a lição 8, que precisa dela a sério, começa por dizer que a lição 0 desse tópico é o
pré-requisito dela.

⚠️ **Se este «nada disto a sério» for modéstia** — se afinal já sabes a tríade da exposição — a lição 0
lê-se em 20 minutos em vez de 2 horas e nada mais muda. O risco de assumir a mais é assimétrico: quem
sabe salta uma lição sem custo, quem não sabe fica sem chão na lição 2.

### 3. Quanto tempo por semana?

**6 horas ou mais.**

### 4. Até quando?

**Sem prazo.** O plano no tempo conta 10 semanas a cerca de 6 h. ⚠️ Com uma ressalva que não existia
no tópico `almanaque`: aqui há uma dependência que não é de horas. **O céu tem de colaborar** — noite
sem nuvens, sem Lua cheia e com o alvo alto. Em Lisboa, no inverno, isso pode ser uma janela por
quinzena. O plano marca as lições que precisam de céu e as que não precisam, para que uma semana de
mau tempo não pare o curso: o *pipeline* trabalha em dados sintéticos gerados pelo teu próprio código
até haver dados teus.

### 5. Como saberemos que aprendeste?

> **Uma imagem minha, com relatório de medições:** produzo uma imagem empilhada e explico-a por
> números — quanto ganhei em SNR, qual é a escala em segundos de arco por píxel, qual foi a largura
> das estrelas, quanto vale o brilho do céu daqui, e **o que limitou o resultado**.

**Porque é que este critério é bom:** cada uma dessas grandezas é uma medição sobre os teus próprios
ficheiros, feita pelo teu próprio código, e cada uma tem uma **previsão** feita antes de medir. A
imagem sozinha não provava nada — uma imagem bonita sai de carregar em botões. O relatório é que
distingue.

⚠️ **A parte do critério que não é de graça:** «o que limitou» obriga-te a escrever a previsão
**antes** de a medição existir. Previsão escrita depois é justificação. A lição 9 faz-te registar as
previsões num ficheiro versionado, e o `projeto.py` **recusa-se a correr** sem ele.

⭐ **E uma coisa que a construção do curso descobriu, e que vale a pena saberes antes de começar.**
Ao validar a lição 5, a primeira medição do ganho de uma pilha deu 75 % abaixo do previsto — e havia
uma explicação plausível já escrita para isso. A explicação não era falsa; era **irrelevante**, porque
o erro estava na medição. Foi o número previsto ao lado que a apanhou. É essa a razão de este curso
insistir tanto na previsão escrita antes.

---

## O que assumi, e o que muda se estiver errado

| Assumi que… | De onde veio | Se estiver errado… |
|---|---|---|
| A câmara grava **RAW** e permite pose, ISO e foco manuais | «câmara + objetiva + tripé» hoje quase implica isto | Sem RAW, o *pipeline* de calibração da lição 4 mede coisas que a câmara já alterou (o JPEG já foi esticado e já teve redução de ruído), e a lição 4 passaria a ter uma segunda metade sobre o que se pode e não se pode recuperar de um JPEG. O resto do curso mantém-se |
| Python 3 e `pip install numpy` disponíveis | É programador full-stack | 🔴 O código do curso é **biblioteca padrão + `numpy`, e mais nada** (D-028). Sem `numpy` o curso corria na mesma, mil vezes mais devagar. Não há `astropy`, nem `rawpy`, nem `OpenCV`: um *pipeline* construído sobre eles não ensina o que está lá dentro |
| Há uma forma de converter RAW → ficheiro legível fora da câmara | Existe software livre para isso em todos os sistemas | Se não houver, o curso trabalha com os JPEG/TIFF da câmara e a lição 4 leva o aviso acima. O formato que o curso lê é **PGM de 16 bits** e **FITS**, ambos com leitor escrito de raiz (≈40 linhas) — de propósito, para que o formato não seja uma caixa preta |
| Céu urbano ou suburbano | Lisboa é a posição de exemplo herdada do `almanaque` | Se o céu for escuro, os números do brilho do céu da lição 7 mudam e o tempo de integração necessário **desce muito** — mas a lição já é escrita para ser medida, não lida: é o teu céu que entra na conta |
| Inglês técnico lê-se sem atrito | Todas as fontes primárias estão em inglês | Se não fosse assim, o curso teria de traduzir a norma FITS e a patente do mosaico de Bayer em vez de remeter para elas |
| Não há seguimento motorizado durante o curso | Resposta explícita ao equipamento | Se aparecer uma montagem, o núcleo não muda — muda o valor da velocidade angular residual na lição 2 e abre-se a extensão sobre amostragem fina na lição 3 |

---

## A fronteira que o diagnóstico já fixa

- **Não** é um curso de astronomia de posição. Coordenadas, ângulo horário, nascer e pôr são do
  tópico [`almanaque`](../../docs/almanaque/index.html). Aqui usam-se, com remissão.
- **Não** é um curso sobre montagens, guiagem, alinhamento polar nem erro periódico. Diz-se onde
  isso entraria e o que mudaria; não se ensina o que não se pode praticar.
- **Não** é um curso de fotografia de paisagem noturna como composição. Enquadramento e estética
  ficam de fora; o que fica dentro é o que se mede.
- **Não** é um manual de um programa. Não há PixInsight, Siril, DeepSkyStacker nem Photoshop no
  núcleo: o *pipeline* é teu. Os programas aparecem na lição 9, como **terceira testemunha** do teu
  resultado.
- **Não** é fotometria científica. Mede-se SNR e largura de estrela para decidir o que fazer a
  seguir, não para publicar magnitudes.

---

## Fase 0 — o que se procurou no repositório

| Procurei | Onde | Resultado |
|---|---|---|
| `astrofotograf`, `astrophoto` | `grep -ril` em `docs/` e `topicos/` | **0** |
| `píxel`, `pixel`, `expos`, `obturador`, `diafragma`, `seeing`, `difra`, `poluição`, `nebulosa`, `poisson`, `arcsec`, `FITS` | idem | **0** em todos |
| `sensor` | idem | 2, ambos falsos: uma coluna `sensor_id` num exemplo de SQL |
| `telesc` | idem | 3, e são o **oposto do que parecem**: o `almanaque` declara na fronteira dele que «**não é astronomia observacional**: não há telescópios nem fotografia do céu». ⭐ Ou seja, este tópico é exatamente o que o vizinho recusou — o que torna a fronteira recíproca obrigatória e não opcional |
| `fotograf` | idem | 3 ficheiros. Em `almanaque/03-o-sol.html` é um caso de uso («planear fotografia de paisagem») e uma frase sobre refração junto ao horizonte, «que é quando se fotografa». **Vizinho a declarar**, e a lição 8 deste curso liga-se ali |
| `abertura` | idem | 6, todos em sentido retórico («abertura, desafio, ação e resolução» de um texto técnico). Zero em sentido ótico |
| `SNR`, `sinal-ruído` | idem | 15 ficheiros, todos em `cassete-*`. **Vizinho forte:** o SNR ali é de áudio, em dB, com ruído aditivo estacionário; aqui é de contagem, com ruído **dependente do sinal** (Poisson). A fronteira tem de ser explícita, senão a intuição de um estraga o outro |
| `dither` | idem | `cassete-dados/02-bias.html`. 🔴 **Homónimo perigoso:** ali *dither* é ruído somado **antes** de quantizar, para descorrelacionar o erro de quantização; aqui é deslocar o enquadramento **entre poses**, para descorrelacionar o padrão fixo do sensor. O parentesco é real (ambos convertem erro sistemático em erro aleatório), a mecânica não é a mesma. Declarado na lição 5 |
| `quantiz`, `gama dinâmica` | idem | `cassete-*`. Mesmo tipo de fronteira: 16 bits de um ADC de áudio e 14 bits de um ADC de câmara fazem-se a mesma pergunta |
| `calibra` | idem | 15, nenhum sobre calibração de imagem (são calibrações de fita e de tolerância) |
| `bias` | idem | 15, e é **outro homónimo**: em `cassete-dados` o *bias* é a corrente de polarização de alta frequência da gravação magnética; aqui é o nível de zero do ADC. **Mesma palavra, física diferente.** Declarado na lição 4 |
| `empilh`, `stack` | idem | Só em sentido de pilha/empilhar frases. Nada de empilhamento de imagens |
| `magnitude`, `estrela`, `céu`, `lua` | idem | `almanaque`, sempre em posição (onde está), nunca em brilho (quanta luz chega). ⭐ A magnitude **como escala de fluxo** não existe no repositório |
| `bayer` | idem | `indices-btree-sql/01-btree-por-dentro.html` — **Rudolf** Bayer, o do artigo de 1972 sobre B-trees. Este curso cita **Bryce E.** Bayer, o do mosaico de cor de 1976, na Kodak. 🔴 Pessoas diferentes, apelido igual: a lição 3 diz isto em caixa, para o aluno não juntar dois e dois e obter cinco |
| Por sintoma e por verbo: `empilhar imagens`, `reduzir ruído`, `média de N`, `raiz de N`, `alinhar`, `histograma`, `logarítm`, `gama` | idem | O `alinh` dá 18 ficheiros, todos no sentido de alinhamento de texto ou de tabelas. `logarítm` dá `cassete-captura` (eixo de um gráfico). **Nada sobre o mecanismo de ganho de SNR por média** |
| `git log -S` para `astrofotograf`, `píxel`, `telescópio`, `fotografia` | histórico inteiro (16 commits) | Só `fotografia`, e só no commit que criou o `almanaque`. **Nunca existiu e nunca foi removido** |
| `INDICE.md` | `grep -in "fotograf\|imagem\|ruído\|sinal\|luz\|estrela"` | Quatro cabeçalhos, todos de `cassete-*` e sobre sinal de áudio |

**Conclusão da Fase 0:** tópico novo, com **um pré-requisito dentro de casa** (`almanaque`, para
coordenadas), **três vizinhos** a declarar fronteira (`almanaque` em posição, `cassete-dados` e
`cassete-captura` em sinal e ruído) e **três colisões de vocabulário** que é preciso desarmar por
escrito: *bias*, *dither* e *Bayer*.

🔴 **Dívida recíproca apanhada aqui:** a fronteira do `almanaque` diz «não há telescópios nem
fotografia do céu» sem dizer para onde ir, porque em 2026-09-16 não havia para onde. Agora há.
Corrigir num sítio é corrigir em todos — essa linha passa a remeter para este tópico.

## Fontes localizadas na Fase 0

Todas abertas a **2026-09-18**, e o que não abriu está dito que não abriu.

| Fonte | Tipo | Estado |
|---|---|---|
| *FITS Standard 4.0* (2018-08-13) · <https://fits.gsfc.nasa.gov/fits_standard.html> | Especificação oficial | ✅ versão e data confirmadas na página oficial. ⚠️ Os pormenores do bloco de 2880 bytes e do cartão de 80 caracteres **não** estão nessa página: vêm do PDF da norma, e o curso confirma-os **a ler ficheiros reais** |
| Patente US 3 971 065, «Color imaging array», Bryce E. Bayer / Eastman Kodak | Fonte primária | ✅ aberta. Registada a 1975-03-05, concedida a 1976-07-20. A justificação do dobro de verdes está lá, citada à letra na lição 3 |
| EMVA 1288 · <https://www.emva.org/standards-technology/emva-1288/> | Norma industrial | ✅ Release 4.0, em vigor desde junho de 2021. ⚠️ A página **não** diz que parâmetros normaliza nem se o PDF é gratuito; o curso não lhe atribui conteúdo que não leu |
| Lupton et al. (2004), *Preparing Red-Green-Blue Images from CCD Data*, PASP **116**(816), 133 · DOI 10.1086/382245 | **Artigo original** | ✅ resumo lido à letra no arXiv (astro-ph/0312483) e volume/página confirmados no IOPscience. É a origem do esticamento `asinh` da lição 6 |
| Falchi et al. (2016), *The new world atlas of artificial night sky brightness*, Science Advances **2**(6), e1600377 · DOI 10.1126/sciadv.1600377 | **Artigo original** | ✅ referência confirmada. ⚠️ O texto integral não foi aberto daqui; o curso só lhe atribui o que está no resumo publicado |
| Stetson (1987), *DAOPHOT: A Computer Program for Crowded-Field Stellar Photometry*, PASP **99**, 191 · DOI 10.1086/131977 | **Artigo original** | ✅ referência confirmada (ADS e IOPscience). ⚠️ Texto integral não aberto: a lição 5 **deriva** a deteção por centroide em vez de citar o método do artigo |
| Merline & Howell (1995), *A realistic model for point-sources imaged on array detectors*, Experimental Astronomy **6**, 163 · DOI 10.1007/BF00421131 | **Artigo original** | ✅ referência confirmada. ⚠️ O PDF é digitalizado e não foi possível lê-lo aqui. 🔴 **Consequência declarada:** a «equação do CCD» da lição 1 **não é citada do artigo** — é derivada de Poisson no próprio texto, e o artigo aparece como leitura, não como autoridade |
| Howell, *Handbook of CCD Astronomy*, 2.ª ed., Cambridge University Press | **Livro** | ✅ ISBN 978-0-521-85215-9 (cartonado) e 978-0-521-61762-8 (brochado) confirmados na página do editor, com a lista de capítulos. ⚠️ Não tenho o exemplar: não se cita página |
| Legault, *Astrophotography*, Rocky Nook, julho de 2014 | **Livro** | ⚠️ ISBN 978-1-937538-43-9 e 240 páginas aparecem na ficha do editor, mas a ligação direta deu **404** hoje. Fica escrito assim, com a ressalva |
| Michaud, *La règle NPF*, Société Astronomique du Havre · <https://sahavre.fr/wp/regle-npf-rule/> | **Artigo** (sociedade de astrónomos amadores) | ✅ aberto, fórmulas copiadas à letra. É a fonte da lição 2 |
| Bortle (2001), *Introducing the Bortle Dark-Sky Scale*, Sky & Telescope | Artigo de revista | 🔴 **Não verificado:** o sítio da Sky & Telescope devolveu **403** e o PDF espelhado não se deixou ler aqui. **Consequência:** a lição 7 não usa a escala de Bortle para nada quantitativo — mede o brilho do céu nas tuas próprias poses, em magnitudes por segundo de arco quadrado |
| *Seeing in the Dark*, de Timothy Ferris (PBS, 2007) · <https://www.pbs.org/seeinginthedark/> | **Documentário** | ✅ existência, autor e emissora confirmados no sítio da própria emissora. ⚠️ Duração e data de estreia **não** foram confirmadas na fonte primária (aparecem num comunicado em PDF que não se deixou ler); por isso não se escrevem |
| Wikipédia, *Astrophotography* | Fonte secundária | ✅ aberta. É o ponto de partida do pedido e as datas históricas da lição 0 vêm de lá, **identificadas como secundárias** |

---

## O plano que sai daqui

10 lições. **Núcleo:** 0 a 7 e 9 — é o percurso até ao critério de sucesso.
**Extensão:** 8 (planear a sessão com efemérides), que depende do tópico `almanaque` e serve o
objetivo de perceber, mas não é preciso para ter a imagem.

Ver o mapa e o plano no tempo em [`docs/astrofotografia/index.html`](../../docs/astrofotografia/index.html).
