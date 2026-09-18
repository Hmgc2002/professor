#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""campo.py — fabrica poses sintéticas que se parecem com as que a tua câmara dá.

Serve para duas coisas, e a segunda é a importante:

1. **Trabalhar sem céu.** Em Lisboa, em novembro, podes ficar três semanas sem uma
   noite limpa. O *pipeline* não tem de esperar.
2. **Saber a resposta certa.** Numa pose tua não sabes quantos electrões aquela
   estrela deu, nem onde ficava o centro dela ao décimo de píxel. Aqui sabes, porque
   foste tu que os puseste — e é por isso que se pode **medir o erro do teu método**,
   em vez de olhar para a imagem e achar que está bem.

🔴 O que sai daqui não é uma fotografia: é um modelo. O que aparece só neste modelo é
do modelo, não do céu (`PROCESSO.md`, registo de falhas, 2026-09-16). Cada defeito
simulado está aqui porque existe num sensor real, e está dito qual é.

    python3 campo.py           # escreve uma sessão completa em ./sessao/
"""

import math
import os
import sys

import numpy as np

from imagem import escrever_pgm, escrever_fits, escrever_png, ler_pgm

# O `numpy` não traz a função erro e não há `scipy` neste curso (D-028). A função
# erro **está** na biblioteca padrão, em `math`, só que é escalar: envolve-se uma vez.
erf_vec = np.frompyfunc(math.erf, 1, 1)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


class Camara:
    """Os seis números que descrevem um sensor. Todos se medem — a lição 4 diz como.

    * `ganho_e_adu` — quantos electrões valem um nível do ADC.
    * `leitura_e` — desvio-padrão do ruído que a eletrónica acrescenta a cada leitura.
    * `escuro_e_s` — electrões por píxel e por segundo gerados por agitação térmica.
    * `nivel_zero` — o deslocamento que o fabricante põe para que o ruído não seja
      cortado em zero. É o *bias*, e 🔴 **não** tem nada que ver com o *bias* das
      cassetes: ali é uma corrente de alta frequência na gravação magnética, aqui é
      um offset somado ao zero do conversor.
    * `poco_e` — o poço: quantos electrões cabem num píxel antes de saturar.
    * `bits` — a resolução do conversor.
    """

    def __init__(self, passo_um=4.0, ganho_e_adu=1.0, leitura_e=3.0, escuro_e_s=0.05,
                 nivel_zero=512, poco_e=40000, bits=14):
        self.passo_um = passo_um
        self.ganho_e_adu = ganho_e_adu
        self.leitura_e = leitura_e
        self.escuro_e_s = escuro_e_s
        self.nivel_zero = nivel_zero
        self.poco_e = poco_e
        self.bits = bits
        self.maximo_adu = 2 ** bits - 1

    def __repr__(self):
        return ("Camara(passo=%.1f µm, ganho=%.2f e⁻/ADU, leitura=%.1f e⁻, "
                "escuro=%.3f e⁻/s, zero=%d ADU, poço=%d e⁻, %d bits)"
                % (self.passo_um, self.ganho_e_adu, self.leitura_e, self.escuro_e_s,
                   self.nivel_zero, self.poco_e, self.bits))


class Campo:
    """Um pedaço de céu: estrelas (x, y, electrões por segundo) e um fundo."""

    def __init__(self, largura=512, altura=512, semente=20260918):
        self.largura, self.altura = largura, altura
        self.rng = np.random.default_rng(semente)
        self.estrelas = []          # (x, y, taxa em e⁻/s)

    def povoar(self, n=120, taxa_min=30.0, taxa_max=6000.0):
        """Estrelas ao acaso, com uma distribuição de brilho muito desequilibrada.

        Poucas brilhantes e muitas fracas — como no céu. A distribuição exata aqui é
        uma lei de potência escolhida por conveniência, **não** medida: serve para
        o campo não ficar com todas as estrelas iguais, e nada no curso depende dela.
        """
        u = self.rng.random(n)
        taxas = taxa_min * (taxa_max / taxa_min) ** (u ** 2.5)
        for k in range(n):
            self.estrelas.append((self.rng.uniform(8, self.largura - 8),
                                  self.rng.uniform(8, self.altura - 8),
                                  float(taxas[k])))
        return self

    def acrescentar(self, x, y, taxa_e_s):
        """Uma estrela num sítio que tu escolhes — a estrela de teste das lições."""
        self.estrelas.append((float(x), float(y), float(taxa_e_s)))
        return self


def _gaussiana_integrada(centros, n, sigma):
    """Fração de luz em cada píxel de uma linha, para uma gaussiana centrada em `centros`.

    Não se avalia a gaussiana no centro do píxel: **integra-se** sobre o píxel, com a
    função erro. A diferença importa quando o sigma é pequeno (estrelas apertadas),
    que é exatamente o caso em que se mede a largura — e uma FWHM medida sobre uma
    PSF mal amostrada sai errada de forma sistemática.
    """
    borda = np.arange(n + 1) - 0.5
    d = (borda[None, :] - np.asarray(centros)[:, None]) / (sigma * math.sqrt(2))
    cdf = 0.5 * (1.0 + erf_vec(d).astype(np.float64))
    return np.diff(cdf, axis=1)


def psf(campo, fwhm_px, desloc=(0.0, 0.0), arrasto_px=0.0, passos=12):
    """Imagem do campo em electrões por segundo, sem ruído: só ótica e seguimento.

    `arrasto_px` é o comprimento do traço deixado pela rotação da Terra durante a
    pose. Faz-se somando `passos` posições ao longo do traço: é o que acontece
    fisicamente — a mesma estrela a depositar luz em píxeis sucessivos.
    """
    sigma = fwhm_px / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    img = np.zeros((campo.altura, campo.largura))
    if not campo.estrelas:
        return img

    xs = np.array([e[0] for e in campo.estrelas]) + desloc[0]
    ys = np.array([e[1] for e in campo.estrelas]) + desloc[1]
    taxas = np.array([e[2] for e in campo.estrelas])

    n = max(1, passos if arrasto_px > 0.5 else 1)
    for k in range(n):
        dx = (k / (n - 1) - 0.5) * arrasto_px if n > 1 else 0.0
        fx = _gaussiana_integrada(xs + dx, campo.largura, sigma)
        fy = _gaussiana_integrada(ys, campo.altura, sigma)
        for i in range(len(taxas)):
            img += (taxas[i] / n) * np.outer(fy[i], fx[i])
    return img


def resposta_plana(camara, largura, altura, poeiras=6, semente=7):
    """O «flat»: quanto de cada píxel chega ao ficheiro, relativamente ao melhor píxel.

    Duas causas, ambas reais e ambas multiplicativas:
    **vinhetagem** (a pupila vista de canto é menor do que vista do centro) e
    **poeiras** no sensor, que fazem sombras desfocadas em forma de anel.
    """
    rng = np.random.default_rng(semente)
    y, x = np.mgrid[0:altura, 0:largura]
    cx, cy = (largura - 1) / 2.0, (altura - 1) / 2.0
    r = np.hypot(x - cx, y - cy) / math.hypot(cx, cy)
    plano = np.cos(np.arctan(r * 0.7)) ** 4          # lei do cos⁴, aproximada
    for _ in range(poeiras):
        px, py = rng.uniform(0, largura), rng.uniform(0, altura)
        raio = rng.uniform(6, 16)
        d = np.hypot(x - px, y - py)
        plano *= 1.0 - 0.25 * np.exp(-(d / raio) ** 2) * (d < 3 * raio)
    plano *= 1.0 + 0.01 * rng.standard_normal((altura, largura))   # ganho píxel a píxel
    return plano / plano.max()


def padrao_escuro(camara, largura, altura, quentes=40, semente=11):
    """Corrente escura por píxel e por segundo, com píxeis quentes.

    A corrente escura **não** é igual em todos os píxeis: uns têm defeitos de rede e
    geram dezenas de vezes mais. São os píxeis quentes, e são fixos — aparecem na
    mesma coordenada em todas as poses, o que é precisamente o que os torna
    removíveis (lição 4) e o que torna o *dithering* eficaz (lição 5).
    """
    rng = np.random.default_rng(semente)
    base = camara.escuro_e_s * (1.0 + 0.25 * rng.standard_normal((altura, largura)))
    base = np.clip(base, 0, None)
    for _ in range(quentes):
        base[rng.integers(0, altura), rng.integers(0, largura)] += rng.uniform(5, 60)
    return base


def padrao_zero(camara, largura, altura, semente=13):
    """O nível de zero não é uma constante: tem estrutura de coluna.

    O ADC lê coluna a coluna e cada amplificador tem o seu desvio. Por isso um
    «bias master» não é um número, é uma imagem — e é por isso que se mede em vez
    de se subtrair uma constante.
    """
    rng = np.random.default_rng(semente)
    colunas = 1.5 * rng.standard_normal(largura)
    return camara.nivel_zero + np.tile(colunas, (altura, 1))


class Sessao:
    """Tudo o que se mantém fixo entre poses da mesma noite: o sensor e os seus defeitos."""

    def __init__(self, camara, largura=512, altura=512, semente=20260918):
        self.camara = camara
        self.largura, self.altura = largura, altura
        self.plano = resposta_plana(camara, largura, altura)
        self.escuro = padrao_escuro(camara, largura, altura)
        self.zero = padrao_zero(camara, largura, altura)
        self.rng = np.random.default_rng(semente)

    def _ler(self, electroes):
        """Do sinal em electrões ao número inteiro que sai da câmara.

        A ordem importa e é a ordem física: o poço satura **antes** do conversor,
        o ruído de leitura entra **depois** do poço, e o corte a 2^bits−1 é do ADC.
        """
        c = self.camara
        electroes = np.minimum(electroes, c.poco_e)
        adu = electroes / c.ganho_e_adu
        adu = adu + self.zero + self.rng.normal(0, c.leitura_e / c.ganho_e_adu,
                                                electroes.shape)
        return np.clip(np.rint(adu), 0, c.maximo_adu)

    def pose(self, campo, t_s, ceu_e_px_s, fwhm_px=2.6, desloc=(0.0, 0.0),
             arrasto_px=0.0, transparencia=1.0):
        """Uma pose de céu: estrelas + céu + escuro, tudo passado por Poisson.

        🔴 O Poisson aplica-se à **soma** dos que chegam, uma só vez. Aplicar Poisson
        a cada parcela e somar depois dá a mesma variância por acaso neste caso, mas
        deixa de dar assim que houver uma parcela que não seja de contagem — e é um
        erro que se propaga silenciosamente.
        """
        sinal = psf(campo, fwhm_px, desloc, arrasto_px) * t_s * transparencia
        chegam = (sinal + ceu_e_px_s * t_s) * self.plano + self.escuro * t_s
        return self._ler(self.rng.poisson(np.maximum(chegam, 0)).astype(np.float64))

    def escuro_bruto(self, t_s):
        """Um «dark»: obturador fechado, mesmo tempo, mesma temperatura."""
        return self._ler(self.rng.poisson(self.escuro * t_s).astype(np.float64))

    def zero_bruto(self):
        """Um «bias»: a pose mais curta que a câmara consegue, obturador fechado."""
        return self._ler(np.zeros((self.altura, self.largura)))

    def plano_bruto(self, nivel_e=7000.0):
        """Um «flat»: superfície uniforme, exposta a meio da escala.

        🔴 «Meio da escala» é do **conversor**, não do poço. Com 14 bits e ganho 1,
        o ficheiro satura aos 16383 ADU muito antes de o poço encher aos 40000 e⁻ —
        e um plano saturado mede zero variância, o que faz o ganho medido na lição 4
        sair alto sem nenhum aviso. O valor por omissão deixa margem de propósito.
        """
        c = self.camara
        if (nivel_e / c.ganho_e_adu + c.nivel_zero) > 0.9 * c.maximo_adu:
            print("⚠️ plano_bruto: %.0f e⁻ enchem o conversor (%d ADU). O ganho medido"
                  " a partir deste plano vai sair errado."
                  % (nivel_e, c.maximo_adu), file=sys.stderr)
        chegam = nivel_e * self.plano
        return self._ler(self.rng.poisson(chegam).astype(np.float64))


def escrever_sessao(pasta="sessao", n_luz=32, t_s=8.0, ceu_e_px_s=12.0,
                    arrasto_px=0.0, deriva_px=6.0, semente=20260918):
    """Uma noite inteira em ficheiros: luzes, escuros, planos e zeros.

    A deriva entre poses é de propósito e não é um defeito: sem tripé perfeito o
    enquadramento desloca-se, e **queremos** que se desloque (lição 5).
    """
    os.makedirs(pasta, exist_ok=True)
    cam = Camara()
    ses = Sessao(cam, semente=semente)
    campo = Campo(semente=semente).povoar(120).acrescentar(256, 256, 1800.0)
    rng = np.random.default_rng(semente + 1)

    desloc = []
    for i in range(n_luz):
        d = (rng.uniform(-deriva_px, deriva_px), rng.uniform(-deriva_px, deriva_px))
        desloc.append(d)
        pose = ses.pose(campo, t_s, ceu_e_px_s, desloc=d, arrasto_px=arrasto_px)
        escrever_pgm(os.path.join(pasta, "luz-%03d.pgm" % i), pose, cam.maximo_adu)
    for i in range(16):
        escrever_pgm(os.path.join(pasta, "escuro-%03d.pgm" % i),
                     ses.escuro_bruto(t_s), cam.maximo_adu)
    for i in range(16):
        escrever_pgm(os.path.join(pasta, "zero-%03d.pgm" % i),
                     ses.zero_bruto(), cam.maximo_adu)
    for i in range(16):
        escrever_pgm(os.path.join(pasta, "plano-%03d.pgm" % i),
                     ses.plano_bruto(), cam.maximo_adu)

    with open(os.path.join(pasta, "VERDADE.txt"), "w", encoding="utf-8") as f:
        f.write("# O que este campo é de facto. Não existe para uma pose tua.\n")
        f.write("# camara: %r\n" % cam)
        f.write("# ceu: %.3f e-/px/s · pose: %.1f s · arrasto: %.2f px\n"
                % (ceu_e_px_s, t_s, arrasto_px))
        f.write("x;y;taxa_e_s\n")
        for x, y, tx in campo.estrelas:
            f.write("%.4f;%.4f;%.4f\n" % (x, y, tx))
        f.write("# deslocamentos aplicados a cada luz (dx;dy)\n")
        for i, d in enumerate(desloc):
            f.write("# luz-%03d %.4f;%.4f\n" % (i, d[0], d[1]))
    return pasta, cam, ses, campo, desloc


if __name__ == "__main__":
    pasta, cam, ses, campo, _ = escrever_sessao()
    print("escrita a sessão em ./%s/" % pasta)
    print(cam)
    print("%d estrelas · %d luzes + 16 escuros + 16 planos + 16 zeros"
          % (len(campo.estrelas), 32))
    uma, _ = ler_pgm(os.path.join(pasta, "luz-000.pgm"))
    print("luz-000: mediana %.1f ADU · máximo %.0f ADU" % (np.median(uma), uma.max()))
    escrever_png(os.path.join(pasta, "luz-000.png"),
                 255 * (np.clip(uma, np.percentile(uma, 1), np.percentile(uma, 99.9))
                        - np.percentile(uma, 1))
                 / (np.percentile(uma, 99.9) - np.percentile(uma, 1)))
    escrever_fits(os.path.join(pasta, "luz-000.fits"), uma,
                  extra=[("EXPTIME", 8, "segundos"), ("GAIN", 1.0, "e-/ADU")])
    print("e os mesmos dados em luz-000.png (para ver) e luz-000.fits (para guardar)")
