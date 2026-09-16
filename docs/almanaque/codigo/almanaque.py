#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""almanaque.py — o núcleo de cálculo do curso «O almanaque».

🔴 Só biblioteca padrão, de propósito. Um almanaque construído sobre o `skyfield`
funciona e não ensina nada: o objetivo do curso é saberes o que está lá dentro.
O `skyfield` aparece só na lição 9, como padrão de comparação — nunca como motor.

Cada função traz, no docstring, DE ONDE veio a fórmula e QUANTO ERRA. Uma função
de efemérides sem erro declarado é um número com ar de facto.

Origem das séries (as três estão abertas e datadas em cada lição):

  * Sol, baixa precisão .... «Low precision formulae for the Sun's coordinates»,
    The Astronomical Almanac, pág. C5. ⚠️ O sítio do USNO não respondeu a
    2026-09-16; os coeficientes vieram de uma reprodução que cita a edição de 2017
    (celestialprogramming.com) e estão VERIFICADOS por medição — ver `ensaio.py`.
  * Sol, precisão média ..... Meeus, «Astronomical Algorithms», 2.ª ed., cap. 25,
    reproduzido em squarewidget.com/solar-coordinates (aberto a 2026-09-16).
    ⚠️ Não tenho o livro: não se cita página.
  * Lua, baixa precisão ..... The Astronomical Almanac, pág. D46 (ed. de 1992),
    transcrita do `skycalc.c` de John Thorstensen (Dartmouth), função `lpmoon`,
    aberto a 2026-09-16 em mso.anu.edu.au/~thomasn/skycalc.fixed.c

Tudo o que este ficheiro devolve é GEOCÊNTRICO e APARENTE, salvo onde se diz.
"""

import math

# ----------------------------------------------------------------- constantes

J2000 = 2451545.0          # JD de 2000-01-01 12:00 TT
DIA = 86400.0

# ΔT = TT − UT1, em segundos. 🔴 É MEDIDO, não calculado: depende de a Terra
# rodar mais depressa ou mais devagar, e isso não se prevê. A Wikipédia (ΔT
# (timekeeping), aberta a 2026-09-16) diz: «Since early 2017 ... ΔT has remained
# within half a second of 69 seconds». É esse o valor por omissão aqui, e a
# lição 2 mostra o que muda se estiver errado por um segundo.
DELTA_T = 69.0

# Altura do centro do Sol ao nascer e ao pôr, em graus. −0,833° = −50′, que é
# 34′ de refração + 16′ de semidiâmetro (Wikipédia, «Sunrise equation», aberta a
# 2026-09-16). Os crepúsculos são convenção internacional, não medição.
H0_NASCER_POR = -0.8333
H0_CIVIL = -6.0
H0_NAUTICO = -12.0
H0_ASTRONOMICO = -18.0


# ---------------------------------------------------------------- utilitários

def graus_para_rad(x):
    return x * math.pi / 180.0


def rad_para_graus(x):
    return x * 180.0 / math.pi


def norm360(x):
    """Reduz um ângulo a [0, 360). Sem isto, as séries com 481267 graus por
    século dão argumentos de milhões de graus e perde-se precisão no seno."""
    return x - 360.0 * math.floor(x / 360.0)


def norm180(x):
    """Reduz a (−180, 180] — para diferenças de ângulos, onde 359° é −1°."""
    x = norm360(x)
    return x - 360.0 if x > 180.0 else x


def sin_g(x):
    return math.sin(graus_para_rad(x))


def cos_g(x):
    return math.cos(graus_para_rad(x))


# --------------------------------------------------------------------- tempo

def dia_juliano(ano, mes, dia, hora=0, minuto=0, segundo=0.0):
    """JD a partir de uma data do calendário gregoriano. `dia` pode ser inteiro.

    Não usa `datetime`: o `datetime` não representa datas antes de 1 e não tem
    fração de dia com a precisão que um almanaque precisa. O truque dos meses
    (janeiro e fevereiro contam como meses 13 e 14 do ano anterior) existe para
    que o ano comece em março e o dia bissexto caia sempre no FIM do ano — assim
    `floor(365.25·ano)` conta os bissextos sem nenhum caso especial.
    """
    d = dia + (hora + minuto / 60.0 + segundo / 3600.0) / 24.0
    if mes <= 2:
        ano -= 1
        mes += 12
    a = ano // 100
    b = 2 - a + a // 4                      # correção gregoriana
    return (math.floor(365.25 * (ano + 4716))
            + math.floor(30.6001 * (mes + 1))
            + d + b - 1524.5)


def civil_de_jd(jd):
    """Inverso de `dia_juliano`. Devolve (ano, mes, dia, hora, minuto, segundo).

    O segundo vem arredondado ao milésimo; o JD é um float de 64 bits e perto de
    2,46 milhões o épsilon vale cerca de 5·10⁻⁴ s — não há precisão abaixo disso.
    """
    jd = jd + 0.5
    z = math.floor(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alfa = math.floor((z - 1867216.25) / 36524.25)
        a = z + 1 + alfa - math.floor(alfa / 4)
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)
    dia_frac = b - d - math.floor(30.6001 * e) + f
    mes = e - 1 if e < 14 else e - 13
    ano = c - 4716 if mes > 2 else c - 4715
    dia = int(math.floor(dia_frac))
    resto = (dia_frac - dia) * 24.0
    hora = int(math.floor(resto))
    resto = (resto - hora) * 60.0
    minuto = int(math.floor(resto))
    segundo = round((resto - minuto) * 60.0, 3)
    if segundo >= 60.0:                     # o arredondamento pode transbordar
        segundo -= 60.0
        minuto += 1
    if minuto >= 60:
        minuto -= 60
        hora += 1
    return ano, mes, dia, hora, minuto, segundo


def seculos_j2000(jd):
    """Séculos julianos (36525 dias) desde J2000. É o T de todas as séries."""
    return (jd - J2000) / 36525.0


def jd_tt(jd_ut1, delta_t=DELTA_T):
    """UT1 → TT. As séries de posição correm em TT (tempo uniforme); a rotação
    da Terra corre em UT1 (tempo do Sol).

    Trocar as duas custa 69 segundos — e 69 segundos valem coisas muito
    diferentes conforme o que indexam, que é a armadilha:
      * na POSIÇÃO do Sol (0,041°/h): 0,0008′. Invisível.
      * na posição da LUA (0,55°/h):  0,63′. Já se vê.
      * na ROTAÇÃO da Terra (15°/h):  17,25′. Catastrófico.
    Por isso é que passar UT1 a `sol()` quase não se nota e passar TT a
    `gmst_graus()` estraga tudo. Ver a lição 2, secção 5.
    """
    return jd_ut1 + delta_t / DIA


def gmst_graus(jd_ut1):
    """Tempo sidéreo médio de Greenwich, em GRAUS (0–360).

    Polinómio clássico da IAU de 1982, na forma para JD arbitrário (não só 0h).
    O termo linear, 360.98564736629 graus por dia, é o que diz tudo: a Terra roda
    360,9856° por dia solar, e não 360°. A diferença, 0,9856°, é o ângulo que a
    Terra percorre na órbita num dia — por isso o dia sidéreo é ~3m56s mais curto.

    Conferido contra o Ângulo de Rotação da Terra (ver `era_graus`): a diferença
    entre os dois é a precessão acumulada e mais nada. Ver `ensaio.py`.
    """
    t = seculos_j2000(jd_ut1)
    g = (280.46061837
         + 360.98564736629 * (jd_ut1 - J2000)
         + 0.000387933 * t * t
         - t * t * t / 38710000.0)
    return norm360(g)


def nutacao_longitude(jd_tt_):
    """Nutação em longitude Δψ, em SEGUNDOS DE ARCO, termo dominante.

    Δψ ≈ −17,20″ · sin Ω, com Ω = 125,04452 − 1934,136261·T o nodo ascendente
    médio da órbita da Lua.

    Porquê só um termo: é o que a fonte aberta (a reprodução do Meeus cap. 25 em
    squarewidget.com, 2026-09-16) traz, e MEDIDO chega — ver o ensaio: com este
    termo só, o GAST reproduz o GHA de Áries do Nautical Almanac com erro médio
    de 0,004′ e máximo de 0,05′, que é exatamente o arredondamento do livro.
    Acrescentar termos de memória seria escrever o que não se abriu.

    A Lua puxa o bojo equatorial da Terra e faz o eixo oscilar com o período do
    nodo, 18,6 anos. É a mesma física que faz a declinação máxima da Lua variar
    entre 18,3° e 28,7° — ver `ensaio.py`, secção 4.
    """
    t = seculos_j2000(jd_tt_)
    return -17.20 * sin_g(125.04452 - 1934.136261 * t)


def gast_graus(jd_ut1, delta_t=DELTA_T):
    """Tempo sidéreo APARENTE de Greenwich, em graus. GAST = GMST + Δψ·cos ε.

    🔴 É ESTE, e não o GMST, que o Nautical Almanac publica na coluna «Aries».
    A diferença — a equação dos equinócios — vale até 1,05 s de tempo, ou seja
    0,263′ de arco (medido em ensaio.py sobre 20 anos), ou seja quase três vezes a
    tolerância do livro.

    ⚠️ A primeira versão deste ficheiro usava o GMST e o erro contra a página de
    20 de março de 2026 era de −0,09′ sistemáticos no GHA de Áries. Com o GAST
    desce para +0,004′. Corrigido a 2026-09-16.
    """
    tt = jd_tt(jd_ut1, delta_t)
    return norm360(gmst_graus(jd_ut1)
                   + nutacao_longitude(tt) * cos_g(sol(tt)["eps"]) / 3600.0)


def era_graus(jd_ut1):
    """Ângulo de Rotação da Terra (ERA), em graus. Definição da IAU de 2000.

    θ = 2π(0.7790572732640 + 1.00273781191135448·t_U), com t_U = JD_UT1 − 2451545.0
    (Wikipédia, «Sidereal time», aberta a 2026-09-16).

    Existe aqui para SERVIR DE SEGUNDA TESTEMUNHA ao `gmst_graus`. Duas fórmulas
    independentes que concordam valem mais do que uma fórmula que parece certa.
    """
    tu = jd_ut1 - J2000
    return norm360(360.0 * (0.7790572732640 + 1.00273781191135448 * tu))


# ----------------------------------------------------------------------- Sol

def sol_baixa_precisao(jd_tt_):
    """Sol pelas fórmulas de baixa precisão do Astronomical Almanac, pág. C5.

    Devolve dict com ra, dec (graus) e lam (longitude eclíptica, graus).
    Exatidão declarada pela fonte: 1° entre 1950 e 2050. É o que cabe numa lição
    e é 600 vezes pior do que uma página do Nautical Almanac — ver lição 3.
    """
    n = jd_tt_ - J2000
    ll = 280.460 + 0.9856474 * n                 # longitude média
    g = 357.528 + 0.9856003 * n                  # anomalia média
    lam = ll + 1.915 * sin_g(g) + 0.020 * sin_g(2 * g)
    eps = 23.439 - 0.0000004 * n
    lam = norm360(lam)
    ra = math.atan2(cos_g(eps) * sin_g(lam), cos_g(lam))
    dec = math.asin(sin_g(eps) * sin_g(lam))
    return {"lam": lam, "eps": eps,
            "ra": norm360(rad_para_graus(ra)),
            "dec": rad_para_graus(dec)}


def sol(jd_tt_):
    """Sol pela série do Meeus, cap. 25 (2.ª ed.), com nutação e aberração.

    Coeficientes reproduzidos em squarewidget.com/solar-coordinates, que cita as
    equações 25.3, 25.4 e 22.2. ⚠️ Não tenho o livro; a verificação que substitui
    a página é a medição contra os instantes publicados dos equinócios e
    solstícios, em `ensaio.py`.

    Devolve dict com ra, dec, lam (aparente), r (UA), sd (semidiâmetro, graus),
    eps (obliquidade verdadeira), eps0 (obliquidade média) e eqt (equação do
    tempo, em minutos, na convenção do USNO: solar aparente MENOS solar médio,
    logo positivo quando o Sol vai à frente do relógio).

    ⚠️ Exatidão MEDIDA, não prometida (ver `ensaio.py`): contra os instantes
    publicados dos equinócios e solstícios de 2025–2027, a longitude erra entre
    −8″ e +28″. São até 0,5′ de ângulo horário — CINCO vezes a tolerância de uma
    página do Nautical Almanac. Chega para a declinação (erro ≤ 0,2′) e para o
    nascer e o pôr; não chega para reproduzir o livro coluna a coluna.
    """
    t = seculos_j2000(jd_tt_)
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = 357.52911 + 35999.05029 * t - 0.0001537 * t * t
    e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t * t
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * sin_g(m)
         + (0.019993 - 0.000101 * t) * sin_g(2 * m)
         + 0.000289 * sin_g(3 * m))
    verdadeira = l0 + c                          # longitude verdadeira
    v = m + c                                    # anomalia verdadeira
    r = 1.000001018 * (1 - e * e) / (1 + e * cos_g(v))

    omega = 125.04 - 1934.136 * t                # nodo lunar: entra na nutação
    lam = verdadeira - 0.00569 - 0.00478 * sin_g(omega)   # aparente
    eps0 = 23.0 + 26.0 / 60.0 + 21.448 / 3600.0 \
        - (46.8150 * t + 0.00059 * t * t - 0.001813 * t * t * t) / 3600.0
    eps = eps0 + 0.00256 * cos_g(omega)

    lam = norm360(lam)
    ra = norm360(rad_para_graus(math.atan2(cos_g(eps) * sin_g(lam), cos_g(lam))))
    dec = rad_para_graus(math.asin(sin_g(eps) * sin_g(lam)))

    # Semidiâmetro: 959,63″ à distância de 1 UA (valor do Astronomical Almanac,
    # usado por todo o lado; entra no nascer/pôr e na correção de altura).
    sd = (959.63 / r) / 3600.0

    # Equação do tempo = (longitude média do Sol aparente) − (ascensão reta).
    # É a diferença entre o Sol que se vê e o relógio. Em minutos de tempo.
    eqt = norm180(l0 - 0.0057183 - ra + (-0.00569 - 0.00478 * sin_g(omega))) * 4.0

    return {"lam": lam, "ra": ra, "dec": dec, "r": r, "sd": sd,
            "eps": eps, "eps0": eps0, "eqt": eqt,
            "l0": norm360(l0), "m": norm360(m)}


# ----------------------------------------------------------------------- Lua

def lua(jd_tt_):
    """Lua pelas fórmulas de baixa precisão do Astronomical Almanac, pág. D46.

    Transcrita do `lpmoon` de `skycalc.c` (John Thorstensen, Dartmouth), aberto a
    2026-09-16. Exatidão declarada na mesma fonte para o algoritmo D22 moderno:
    cerca de 0,5° entre 1900 e 2100.

    🔴 Meio grau é o dobro do diâmetro aparente da Lua. Serve para saber onde
    apontar os olhos e para a fase; NÃO serve para navegar. Ver lição 5.

    Devolve dict com ra, dec, lam, beta, paralaxe (graus) e distancia (raios
    terrestres).
    """
    t = seculos_j2000(jd_tt_)
    lam = (218.32 + 481267.883 * t
           + 6.29 * sin_g(134.9 + 477198.85 * t)
           - 1.27 * sin_g(259.2 - 413335.38 * t)
           + 0.66 * sin_g(235.7 + 890534.23 * t)
           + 0.21 * sin_g(269.9 + 954397.70 * t)
           - 0.19 * sin_g(357.5 + 35999.05 * t)
           - 0.11 * sin_g(186.6 + 966404.05 * t))
    beta = (5.13 * sin_g(93.3 + 483202.03 * t)
            + 0.28 * sin_g(228.2 + 960400.87 * t)
            - 0.28 * sin_g(318.3 + 6003.18 * t)
            - 0.17 * sin_g(217.6 - 407332.20 * t))
    pi_h = (0.9508
            + 0.0518 * cos_g(134.9 + 477198.85 * t)
            + 0.0095 * cos_g(259.2 - 413335.38 * t)
            + 0.0078 * cos_g(235.7 + 890534.23 * t)
            + 0.0028 * cos_g(269.9 + 954397.70 * t))
    eps = 23.439291 + t * (-0.0130042 - 0.00000016 * t)

    lam = norm360(lam)
    lr, br, er = map(graus_para_rad, (lam, beta, eps))
    x = math.cos(br) * math.cos(lr)
    y = math.cos(er) * math.cos(br) * math.sin(lr) - math.sin(er) * math.sin(br)
    z = math.sin(er) * math.cos(br) * math.sin(lr) + math.cos(er) * math.sin(br)
    ra = norm360(rad_para_graus(math.atan2(y, x)))
    dec = rad_para_graus(math.asin(z))
    return {"lam": lam, "beta": beta, "ra": ra, "dec": dec,
            "paralaxe": pi_h, "distancia": 1.0 / math.sin(graus_para_rad(pi_h))}


def elongacao(jd_tt_):
    """Diferença de longitude eclíptica Lua − Sol, em graus [0, 360).

    0° = lua nova, 90° = quarto crescente, 180° = lua cheia, 270° = minguante.
    É esta grandeza — e não a iluminação — que define as fases: a fase é um
    instante de geometria, não um aspeto.
    """
    return norm360(lua(jd_tt_)["lam"] - sol(jd_tt_)["lam"])


def fraccao_iluminada(jd_tt_):
    """Fração do disco lunar iluminada, 0 a 1. (1 − cos i)/2 com i = elongação.

    Aproximação geocêntrica: ignora a paralaxe do observador e trata o Sol como
    infinitamente distante. Erra menos de 0,5 % — que é menos do que o erro da
    própria elongação vinda da série de baixa precisão.
    """
    return (1.0 - cos_g(elongacao(jd_tt_))) / 2.0


# ------------------------------------------------- do céu para o almanaque

def gha(ra_graus, jd_ut1):
    """Ângulo Horário em Greenwich (GHA), em graus, medido para OESTE de 0 a 360.

    GHA = GAST − α. É esta a grandeza que o Nautical Almanac tabela, e não a
    ascensão reta, porque o navegador precisa de saber onde está o astro EM
    RELAÇÃO À TERRA, não em relação às estrelas.

    🔴 GAST, não GMST — ver `gast_graus`. Trocar os dois custa até 0,263′.
    """
    return norm360(gast_graus(jd_ut1) - ra_graus)


def lha(gha_graus, longitude_graus):
    """Ângulo horário local. Longitude POSITIVA a leste (convenção deste curso).

    ⚠️ A convenção náutica clássica é a contrária (oeste positivo). O curso usa
    leste-positivo porque é a de toda a gente que escreve código hoje, incluindo
    o `datetime`, o ISO 6709 e o GeoJSON — e declara-se aqui para não haver
    dúvida. Um sinal trocado aqui dá um erro de longitude do dobro do valor.
    """
    return norm360(gha_graus + longitude_graus)


def altitude_azimute(lat_graus, dec_graus, lha_graus):
    """Altura e azimute de um astro. Devolve (Hc, Zn) em graus.

    sin Hc = sin φ · sin δ + cos φ · cos δ · cos LHA
    Zn = atan2(−sin LHA, tan δ · cos φ − sin φ · cos LHA), reduzido a [0, 360)

    A primeira é a lei dos cossenos aplicada ao triângulo esférico polo–zénite–
    astro. A segunda é a mesma lei resolvida para o outro ângulo, escrita com
    `atan2` para não perder o quadrante — que é o erro clássico de quem a escreve
    com `atan` e depois anda a corrigir sinais à mão.
    """
    phi, d, h = map(graus_para_rad, (lat_graus, dec_graus, lha_graus))
    sin_hc = math.sin(phi) * math.sin(d) + math.cos(phi) * math.cos(d) * math.cos(h)
    hc = math.asin(max(-1.0, min(1.0, sin_hc)))
    zn = math.atan2(-math.sin(h),
                    math.tan(d) * math.cos(phi) - math.sin(phi) * math.cos(h))
    return rad_para_graus(hc), norm360(rad_para_graus(zn))


# -------------------------------------------------------- nascer, pôr, trânsito

class SemEvento(Exception):
    """O astro não cruza a altura pedida nesse dia, no sentido pedido.

    Não é um caso raro que se ignora — acima do círculo polar é o caso NORMAL
    metade do ano, e um almanaque que devolve `None` em silêncio produz linhas
    em branco sem explicação. Ver lição 4.

    🔴 Há TRÊS causas diferentes com o mesmo sintoma, e a exceção diz qual é no
    atributo `causa`:

      "sempre-acima"  — o astro nunca desce abaixo de h0 (circumpolar, sol da
                        meia-noite). Acontece em latitudes altas.
      "sempre-abaixo" — o astro nunca sobe acima de h0 (noite polar).
      "fora-do-dia"   — o astro nasce e põe-se, mas o cruzamento que se pediu
                        caiu fora desta janela de 24 h. É o caso NORMAL da Lua
                        cerca de uma vez por mês, porque ela atrasa ~50 min/dia
                        e há dias de calendário em que salta um dos eventos.

    ⚠️ A primeira versão deste ficheiro só distinguia as duas primeiras, e o
    gerador etiquetava 25 dias do ano em Lisboa como «sempre-acima» quando a Lua
    lá não é circumpolar coisa nenhuma. Um resultado negativo mal classificado é
    pior do que nenhum resultado.
    """

    def __init__(self, mensagem, causa=None, alt_min=None, alt_max=None):
        super().__init__(mensagem)
        self.causa, self.alt_min, self.alt_max = causa, alt_min, alt_max


def _altura(corpo, lat, lon, jd_ut1):
    d = corpo(jd_tt(jd_ut1))
    return altitude_azimute(lat, d["dec"], lha(gha(d["ra"], jd_ut1), lon))[0]


def evento(corpo, lat, lon, jd_meia_noite, h0=H0_NASCER_POR, subir=True,
           passos=48, tol=1e-6, max_iter=60):
    """Instante (JD UT1) em que `corpo` cruza a altura `h0`, a subir ou a descer.

    Método: varre o dia em `passos` intervalos à procura de uma troca de sinal de
    (altura − h0) com o sentido pedido, e depois fecha por bisseção.

    Porquê bisseção e não a fórmula fechada cos H = (sin h₀ − sin φ sin δ)/(cos φ cos δ):
    a fórmula assume a declinação CONSTANTE durante o dia, e a do Sol muda até
    0,4°/dia perto dos equinócios — o que dá mais de um minuto de erro. A bisseção
    reavalia a declinação a cada passo, por isso não tem essa hipótese lá dentro.
    Custa cerca de 100 avaliações; a máquina não dá por isso e o aluno não precisa
    de saber quando a aproximação parte.
    """
    passo = 1.0 / passos
    alturas = [_altura(corpo, lat, lon, jd_meia_noite)]
    anterior = alturas[0] - h0
    for i in range(1, passos + 1):
        t = jd_meia_noite + i * passo
        a = _altura(corpo, lat, lon, t)
        alturas.append(a)
        actual = a - h0
        cruza = (anterior < 0 <= actual) if subir else (anterior >= 0 > actual)
        if cruza:
            lo, hi = t - passo, t
            for _ in range(max_iter):
                meio = (lo + hi) / 2.0
                v = _altura(corpo, lat, lon, meio) - h0
                if (v < 0) == subir:
                    lo = meio
                else:
                    hi = meio
                if hi - lo < tol:
                    break
            return (lo + hi) / 2.0
        anterior = actual
    mn, mx = min(alturas), max(alturas)
    if mn > h0:
        causa = "sempre-acima"
    elif mx < h0:
        causa = "sempre-abaixo"
    else:
        causa = "fora-do-dia"
    raise SemEvento(
        "sem cruzamento de %.4f° %s neste dia (%s; altura entre %.2f° e %.2f°)"
        % (h0, "a subir" if subir else "a descer", causa, mn, mx),
        causa=causa, alt_min=mn, alt_max=mx)


def transito(corpo, lon, jd_meia_noite, passos=48, tol=1e-7):
    """Passagem meridiana: o instante (JD UT1) em que LHA passa por 0°.

    Procura-se o zero de uma função em DENTE DE SERRA (o LHA salta de 360 para 0),
    e por isso o sinal converte-se para o intervalo (−180, 180] antes de procurar
    a troca. Quem esquece isto encontra o trânsito a meio da noite.
    """
    passo = 1.0 / passos

    def h(t):
        d = corpo(jd_tt(t))
        return norm180(lha(gha(d["ra"], t), lon))

    anterior = h(jd_meia_noite)
    for i in range(1, passos + 1):
        t = jd_meia_noite + i * passo
        actual = h(t)
        if anterior < 0 <= actual:
            lo, hi = t - passo, t
            for _ in range(60):
                meio = (lo + hi) / 2.0
                if h(meio) < 0:
                    lo = meio
                else:
                    hi = meio
                if hi - lo < tol:
                    break
            return (lo + hi) / 2.0
        anterior = actual
    raise SemEvento("sem passagem meridiana neste dia")


# ------------------------------------------------------ correções de altura

def refraccao_bennett(h_aparente_graus, pressao_hpa=1010.0, temp_c=10.0):
    """Refração atmosférica, em minutos de arco, pela fórmula de Bennett (1982).

    R = 1 / tan(h + 7.31/(h + 4.4))   [minutos de arco], h em graus.

    ⚠️ É um AJUSTE a uma atmosfera-padrão, não uma lei. Perto do horizonte a
    refração real varia com a temperatura ao nível do mar e chega a diferir 0,5′
    do valor tabelado — que é cinco vezes a tolerância de uma página do almanaque.
    É por isso que ninguém, em navegação a sério, usa alturas abaixo de ~15°
    quando pode evitá-lo.
    """
    r = 1.0 / math.tan(graus_para_rad(h_aparente_graus + 7.31 / (h_aparente_graus + 4.4)))
    return r * (pressao_hpa / 1010.0) * (283.0 / (273.0 + temp_c))


def depressao_horizonte(altura_olho_m):
    """Depressão do horizonte («dip»), em minutos de arco.

    dip ≈ 1.76 · √(altura em metros). Vem de geometria mais refração: de 10 m
    acima do mar vês 1,76·3,16 = 5,6′ ABAIXO da horizontal, e toda a altura
    medida a partir do horizonte do mar sai grande por essa quantidade.
    """
    return 1.76 * math.sqrt(altura_olho_m)


def altura_observada(hs_graus, altura_olho_m=0.0, erro_indice_min=0.0,
                     semidiametro_min=0.0, paralaxe_min=0.0,
                     bordo_inferior=True, pressao_hpa=1010.0, temp_c=10.0):
    """Hs (o que o sextante diz) → Ho (altura verdadeira do centro do astro).

    Pela ordem, e a ordem importa:
      1. erro de índice        — defeito do instrumento
      2. depressão do horizonte — defeito da referência (só com horizonte do mar)
      3. refração              — defeito da atmosfera; aplica-se à altura APARENTE,
                                 que é a de depois de 1 e 2, nunca à de antes
      4. semidiâmetro          — mediste o bordo, queres o centro
      5. paralaxe              — só a Lua a tem a sério (até 1°); o Sol tem 0,15′

    Devolve Ho em graus.
    """
    ha = hs_graus + erro_indice_min / 60.0 - depressao_horizonte(altura_olho_m) / 60.0
    ho = ha - refraccao_bennett(ha, pressao_hpa, temp_c) / 60.0
    ho += (semidiametro_min if bordo_inferior else -semidiametro_min) / 60.0
    ho += paralaxe_min * cos_g(ha) / 60.0
    return ho


# ------------------------------------------------------------ reta de altura

def intercepto(ho_graus, hc_graus):
    """Intercepto de Marcq St Hilaire, em MILHAS NÁUTICAS, com sinal.

    Positivo = na direção do astro («towards»); negativo = afastado.
    Regra mnemónica inglesa: «computed greater away» — se o calculado é maior do
    que o observado, estás mais longe do que a posição assumida.

    Porque é que 1 minuto de arco = 1 milha náutica: é a definição da milha
    náutica. A milha foi DEFINIDA como o minuto de meridiano, precisamente para
    esta conta não precisar de fator de conversão.
    """
    return (ho_graus - hc_graus) * 60.0


# ------------------------------------------------------------------- marés

# Velocidades em graus por hora das constituintes principais, da tabela da
# Wikipédia «Theory of tides» (aberta a 2026-09-16). Cada uma CONFERE-SE por
# cálculo na lição 8: velocidade = 360 / período.
CONSTITUINTES = {
    "M2": 28.9841042,   # semidiurna lunar principal
    "S2": 30.0,         # semidiurna solar principal
    "N2": 28.4397295,   # semidiurna lunar elíptica maior
    "K2": 30.0821373,   # semidiurna lunissolar
    "K1": 15.0410686,   # diurna lunissolar
    "O1": 13.9430356,   # diurna lunar
    "P1": 14.9589314,   # diurna solar
    "Q1": 13.3986609,   # diurna lunar elíptica maior
}


def altura_mare(horas, z0, termos):
    """h(t) = Z₀ + Σ Aᵢ·cos(σᵢ·t − φᵢ)

    `termos`: lista de (nome, amplitude, fase em graus). `horas` conta a partir
    da época a que as fases se referem.

    🔴 Isto NÃO é física da maré: é uma soma de cossenos cujas FREQUÊNCIAS vêm da
    astronomia e cujas AMPLITUDES E FASES vêm de medir aquele porto durante um
    ano. Por isso uma tábua de marés é local e um almanaque astronómico não é.
    """
    h = z0
    for nome, amp, fase in termos:
        h += amp * cos_g(CONSTITUINTES[nome] * horas - fase)
    return h


# ------------------------------------------------------------------ formatação

def graus_para_gm(x, casas=1):
    """Graus decimais → «ggg° mm,m′», que é como o almanaque escreve os ângulos.

    Não é decoração: o navegador soma e subtrai estes números à mão, e minutos
    com décimas somam-se de cabeça — graus decimais com quatro casas não.
    """
    sinal = "-" if x < 0 else ""
    x = abs(x)
    g = int(x)
    m = (x - g) * 60.0
    if round(m, casas) >= 60.0:
        m -= 60.0
        g += 1
    return "%s%d° %0*.*f′" % (sinal, g, casas + 3, casas, m)


def jd_para_hms(jd):
    """JD → «HH:MM:SS» do dia correspondente (UT)."""
    _, _, _, h, mi, s = civil_de_jd(jd)
    return "%02d:%02d:%02d" % (h, mi, int(round(s)))


def jd_para_hm(jd):
    """JD → «HH:MM», arredondado ao minuto — como o almanaque imprime."""
    a, me, d, h, mi, s = civil_de_jd(jd)
    total = h * 60 + mi + (1 if s >= 30 else 0)
    return "%02d:%02d" % ((total // 60) % 24, total % 60)
