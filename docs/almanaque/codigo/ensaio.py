#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ensaio.py — o que prova que o `almanaque.py` está certo.

🔴 Correr isto é a Fase 3 do curso em ficheiro. Cada ensaio compara contra um
número PUBLICADO, aberto e datado — não contra outra função deste repositório.
Um teste que compara o código consigo próprio confirma; não verifica.

    python3 ensaio.py

Os valores de referência e onde foram abertos:

  EQUINÓCIOS E SOLSTÍCIOS ... Wikipédia, «Equinox», tabela de datas em UTC,
      aberta a 2026-09-16. Verifica a LONGITUDE ECLÍPTICA do Sol: o equinócio de
      março é, por definição, o instante em que ela passa por 0°.
  LUAS CHEIAS ............... timeanddate.com (fonte secundária, aberta a
      2026-09-16). Verifica a ELONGAÇÃO Lua−Sol: a lua cheia é a elongação a 180°.
  ΔT ........................ Wikipédia, «ΔT (timekeeping)», aberta a 2026-09-16.
  DIA SIDÉREO ............... Wikipédia, «Sidereal time»: 86164,0905 s.
  CONSTITUINTES DE MARÉ ..... Wikipédia, «Theory of tides»: períodos e velocidades.
"""

import math
import sys

# Numa consola de Windows a codificação por omissão é cp1252 e um simples «Δ»
# atira UnicodeEncodeError. Este repositório já tinha pago esta falha uma vez
# (PROCESSO.md, registo de falhas, 2026-09-16, no `validar.py`) e ela voltou a
# acontecer aqui, na primeira execução. Fica a correção, e fica dito porquê.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from almanaque import (J2000, DIA, dia_juliano, civil_de_jd, jd_tt, gmst_graus,
                       era_graus, sol, sol_baixa_precisao, lua, elongacao,
                       norm180, norm360, altitude_azimute, CONSTITUINTES,
                       jd_para_hms, jd_para_hm, graus_para_gm, evento,
                       H0_NASCER_POR, H0_CIVIL, H0_NAUTICO, H0_ASTRONOMICO)

FALHAS = []


def diz(rotulo, obtido, esperado, tolerancia, unidade):
    ok = abs(obtido - esperado) <= tolerancia
    if not ok:
        FALHAS.append(rotulo)
    print("  %-46s %12.4f  esperado %12.4f  Δ %9.4f %-4s %s"
          % (rotulo, obtido, esperado, obtido - esperado, unidade,
             "ok" if ok else "FALHA"))


def titulo(t):
    print("\n" + t)
    print("-" * len(t))


# ------------------------------------------------------------------ 1. o JD

titulo("1. Dia juliano — contra valores de definição")

# Definição: JD 2451545.0 = 2000-01-01 12:00 TT.
diz("JD de 2000-01-01 12:00", dia_juliano(2000, 1, 1, 12), 2451545.0, 0.0, "d")
# Meeus dá estes como exemplos canónicos do capítulo do calendário.
diz("JD de 1957-10-04 19:26:24 (Sputnik 1)",
    dia_juliano(1957, 10, 4, 19, 26, 24), 2436116.31, 0.005, "d")
diz("JD de 1987-01-27 00:00", dia_juliano(1987, 1, 27), 2446822.5, 0.0, "d")
diz("JD de 1988-06-19 12:00", dia_juliano(1988, 6, 19, 12), 2447332.0, 0.0, "d")

# Ida e volta: 20 000 dias, um a um, têm de voltar ao mesmo sítio.
pior = 0.0
for k in range(20000):
    jd = 2440000.5 + k + 0.123456
    a, m, d, h, mi, s = civil_de_jd(jd)
    volta = dia_juliano(a, m, d, h, mi, s)
    pior = max(pior, abs(volta - jd))
print("  ida-e-volta em 20 000 dias, pior erro: %.6f s" % (pior * DIA))
if pior * DIA > 0.01:
    FALHAS.append("ida-e-volta do JD")

# O dia bissexto secular: 1900 NÃO foi bissexto, 2000 foi.
print("  1900-02-28 → 1900-03-01 são %.0f dia(s) (gregoriano: sem 29/2)"
      % (dia_juliano(1900, 3, 1) - dia_juliano(1900, 2, 28)))
print("  2000-02-28 → 2000-03-01 são %.0f dia(s) (2000 é bissexto)"
      % (dia_juliano(2000, 3, 1) - dia_juliano(2000, 2, 28)))
if dia_juliano(1900, 3, 1) - dia_juliano(1900, 2, 28) != 1:
    FALHAS.append("bissexto de 1900")
if dia_juliano(2000, 3, 1) - dia_juliano(2000, 2, 28) != 2:
    FALHAS.append("bissexto de 2000")


# -------------------------------------------------------- 2. tempo sidéreo

titulo("2. Tempo sidéreo — duas fórmulas independentes têm de concordar")

# GMST (polinómio da IAU 1982) contra ERA (definição da IAU 2000). A diferença é
# a precessão acumulada desde J2000 e mais nada: cresce ~1,28°/século.
for ano in (2000, 2010, 2026, 2050):
    jd = dia_juliano(ano, 1, 1)
    d = norm180(gmst_graus(jd) - era_graus(jd))
    t = (jd - J2000) / 36525.0
    esperado = (0.014506 + 4612.156534 * t + 1.3915817 * t * t) / 3600.0
    diz("GMST − ERA em %d" % ano, d, esperado, 0.0002, "°")

# O dia sidéreo medido a partir do próprio polinómio.
#
# ⚠️ A PRIMEIRA VERSÃO DESTE ENSAIO FALHOU, e a falha não era da fórmula: media a
# taxa com um passo de 1 SEGUNDO e deu 86164,5604 s — meio segundo a mais. Com
# passo de 1 hora dá 86164,0908 s. A razão é cancelamento catastrófico: em 2026,
# 360.98564736629 × (JD − J2000) vale cerca de 3,5 milhões de graus, e um float
# de 64 bits só tem ~16 algarismos, por isso restam ~10⁻⁹° de resolução absoluta.
# Num sinal de 0,004° (o que o GMST anda num segundo) isso é ruído de 10⁻⁷
# relativos. Está na lição 2, em «Erros comuns», porque é o género de bug que
# passa despercebido: o código não rebenta, só mente na 4.ª casa.
jd = dia_juliano(2026, 6, 1)
for passo, rotulo in ((1.0 / 86400.0, "1 s"), (1.0 / 24.0, "1 h")):
    taxa = norm180(gmst_graus(jd + passo) - gmst_graus(jd)) / passo   # °/dia
    dia_sid = 360.0 / taxa * DIA
    diz("dia sidéreo medido do GMST (passo de %s)" % rotulo,
        dia_sid, 86164.0905, 0.6 if rotulo == "1 s" else 0.01, "s")
taxa = norm180(gmst_graus(jd + 1.0 / 24) - gmst_graus(jd)) * 24.0
dia_sid = 360.0 / taxa * DIA
print("  ou seja, %s mais curto do que o dia solar"
      % ("%d m %04.1f s" % divmod(DIA - dia_sid, 60)))


# ----------------------------------------------------- 3. o Sol: equinócios

titulo("3. Sol — instantes publicados dos equinócios e solstícios de 2025–2027")

# (ano, mês, dia, hora, minuto UTC, longitude eclíptica que define o evento)
EVENTOS = [
    (2025, 3, 20, 9, 1, 0.0), (2025, 6, 21, 2, 42, 90.0),
    (2025, 9, 22, 18, 19, 180.0), (2025, 12, 21, 15, 3, 270.0),
    (2026, 3, 20, 14, 46, 0.0), (2026, 6, 21, 8, 25, 90.0),
    (2026, 9, 23, 0, 6, 180.0), (2026, 12, 21, 20, 50, 270.0),
    (2027, 3, 20, 20, 25, 0.0), (2027, 6, 21, 14, 11, 90.0),
    (2027, 9, 23, 6, 2, 180.0), (2027, 12, 22, 2, 43, 270.0),
]


def instante_de_longitude(alvo, jd_perto, func=sol):
    """Bisseção sobre a longitude eclíptica aparente, ±2 dias em torno de jd."""
    lo, hi = jd_perto - 2.0, jd_perto + 2.0

    def f(t):
        return norm180(func(jd_tt(t))["lam"] - alvo)

    for _ in range(80):
        meio = (lo + hi) / 2.0
        if f(lo) * f(meio) <= 0:
            hi = meio
        else:
            lo = meio
    return (lo + hi) / 2.0


# 🔴 O ensaio mede o ERRO DE LONGITUDE em segundos de arco, e não o erro do
# INSTANTE em minutos, e a razão é o eixo do curso. O Sol anda 0,9856°/dia: um
# erro de 0,01° de longitude — que é a exatidão declarada da série do Meeus,
# cap. 25 — sai como ±15 MINUTOS no instante do equinócio. Testar pelo instante
# faz uma série boa parecer péssima. O que interessa a um almanaque é o ângulo.
print("  erro de longitude eclíptica, em segundos de arco:")
print("    %-12s %12s %12s   %14s" % ("evento", "Meeus", "baixa prec.", "declinação"))
erros_meeus, erros_baixa = [], []
for (a, m, d, h, mi, alvo) in EVENTOS:
    jd = jd_tt(dia_juliano(a, m, d, h, mi))
    e1 = norm180(sol(jd)["lam"] - alvo) * 3600.0
    e2 = norm180(sol_baixa_precisao(jd)["lam"] - alvo) * 3600.0
    erros_meeus.append(e1)
    erros_baixa.append(e2)
    print("    %04d-%02d-%02d   %+11.1f″ %+11.1f″   %14s"
          % (a, m, d, e1, e2, graus_para_gm(sol(jd)["dec"], 2)))

pior_meeus = max(abs(e) for e in erros_meeus)
pior_baixa = max(abs(e) for e in erros_baixa)
print("  pior erro de longitude: Meeus %.1f″ (%.2f′) · baixa precisão %.1f″ (%.2f′)"
      % (pior_meeus, pior_meeus / 60, pior_baixa, pior_baixa / 60))
print("  🔴 uma página do Nautical Almanac tabela a 0,1′. A série do Meeus erra até")
print("     %.2f′ de longitude, logo NÃO reproduz o livro coluna a coluna — lição 9."
      % (pior_meeus / 60))
# Tolerâncias tiradas da exatidão DECLARADA por cada fonte, não do que deu.
if pior_meeus > 36.0:        # 0,01° = 36″, exatidão declarada do Meeus cap. 25
    FALHAS.append("série do Sol (Meeus) pior do que os 0,01° declarados")
if pior_baixa > 3600.0:      # 1°, exatidão declarada do Astronomical Almanac C5
    FALHAS.append("série do Sol (baixa precisão) pior do que o 1° declarado")

# E agora o mesmo erro visto como tempo, para ficar claro porque é que não se
# testa assim — mas com a tolerância certa desta vez.
pior_instante = 0.0
for (a, m, d, h, mi, alvo) in EVENTOS:
    ref = dia_juliano(a, m, d, h, mi)
    obtido = instante_de_longitude(alvo, ref)
    pior_instante = max(pior_instante, abs(obtido - ref) * 24 * 60)
print("  o mesmo erro lido como instante do equinócio: até %.1f min" % pior_instante)
if pior_instante > 15.0:
    FALHAS.append("instante dos equinócios fora dos 15 min que 0,01° implica")

# A obliquidade MÉDIA em J2000 é uma constante de definição: 23° 26′ 21,448″ na
# expressão da IAU 1980 que esta série usa.
# ⚠️ A primeira versão deste ensaio comparava `eps` (obliquidade VERDADEIRA, com
# nutação) contra a constante da obliquidade MÉDIA e falhava por 5,4″ — que é
# precisamente a nutação em obliquidade no instante J2000. Era erro do ensaio,
# não do código: duas grandezas com nomes parecidos e significados diferentes.
d0 = sol(J2000)
diz("obliquidade MÉDIA em J2000", d0["eps0"], 23 + 26 / 60 + 21.448 / 3600, 1e-6, "°")
diz("nutação em obliquidade em J2000 (″)", (d0["eps"] - d0["eps0"]) * 3600, -5.4, 0.2, "″")

# A distância Terra–Sol no periélio e no afélio (cerca de 0,983 e 1,017 UA).
rr = [sol(dia_juliano(2026, 1, 1) + k)["r"] for k in range(366)]
print("  distância ao Sol em 2026: mínimo %.5f UA, máximo %.5f UA" % (min(rr), max(rr)))
if not (0.982 < min(rr) < 0.984 and 1.016 < max(rr) < 1.018):
    FALHAS.append("distância Terra–Sol fora dos limites conhecidos")

# Equação do tempo. Este é o ensaio mais forte do Sol, e é preciso perceber
# porquê: a EqT é a diferença entre DUAS grandezas do modelo (longitude média e
# ascensão reta aparente), por isso um erro comum às duas cancela-se e o que
# sobra é a forma da órbita mais a obliquidade. Os quatro extremos e as quatro
# passagens por zero estão publicados (Wikipédia, «Equation of time», convenção
# do USNO: aparente MENOS médio), com DATA — e a data é um teste mais apertado
# do que o valor, porque depende da fase e não da amplitude.
eq = [(sol(jd_tt(dia_juliano(2026, 1, 1) + k / 24.0))["eqt"], k / 24.0)
      for k in range(24 * 365)]
EXTREMOS = [("mínimo de fevereiro", min(e for e in eq if e[1] < 100), -14.25, 2, 11),
            ("máximo de maio", max(e for e in eq if 100 < e[1] < 180), 3.683, 5, 14),
            ("mínimo de julho", min(e for e in eq if 180 < e[1] < 250), -6.50, 7, 26),
            ("máximo de novembro", max(e for e in eq if e[1] > 250), 16.417, 11, 3)]
for rotulo, (valor, k), esperado, mes_esp, dia_esp in EXTREMOS:
    _, me, di = civil_de_jd(dia_juliano(2026, 1, 1) + k)[:3]
    ok = abs(valor - esperado) <= 0.12 and (me, di) == (mes_esp, dia_esp)
    if not ok:
        FALHAS.append("equação do tempo: " + rotulo)
    print("  %-22s %+7.2f min a %02d-%02d   publicado %+7.2f min a %02d-%02d   %s"
          % (rotulo, valor, me, di, esperado, mes_esp, dia_esp, "ok" if ok else "FALHA"))

# As quatro passagens por zero, publicadas: 15/4, 13/6, 1/9, 25/12 («podem variar
# um dia de ano para ano»), logo a tolerância é de 1 dia e está dita na fonte.
zeros = []
for i in range(1, len(eq)):
    if (eq[i - 1][0] < 0) != (eq[i][0] < 0):
        zeros.append(civil_de_jd(dia_juliano(2026, 1, 1) + eq[i][1])[:3])
esperados = [(4, 15), (6, 13), (9, 1), (12, 25)]
print("  passagens por zero em 2026: %s   publicadas: %s"
      % (", ".join("%02d-%02d" % (z[1], z[2]) for z in zeros),
         ", ".join("%02d-%02d" % e for e in esperados)))
if len(zeros) != 4 or any(abs(z[2] - e[1]) > 1 or z[1] != e[0]
                          for z, e in zip(zeros, esperados)):
    FALHAS.append("passagens por zero da equação do tempo")


# ------------------------------------------------------- 4. a Lua: fases

titulo("4. Lua — instantes publicados de lua cheia (elongação = 180°)")

CHEIAS = [(2026, 1, 3, 10, 2), (2026, 2, 1, 22, 9), (2026, 3, 3, 11, 37)]


def instante_elongacao(alvo, jd_perto):
    lo, hi = jd_perto - 1.5, jd_perto + 1.5

    def f(t):
        return norm180(elongacao(jd_tt(t)) - alvo)

    for _ in range(80):
        meio = (lo + hi) / 2.0
        if f(lo) * f(meio) <= 0:
            hi = meio
        else:
            lo = meio
    return (lo + hi) / 2.0


erros_lua = []
for (a, m, d, h, mi) in CHEIAS:
    ref = dia_juliano(a, m, d, h, mi)
    obtido = instante_elongacao(180.0, ref)
    erro_min = (obtido - ref) * 24 * 60
    erros_lua.append(erro_min)
    print("    %04d-%02d-%02d  publicado %02d:%02d UT   calculado %s   Δ %+6.1f min"
          % (a, m, d, h, mi, jd_para_hms(obtido), erro_min))
pior_lua = max(abs(e) for e in erros_lua)
print("  pior erro: %.1f min. A Lua anda 0,55°/h em elongação, logo isto vale %.2f°"
      % (pior_lua, pior_lua / 60.0 * 0.55))
if pior_lua > 240.0:
    FALHAS.append("fases da Lua fora de 4 h")

# A paralaxe horizontal da Lua varia entre cerca de 54' (apogeu) e 61,5' (perigeu).
pl = [lua(jd_tt(dia_juliano(2026, 1, 1) + k / 4.0))["paralaxe"] * 60 for k in range(4 * 366)]
print("  paralaxe horizontal em 2026: %.1f′ a %.1f′ (distância %.0f a %.0f raios terrestres)"
      % (min(pl), max(pl),
         1 / math.sin(math.radians(max(pl) / 60)), 1 / math.sin(math.radians(min(pl) / 60))))
if not (53.0 < min(pl) < 55.5 and 60.0 < max(pl) < 62.5):
    FALHAS.append("paralaxe da Lua fora dos limites conhecidos")

# A declinação da Lua vai muito além da do Sol: o ciclo de 18,6 anos leva-a a
# ±28,7° nos anos de «lunistício maior» e só a ±18,3° nos de menor.
for ano in (2025, 2026, 2034):
    decs = [abs(lua(jd_tt(dia_juliano(ano, 1, 1) + k / 2.0))["dec"]) for k in range(2 * 366)]
    print("  declinação máxima da Lua em %d: %.1f°" % (ano, max(decs)))


# ------------------------------------------- 5. o triângulo de posição

titulo("5. Triângulo de posição — identidades que têm de valer sempre")

# No trânsito superior, a altura é 90 − |φ − δ|. É a identidade que sustenta a
# «latitude pelo Sol ao meio-dia», e portanto a navegação inteira antes do rádio.
for lat, dec in ((38.7, 23.4), (38.7, -23.4), (-33.9, 5.0), (70.0, 23.4), (0.0, 0.0)):
    hc, zn = altitude_azimute(lat, dec, 0.0)
    diz("altura no trânsito φ=%.1f δ=%.1f" % (lat, dec), hc, 90 - abs(lat - dec), 1e-9, "°")

# Simetria leste-oeste: LHA = +h e LHA = −h dão a mesma altura e azimutes
# simétricos em relação ao meridiano.
hc1, zn1 = altitude_azimute(38.7, 10.0, 40.0)
hc2, zn2 = altitude_azimute(38.7, 10.0, 320.0)
diz("simetria LHA ±40°: alturas", hc1, hc2, 1e-9, "°")
diz("simetria LHA ±40°: azimutes somam 360", zn1 + zn2, 360.0, 1e-9, "°")

# No equador com declinação 0, o astro nasce exatamente a leste (Zn = 90°).
hc, zn = altitude_azimute(0.0, 0.0, 270.0)
diz("no equador, δ=0, LHA=270°: azimute", zn, 90.0, 1e-9, "°")

# A soma das alturas do trânsito superior e inferior é 2·(90 − |φ|) + ... : usa-se
# a identidade mais simples — no trânsito inferior a altura é |φ| + δ − 90 para
# um observador no hemisfério norte com δ > 0.
hc_inf, _ = altitude_azimute(70.0, 23.4, 180.0)
diz("trânsito inferior φ=70 δ=23.4", hc_inf, 70.0 + 23.4 - 90.0, 1e-9, "°")


# --------------------------------------------------- 6. marés: as frequências

titulo("6. Marés — cada velocidade confere com 360/período")

PERIODOS = {"M2": 12.4206012, "S2": 12.0, "N2": 12.65834751, "K2": 11.96723606,
            "K1": 23.93447213, "O1": 25.81933871, "P1": 24.06588766,
            "Q1": 26.868350}
for nome, per in sorted(PERIODOS.items()):
    diz("%s: 360/período" % nome, CONSTITUINTES[nome], 360.0 / per, 5e-6, "°/h")

# K1 é o dia sidéreo, S2 é meio dia solar, M2 é meio dia lunar. Confere-se.
diz("período de K1 = dia sidéreo", 360.0 / CONSTITUINTES["K1"] * 3600,
    86164.0905, 1.0, "s")
diz("período de S2 = meio dia solar", 360.0 / CONSTITUINTES["S2"] * 3600,
    43200.0, 1e-6, "s")

# O batimento M2/S2 é o ciclo das marés vivas e mortas: 14,765 dias.
batimento = 360.0 / abs(CONSTITUINTES["M2"] - CONSTITUINTES["S2"]) / 24.0
diz("batimento M2−S2 (marés vivas)", batimento, 14.765, 0.002, "d")


# ------------------------------------- 7. contra o Nautical Almanac oficial

titulo("7. Nautical Almanac de 2026, página de 20 de março — o teste que conta")

# Valores copiados da página diária de 2026 March 20, 21, 22 do Nautical Almanac
# publicado em <https://thenauticalalmanac.com> (PDF aberto a 2026-09-16, pág. 55
# do ficheiro). ⚠️ Não foram escritos à mão: foram EXTRAÍDOS do PDF pelo
# `comparar.py` e colados daqui. O PDF não está no repositório — tem direitos de
# autor; vai buscá-lo tu e corre `comparar.py` para repetires isto em qualquer dia.
#
# A mesma página declara ΔT = TT − UT1 = +69,1265 s. A constante DELTA_T deste
# curso é 69,0 — erra 0,13 s, que valem 0,005″ de Sol. Ver lição 2.
GHA_ARIES_20MAR2026 = [
    177.5433, 192.5833, 207.6250, 222.6667, 237.7067, 252.7483,
    267.7900, 282.8300, 297.8717, 312.9133, 327.9533, 342.9950,
    358.0350, 13.0767, 28.1183, 43.1583, 58.2000, 73.2417,
    88.2817, 103.3233, 118.3650, 133.4050, 148.4467, 163.4867]
SOL_20MAR2026 = [
    (178.1050, -0.2433), (193.1067, -0.2267), (208.1100, -0.2100),
    (223.1133, -0.1933), (238.1167, -0.1767), (253.1200, -0.1600),
    (268.1233, -0.1450), (283.1250, -0.1283), (298.1283, -0.1117),
    (313.1317, -0.0950), (328.1350, -0.0783), (343.1383, -0.0617),
    (358.1417, -0.0450), (13.1433, -0.0283), (28.1467, -0.0133),
    (43.1500, 0.0033), (58.1533, 0.0200), (73.1567, 0.0367),
    (88.1600, 0.0533), (103.1617, 0.0700), (118.1650, 0.0867),
    (133.1683, 0.1033), (148.1717, 0.1200), (163.1750, 0.1350)]

from almanaque import gast_graus, gha   # noqa: E402  (fica aqui por clareza)

e_aries, e_gha, e_dec = [], [], []
for h in range(24):
    jdu = dia_juliano(2026, 3, 20, h)
    d = sol(jd_tt(jdu))
    e_aries.append(norm180(gast_graus(jdu) - GHA_ARIES_20MAR2026[h]) * 60)
    e_gha.append(norm180(gha(d["ra"], jdu) - SOL_20MAR2026[h][0]) * 60)
    e_dec.append((d["dec"] - SOL_20MAR2026[h][1]) * 60)

for rot, v, limite in (("GHA de Áries", e_aries, 0.06),
                       ("GHA do Sol", e_gha, 0.50),
                       ("Dec do Sol", e_dec, 0.25)):
    pior = max(abs(x) for x in v)
    ok = pior <= limite
    if not ok:
        FALHAS.append("contra o almanaque oficial: " + rot)
    print("  %-14s média %+7.3f′   pior %6.3f′   (limite %.2f′)  %s"
          % (rot, sum(v) / len(v), pior, limite, "ok" if ok else "FALHA"))

print("  🔴 Leitura: o tempo sidéreo REPRODUZ o livro (0,06′ é o arredondamento do")
print("     próprio livro, que imprime a 0,1′). O Sol NÃO reproduz: erra até 0,4′ de")
print("     GHA, que são 0,4 milhas náuticas de longitude à latitude do equador.")
print("     Não é bug — é a exatidão declarada da série (0,01° = 36″). Lição 9.")

# ⚠️ E porque é que 0,06′ no Áries e 0,4′ no Sol? O que o ensaio 2 mostrou é que
# o GMST é exato por construção (é um polinómio de definição, não uma órbita). O
# Sol é uma órbita truncada. Duas grandezas com o mesmo ar e naturezas diferentes.


# --------------------------- 8. nascer, pôr e crepúsculos contra o livro

titulo("8. Nascer, pôr e crepúsculos — mesma página, latitude N 40")

# 🔴 O livro dá UMA linha de nascer/pôr por página de três dias, e ela é do DIA
# DO MEIO — 21 de março. Quem compara com o primeiro dia acha que tem 2 minutos
# de erro e vai procurar um bug que não existe. Os valores são LMT, iguais em
# qualquer longitude, por isso comparam-se com o cálculo à longitude 0.
OFICIAL_N40_21MAR = {"crep. náutico manhã": (H0_NAUTICO, True, "05:03"),
                     "crep. civil manhã": (H0_CIVIL, True, "05:35"),
                     "nascer do Sol": (H0_NASCER_POR, True, "06:02"),
                     "pôr do Sol": (H0_NASCER_POR, False, "18:13"),
                     "crep. civil tarde": (H0_CIVIL, False, "18:40"),
                     "crep. náutico tarde": (H0_NAUTICO, False, "19:12")}
jd0 = dia_juliano(2026, 3, 21)
for rot, (h0, sobe, esperado) in OFICIAL_N40_21MAR.items():
    obtido = jd_para_hm(evento(sol, 40.0, 0.0, jd0, h0, sobe))
    ok = obtido == esperado
    if not ok:
        FALHAS.append("nascer/pôr: " + rot)
    print("  %-22s %s   oficial %s   %s" % (rot, obtido, esperado, "ok" if ok else "FALHA"))

# A Lua, nos três dias da página. O livro dá uma linha por dia porque a Lua
# atrasa ~50 min por dia e uma média de três dias não serviria para nada.
print("  Lua, latitude N 40 (LMT):")
LUA_N40 = [(20, "06:31", "20:12"), (21, "06:59", "21:28"), (22, "07:31", "22:46")]
for dia, nasce_of, poe_of in LUA_N40:
    jd = dia_juliano(2026, 3, dia)
    # 0,125° é a altura a que o livro considera a Lua nascida: a refração e o
    # semidiâmetro quase cancelam a paralaxe, e o resultado é uma altura POSITIVA
    # — ao contrário do Sol. É a única correção do curso que muda de sinal.
    nasce = jd_para_hm(evento(lua, 40.0, 0.0, jd, 0.125, True))
    poe = jd_para_hm(evento(lua, 40.0, 0.0, jd, 0.125, False))
    d_n = abs(int(nasce[:2]) * 60 + int(nasce[3:]) - int(nasce_of[:2]) * 60 - int(nasce_of[3:]))
    d_p = abs(int(poe[:2]) * 60 + int(poe[3:]) - int(poe_of[:2]) * 60 - int(poe_of[3:]))
    print("    %d mar  nascer %s (oficial %s, Δ %d min)   ocaso %s (oficial %s, Δ %d min)"
          % (dia, nasce, nasce_of, d_n, poe, poe_of, d_p))
    if d_n > 1 or d_p > 1:
        FALHAS.append("nascer/ocaso da Lua a %d de março" % dia)

# E a Lua em posição, na mesma página: GHA, Dec e paralaxe horizontal a 0h e 12h.
print("  Lua em posição (a série D46 declara 0,5° de erro):")
for h, g_of, d_of, hp_of in ((0, 167 + 52.6 / 60, 7 + 15.3 / 60, 59.1),
                             (12, 341 + 55.8 / 60, 10 + 30.2 / 60, 59.3)):
    jdu = dia_juliano(2026, 3, 20, h)
    d = lua(jd_tt(jdu))
    eg = norm180(gha(d["ra"], jdu) - g_of) * 60
    ed = (d["dec"] - d_of) * 60
    ehp = d["paralaxe"] * 60 - hp_of
    print("    %2dh  GHA %+6.2f′   Dec %+6.2f′   HP %+5.2f′" % (h, eg, ed, ehp))
    if abs(eg) > 30 or abs(ed) > 30:
        FALHAS.append("Lua em posição às %dh" % h)
print("  ⭐ O erro medido (≈6′) é MUITO melhor do que os 0,5° declarados — mas 0,5°")
print("     é o que a fonte garante, e é esse o número que se usa a decidir. Uma")
print("     medição num dia não substitui a garantia da fonte.")


# ------------------------------------------------------------------- resumo

titulo("Resumo")
if FALHAS:
    print("  %d ENSAIO(S) FALHARAM:" % len(FALHAS))
    for f in FALHAS:
        print("    - " + f)
    sys.exit(1)
print("  todos os ensaios passaram.")
