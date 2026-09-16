#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""comparar.py — mede o teu almanaque contra o Nautical Almanac oficial.

    python3 comparar.py 2026_Nautical_Almanac.pdf 2026-03-20 [2026-06-21 ...]

🔴 O PDF não vem no repositório, e é de propósito: tem direitos de autor. Vai
buscá-lo tu a <https://thenauticalalmanac.com> (páginas diárias de 1911 a 2030,
grátis). O que este ficheiro faz é LER o teu exemplar, não distribuí-lo.

O que isto faz e porque é que interessa: extrai as colunas GHA/Dec do Sol e o
GHA de Áries da página diária, corre o `almanaque.py` para as mesmas 24 horas, e
imprime a diferença. É o critério de sucesso do curso transformado em número.

🔴 Declara a tolerância ANTES de correr isto (lição 9). Se olhares primeiro para
o resultado e só depois escolheres o limiar, não mediste nada: escolheste.

Como lê o PDF: só com `zlib` e `re` da biblioteca padrão. Os fluxos de conteúdo
trazem o texto em claro, com a posição de cada pedaço num `Td`; reconstrói-se a
linha pela coordenada Y e a coluna pela X. Não é um leitor de PDF a sério — é o
suficiente para estas páginas, e rebenta com barulho se o formato mudar, que é o
que se quer de um extrator de dados alheios.
"""

import re
import sys
import zlib
import datetime

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from almanaque import (dia_juliano, jd_tt, sol, sol_baixa_precisao, lua, gha,
                       gast_graus, norm180, graus_para_gm)

MESES = ["January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"]


# ------------------------------------------------------------------ o leitor

def fluxos_de_texto(caminho):
    dados = open(caminho, "rb").read()
    saida = []
    for bruto in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", dados, re.S):
        try:
            t = zlib.decompress(bruto)
        except zlib.error:
            continue
        if b"TJ" in t or b"Tj" in t:
            saida.append(t.decode("latin-1"))
    return saida


def linhas_de(fluxo):
    """Reconstrói as linhas de texto de um fluxo, ordenadas de cima para baixo."""
    itens = []
    x = y = 0.0
    for m in re.finditer(r"([-\d.]+)\s+([-\d.]+)\s+Td|\[(.*?)\]TJ|BT", fluxo):
        if m.group(1) is not None:
            x += float(m.group(1))
            y += float(m.group(2))
        elif m.group(3) is not None:
            itens.append((round(y, 1), round(x, 1),
                          "".join(re.findall(r"\((.*?)\)", m.group(3)))))
        else:
            x = y = 0.0
    por_linha = {}
    for yy, xx, t in itens:
        por_linha.setdefault(yy, []).append((xx, t))
    return [" ".join(t for _, t in sorted(por_linha[yy]))
            for yy in sorted(por_linha, reverse=True)]


# Uma linha de hora vem em três formas, porque o livro só repete o N/S de seis em
# seis horas e o kerning cola os dois números quando não há letra a separá-los.
RE_SINAL = re.compile(r"^(\d{1,2}) (\d{1,3}) (\d{2}\.\d) ([NS]) (\d{2}) (\d{2}\.\d) ")
# ⚠️ Quarta forma, encontrada só ao correr sobre janeiro: quando a declinação
# muda de GRAU sem mudar de hemisfério, o grau novo vem colado aos minutos do
# GHA e os minutos da declinação ficam soltos — «20 117 37.421 00.4». Sem esta
# linha, duas horas de cada página de janeiro desapareciam em silêncio.
RE_GRAU = re.compile(r"^(\d{1,2}) (\d{1,3}) (\d{2}\.\d)(\d{2}) (\d{2}\.\d) ")
RE_COLADO = re.compile(r"^(\d{1,2}) (\d{1,3}) (\d{2}\.\d)(\d{2}\.\d) ")
RE_SOLTO = re.compile(r"^(\d{1,2}) (\d{1,3}) (\d{2}\.\d) (\d{2}\.\d) ")


def tabela_do_sol(linhas):
    """[(hora, GHA em graus, Dec em graus)] — 24 por dia, até 3 dias por página."""
    sinal = None
    grau_dec = 0
    fora = []
    for L in linhas:
        m = RE_SINAL.match(L)
        if m:
            h, gd, gm, sg, dd, dm = m.groups()
            sinal, grau_dec = sg, int(dd)
            fora.append((int(h), int(gd) + float(gm) / 60,
                         (1 if sg == "N" else -1) * (grau_dec + float(dm) / 60)))
            continue
        m = RE_GRAU.match(L)
        if m and sinal:
            h, gd, gm, dd, dm = m.groups()
            grau_dec = int(dd)
            fora.append((int(h), int(gd) + float(gm) / 60,
                         (1 if sinal == "N" else -1) * (grau_dec + float(dm) / 60)))
            continue
        m = RE_COLADO.match(L) or RE_SOLTO.match(L)
        if m and sinal:
            h, gd, gm, dm = m.groups()
            fora.append((int(h), int(gd) + float(gm) / 60,
                         (1 if sinal == "N" else -1) * (grau_dec + float(dm) / 60)))
    return fora


def tabela_de_aries(linhas):
    fora = []
    for L in linhas:
        m = re.match(r"^(\d{1,2}) (\d{1,3}) (\d{2}\.\d) ", L)
        if m:
            h, gd, gm = m.groups()
            fora.append((int(h), int(gd) + float(gm) / 60))
    return fora


def paginas_da_data(fluxos, data):
    """Devolve (linhas_de_aries, linhas_do_sol, deslocamento_do_dia) para `data`.

    O livro põe três dias por abertura: a página esquerda tem Áries e os planetas,
    a direita o Sol e a Lua. O cabeçalho da esquerda diz que três dias são.
    """
    alvo = MESES[data.month - 1][:3]
    for i, f in enumerate(fluxos):
        linhas = linhas_de(f)
        if not linhas:
            continue
        # «March20,21,22UT(Fri.,Sat.,Sun.)». ⚠️ A primeira versão procurava os
        # dias com `\b(\d{1,2}),` e PERDIA SEMPRE O PRIMEIRO: entre «March» e
        # «20» não há fronteira de palavra, porque as duas são caracteres de
        # palavra. O sintoma era um dia de erro — 59′ de GHA — e não um erro de
        # extração, que é muito pior do que rebentar.
        m = re.match(r"^([A-Za-z.]+)((?:\d{1,2},)*\d{1,2})UT", cab_de(linhas))
        if not m or not m.group(1).startswith(alvo):
            continue
        dias = [int(x) for x in m.group(2).split(",")]
        if data.day in dias and i + 1 < len(fluxos):
            return linhas, linhas_de(fluxos[i + 1]), dias.index(data.day)
    return None, None, None


def cab_de(linhas):
    return linhas[0] if linhas else ""


def delta_t_da_pagina(linhas):
    """O ΔT que a própria página declara, em segundos — ou None.

    A página direita traz «T=TT-UT1=+69.1265sec» e «DUT1=UT1-UTC=+0.0575sec»,
    com a data dos dados do IERS ao fundo. É a prova, no próprio livro, de que o
    ΔT é MEDIDO e não calculado: muda de página para página dentro do mesmo ano.
    """
    for L in linhas[:3]:
        m = re.search(r"T=TT-UT1=([-+]?[\d.]+)sec", L)
        if m:
            return float(m.group(1))
    return None


# ---------------------------------------------------------------- a comparação

def comparar(caminho, datas):
    fluxos = fluxos_de_texto(caminho)
    print("PDF: %s  (%d fluxos de texto)" % (caminho, len(fluxos)))
    resumo = []
    for data in datas:
        esq, dir_, k = paginas_da_data(fluxos, data)
        if esq is None:
            print("\n%s: página não encontrada no PDF" % data)
            continue
        aries = tabela_de_aries(esq)[k * 24:(k + 1) * 24]
        solt = tabela_do_sol(dir_)[k * 24:(k + 1) * 24]
        if len(aries) < 24 or len(solt) < 24:
            print("\n%s: só extraí %d/%d horas — formato inesperado"
                  % (data, len(aries), len(solt)))
            continue
        dt = delta_t_da_pagina(dir_)
        print("\n%s  —  %d horas extraídas%s"
              % (data, len(solt),
                 "  ·  a página declara ΔT = %+.4f s" % dt if dt else ""))
        print("  %2s | %-12s %-12s | %-11s %-11s | %-9s"
              % ("h", "GHA Áries", "erro", "GHA Sol", "erro", "Dec erro"))
        e_ar, e_gh, e_de = [], [], []
        for (h, ga), (h2, gs, ds) in zip(aries, solt):
            jdu = dia_juliano(data.year, data.month, data.day, h)
            d = sol(jd_tt(jdu))
            ea = norm180(gast_graus(jdu) - ga) * 60
            eg = norm180(gha(d["ra"], jdu) - gs) * 60
            ed = (d["dec"] - ds) * 60
            e_ar.append(ea)
            e_gh.append(eg)
            e_de.append(ed)
            if h % 6 == 0:
                print("  %2d | %-12s %+7.3f′    | %-11s %+7.3f′   | %+7.3f′"
                      % (h, graus_para_gm(ga), ea, graus_para_gm(gs), eg, ed))
        for rot, v in (("GHA Áries", e_ar), ("GHA Sol", e_gh), ("Dec Sol", e_de)):
            print("  %-10s média %+7.3f′   máximo |%.3f′|"
                  % (rot, sum(v) / len(v), max(abs(x) for x in v)))
        resumo.append((data, max(abs(x) for x in e_ar),
                       max(abs(x) for x in e_gh), max(abs(x) for x in e_de)))

    if resumo:
        print("\nResumo — pior erro de cada dia, em minutos de arco")
        print("  %-12s %10s %10s %10s" % ("data", "Áries", "GHA Sol", "Dec Sol"))
        for data, a, g, d in resumo:
            print("  %-12s %10.3f %10.3f %10.3f" % (data, a, g, d))
        print("\n  🔴 0,1′ é o passo a que o livro imprime, logo ±0,05′ é ruído de")
        print("     arredondamento e não erro teu. Tudo acima disso é do teu modelo.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    comparar(sys.argv[1],
             [datetime.date.fromisoformat(a) for a in sys.argv[2:]])
