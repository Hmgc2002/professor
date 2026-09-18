#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""foton.py — de uma magnitude no céu a electrões num píxel, e ao ruído que vem com eles.

Tudo neste ficheiro é uma cadeia de multiplicações e uma raiz quadrada. O valor de
ensinar está em **cada fator ter um nome e uma unidade**: quando a conta dá um número
absurdo, o fator errado identifica-se por dimensão, não por tentativa.

    fluxo da fonte  ×  área da pupila  ×  tempo  ×  transmissão  ×  eficiência
    ────────────────────────────────────────────────────────────────────────── = electrões
                        (e a atmosfera tira a sua parte pelo caminho)

🔴 O ponto zero fotométrico (`ZP_V_JY`) é o único número deste ficheiro que vem de fora
e que **não** consegues medir sem uma estrela de referência. Está identificado como tal,
com a fonte e o que ela é. Todos os outros ou são definições (2,5 log₁₀), ou geometria
(206265), ou parâmetros do teu material, que se medem.
"""

import math
import sys

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# ------------------------------------------------------- constantes, e de onde vêm

# Fluxo de uma estrela de magnitude V = 0, em jansky, e a conversão de jansky para
# fotões. ⚠️ Fonte secundária: apontamentos de curso (astroweb.case.edu/ssm/ASTR620/mags.html,
# abertos a 2026-09-18), adaptados de um manuscrito não publicado. O valor 3640 Jy é
# atribuído a Bessell et al. (1998) na literatura, mas o artigo não foi aberto aqui.
# Consequência: trata-se isto como uma ordem de grandeza calibrável, não como uma
# constante física. A lição 9 mostra como medir o TEU ponto zero a partir de uma
# estrela conhecida no teu enquadramento — e aí este número deixa de ser preciso.
ZP_V_JY = 3640.0            # jansky, para V = 0
JY_PARA_FOTOES = 1.51e7     # fotões s⁻¹ m⁻² por unidade de (Δλ/λ), por jansky
BANDA_V = 0.16              # Δλ/λ da banda V (λ_c = 0,55 µm)

ARCSEC_POR_RADIANO = 180.0 * 3600.0 / math.pi   # 206264,806…
VELOCIDADE_SIDERAL = 360.0 / 86164.0905 * 3600.0  # segundos de arco por segundo de tempo


def fotoes_por_cm2_s(mag):
    """Fotões por centímetro quadrado e por segundo, acima da atmosfera, banda V."""
    por_m2 = JY_PARA_FOTOES * ZP_V_JY * BANDA_V * 10 ** (-0.4 * mag)
    return por_m2 / 1e4


def area_pupila_cm2(focal_mm, f_numero):
    """Área da pupila de entrada. É **isto** que a abertura significa: uma área.

    O «f/2» não é um número mágico: é focal ÷ diâmetro. Passar de f/4 para f/2
    duplica o diâmetro e **quadruplica** a área — e é por isso que vale um fator 4
    em fotões, não um fator 2.
    """
    diametro_mm = focal_mm / f_numero
    return math.pi * (diametro_mm / 20.0) ** 2      # mm → cm: /10, e raio: /2


def escala_arcsec_px(focal_mm, passo_um):
    """Segundos de arco por píxel. Geometria pura: o passo do píxel visto da distância focal."""
    return ARCSEC_POR_RADIANO * (passo_um / 1000.0) / focal_mm


def electroes_estrela(mag, focal_mm, f_numero, t_s, transmissao=0.9, qe=0.5,
                      extincao_mag=0.2):
    """Electrões que uma estrela de magnitude `mag` deposita em `t_s` segundos.

    `extincao_mag` é o que a atmosfera come, em magnitudes, no ângulo em que
    estás a olhar — some-se à magnitude, porque magnitude é logaritmo de fluxo.
    """
    fluxo = fotoes_por_cm2_s(mag + extincao_mag)
    return fluxo * area_pupila_cm2(focal_mm, f_numero) * t_s * transmissao * qe


def electroes_ceu_px(mu, focal_mm, f_numero, passo_um, t_s, transmissao=0.9, qe=0.5):
    """Electrões de **fundo de céu** por píxel.

    `mu` é o brilho do céu em magnitudes por segundo de arco quadrado. O céu é uma
    fonte extensa: o que chega a um píxel depende da área de céu que esse píxel vê,
    e é por isso que a escala entra ao quadrado.
    """
    esc = escala_arcsec_px(focal_mm, passo_um)
    fluxo = fotoes_por_cm2_s(mu) * esc ** 2
    return fluxo * area_pupila_cm2(focal_mm, f_numero) * t_s * transmissao * qe


# ------------------------------------------------------- ruído

def snr_pose(sinal_e, ceu_e_px, n_px, escuro_e_px=0.0, leitura_e=0.0):
    """Sinal-ruído de **uma** pose, para uma estrela medida em `n_px` píxeis.

    A conta tem uma só ideia: **as variâncias somam-se, os desvios-padrão não.**

        variância = sinal + n_px·(céu + escuro + leitura²)

    O sinal aparece na variância porque a chegada de fotões é um processo de
    Poisson: contar N fotões traz ±√N de incerteza que não vem de defeito nenhum
    do equipamento. O ruído de leitura entra ao quadrado porque é dado em
    electrões de desvio-padrão, e o que se soma são variâncias.
    """
    variancia = sinal_e + n_px * (ceu_e_px + escuro_e_px + leitura_e ** 2)
    return sinal_e / math.sqrt(variancia) if variancia > 0 else float("inf")


def snr_pilha(n, sinal_e, ceu_e_px, n_px, escuro_e_px=0.0, leitura_e=0.0):
    """Sinal-ruído de `n` poses iguais somadas.

    Sai exatamente √n vezes o de uma pose — **em teoria**. O sinal cresce n vezes,
    a variância também, e a raiz dá √n. A lição 5 mede o que sai na prática e a
    diferença tem nome e causa.
    """
    return math.sqrt(n) * snr_pose(sinal_e, ceu_e_px, n_px, escuro_e_px, leitura_e)


def poses_para_snr(alvo, sinal_e, ceu_e_px, n_px, escuro_e_px=0.0, leitura_e=0.0):
    """Quantas poses são precisas para chegar a `alvo` de SNR. Arredonda para cima."""
    uma = snr_pose(sinal_e, ceu_e_px, n_px, escuro_e_px, leitura_e)
    return math.ceil((alvo / uma) ** 2)


# ------------------------------------------------------- a Terra roda

def arrasto_px(t_s, focal_mm, passo_um, declinacao_graus):
    """Comprimento do traço de uma estrela, em píxeis, numa pose de `t_s` segundos.

    A estrela anda no céu a 15,04″ por segundo **vezes o cosseno da declinação**:
    uma estrela junto ao polo descreve um círculo pequeno e quase não se mexe; uma
    estrela no equador celeste percorre o círculo todo.
    """
    arco = VELOCIDADE_SIDERAL * t_s * math.cos(math.radians(declinacao_graus))
    return arco / escala_arcsec_px(focal_mm, passo_um)


def t_max_por_arrasto(px_tolerados, focal_mm, passo_um, declinacao_graus):
    """Pose máxima para que o traço não passe de `px_tolerados` píxeis."""
    esc = escala_arcsec_px(focal_mm, passo_um)
    cos = math.cos(math.radians(declinacao_graus))
    return px_tolerados * esc / (VELOCIDADE_SIDERAL * cos)


def regra_500(focal_mm):
    """A «regra dos 500»: 500 ÷ focal. ⚠️ É convenção, não física.

    Não conhece o passo do píxel, nem a declinação, nem a abertura. A lição 2
    mostra por quanto erra para um sensor moderno — e a resposta depende da câmara.
    """
    return 500.0 / focal_mm


def regra_npf(f_numero, focal_mm, passo_um, declinacao_graus=0.0, k=1.0):
    """A regra NPF, na forma completa publicada pela Société Astronomique du Havre.

        t = k · (16,9·N + 0,1·f + 13,7·p) / (f · cos δ)

    N é o número de abertura, f a focal em milímetros, p o passo do píxel em
    micrómetros, δ a declinação e k o grau de alongamento que aceitas (1 a 3).
    Fonte: <https://sahavre.fr/wp/regle-npf-rule/>, aberta a 2026-09-18.
    """
    cos = math.cos(math.radians(declinacao_graus))
    return k * (16.9 * f_numero + 0.1 * focal_mm + 13.7 * passo_um) / (focal_mm * cos)


if __name__ == "__main__":
    print("Uma objetiva de 50 mm a f/2, píxeis de 4 µm:")
    print("  área da pupila     %8.2f cm²" % area_pupila_cm2(50, 2))
    print("  escala             %8.2f ″/px" % escala_arcsec_px(50, 4.0))
    print("  fotões de V=0      %8.3g por cm² e por segundo" % fotoes_por_cm2_s(0))
    print("  electrões de V=6 em 10 s: %.0f" % electroes_estrela(6, 50, 2, 10))
