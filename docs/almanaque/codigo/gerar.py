#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gerar.py — produz o teu almanaque. É o projeto do curso.

    python3 gerar.py 2027                      # o ano inteiro, para a posição por omissão
    python3 gerar.py 2027 --lat 38.7083 --lon -9.1867
    python3 gerar.py 2027 --dia 2027-03-20     # só um dia, em formato de página diária

🔴 Antes de correres isto, escreve a tua tolerância em `TOLERANCIA.md`. A lição 9
explica porquê: escolher o limiar depois de ver o resultado não é medir, é
justificar. O script recusa-se a comparar sem esse ficheiro.

Saídas:
  * `almanaque-<ano>.csv`  — uma linha por hora: GHA e Dec do Sol, de Áries e da Lua
  * `eventos-<ano>.csv`    — uma linha por dia: nascer, pôr, crepúsculos, trânsito,
                             nascer e ocaso da Lua, fase e equação do tempo
  * na consola, a página diária de um dia, no formato do livro

A posição por omissão é o Observatório Astronómico de Lisboa (Tapada da Ajuda),
38° 42,5′ N · 9° 11,2′ W — pública e arbitrária, como o diagnóstico decidiu.
"""

import argparse
import csv
import sys

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from almanaque import (dia_juliano, civil_de_jd, jd_tt, sol, lua, gha, gast_graus,
                       evento, transito, SemEvento, elongacao, fraccao_iluminada,
                       graus_para_gm, jd_para_hm, norm180, norm360,
                       H0_NASCER_POR, H0_CIVIL, H0_NAUTICO, H0_ASTRONOMICO)

LAT_OAL, LON_OAL = 38 + 42.5 / 60, -(9 + 11.2 / 60)
H0_LUA = 0.125          # ver a lição 5: a paralaxe torna esta altura positiva
NOMINAL_LUA = 14.3166667


def dias_do_ano(ano):
    jd = dia_juliano(ano, 1, 1)
    fim = dia_juliano(ano + 1, 1, 1)
    while jd < fim:
        yield jd
        jd += 1


def tabela_horaria(ano, caminho):
    """Uma linha por hora do ano. É o miolo do almanaque — e a parte comparável."""
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["data", "hora_ut", "gha_aries", "gha_sol", "dec_sol",
                    "gha_lua", "v_lua", "dec_lua", "d_lua", "hp_lua"])
        for jd0 in dias_do_ano(ano):
            a, m, d = civil_de_jd(jd0)[:3]
            for h in range(24):
                t = jd0 + h / 24.0
                t1 = t + 1 / 24.0
                s = sol(jd_tt(t))
                l0, l1 = lua(jd_tt(t)), lua(jd_tt(t1))
                gl0, gl1 = gha(l0["ra"], t), gha(l1["ra"], t1)
                w.writerow(["%04d-%02d-%02d" % (a, m, d), h,
                            "%.5f" % gast_graus(t),
                            "%.5f" % gha(s["ra"], t), "%.5f" % s["dec"],
                            "%.5f" % gl0,
                            "%.2f" % ((norm180(gl1 - gl0) - NOMINAL_LUA) * 60),
                            "%.5f" % l0["dec"],
                            "%.2f" % ((l1["dec"] - l0["dec"]) * 60),
                            "%.2f" % (l0["paralaxe"] * 60)])
    print("escrito %s" % caminho)


def _ou(corpo, lat, lon, jd0, h0, sobe):
    """Devolve HH:MM, ou a CAUSA declarada quando o evento não existe.

    🔴 Nunca devolve vazio. Uma célula em branco num almanaque é um bug com ar de
    dado. E nunca devolve uma causa adivinhada: a causa vem de `SemEvento`, que a
    determina a partir das alturas mínima e máxima do dia — ver o docstring dela.
    """
    try:
        return jd_para_hm(evento(corpo, lat, lon, jd0, h0, sobe))
    except SemEvento as e:
        return e.causa


def tabela_diaria(ano, lat, lon, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["data", "crep_naut_m", "crep_civil_m", "nascer_sol", "transito_sol",
                    "por_sol", "crep_civil_t", "crep_naut_t", "eq_tempo_min",
                    "dec_sol_12h", "nascer_lua", "ocaso_lua", "fase_graus", "iluminada"])
        for jd0 in dias_do_ano(ano):
            a, m, d = civil_de_jd(jd0)[:3]
            meio = jd0 + 0.5
            s = sol(jd_tt(meio))
            try:
                tr = jd_para_hm(transito(sol, lon, jd0))
            except SemEvento:
                tr = "sem-transito"
            w.writerow(["%04d-%02d-%02d" % (a, m, d),
                        _ou(sol, lat, lon, jd0, H0_NAUTICO, True),
                        _ou(sol, lat, lon, jd0, H0_CIVIL, True),
                        _ou(sol, lat, lon, jd0, H0_NASCER_POR, True),
                        tr,
                        _ou(sol, lat, lon, jd0, H0_NASCER_POR, False),
                        _ou(sol, lat, lon, jd0, H0_CIVIL, False),
                        _ou(sol, lat, lon, jd0, H0_NAUTICO, False),
                        "%.2f" % s["eqt"], "%.4f" % s["dec"],
                        _ou(lua, lat, lon, jd0, H0_LUA, True),
                        _ou(lua, lat, lon, jd0, H0_LUA, False),
                        "%.1f" % elongacao(jd_tt(meio)),
                        "%.3f" % fraccao_iluminada(jd_tt(meio))])
    print("escrito %s" % caminho)


def pagina_diaria(ano, mes, dia, lat, lon):
    """Uma página diária no formato do livro, para se poder comparar à vista."""
    jd0 = dia_juliano(ano, mes, dia)
    print("\n%04d %s %d  —  página diária (UT)" % (ano, MESES[mes - 1], dia))
    print("ΔT usado: 69,0 s  ·  posição: %s %s, %s %s"
          % (graus_para_gm(abs(lat)), "N" if lat >= 0 else "S",
             graus_para_gm(abs(lon)), "E" if lon >= 0 else "W"))
    print("\n h |  GHA Áries   |   GHA Sol    |   Dec Sol   |   GHA Lua    |    v |   Dec Lua   |    d |   HP")
    print("---+--------------+--------------+-------------+--------------+------+-------------+------+------")
    for h in range(24):
        t = jd0 + h / 24.0
        t1 = t + 1 / 24.0
        s = sol(jd_tt(t))
        l0, l1 = lua(jd_tt(t)), lua(jd_tt(t1))
        gl0, gl1 = gha(l0["ra"], t), gha(l1["ra"], t1)
        print("%2d | %-12s | %-12s | %-11s | %-12s | %4.1f | %-11s | %4.1f | %4.1f"
              % (h, graus_para_gm(gast_graus(t)), graus_para_gm(gha(s["ra"], t)),
                 graus_para_gm(s["dec"]), graus_para_gm(gl0),
                 (norm180(gl1 - gl0) - NOMINAL_LUA) * 60,
                 graus_para_gm(l0["dec"]), (l1["dec"] - l0["dec"]) * 60,
                 l0["paralaxe"] * 60))
    meio = jd0 + 0.5
    s = sol(jd_tt(meio))
    print("---+--------------+--------------+-------------+--------------+------+-------------+------+------")
    print("SD do Sol %.1f′   ·   Eq. do tempo %+.1f min   ·   fase %.1f° (%.0f%% iluminada)"
          % (s["sd"] * 60, s["eqt"], elongacao(jd_tt(meio)), fraccao_iluminada(jd_tt(meio)) * 100))
    print("\nNa latitude %s (hora local média):" % graus_para_gm(lat))
    for rot, h0, sobe in (("crepúsculo náutico", H0_NAUTICO, True),
                          ("crepúsculo civil", H0_CIVIL, True),
                          ("nascer do Sol", H0_NASCER_POR, True),
                          ("pôr do Sol", H0_NASCER_POR, False),
                          ("crepúsculo civil", H0_CIVIL, False),
                          ("crepúsculo náutico", H0_NAUTICO, False)):
        print("  %-20s %s" % (rot + (" (manhã)" if sobe else " (tarde)"),
                              _ou(sol, lat, 0.0, jd0, h0, sobe)))
    print("  %-20s %s" % ("nascer da Lua", _ou(lua, lat, 0.0, jd0, H0_LUA, True)))
    print("  %-20s %s" % ("ocaso da Lua", _ou(lua, lat, 0.0, jd0, H0_LUA, False)))


MESES = ["January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ano", type=int)
    p.add_argument("--lat", type=float, default=LAT_OAL)
    p.add_argument("--lon", type=float, default=LON_OAL, help="leste positivo")
    p.add_argument("--dia", help="AAAA-MM-DD: imprime só a página desse dia")
    p.add_argument("--csv", action="store_true", help="escreve os dois CSV do ano")
    a = p.parse_args()

    if a.dia:
        y, m, d = (int(x) for x in a.dia.split("-"))
        pagina_diaria(y, m, d, a.lat, a.lon)
    if a.csv or not a.dia:
        tabela_horaria(a.ano, "almanaque-%d.csv" % a.ano)
        tabela_diaria(a.ano, a.lat, a.lon, "eventos-%d.csv" % a.ano)
        print("\nAgora compara. 🔴 Primeiro escreve a tolerância, depois corre:")
        print("  python3 comparar.py <o-teu>_Nautical_Almanac.pdf %d-03-20 %d-06-21" % (a.ano, a.ano))


if __name__ == "__main__":
    main()
