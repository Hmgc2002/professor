#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""projeto.py — o pipeline inteiro, de uma pasta de ficheiros ao relatório.

    python3 campo.py                        # se ainda não tiveres poses tuas
    python3 projeto.py sessao --focal 50 --abertura 2 --passo 4 --pose 8

🔴 Este programa recusa-se a correr sem `PREVISOES.md`. A razão está na lição 9 e não
é burocracia: uma previsão escrita depois de ver o resultado não é uma previsão, é uma
justificação. O ficheiro tem de existir, e o teu *commit* dele tem de ser anterior ao
da entrega — é isso que torna a afirmação verificável por outra pessoa.

O relatório sai em texto, para colar em `topicos/astrofotografia/respostas/`, e a
imagem final sai em PNG, só para olhar.
"""

import argparse
import glob
import math
import os
import sys

import numpy as np

import esticar
import foton
import medir
import pilha
from imagem import escrever_png, ler_pgm

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def carregar(pasta, prefixo):
    caminhos = sorted(glob.glob(os.path.join(pasta, prefixo + "*.pgm")))
    return [ler_pgm(c)[0] for c in caminhos], caminhos


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pasta")
    p.add_argument("--focal", type=float, required=True, help="milímetros")
    p.add_argument("--abertura", type=float, required=True, help="número f")
    p.add_argument("--passo", type=float, required=True, help="micrómetros")
    p.add_argument("--pose", type=float, required=True, help="segundos")
    p.add_argument("--alvo", type=float, nargs=2, metavar=("X", "Y"),
                   help="coordenadas da estrela de referência (por omissão, a mais brilhante)")
    p.add_argument("--metodo", default="sigma", choices=("media", "mediana", "sigma"))
    p.add_argument("--desloc", default="inteiro", choices=("inteiro", "bilinear"),
                   help="🔴 «inteiro» para medir; «bilinear» só para a imagem final")
    p.add_argument("--previsoes", default="PREVISOES.md")
    a = p.parse_args()

    if not os.path.exists(a.previsoes):
        print("🔴 Falta o ficheiro %s." % a.previsoes, file=sys.stderr)
        print("   Escreve as tuas previsões primeiro — SNR de uma pose, ganho esperado,",
              file=sys.stderr)
        print("   FWHM, brilho do céu — e faz commit. Só depois se mede.", file=sys.stderr)
        return 2

    luzes, nomes = carregar(a.pasta, "luz-")
    zeros, _ = carregar(a.pasta, "zero-")
    escuros, _ = carregar(a.pasta, "escuro-")
    planos, _ = carregar(a.pasta, "plano-")
    if not luzes:
        print("Nenhuma pose luz-*.pgm em %s" % a.pasta, file=sys.stderr)
        return 2
    print("%d luzes · %d zeros · %d escuros · %d planos"
          % (len(luzes), len(zeros), len(escuros), len(planos)))

    # --- o que se mede antes de calibrar seja o que for
    if len(planos) >= 2 and len(zeros) >= 2:
        ganho, leitura = medir.ganho_e_leitura(planos[0], planos[1], zeros[0], zeros[1])
        topo = 100 * float((planos[0] >= planos[0].max()).mean())
        if np.median(planos[0]) > 0.75 * planos[0].max():
            print("⚠️ os planos estão expostos a %.0f %% do máximo — o ganho pode sair alto"
                  % (100 * np.median(planos[0]) / planos[0].max()))
    else:
        ganho, leitura = 1.0, float("nan")
        print("⚠️ sem dois planos e dois zeros não há ganho medido; assume-se 1 e⁻/ADU")

    zero_m = pilha.mestre(zeros, "media") if zeros else None
    escuro_m = pilha.mestre(escuros, "media") if escuros else None
    plano_m = pilha.mestre(planos) if planos else None

    cals = [pilha.calibrar(l, zero_m, escuro_m, plano_m, a.pose, a.pose) for l in luzes]
    fundo_calibrado = float(np.median(cals[0]))
    if fundo_calibrado < 0:
        print("🔴 a mediana da primeira pose calibrada é %.1f ADU — negativa."
              % fundo_calibrado)
        print("   Sintoma clássico de subtrair o nível de zero duas vezes (lição 4).")

    alinhadas, deslocs = pilha.alinhar(cals, metodo=a.desloc)
    empilhada = pilha.empilhar(alinhadas, a.metodo)

    if a.alvo:
        ax, ay = a.alvo
    else:
        detetadas = pilha.detetar(empilhada, sigmas=8.0)
        if not detetadas:
            print("Nenhuma estrela detetada acima de 8σ.", file=sys.stderr)
            return 2
        ax, ay = detetadas[0][0], detetadas[0][1]
    ax, ay = pilha.centroide(empilhada, int(round(ax)), int(round(ay)), raio=5)

    n = len(cals)
    uma = medir.fotometria(cals[0], *pilha.centroide(cals[0], int(round(ax)),
                                                     int(round(ay)), raio=5),
                           ganho_e_adu=ganho)
    pil = medir.fotometria(empilhada, ax, ay, ganho_e_adu=ganho, n_poses=n)

    # 🔴 A transparência mede-se nas poses **alinhadas**: nas brutas, a estrela está
    # em coordenadas diferentes em cada uma, e medir sempre no mesmo sítio dá lixo
    # (na primeira versão deste ficheiro deu «mínimo −0,00, mediana 0,30»).
    fluxos = [medir.fotometria(c, ax, ay, ganho_e_adu=ganho)["fluxo_adu"]
              for c in alinhadas]
    transparencia = np.array(fluxos) / max(fluxos)

    esc = foton.escala_arcsec_px(a.focal, a.passo)
    linhas = [["grandeza", "valor", "como foi medido"],
              ["poses", "%d × %.1f s = %.1f min" % (n, a.pose, n * a.pose / 60),
               "contadas"],
              ["escala", "%.2f ″/px" % esc, "206265·p/f"],
              ["ganho", "%.3f e⁻/ADU" % ganho, "dois planos e dois zeros"],
              ["ruído de leitura", "%.2f e⁻" % leitura, "dos dois zeros"],
              ["FWHM da pilha", "%.2f px = %.1f ″" % (medir.fwhm(empilhada, ax, ay),
                                                      medir.fwhm(empilhada, ax, ay) * esc),
               "segundo momento, janela iterada"],
              ["fundo do céu", "%.1f ADU" % float(np.median(empilhada)),
               "mediana da pilha"],
              ["brilho do céu",
               "%.2f mag/arcsec²" % medir.brilho_ceu(float(np.median(empilhada)),
                                                     a.pose, ganho, a.focal,
                                                     a.abertura, a.passo),
               "⚠️ assume qe=0,5 e T=0,9"],
              ["transparência",
               "mín %.2f · mediana %.2f" % (transparencia.min(),
                                            float(np.median(transparencia))),
               "fluxo da estrela, pose a pose"],
              ["SNR de uma pose", "%.2f" % uma["snr"], "abertura + anel"],
              ["SNR da pilha", "%.2f" % pil["snr"], "idem, com n_poses=%d" % n],
              ["ganho medido", "×%.2f" % (pil["snr"] / uma["snr"]), ""],
              ["previsto √N", "×%.2f" % math.sqrt(n), ""],
              ["diferença", "%+.1f %%" % (100 * (pil["snr"] / uma["snr"]
                                                 / math.sqrt(n) - 1)), ""]]
    print()
    medir.relatorio(linhas)

    print()
    print("O QUE LIMITOU — responde tu, com estes números na mão:")
    ceu_e = float(np.median(empilhada)) * ganho
    print("  · céu por pose:      %.1f e⁻/px      (variância %.0f em 9 px)"
          % (ceu_e, 9 * ceu_e))
    print("  · leitura:           %.2f e⁻         (variância %.0f em 9 px)"
          % (leitura, 9 * leitura ** 2))
    print("  · sinal do alvo:     %.0f e⁻         (variância %.0f)"
          % (uma["fluxo_adu"] * ganho, uma["fluxo_adu"] * ganho))
    print("  A maior destas três é o que limitou. Escreve-o na primeira linha do")
    print("  relatório, antes de mostrares a imagem.")

    y, par = esticar.automatico(empilhada)
    escrever_png(os.path.join(a.pasta, "final.png"), esticar.para_8bits(y))
    print()
    print("imagem escrita em %s (ponto preto %.1f ADU, ponto médio %.4f)"
          % (os.path.join(a.pasta, "final.png"), par["ponto_preto"], par["ponto_medio"]))
    print("🔴 A imagem é para olhar. As medições acima saíram da pilha linear.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
