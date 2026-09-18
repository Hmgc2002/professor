#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pilha.py — calibrar, encontrar estrelas, alinhar e empilhar.

É o *pipeline* todo, e cabe em duzentas linhas porque cada passo faz **uma** coisa:

    bruto ─ zero ─ escuro·t ─── ÷ plano ──→ alinhado ──→ empilhado
      │        │        │           │           │            │
   o que  o zero do  o que o    a resposta   a Terra     a média que
   saiu    ADC       calor fez  do sistema   rodou       mata o ruído

🔴 A ordem não é arbitrária e não se pode trocar. O zero subtrai-se primeiro porque
está em tudo o resto, incluindo nos escuros e nos planos. A divisão pelo plano vem
**depois** das subtrações porque o plano é multiplicativo: dividir antes de subtrair
divide também o offset, e o offset não passou pela ótica.
"""

import math
import sys

import numpy as np

from imagem import ler_pgm

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# ------------------------------------------------------- juntar calibrações

def mestre(imagens, metodo="mediana"):
    """Combina N calibrações numa só.

    Mediana e não média, por omissão: um raio cósmico ou um satélite numa das poses
    entra na média e não entra na mediana. O preço é ruído — a mediana de N amostras
    normais tem ≈1,25 vezes o desvio da média — e é um preço que se paga de bom grado
    numa calibração, onde N é grande e barato.
    """
    pilha = np.stack(imagens)
    return np.median(pilha, axis=0) if metodo == "mediana" else np.mean(pilha, axis=0)


def calibrar(luz, zero_m=None, escuro_m=None, plano_m=None,
             t_luz=1.0, t_escuro=1.0, zero_do_escuro=True, zero_do_plano=True):
    """Aplica o modelo do sinal a uma pose.

        calibrada = (luz − zero − escuro·(t_luz/t_escuro)) / plano_normalizado

    ⚠️ Se o teu «escuro» foi tirado com o mesmo tempo da luz — que é o caso normal —
    o fator é 1 e o escuro já traz o zero lá dentro. Aí **não** se subtrai o zero duas
    vezes: é o erro mais comum desta lição, e dá um fundo negativo.
    """
    x = np.array(luz, dtype=np.float64)
    if escuro_m is not None:
        e = np.array(escuro_m, dtype=np.float64) * (t_luz / t_escuro)
        if zero_do_escuro and zero_m is not None:
            e = e - np.array(zero_m, dtype=np.float64) * (t_luz / t_escuro)
        x = x - e
    if zero_m is not None:
        x = x - np.array(zero_m, dtype=np.float64)
    if plano_m is not None:
        p = np.array(plano_m, dtype=np.float64)
        # 🔴 O plano também saiu da câmara com o nível de zero em cima. Dividir por
        # um plano que ainda tem o offset corrige menos do que devia, porque o
        # offset é aditivo e não passou pela ótica: a vinhetagem fica por corrigir
        # na proporção do offset. A lição 4 mede o resto que sobra.
        if zero_do_plano and zero_m is not None:
            p = p - np.array(zero_m, dtype=np.float64)
        p = p / np.median(p)
        x = x / np.where(p > 1e-6, p, 1e-6)
    return x


# ------------------------------------------------------- encontrar estrelas

def fundo_e_ruido(img, amostras=20000, semente=3):
    """Mediana e desvio robusto do fundo.

    O desvio usa o **MAD** (desvio absoluto mediano) vezes 1,4826, e não o
    desvio-padrão: o desvio-padrão de um campo com estrelas mede sobretudo as
    estrelas. O 1,4826 é o fator que faz o MAD coincidir com σ numa gaussiana
    — é 1/Φ⁻¹(3/4), e não um número inventado.
    """
    rng = np.random.default_rng(semente)
    v = img.ravel()
    if v.size > amostras:
        v = v[rng.integers(0, v.size, amostras)]
    med = np.median(v)
    return med, 1.4826 * np.median(np.abs(v - med))


def detetar(img, sigmas=6.0, raio=3, maximo=400):
    """Devolve [(x, y, brilho)] das estrelas, por brilho decrescente.

    Máximos locais acima de `sigmas` vezes o ruído do fundo. Não é o DAOPHOT — não
    ajusta perfis nem separa estrelas encostadas — e para alinhar não precisa de ser.
    """
    fundo, sigma = fundo_e_ruido(img)
    limiar = fundo + sigmas * sigma
    alt, larg = img.shape
    ys, xs = np.nonzero(img > limiar)
    picos = []
    for y, x in zip(ys, xs):
        if y < raio or x < raio or y >= alt - raio or x >= larg - raio:
            continue
        janela = img[y - raio:y + raio + 1, x - raio:x + raio + 1]
        if img[y, x] >= janela.max():
            picos.append((x, y, img[y, x] - fundo))
    picos.sort(key=lambda p: -p[2])

    # Máximos vizinhos do mesmo astro: fica o mais brilhante.
    limpos = []
    for x, y, b in picos:
        if all((x - u) ** 2 + (y - v) ** 2 > (2 * raio) ** 2 for u, v, _ in limpos):
            limpos.append((x, y, b))
        if len(limpos) >= maximo:
            break
    return [(centroide(img, x, y, raio, fundo) + (b,)) for x, y, b in limpos]


def centroide(img, x, y, raio=3, fundo=None):
    """Centro de massa da luz numa janela — a posição ao décimo de píxel.

    O píxel mais brilhante dá a posição a ±0,5 px. O centro de massa dá muito melhor,
    e é isso que permite alinhar sem ver bordas serradas. 🔴 Subtrair o fundo **antes**
    de pesar não é um pormenor: com fundo, o centro de massa é puxado para o centro
    geométrico da janela, e o erro é maior quanto mais fraca for a estrela.
    """
    if fundo is None:
        fundo, _ = fundo_e_ruido(img)
    j = img[y - raio:y + raio + 1, x - raio:x + raio + 1] - fundo
    j = np.maximum(j, 0)
    total = j.sum()
    if total <= 0:
        return float(x), float(y)
    gy, gx = np.mgrid[y - raio:y + raio + 1, x - raio:x + raio + 1]
    return float((gx * j).sum() / total), float((gy * j).sum() / total)


# ------------------------------------------------------- alinhar

def deslocamento(ref, outra, tolerancia=12.0, voltas=3):
    """Deslocamento (dx, dy) que leva `outra` para cima de `ref`, por emparelhamento.

    Emparelha cada estrela com a mais próxima da referência e tira a **mediana** dos
    deslocamentos. Repete, já com o campo aproximado, para apertar. A mediana é o que
    torna isto robusto: bastam metade dos pares certos.
    """
    if not ref or not outra:
        return 0.0, 0.0
    rx = np.array([p[0] for p in ref]); ry = np.array([p[1] for p in ref])
    ox = np.array([p[0] for p in outra]); oy = np.array([p[1] for p in outra])
    dx = dy = 0.0
    for _ in range(voltas):
        ds = []
        for k in range(len(ox)):
            d2 = (rx - (ox[k] + dx)) ** 2 + (ry - (oy[k] + dy)) ** 2
            i = int(np.argmin(d2))
            if d2[i] < tolerancia ** 2:
                ds.append((rx[i] - ox[k], ry[i] - oy[k]))
        if not ds:
            break
        dx = float(np.median([d[0] for d in ds]))
        dy = float(np.median([d[1] for d in ds]))
    return dx, dy


def deslocar(img, dx, dy, metodo="bilinear"):
    """Move a imagem (dx, dy). «inteiro» arredonda; «bilinear» interpola.

    ⚠️ A interpolação bilinear **suaviza**: mistura píxeis vizinhos e baixa o ruído
    independente entre eles. Uma pilha alinhada assim parece ter menos ruído do que
    tem, porque o ruído ficou correlacionado. A lição 5 mede os dois e o efeito.
    """
    if metodo == "inteiro":
        return np.roll(np.roll(img, int(round(dy)), axis=0), int(round(dx)), axis=1)

    ix, iy = math.floor(dx), math.floor(dy)
    fx, fy = dx - ix, dy - iy
    base = np.roll(np.roll(img, iy, axis=0), ix, axis=1)
    dir_ = np.roll(base, 1, axis=1)
    baixo = np.roll(base, 1, axis=0)
    diag = np.roll(baixo, 1, axis=1)
    return ((1 - fx) * (1 - fy) * base + fx * (1 - fy) * dir_
            + (1 - fx) * fy * baixo + fx * fy * diag)


def alinhar(imagens, metodo="bilinear", sigmas=6.0):
    """Alinha todas pela primeira. Devolve (lista alinhada, lista de deslocamentos)."""
    ref = detetar(imagens[0], sigmas=sigmas)
    saida, deslocs = [imagens[0]], [(0.0, 0.0)]
    for img in imagens[1:]:
        dx, dy = deslocamento(ref, detetar(img, sigmas=sigmas))
        deslocs.append((dx, dy))
        saida.append(deslocar(img, dx, dy, metodo))
    return saida, deslocs


# ------------------------------------------------------- empilhar

def empilhar(imagens, metodo="media", kappa=3.0, voltas=3):
    """Combina as poses alinhadas.

    * **media** — o melhor ruído possível, e nenhuma defesa contra intrusos.
    * **mediana** — imune a aviões e satélites, ≈25 % pior em ruído.
    * **sigma** — média com rejeição: corta o que estiver a mais de `kappa` desvios
      da mediana, e volta a fazer a conta. Fica quase tão bom como a média e quase
      tão robusto como a mediana, que é a razão de existir.
    """
    p = np.stack(imagens)
    if metodo == "media":
        return p.mean(axis=0)
    if metodo == "mediana":
        return np.median(p, axis=0)

    bons = np.ones(p.shape, dtype=bool)
    for _ in range(voltas):
        n = bons.sum(axis=0)
        med = np.median(np.where(bons, p, np.nan), axis=0)
        desv = np.sqrt(np.nansum(np.where(bons, (p - med) ** 2, 0), axis=0)
                       / np.maximum(n - 1, 1))
        novos = np.abs(p - med) <= kappa * np.maximum(desv, 1e-9)
        novos |= (n <= 2)                      # nunca deixar menos de duas amostras
        if np.array_equal(novos, bons):
            break
        bons = novos
    soma = np.where(bons, p, 0).sum(axis=0)
    n = np.maximum(bons.sum(axis=0), 1)
    return soma / n


def taxa_rejeicao(imagens, kappa=3.0):
    """Que fração das amostras é que o sigma-clip deitou fora. Um número que se vigia."""
    p = np.stack(imagens)
    med = np.median(p, axis=0)
    desv = p.std(axis=0, ddof=1)
    fora = np.abs(p - med) > kappa * np.maximum(desv, 1e-9)
    return float(fora.mean())


def carregar(padrao, n=None):
    """Lê PGMs por ordem alfabética. `padrao` é um glob."""
    import glob
    caminhos = sorted(glob.glob(padrao))[:n]
    return [ler_pgm(c)[0] for c in caminhos], caminhos
