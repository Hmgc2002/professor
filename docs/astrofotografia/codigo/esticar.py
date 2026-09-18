#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esticar.py — do ficheiro linear à imagem que se vê.

Uma pose astronómica é **linear**: o número no ficheiro é proporcional aos fotões.
Isso é o que a torna mensurável e é o que a torna invisível — o céu está em 3 % da
escala e a nebulosa em 3,2 %, e num ecrã isso é preto contra preto.

Esticar é escolher a função que leva [mínimo, máximo] a [0, 255]. **Não** é «aumentar
o brilho»: aumentar o brilho é multiplicar, e multiplicar uma imagem linear satura as
estrelas antes de a nebulosa aparecer, porque a razão entre as duas não muda.

🔴 A partir daqui a imagem deixa de servir para medir. Mede-se primeiro, estica-se
depois — e guarda-se a linear.
"""

import math
import sys

import numpy as np

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def normalizar(img, corte_baixo=0.0, corte_alto=None):
    """Leva a imagem a [0, 1], cortando abaixo de `corte_baixo`.

    `corte_baixo` é o **ponto preto**, e é a decisão com mais consequências de toda
    a lição 6: pô-lo acima do céu apaga o que é mais fraco do que o céu, e isso não
    se desfaz.
    """
    alto = img.max() if corte_alto is None else corte_alto
    if alto <= corte_baixo:
        return np.zeros_like(img)
    return np.clip((img - corte_baixo) / (alto - corte_baixo), 0.0, 1.0)


def asinh(img, suavidade=0.01, corte_baixo=0.0):
    """Esticamento arco-seno hiperbólico.

        y = asinh(x / β) / asinh(1 / β)

    Perto de zero, asinh(u) ≈ u: o fundo continua **linear**, e portanto continua a
    parecer o que é. Longe de zero, asinh(u) ≈ ln(2u): as estrelas brilhantes são
    comprimidas em vez de saturarem, e mantêm a cor e a estrutura.

    É a função proposta por Lupton et al. (2004), PASP 116, 133, exatamente por isto:
    «allows us to show faint objects while simultaneously preserving the structure of
    brighter objects in the field, such as the spiral arms of large galaxies».
    """
    x = normalizar(img, corte_baixo)
    b = max(suavidade, 1e-9)
    return np.arcsinh(x / b) / math.asinh(1.0 / b)


def mtf(img, ponto_medio=0.25, corte_baixo=0.0):
    """Função de transferência de meios-tons, com um só parâmetro.

        y = ((m − 1)·x) / ((2m − 1)·x − m)

    Leva 0 a 0, 1 a 1, e `ponto_medio` a 0,5. É a forma usada pelos programas de
    astrofotografia para o esticamento automático, e a sua virtude é ser monótona e
    invertível: nada do que ela faz destrói a ordem entre dois píxeis.
    """
    x = normalizar(img, corte_baixo)
    m = min(max(ponto_medio, 1e-6), 1 - 1e-6)
    return ((m - 1.0) * x) / ((2.0 * m - 1.0) * x - m)


def automatico(img, alvo_fundo=0.12, sigmas_abaixo=2.8):
    """Escolhe sozinho o ponto preto e o ponto médio, e diz quais escolheu.

    O ponto preto fica alguns desvios **abaixo** da mediana do fundo, não na mediana:
    cortar na mediana deita fora metade do ruído do céu, e com ele o sinal que está
    por baixo. O ponto médio é o que leva a mediana do fundo a `alvo_fundo`.

    Devolve (imagem, {parâmetros}) — 🔴 a segunda parte é o que faz isto ser
    reprodutível em vez de mágico.
    """
    med = float(np.median(img))
    sigma = 1.4826 * float(np.median(np.abs(img - med)))
    preto = med - sigmas_abaixo * sigma
    x = normalizar(img, preto)
    med_n = float(np.median(x))
    # Resolve m tal que mtf(b) = a, com b = mediana normalizada e a = alvo.
    #   ((m−1)·b) / ((2m−1)·b − m) = a   ⟹   m = b(1−a) / (a + b − 2ab)
    # ⚠️ Trocar o a pelo b aqui dá um m perto de 1, que **escurece** em vez de
    # esticar, e a imagem sai plausível o suficiente para ninguém reparar. Foi
    # apanhado na Fase 3 deste curso, a comparar a razão estrela/fundo antes e
    # depois: não tinha mudado nada.
    a, b = alvo_fundo, med_n
    den = a + b - 2 * a * b
    m = (b * (1 - a) / den) if den != 0 else 0.5
    m = min(max(m, 1e-6), 1 - 1e-6)
    return mtf(img, m, preto), {"ponto_preto": preto, "ponto_medio": m,
                                "mediana_do_fundo": med, "sigma_do_fundo": sigma}


def gradiente_plano(img, margem=8, grau=1, kappa=2.5, voltas=5):
    """Ajusta um plano (ou uma superfície de grau 2) ao fundo e devolve-o.

    O gradiente da poluição luminosa é suave e aditivo: entra pelo lado de onde vem a
    cidade e some para o outro.

    🔴 A parte difícil não é o ajuste, é **escolher os píxeis**. Ajustar a tudo faz o
    plano seguir as estrelas. Ajustar só ao que está abaixo da mediana global parece
    a correção óbvia e **está errado**: com um gradiente, «abaixo da mediana» é quase
    só o lado escuro da imagem, e o declive sai encurtado quase para metade. (Medido
    na Fase 3 deste curso: 23 ADU ajustados para 40 ADU postos.)

    O que funciona é rejeitar por resíduo: ajusta-se a tudo, deitam-se fora os píxeis
    que ficam `kappa` desvios **acima** do ajuste — que são as fontes — e repete-se.
    A rejeição é só de um lado, de propósito: o ruído do fundo é simétrico, as
    estrelas não.
    """
    alt, larg = img.shape
    gy, gx = np.mgrid[0:alt, 0:larg]
    termos = [np.ones_like(gx, dtype=np.float64), gx.astype(np.float64),
              gy.astype(np.float64)]
    if grau >= 2:
        termos += [gx * gx * 1.0, gy * gy * 1.0, gx * gy * 1.0]

    dentro = ((gx >= margem) & (gx < larg - margem)
              & (gy >= margem) & (gy < alt - margem))
    m, coef = dentro.copy(), None
    for _ in range(voltas):
        A = np.stack([t[m] for t in termos], axis=1)
        coef, *_ = np.linalg.lstsq(A, img[m], rcond=None)
        res = img - sum(c * t for c, t in zip(coef, termos))
        s = 1.4826 * np.median(np.abs(res[m] - np.median(res[m])))
        novo = dentro & (res < kappa * s)
        if novo.sum() < 100 or np.array_equal(novo, m):
            break
        m = novo
    return sum(c * t for c, t in zip(coef, termos)), coef


def para_8bits(x):
    """De [0, 1] para [0, 255]."""
    return np.clip(np.rint(x * 255.0), 0, 255)
