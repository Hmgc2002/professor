#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""medir.py — os cinco números que fazem o relatório do projeto.

    escala (″/px) · largura das estrelas (FWHM) · SNR · ganho e ruído de leitura ·
    brilho do céu (mag/arcsec²)

🔴 Todos são medidos **dos teus ficheiros**, nenhum é lido de uma especificação. A
especificação diz o que o fabricante prometeu à temperatura dele; a medição diz o que
o teu sensor fez naquela noite. Quando os dois discordam, o relatório fica mais
interessante, não menos — e o primeiro sítio a procurar a causa é a temperatura.
"""

import math
import sys

import numpy as np

import foton

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def _anel(img, x, y, r_int, r_ext):
    alt, larg = img.shape
    y0, y1 = max(0, int(y - r_ext)), min(alt, int(y + r_ext) + 1)
    x0, x1 = max(0, int(x - r_ext)), min(larg, int(x + r_ext) + 1)
    gy, gx = np.mgrid[y0:y1, x0:x1]
    d = np.hypot(gx - x, gy - y)
    m = (d >= r_int) & (d <= r_ext)
    return img[y0:y1, x0:x1][m]


def _disco(img, x, y, r):
    alt, larg = img.shape
    y0, y1 = max(0, int(y - r) - 1), min(alt, int(y + r) + 2)
    x0, x1 = max(0, int(x - r) - 1), min(larg, int(x + r) + 2)
    gy, gx = np.mgrid[y0:y1, x0:x1]
    d = np.hypot(gx - x, gy - y)
    m = d <= r
    return img[y0:y1, x0:x1][m], int(m.sum())


def desvio_robusto(v, kappa=3.0, voltas=5):
    """Desvio-padrão com rejeição — o estimador de ruído que este curso usa para medir.

    ⚠️ Porque não o MAD, que `pilha.fundo_e_ruido` usa: o MAD é ótimo para *detetar*
    (onde o que interessa é não ser enganado por estrelas) mas é um estimador
    quantizado quando os dados também o são, e numa pose de 14 bits dividida pelo
    plano isso vale alguns por cento. Alguns por cento aqui são a diferença entre
    «a pilha deu √N» e «a pilha deu mais do que √N», que é impossível.

    Isto é uma média-com-rejeição da variância: corta o que está a mais de `kappa`
    desvios e volta a contar, até estabilizar.
    """
    v = np.asarray(v, dtype=np.float64)
    m = np.ones(v.shape, dtype=bool)
    for _ in range(voltas):
        med, s = np.median(v[m]), v[m].std(ddof=1)
        novo = np.abs(v - med) < kappa * s
        if novo.sum() < 10 or np.array_equal(novo, m):
            break
        m = novo
    return float(v[m].std(ddof=1))


def fotometria(img, x, y, r_abertura=5.0, r_int=9.0, r_ext=14.0, ganho_e_adu=1.0,
               n_poses=1):
    """Fluxo, fundo, ruído e SNR de uma estrela, por abertura.

    O fundo vem de um **anel** à volta e não do canto da imagem: o céu tem gradiente,
    e um fundo medido longe da estrela mede outro sítio. A mediana do anel também
    ignora as estrelas que por acaso lá caiam.

    O ruído tem os dois termos que a lição 1 derivou, e **medidos**, não assumidos:
    o do céu sai do desvio do anel, o da estrela sai do próprio fluxo (Poisson).

    🔴 `n_poses` não é decoração. Numa **média** de N poses, o fluxo lido continua a
    ser o de uma pose, mas os electrões que o produziram foram N vezes mais: a
    variância de Poisson do próprio astro cai N vezes. Medir a pilha com `n_poses=1`
    conta esse termo N vezes a mais e faz o ganho parecer muito menor do que foi.
    Este erro é fácil de cometer e difícil de ver — foi apanhado na Fase 3 deste curso.
    """
    ceu = _anel(img, x, y, r_int, r_ext)
    fundo = float(np.median(ceu))
    sigma_ceu = desvio_robusto(ceu)

    disco, n_px = _disco(img, x, y, r_abertura)
    fluxo = float(disco.sum() - n_px * fundo)

    var = (n_px * sigma_ceu ** 2
           + max(fluxo, 0.0) / max(ganho_e_adu * n_poses, 1e-9))
    ruido = math.sqrt(var)
    return {"fluxo_adu": fluxo, "fundo_adu": fundo, "sigma_ceu_adu": sigma_ceu,
            "n_px": n_px, "ruido_adu": ruido,
            "snr": fluxo / ruido if ruido > 0 else float("inf")}


def fwhm(img, x, y, palpite=3.0, voltas=4, fator_janela=1.5):
    """Largura a meia altura, em píxeis, pelo segundo momento da luz numa janela.

    Para uma gaussiana, FWHM = 2√(2 ln 2)·σ ≈ 2,3548·σ. Duas decisões, e as duas
    são de medição, não de gosto:

    * **A janela acompanha o resultado.** Mede-se, ajusta-se a janela a 1,5 vezes a
      largura encontrada, mede-se outra vez. Com janela fixa e larga, o segundo
      momento pesa cada píxel por d² e o ruído das bordas domina — o valor medido
      *cresce com o raio*, que é o sintoma pelo qual se apanha o erro.
    * **Não se cortam os valores negativos.** Cortar o ruído negativo do fundo e
      deixar o positivo transforma ruído simétrico em sinal, e o viés cresce com d².

    ⚠️ Há um piso: o próprio píxel tem largura. Uma estrela de FWHM 0 medida numa
    grelha dá √(1/12) de desvio-padrão, ou seja 0,68 px de FWHM — e é por isso que
    uma estrela de 0,8 px mede 1,06. A lição 3 mede este piso.
    """
    alt, larg = img.shape
    f = palpite
    for _ in range(voltas):
        raio = max(2.5, fator_janela * f)
        anel = _anel(img, x, y, raio + 2, raio + 8)
        fundo = float(np.median(anel)) if anel.size > 20 else float(np.median(img))
        y0, y1 = max(0, int(y - raio) - 1), min(alt, int(y + raio) + 2)
        x0, x1 = max(0, int(x - raio) - 1), min(larg, int(x + raio) + 2)
        gy, gx = np.mgrid[y0:y1, x0:x1]
        d2 = (gx - x) ** 2 + (gy - y) ** 2
        p = np.where(d2 <= raio ** 2, img[y0:y1, x0:x1] - fundo, 0.0)
        total = p.sum()
        if total <= 0:
            return float("nan")
        sigma2 = (p * d2).sum() / total / 2.0      # média das duas direções
        f = 2.0 * math.sqrt(2.0 * math.log(2.0)) * math.sqrt(max(sigma2, 0.0))
    return f


def ganho_e_leitura(plano_a, plano_b, zero_a, zero_b):
    """Ganho (e⁻/ADU) e ruído de leitura (e⁻) pelo método da curva de transferência.

    A ideia toda numa linha: **num sinal de Poisson, a variância é igual à média —
    em electrões.** Em ADU, a variância fica dividida pelo ganho ao quadrado e a
    média pelo ganho, portanto média/variância **é** o ganho.

    Usa-se a diferença de dois planos, e não um plano sozinho, porque a diferença
    cancela o padrão fixo (a vinhetagem, as poeiras, o ganho de cada píxel) e deixa
    só o ruído. O fator 2 na variância é porque a diferença de duas variáveis
    independentes tem o dobro da variância.
    """
    mf = float(np.mean(plano_a) + np.mean(plano_b))
    mz = float(np.mean(zero_a) + np.mean(zero_b))
    vf = float(np.var(plano_a - plano_b, ddof=1))
    vz = float(np.var(zero_a - zero_b, ddof=1))
    ganho = (mf - mz) / (vf - vz)
    leitura = ganho * math.sqrt(vz / 2.0)
    return ganho, leitura


def escuro_por_segundo(escuro_m, zero_m, t_s, ganho_e_adu):
    """Corrente escura mediana, em electrões por píxel e por segundo.

    🔴 Os mestres têm de ser combinados por **média** e não por mediana: com meio
    electrão por píxel, a mediana de valores inteiros dá saltos e o resultado sai
    enviesado. E o tempo tem de ser longo — a lição 4 mede o que acontece quando não é.
    """
    return float(np.median(escuro_m - zero_m)) * ganho_e_adu / t_s


def brilho_ceu(fundo_adu_por_px, t_s, ganho_e_adu, focal_mm, f_numero, passo_um,
               transmissao=0.9, qe=0.5):
    """Brilho do céu em magnitudes por segundo de arco quadrado.

    É a conta da lição 0 ao contrário. ⚠️ O resultado depende da transmissão e da
    eficiência quântica assumidas, que tu não mediste: um erro de 2× em `qe` desloca
    o resultado 0,75 mag. Por isso o número serve para **comparar** noites e sítios
    com o mesmo material, e não para publicar.
    """
    e_por_s = fundo_adu_por_px * ganho_e_adu / t_s
    esc = foton.escala_arcsec_px(focal_mm, passo_um)
    area = foton.area_pupila_cm2(focal_mm, f_numero)
    fluxo = e_por_s / (esc ** 2 * area * transmissao * qe)
    return -2.5 * math.log10(fluxo / foton.fotoes_por_cm2_s(0.0))


def relatorio(linhas):
    """Imprime uma tabela simples. O relatório do projeto sai daqui."""
    larg = [max(len(str(l[i])) for l in linhas) for i in range(len(linhas[0]))]
    for k, l in enumerate(linhas):
        print("  ".join(str(c).ljust(larg[i]) for i, c in enumerate(l)).rstrip())
        if k == 0:
            print("  ".join("-" * larg[i] for i in range(len(l))))
