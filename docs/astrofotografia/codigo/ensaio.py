#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ensaio.py — todas as medições que as lições citam, num sítio só.

🔴 Porque é que isto existe: o registo de falhas do `PROCESSO.md` tem **quatro** linhas
sobre números escritos na prosa antes de o código correr, e nenhum deles estava certo.
Aqui, cada número que aparece numa lição sai de uma destas secções. Se mudares o
modelo, corres isto e os números das lições mudam com ele.

    python3 ensaio.py            # tudo
    python3 ensaio.py 5 6        # só as secções 5 e 6
"""

import math
import sys
import time

import numpy as np

import esticar
import foton
import medir
import pilha
from campo import Camara, Campo, Sessao

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# A configuração de referência do curso: uma objetiva normal num sensor comum.
FOCAL, FNUM, PASSO = 50.0, 2.0, 4.0
CEU_URBANO, CEU_ESCURO = 19.0, 21.5       # mag/arcsec², os dois extremos do curso

SECCOES = {}


def seccao(n, titulo):
    def envolver(f):
        SECCOES[n] = (titulo, f)
        return f
    return envolver


def cab(t):
    print()
    print("─" * 74)
    print("  " + t)
    print("─" * 74)


# ═══════════════════════════════════════════════════════════ 0
@seccao(0, "A luz como contagem (lição 0)")
def s0():
    cab("Quantos fotões chegam, e de que depende")
    print("V=0, acima da atmosfera: %.3g fotões por cm² e por segundo"
          % foton.fotoes_por_cm2_s(0))
    print()
    print(" abertura   diâmetro   área      e⁻ de uma estrela V=8 em 10 s")
    for fn in (1.4, 2.0, 2.8, 4.0, 5.6):
        print("   f/%-6.1f %5.1f mm  %6.2f cm²   %10.0f"
              % (fn, FOCAL / fn, foton.area_pupila_cm2(FOCAL, fn),
                 foton.electroes_estrela(8, FOCAL, fn, 10)))
    a2, a4 = foton.area_pupila_cm2(FOCAL, 2), foton.area_pupila_cm2(FOCAL, 4)
    print()
    print("  f/2 contra f/4: área ×%.2f  →  fotões ×%.2f  (dois «passos», não um)"
          % (a2 / a4, a2 / a4))

    cab("O que o ISO faz, e o que não faz")
    print("O ISO muda o ganho: quantos electrões valem um nível do ficheiro.")
    print("Não muda os electrões. Prova: o mesmo sinal, dois ganhos.")
    print()
    for nome, c in (("ISO baixo (ganho 4 e⁻/ADU, leitura 6 e⁻)",
                     Camara(ganho_e_adu=4.0, leitura_e=6.0)),
                    ("ISO alto  (ganho 1 e⁻/ADU, leitura 3 e⁻)",
                     Camara(ganho_e_adu=1.0, leitura_e=3.0))):
        sinal_e = 2000.0
        print("  %-42s sinal %5.0f e⁻ → %6.0f ADU · leitura %.1f e⁻ = %.1f ADU"
              % (nome, sinal_e, sinal_e / c.ganho_e_adu, c.leitura_e,
                 c.leitura_e / c.ganho_e_adu))
    print()
    print("  Os electrões são os mesmos. O que muda é quanto do ruído de leitura")
    print("  sobrevive à digitalização — e por isso o ISO alto ajuda quando o sinal é")
    print("  pequeno, e desperdiça poço quando não é.")

    cab("Uma conta que se faz de cabeça e se confere aqui")
    for mag in (0, 5, 10, 15):
        e = foton.electroes_estrela(mag, FOCAL, FNUM, 10)
        print("  V=%-3d %12.0f e⁻ em 10 s   (√N = %.0f)" % (mag, e, math.sqrt(e)))
    r = (foton.electroes_estrela(0, FOCAL, FNUM, 10)
         / foton.electroes_estrela(5, FOCAL, FNUM, 10))
    print()
    print("  De cinco em cinco magnitudes o fluxo divide por %.1f — é a definição da" % r)
    print("  escala, não uma aproximação. E repara na coluna √N: a estrela V=15 traz")
    print("  %.0f electrões com ±%.0f de incerteza que ninguém pode remover."
          % (foton.electroes_estrela(15, FOCAL, FNUM, 10),
             math.sqrt(foton.electroes_estrela(15, FOCAL, FNUM, 10))))


# ═══════════════════════════════════════════════════════════ 1
@seccao(1, "O ruído (lição 1)")
def s1():
    cab("A variância de uma contagem é a própria contagem")
    rng = np.random.default_rng(1)
    print("  média pedida   média obtida   variância obtida   √média   desvio obtido")
    for lam in (4, 25, 400, 10000):
        a = rng.poisson(lam, 200000).astype(np.float64)
        print("  %12d   %12.3f   %16.3f   %6.2f   %13.3f"
              % (lam, a.mean(), a.var(ddof=1), math.sqrt(lam), a.std(ddof=1)))
    print()
    print("  Não é aproximado: para Poisson, variância = média, exatamente.")

    cab("Os quatro ruídos, e qual manda em cada regime")
    print("Objetiva de %g mm a f/%g, píxeis de %g µm, estrela medida em 9 píxeis,"
          % (FOCAL, FNUM, PASSO))
    print("céu de %g mag/arcsec², escuro 0,05 e⁻/px/s, leitura 3 e⁻." % CEU_URBANO)
    print()
    print("  pose    céu     sinal    σ_sinal  σ_céu   σ_escuro  σ_leitura   SNR   manda")
    for t in (0.25, 1, 4, 16, 64, 256):
        s = foton.electroes_estrela(10, FOCAL, FNUM, t)
        c = foton.electroes_ceu_px(CEU_URBANO, FOCAL, FNUM, PASSO, t)
        d, lei = 0.05 * t, 3.0
        termos = {"sinal": s, "céu": 9 * c, "escuro": 9 * d, "leitura": 9 * lei ** 2}
        print("  %5.2fs %7.1f %9.0f %9.1f %7.1f %9.2f %10.1f %6.1f   %s"
              % (t, c, s, math.sqrt(s), math.sqrt(9 * c), math.sqrt(9 * d),
                 math.sqrt(9 * lei ** 2), foton.snr_pose(s, c, 9, d, lei),
                 max(termos, key=termos.get)))
    t_igual = 9 * 3.0 ** 2 / (9 * foton.electroes_ceu_px(CEU_URBANO, FOCAL, FNUM,
                                                         PASSO, 1.0))
    print()
    print("  O céu iguala a leitura aos %.2f s de pose: é a raiz de 9·σ² = 9·céu·t." % t_igual)
    print("  Acima disso, a pose está «limitada pelo céu» e alongá-la já não melhora")
    print("  a razão entre o que queres e o que te atrapalha.")

    cab("Empilhar: o que a teoria promete")
    s = foton.electroes_estrela(12, FOCAL, FNUM, 8)
    c = foton.electroes_ceu_px(CEU_URBANO, FOCAL, FNUM, PASSO, 8)
    uma = foton.snr_pose(s, c, 9, 0.4, 3.0)
    print("  Uma pose de 8 s numa estrela V=12: sinal %.0f e⁻, céu %.1f e⁻/px, SNR %.2f"
          % (s, c, uma))
    for n in (4, 16, 64, 256):
        print("  %3d poses → SNR %6.2f   (×%.2f = √%d)"
              % (n, foton.snr_pilha(n, s, c, 9, 0.4, 3.0), math.sqrt(n), n))
    n20 = foton.poses_para_snr(20, s, c, 9, 0.4, 3.0)
    print()
    print("  Para SNR=20 são precisas %d poses de 8 s = %.0f minutos. Para SNR=40,"
          % (n20, n20 * 8 / 60))
    n40 = foton.poses_para_snr(40, s, c, 9, 0.4, 3.0)
    print("  são %d poses = %.0f minutos: o dobro de SNR custa **quatro** vezes o tempo."
          % (n40, n40 * 8 / 60))


# ═══════════════════════════════════════════════════════════ 2
@seccao(2, "A Terra roda (lição 2)")
def s2():
    cab("Quanto anda uma estrela, em píxeis")
    print("  velocidade sideral: %.4f ″/s no equador celeste" % foton.VELOCIDADE_SIDERAL)
    print()
    print("  focal   escala     arrasto em 10 s (px)        pose para 1 px (s)")
    print("           (″/px)   δ=0°    δ=45°   δ=80°      δ=0°   δ=45°   δ=80°")
    for f in (14, 24, 50, 135, 300):
        print("  %4d mm  %6.2f  %6.2f  %6.2f  %6.2f    %6.2f  %6.2f  %6.2f"
              % (f, foton.escala_arcsec_px(f, PASSO),
                 foton.arrasto_px(10, f, PASSO, 0), foton.arrasto_px(10, f, PASSO, 45),
                 foton.arrasto_px(10, f, PASSO, 80),
                 foton.t_max_por_arrasto(1, f, PASSO, 0),
                 foton.t_max_por_arrasto(1, f, PASSO, 45),
                 foton.t_max_por_arrasto(1, f, PASSO, 80)))

    cab("As duas regras, contra a medição")
    print("  Píxeis de %g µm, δ=0°, k=1." % PASSO)
    print()
    print("  focal   regra 500   arrasto que ela deixa   NPF      arrasto do NPF")
    for f in (14, 24, 50, 135, 300):
        t5 = foton.regra_500(f)
        tn = foton.regra_npf(FNUM, f, PASSO, 0.0, 1.0)
        print("  %4d mm  %8.2f s  %14.2f px  %8.2f s  %12.2f px"
              % (f, t5, foton.arrasto_px(t5, f, PASSO, 0), tn,
                 foton.arrasto_px(tn, f, PASSO, 0)))
    print()
    print("  🔴 A coluna do arrasto da regra 500 é **constante**. Não é coincidência:")
    print("     arrasto = 15,04·(500/f) / (206,265·p/f) — o f cancela, e sobra")
    print("     15,04·500/(206,265·p) = %.2f px para p = %g µm."
          % (foton.VELOCIDADE_SIDERAL * 500 / (foton.ARCSEC_POR_RADIANO * PASSO / 1000),
             PASSO))
    print("     A «regra da focal» é, por baixo, uma regra sobre o passo do píxel —")
    print("     e foi escrita quando o «píxel» era o grão do filme.")
    print()
    print("  passo do píxel   arrasto que a regra 500 deixa passar")
    for p in (2.0, 3.0, 4.0, 6.0, 8.5):
        print("  %10.1f µm   %10.2f px"
              % (p, foton.VELOCIDADE_SIDERAL * 500
                 / (foton.ARCSEC_POR_RADIANO * p / 1000)))

    cab("Uma longa contra muitas curtas — o mesmo tempo total")
    s_tot = foton.electroes_estrela(12, FOCAL, FNUM, 64)
    c_tot = foton.electroes_ceu_px(CEU_URBANO, FOCAL, FNUM, PASSO, 64)
    print("  64 s de integração total numa estrela V=12, céu %g mag/arcsec²." % CEU_URBANO)
    print("  Só muda uma coisa entre as linhas: quantas vezes se lê o sensor.")
    print()
    print("   poses   cada     SNR      perda contra 1×64 s   arrasto por pose")
    base = None
    for n in (1, 2, 4, 8, 16, 32, 64):
        var = s_tot + 9 * (c_tot + 0.05 * 64 + n * 3.0 ** 2)
        snr = s_tot / math.sqrt(var)
        base = base or snr
        print("   %3d×  %5.1fs  %7.2f   %17.1f %%   %12.2f px"
              % (n, 64 / n, snr, 100 * (1 - snr / base),
                 foton.arrasto_px(64 / n, FOCAL, PASSO, 0)))
    print()
    print("  A perda é **só** o ruído de leitura repetido: (n−1)·n_px·σ². Tudo o resto")
    print("  é igual. É esta conta que decide a pose — não uma regra decorada. E com")
    print("  ela na mão vê-se o compromisso inteiro: 8×8 s custa %.1f %% de SNR e"
          % (100 * (1 - (s_tot / math.sqrt(s_tot + 9 * (c_tot + 3.2 + 8 * 9))) / base)))
    print("  reduz o traço de %.1f px para %.1f px."
          % (foton.arrasto_px(64, FOCAL, PASSO, 0),
             foton.arrasto_px(8, FOCAL, PASSO, 0)))


# ═══════════════════════════════════════════════════════════ 3
@seccao(3, "Do céu ao píxel (lição 3)")
def s3():
    cab("Escala e campo")
    print("  passo de %g µm; sensor de 6000×4000 píxeis" % PASSO)
    print()
    print("  focal    ″/px      campo (graus)")
    for f in (14, 24, 50, 135, 300):
        e = foton.escala_arcsec_px(f, PASSO)
        print("  %4d mm  %6.2f    %5.2f × %5.2f"
              % (f, e, 6000 * e / 3600, 4000 * e / 3600))

    cab("Quem é que decide a largura de uma estrela")
    print("  Difração: FWHM do disco de Airy ≈ 1,03·λ/D, com λ = 550 nm.")
    print("  Seeing: 2,5″ é um valor corrente de noite razoável em terreno baixo.")
    print()
    print("  focal  abertura   D (mm)   Airy (″)   escala (″/px)   Airy (px)   seeing (px)")
    for f, nfn in ((14, 2.8), (24, 2.0), (50, 2.0), (135, 2.8), (300, 4.0)):
        d_mm = f / nfn
        airy = 1.03 * 550e-9 / (d_mm / 1000.0) * foton.ARCSEC_POR_RADIANO
        esc = foton.escala_arcsec_px(f, PASSO)
        print("  %4dmm  f/%-6.1f %6.1f   %8.2f   %13.2f   %9.2f   %11.2f"
              % (f, nfn, d_mm, airy, esc, airy / esc, 2.5 / esc))
    print()
    print("  🔴 Com objetivas de fotografia, nem a difração nem o seeing chegam a um píxel.")
    print("  A largura das tuas estrelas é decidida pelas **aberrações da objetiva** e pelo")
    print("  próprio píxel — não pela atmosfera. «O seeing estava mau» é uma explicação")
    print("  emprestada da astronomia de telescópio e que aqui quase nunca se aplica.")

    cab("Amostragem: o que acontece quando a estrela cabe num píxel")
    cam = Camara()
    print("  60 estrelas sintéticas por linha, posição verdadeira conhecida.")
    print()
    print("  FWHM real   FWHM medida   erro do centroide (px, rms)")
    rng = np.random.default_rng(5)
    for fw in (0.8, 1.2, 1.8, 2.6, 4.0, 6.0):
        erros, medidas = [], []
        for k in range(60):
            c = Campo(largura=64, altura=64, semente=100 + k)
            x0, y0 = 32 + rng.uniform(-0.5, 0.5), 32 + rng.uniform(-0.5, 0.5)
            c.acrescentar(x0, y0, 4000.0)
            ses = Sessao(cam, largura=64, altura=64, semente=900 + k)
            img = ses.pose(c, 4.0, 5.0, fwhm_px=fw)
            xc, yc = pilha.centroide(img, 32, 32, raio=max(3, int(2 * fw)))
            erros.append(math.hypot(xc - x0, yc - y0))
            medidas.append(medir.fwhm(img, xc, yc))
        print("  %8.1f   %11.2f   %20.3f"
              % (fw, np.nanmedian(medidas), math.sqrt(np.mean(np.square(erros)))))
    piso = 2.3548 * math.sqrt(1.0 / 12.0)
    print()
    print("  O píxel tem largura, e isso tem um preço fixo: uma fonte perfeitamente")
    print("  pontual medida numa grelha dá σ = √(1/12) px, ou seja FWHM = %.2f px." % piso)
    print("  É o piso da coluna do meio, e é por isso que 0,8 não dá 0,8.")
    print("  O centroide piora nos dois sentidos: com a estrela apertada não há píxeis")
    print("  onde pesar; com ela larga, cada píxel recebe menos sinal.")


# ═══════════════════════════════════════════════════════════ 4
@seccao(4, "Calibrar (lição 4)")
def s4():
    cam = Camara()
    ses = Sessao(cam, semente=44)
    cab("Medir o ganho e o ruído de leitura — sem abrir a folha de especificações")
    zeros = [ses.zero_bruto() for _ in range(16)]
    planos = [ses.plano_bruto(7000.0) for _ in range(16)]
    g, r = medir.ganho_e_leitura(planos[0], planos[1], zeros[0], zeros[1])
    print("  verdade posta no simulador:  ganho %.3f e⁻/ADU · leitura %.2f e⁻"
          % (cam.ganho_e_adu, cam.leitura_e))
    print("  medido por transferência:    ganho %.3f e⁻/ADU · leitura %.2f e⁻" % (g, r))
    print("  erro relativo:               ganho %+.2f %% · leitura %+.2f %%"
          % (100 * (g / cam.ganho_e_adu - 1), 100 * (r / cam.leitura_e - 1)))
    print()
    print("  ⚠️ O mesmo método, com o plano cada vez mais perto do topo da escala:")
    print()
    print("  nível do plano   % de píxeis no topo   ganho medido   erro")
    for nivel in (7000.0, 12000.0, 16000.0, 20000.0, 30000.0):
        par = [ses.plano_bruto(nivel) for _ in range(2)]
        gs, _ = medir.ganho_e_leitura(par[0], par[1], zeros[2], zeros[3])
        topo = 100 * float((par[0] >= cam.maximo_adu).mean())
        print("  %10.0f e⁻   %17.1f %%   %12.3f   %+6.0f %%"
              % (nivel, topo, gs, 100 * (gs / cam.ganho_e_adu - 1)))
    print()
    print("  O conversor corta a variância dos píxeis que chegam ao topo, e variância")
    print("  a menos aparece como **ganho a mais**. Repara que aos 16000 e⁻ ainda só")
    print("  o centro satura — a vinhetagem salva as bordas — e por isso o erro ainda")
    print("  é pequeno e completamente invisível a olho.")

    cab("A corrente escura, e o que é preciso para a medir")
    zero_m = pilha.mestre(zeros, "media")
    print("  posta no simulador: %.3f e⁻/px/s" % cam.escuro_e_s)
    print("  cada linha é medida 5 vezes, com escuros independentes")
    print()
    print("  tempo   e⁻ térmicos   σ de leitura   medido (e⁻/px/s)   dispersão das 5")
    for t in (8.0, 30.0, 120.0, 600.0):
        vs = [medir.escuro_por_segundo(
                  pilha.mestre([ses.escuro_bruto(t) for _ in range(16)], "media"),
                  zero_m, t, g) for _ in range(5)]
        print("  %4.0f s   %11.1f   %10.1f e⁻   %16.4f   %13.1f %%"
              % (t, cam.escuro_e_s * t, cam.leitura_e, float(np.mean(vs)),
                 100 * float(np.std(vs)) / cam.escuro_e_s))
    print()
    print("  Aos 8 s há 0,4 electrões térmicos contra 3 de ruído de leitura: a medição")
    print("  existe, mas a dispersão dela é da ordem do próprio valor. O escuro de 8 s")
    print("  é quase um «zero» com outro nome — e é essa a razão por que, em poses")
    print("  curtas, tirar escuros muda tão pouco no fundo. O que eles lá tiram mesmo")
    print("  são os píxeis quentes, que não dependem de a média ser mensurável.")

    escuro_m = pilha.mestre([ses.escuro_bruto(8.0) for _ in range(16)], "media")
    plano_m = pilha.mestre(planos)

    cab("O que cada calibração corrige, medido no mesmo sítio")
    campo = Campo(semente=44).povoar(80).acrescentar(256, 256, 1500.0)
    luz = ses.pose(campo, 8.0, 12.0)

    def perfil(img, etiqueta):
        centro = float(np.median(img[236:276, 236:276]))
        canto = float(np.median(img[8:48, 8:48]))
        print("  %-36s centro %8.1f   canto %8.1f   razão %.3f"
              % (etiqueta, centro, canto, canto / centro if centro else float("nan")))

    perfil(luz, "bruta")
    perfil(pilha.calibrar(luz, zero_m), "− zero")
    perfil(pilha.calibrar(luz, zero_m, escuro_m, None, 8.0, 8.0), "− zero − escuro")
    perfil(pilha.calibrar(luz, zero_m, escuro_m, plano_m, 8.0, 8.0),
           "− zero − escuro ÷ plano")
    perfil(pilha.calibrar(luz, zero_m, escuro_m, plano_m, 8.0, 8.0,
                          zero_do_plano=False),
           "… mas com o zero por tirar do plano")
    print()
    print("  A razão canto/centro só chega perto de 1 depois do plano: a vinhetagem é")
    print("  multiplicativa e nenhuma subtração a corrige. A última linha é o preço de")
    print("  dividir por um plano que ainda tem o nível de zero em cima.")

    cab("O erro de subtrair o zero duas vezes")
    errada = luz - zero_m - escuro_m          # o escuro já tem o zero lá dentro
    certa = pilha.calibrar(luz, zero_m, escuro_m, None, 8.0, 8.0)
    print("  fundo depois da calibração certa:  %8.2f ADU" % np.median(certa))
    print("  fundo depois de subtrair a dobrar: %8.2f ADU" % np.median(errada))
    print("  diferença: %.1f ADU — exatamente o nível de zero (%d ADU)."
          % (np.median(certa) - np.median(errada), cam.nivel_zero))
    print("  Sintoma: %.1f %% dos píxeis ficam negativos."
          % (100 * (errada < 0).mean()))
    print("  ⚠️ E o esticamento da lição 6 corta em zero de qualquer maneira, por isso")
    print("  a imagem **parece** bem. O erro só aparece quando se mede.")

    cab("Quantos escuros e quantos zeros")
    print("  O ruído que a calibração acrescenta é o do próprio mestre, e cai com √N.")
    print()
    print("   N     σ do zero mestre (ADU)   previsto σ₁/√N   acrescenta ao total")
    um = float(np.std(zeros[0]))
    for n in (1, 4, 9, 16, 32):
        m = pilha.mestre([ses.zero_bruto() for _ in range(n)], "media")
        print("  %3d   %20.3f   %14.3f   %15.1f %%"
              % (n, float(np.std(m)), um / math.sqrt(n),
                 100 * (math.sqrt(1 + 1 / n) - 1)))
    print()
    print("  σ de um zero sozinho: %.3f ADU. Com 16 zeros a calibração acrescenta" % um)
    print("  %.1f %% ao ruído final; com 1, acrescenta %.0f %%. Passar de 16 para 32"
          % (100 * (math.sqrt(1 + 1 / 16) - 1), 100 * (math.sqrt(2) - 1)))
    print("  poupa %.1f pontos percentuais — é aí que deixa de valer a pena."
          % (100 * (math.sqrt(1 + 1 / 16) - math.sqrt(1 + 1 / 32))))


# ═══════════════════════════════════════════════════════════ 5
@seccao(5, "Alinhar e empilhar (lição 5)")
def s5():
    cam = Camara()
    ses = Sessao(cam, semente=55)
    campo = Campo(semente=55).povoar(100).acrescentar(256, 256, 900.0)
    rng = np.random.default_rng(55)
    n = 32
    deslocs = [(0.0, 0.0)] + [(rng.uniform(-6, 6), rng.uniform(-6, 6))
                              for _ in range(n - 1)]
    luzes = [ses.pose(campo, 8.0, 12.0, desloc=d) for d in deslocs]
    zero_m = pilha.mestre([ses.zero_bruto() for _ in range(16)], "media")
    escuro_m = pilha.mestre([ses.escuro_bruto(8.0) for _ in range(16)], "media")
    plano_m = pilha.mestre([ses.plano_bruto(7000.0) for _ in range(16)])
    cals = [pilha.calibrar(l, zero_m, escuro_m, plano_m, 8.0, 8.0) for l in luzes]

    cab("Quão bem é que o alinhamento acerta")
    ref = pilha.detetar(cals[0])
    print("  %d estrelas detetadas na pose de referência (limiar 6σ)" % len(ref))
    erros = []
    for i in range(1, n):
        dx, dy = pilha.deslocamento(ref, pilha.detetar(cals[i]))
        erros.append((dx - (deslocs[0][0] - deslocs[i][0]),
                      dy - (deslocs[0][1] - deslocs[i][1])))
    print("  erro do deslocamento estimado: %.3f px em x, %.3f px em y (rms)"
          % (math.sqrt(np.mean([e[0] ** 2 for e in erros])),
             math.sqrt(np.mean([e[1] ** 2 for e in erros]))))
    print("  pior caso: %.3f px" % max(math.hypot(*e) for e in erros))

    cab("O ganho de SNR: previsto contra medido")
    g = cam.ganho_e_adu
    uma = medir.fotometria(cals[0], 256, 256, ganho_e_adu=g)
    print("  SNR numa pose: %.2f · previsto para %d poses: %.2f (×√%d = %.3f)"
          % (uma["snr"], n, uma["snr"] * math.sqrt(n), n, math.sqrt(n)))
    print("  ⚠️ A pilha é uma **média**: mede-se com n_poses=%d, senão o termo de" % n)
    print("  Poisson do próprio astro é contado %d vezes a mais." % n)
    print()
    linhas = [["combinação", "deslocamento", "SNR", "ganho", "previsto", "diferença"]]
    for met in ("media", "mediana", "sigma"):
        for desl in ("inteiro", "bilinear"):
            al, _ = pilha.alinhar(cals, metodo=desl)
            m = medir.fotometria(pilha.empilhar(al, met), 256, 256,
                                 ganho_e_adu=g, n_poses=n)
            ganho = m["snr"] / uma["snr"]
            linhas.append([met, desl, "%.2f" % m["snr"], "×%.2f" % ganho,
                           "×%.2f" % math.sqrt(n),
                           "%+.1f %%" % (100 * (ganho / math.sqrt(n) - 1))])
    medir.relatorio(linhas)
    print()
    print("  Como ler esta tabela: a mediana paga em ruído o que ganha em robustez;")
    print("  o sigma-clip fica entre as duas; e o deslocamento bilinear **parece**")
    print("  melhor do que o inteiro porque a interpolação mistura píxeis vizinhos, o")
    print("  que correlaciona o ruído e faz o fundo do anel medir menos do que é.")
    print("  🔴 Um ganho acima de √N não é um ganho: é uma medição contaminada.")

    cab("O que acontece quando a noite não é constante")
    print("  As linhas de cima assumem 32 poses iguais. Uma noite real tem cirros e")
    print("  humidade, e a transparência só desce: a pose 0 é a melhor que houve, e é")
    print("  contra ela que se compara.")
    print()
    print("  perda média   transparência média   SNR da pilha   ganho   √N·t̄ previsto")
    for espalha in (0.0, 0.05, 0.15, 0.30, 0.50):
        r2 = np.random.default_rng(1234)
        tr = np.clip(1.0 - espalha * np.abs(r2.standard_normal(n)), 0.05, 1.0)
        tr[0] = 1.0
        lz = [ses.pose(campo, 8.0, 12.0, desloc=d, transparencia=float(t))
              for d, t in zip(deslocs, tr)]
        cl = [pilha.calibrar(l, zero_m, escuro_m, plano_m, 8.0, 8.0) for l in lz]
        a2, _ = pilha.alinhar(cl, metodo="inteiro")
        u2 = medir.fotometria(cl[0], 256, 256, ganho_e_adu=g)
        p2 = medir.fotometria(pilha.empilhar(a2, "media"), 256, 256,
                              ganho_e_adu=g, n_poses=n)
        gh = p2["snr"] / u2["snr"]
        print("  %10.0f %%   %18.3f   %12.2f   ×%.2f   %13.2f"
              % (100 * espalha, float(tr.mean()), p2["snr"], gh,
                 math.sqrt(n) * float(tr.mean())))
    print()
    print("  🔴 É aqui que o √N se parte, e não na aritmética. A média pesa todas as")
    print("  poses por igual, por isso uma pose com metade da luz traz metade do sinal")
    print("  e o ruído do céu inteiro.")
    print("  ⚠️ E repara que o ganho medido cai **mais devagar** do que √N·t̄: a coluna")
    print("  da direita é um limite pessimista, porque assume que todo o ruído vem do")
    print("  céu. Parte dele vem da própria estrela, e esse desce com a transparência")
    print("  também. Quanto mais o teu alvo dominar o ruído, menos as nuvens custam —")
    print("  o que é outra maneira de dizer que o céu é que manda em alvos fracos.")
    print("  Uma pilha **ponderada** recupera parte disto: é o exercício E3 desta lição.")

    cab("Os píxeis quentes, com e sem deslocamento entre poses")
    quentes = ses.escuro > 1.0        # a verdade do simulador: onde eles estão
    print("  %d píxeis quentes postos no simulador (>1 e⁻/px/s)" % int(quentes.sum()))
    sem_dither = [pilha.calibrar(ses.pose(campo, 8.0, 12.0), zero_m, None, plano_m,
                                 8.0, 8.0) for _ in range(n)]
    com_dither = [pilha.calibrar(ses.pose(campo, 8.0, 12.0,
                                          desloc=(rng.uniform(-6, 6),
                                                  rng.uniform(-6, 6))),
                                 zero_m, None, plano_m, 8.0, 8.0) for _ in range(n)]
    al_dither, _ = pilha.alinhar(com_dither, metodo="inteiro")
    print()
    print("  (nenhuma destas pilhas leva escuro subtraído — é o ponto do ensaio)")
    print()
    print("  pilha                              excesso mediano nos píxeis quentes")
    for nome, imgs in (("sem deslocar, média", sem_dither),
                       ("sem deslocar, sigma-clip", sem_dither),
                       ("com deslocar, sigma-clip", al_dither)):
        met = "media" if "média" in nome else "sigma"
        e = pilha.empilhar(imgs, met)
        fundo, _ = pilha.fundo_e_ruido(e)
        print("  %-34s %12.1f ADU" % (nome, float(np.median(e[quentes] - fundo))))
    print()
    print("  O deslocamento não corrige o píxel quente: espalha-o. Depois de espalhado,")
    print("  a rejeição apanha-o, porque deixou de estar no mesmo sítio em todas as")
    print("  poses — repara que sem deslocar o sigma-clip não serve de nada, porque o")
    print("  intruso está em **todas** as amostras e passa a ser a mediana.")
    print("  ⚠️ É a mesma ideia do *dither* dos tópicos da cassete — converter erro")
    print("  sistemático em erro aleatório — mas não é a mesma mecânica: ali soma-se")
    print("  ruído antes de quantizar, aqui move-se a câmara entre poses.")

    cab("Quanto é que o sigma-clip deita fora")
    for k in (2.0, 2.5, 3.0, 4.0):
        print("  κ=%.1f → %.2f %% das amostras rejeitadas"
              % (k, 100 * pilha.taxa_rejeicao(al_dither, k)))
    print()
    print("  Numa gaussiana, |x−μ| > 3σ acontece em 0,27 % das vezes. Muito acima disso")
    print("  significa que o que estás a rejeitar não é ruído: é sinal que se moveu.")


# ═══════════════════════════════════════════════════════════ 6
@seccao(6, "Esticar (lição 6)")
def s6():
    cam = Camara()
    ses = Sessao(cam, semente=66)
    campo = Campo(semente=66).povoar(100).acrescentar(256, 256, 900.0)
    zero_m = pilha.mestre([ses.zero_bruto() for _ in range(8)], "media")
    plano_m = pilha.mestre([ses.plano_bruto(7000.0) for _ in range(8)])
    img = pilha.calibrar(ses.pose(campo, 8.0, 12.0), zero_m, None, plano_m, 8.0, 8.0)

    cab("Onde é que a imagem linear vive")
    for p in (50, 90, 99, 99.9, 100):
        v = np.percentile(img, p)
        print("  percentil %5.1f: %9.1f ADU  →  %6.2f %% da escala de 14 bits"
              % (p, v, 100 * v / 16383))
    print()
    print("  Metade da imagem está abaixo de %.2f %% da escala. Num ecrã, isso é preto."
          % (100 * np.percentile(img, 50) / 16383))

    cab("Multiplicar não é esticar")
    med = np.median(img)
    print("  fator   fundo na escala   píxeis saturados")
    for k in (1, 4, 16, 64, 256):
        print("  ×%-5d %12.2f %%   %14.3f %%"
              % (k, 100 * med * k / 16383, 100 * ((img * k) > 16383).mean()))
    print()
    print("  O fundo só chega a um cinzento visível quando as estrelas já queimaram:")
    print("  multiplicar não muda a razão entre os dois, e o problema é a razão.")

    cab("As três funções, no mesmo sítio")
    p1 = float(np.percentile(img, 1))
    lin = esticar.normalizar(img, p1)
    a = esticar.asinh(img, 0.01, p1)
    m, par = esticar.automatico(img)
    linhas = [["função", "fundo (0-1)", "estrela de teste", "razão estrela/fundo"]]
    for nome, y in (("linear", lin), ("asinh β=0,01", a), ("MTF automático", m)):
        f = float(np.median(y))
        e = float(y[250:263, 250:263].max())
        linhas.append([nome, "%.4f" % f, "%.4f" % e, "%.1f" % (e / max(f, 1e-9))])
    medir.relatorio(linhas)
    print()
    r_lin = float(lin[250:263, 250:263].max()) / max(float(np.median(lin)), 1e-9)
    r_as = float(a[250:263, 250:263].max()) / max(float(np.median(a)), 1e-9)
    r_mtf = float(m[250:263, 250:263].max()) / max(float(np.median(m)), 1e-9)
    print("  O linear mantém a razão %.0f:1 entre a estrela e o fundo, e por isso o" % r_lin)
    print("  fundo fica em zero; o asinh baixa-a para %.1f:1 e o MTF para %.1f:1. É"
          % (r_as, r_mtf))
    print("  isso que um ecrã de 8 bits consegue mostrar ao mesmo tempo.")
    print("  parâmetros que o automático escolheu: ponto preto %.1f ADU, ponto médio %.4f"
          % (par["ponto_preto"], par["ponto_medio"]))
    print("  (mediana do fundo %.1f ADU, σ do fundo %.2f ADU)"
          % (par["mediana_do_fundo"], par["sigma_do_fundo"]))

    cab("O ponto preto: o que se perde ao cortá-lo no sítio errado")
    med, sig = pilha.fundo_e_ruido(img)
    for k in (-3, -1, 0, 1, 2):
        print("  corte em mediana%+d σ → %6.2f %% dos píxeis foram a zero"
              % (k, 100 * (img < med + k * sig).mean()))
    print()
    print("  O que vai a zero não volta. Um objeto mais fraco do que o céu vive nesses")
    print("  píxeis — e é por isso que o ponto preto se põe **abaixo** da mediana.")


# ═══════════════════════════════════════════════════════════ 7
@seccao(7, "O céu que atrapalha (lição 7)")
def s7():
    cab("Ler o brilho do céu nas tuas próprias poses")
    cam = Camara()
    ses0 = Sessao(cam, semente=77)
    print("  céu posto   e⁻/px em 8 s   lido de volta   erro")
    erros = []
    for mu in (17.0, 19.0, 20.5, 21.5, 22.0):
        c = foton.electroes_ceu_px(mu, FOCAL, FNUM, PASSO, 8.0)
        ses = Sessao(cam, semente=77)
        campo = Campo(semente=77).povoar(60)
        zero_m = pilha.mestre([ses.zero_bruto() for _ in range(8)], "media")
        plano_m = pilha.mestre([ses.plano_bruto(7000.0) for _ in range(8)])
        img = pilha.calibrar(ses.pose(campo, 8.0, c / 8.0), zero_m, None, plano_m,
                             8.0, 8.0)
        lido = medir.brilho_ceu(float(np.median(img)), 8.0, cam.ganho_e_adu,
                                FOCAL, FNUM, PASSO)
        erros.append(lido - mu)
        print("  %9.1f   %12.1f   %13.2f   %+.2f mag" % (mu, c, lido, lido - mu))
    previsto = -2.5 * math.log10(float(np.median(ses0.plano)) / ses0.plano.max())
    print()
    print("  🔴 O desvio é sistemático, e tem um valor exato: %+.2f mag." % previsto)
    print("  É −2,5·log₁₀(mediana do plano ÷ máximo do plano) = %+.2f. Dividir por um"
          % previsto)
    print("  plano normalizado à **mediana** faz a imagem passar a representar «um")
    print("  píxel médio» em vez do melhor píxel, e o céu sai atenuado nessa proporção.")
    print("  Não é um erro: é uma convenção de normalização. Mas é preciso saber que")
    print("  existe, senão compara-se o teu céu com o de outra pessoa que normalizou")
    print("  de outra maneira e conclui-se o que não se pode.")
    print("  ⚠️ Além disso: aqui a transmissão e a eficiência quântica usadas para ler")
    print("  são as mesmas que o simulador usou para escrever. Na tua câmara não são")
    print("  conhecidas — o número serve para comparar noites, não para publicar.")

    cab("O que o céu custa em tempo")
    s8 = foton.electroes_estrela(14, FOCAL, FNUM, 8)
    print("  Estrela V=14 (%.0f e⁻ por pose), poses de 8 s, alvo SNR=20, 9 píxeis." % s8)
    print()
    print("  céu (mag/arcsec²)   e⁻/px por pose   poses   tempo total")
    for mu in (17.0, 19.0, 20.5, 21.5):
        c = foton.electroes_ceu_px(mu, FOCAL, FNUM, PASSO, 8.0)
        n = foton.poses_para_snr(20, s8, c, 9, 0.4, 3.0)
        print("  %14.1f   %14.1f   %5d   %6.1f min" % (mu, c, n, n * 8 / 60))
    r = (foton.poses_para_snr(20, s8, foton.electroes_ceu_px(19.0, FOCAL, FNUM, PASSO, 8), 9, 0.4, 3.0)
         / foton.poses_para_snr(20, s8, foton.electroes_ceu_px(21.5, FOCAL, FNUM, PASSO, 8), 9, 0.4, 3.0))
    print()
    ceu215 = foton.electroes_ceu_px(21.5, FOCAL, FNUM, PASSO, 8)
    print("  Entre 19 e 21,5 há 2,5 magnitudes, ou seja um fator 10 no fluxo do fundo.")
    print("  O tempo necessário muda por um fator %.1f — **metade** do fator do céu." % r)
    print("  A razão está na tabela: a 21,5 o céu dá %.1f e⁻ por píxel e por pose, e o"
          % ceu215)
    print("  ruído de leitura vale σ²=9 e⁻ no mesmo píxel. Deixou de ser o céu a mandar,")
    print("  e a partir daí escurecer mais o céu já não paga o mesmo. Um céu melhor vale")
    print("  muito — até ao ponto em que a tua eletrónica passa a ser o limite.")

    cab("O gradiente, e o que sobra depois de o tirar")
    print("  🔴 O gradiente entra aqui como **luz**, não como um número somado: são")
    print("  fotões da cidade, e trazem o seu Poisson. É essa a diferença toda.")
    print()
    ses = Sessao(cam, semente=78)
    campo = Campo(semente=78).povoar(80)
    zero_m = pilha.mestre([ses.zero_bruto() for _ in range(8)], "media")
    plano_m = pilha.mestre([ses.plano_bruto(7000.0) for _ in range(8)])
    alt, larg = 512, 512
    gy, gx = np.mgrid[0:alt, 0:larg]
    ceu_uniforme = 12.0
    ceu_cidade = ceu_uniforme + 5.0 * (gx / larg) + 1.9 * (gy / alt)
    limpa = pilha.calibrar(ses.pose(campo, 8.0, ceu_uniforme), zero_m, None,
                           plano_m, 8.0, 8.0)
    suja = pilha.calibrar(ses.pose(campo, 8.0, ceu_cidade), zero_m, None,
                          plano_m, 8.0, 8.0)
    ajuste, coef = esticar.gradiente_plano(suja, grau=1)
    corrigida = suja - ajuste + np.median(ajuste)
    atenua = float(np.median(ses.plano)) / ses.plano.max()
    print("  gradiente posto na luz do céu:  %.1f ADU da esquerda para a direita"
          % (5.0 * 8.0))
    print("  previsto depois de calibrar:    %.1f ADU  (×%.3f, a mesma normalização"
          % (5.0 * 8.0 * atenua, atenua))
    print("                                  do plano que desloca o céu 0,35 mag)")
    print("  ajustado pelo código:           %.2f ADU  e %.2f ADU na vertical"
          % (coef[1] * larg, coef[2] * alt))
    print()
    print("  imagem                       esquerda    direita   diferença   σ do fundo")
    for nome, a in (("céu uniforme (referência)", limpa), ("com gradiente", suja),
                    ("gradiente ajustado e tirado", corrigida)):
        esq, dir_ = float(np.median(a[:, :64])), float(np.median(a[:, -64:]))
        _, sig = pilha.fundo_e_ruido(a)
        print("  %-28s %8.2f %10.2f %11.2f %12.2f"
              % (nome, esq, dir_, dir_ - esq, sig))
    print()
    print("  ⚠️ O ajuste tira o **declive** e não devolve nada: o σ do fundo depois de")
    print("  corrigir continua acima do da noite sem cidade. Os fotões da cidade já")
    print("  chegaram e a raiz deles ficou lá dentro. Tirar o gradiente melhora a")
    print("  vista; o que ele custou em SNR não se recupera na edição.")


# ═══════════════════════════════════════════════════════════ 8
@seccao(8, "Planear a sessão (lição 8)")
def s8():
    cab("A massa de ar e o que ela come")
    print("  altura h   massa de ar   extinção (0,20 mag/massa)   fluxo que resta")
    for h in (10, 20, 30, 45, 60, 90):
        X = 1.0 / math.sin(math.radians(h))
        print("  %6d°   %11.3f   %24.2f mag   %13.1f %%"
              % (h, X, 0.20 * X, 100 * 10 ** (-0.4 * 0.20 * X)))
    perda = 1 - 10 ** (-0.4 * 0.20 * (1 / math.sin(math.radians(20)) - 1))
    print()
    print("  A 20° de altura perde-se %.0f %% da luz em relação ao zénite. Duas horas"
          % (100 * perda))
    print("  com o alvo baixo podem render menos do que uma hora com ele alto — e isso")
    print("  decide-se no planeamento, não na edição.")

    cab("O orçamento de uma noite")
    print("  Alvo V=13 medido em 9 píxeis, poses de 8 s, céu %g mag/arcsec²." % CEU_URBANO)
    print()
    print("  altura   extinção   e⁻ por pose   SNR/pose   poses p/ SNR 30   tempo")
    for h in (15, 25, 40, 60, 80):
        ext = 0.20 / math.sin(math.radians(h))
        s = foton.electroes_estrela(13, FOCAL, FNUM, 8, extincao_mag=ext)
        c = foton.electroes_ceu_px(CEU_URBANO, FOCAL, FNUM, PASSO, 8)
        n = foton.poses_para_snr(30, s, c, 9, 0.4, 3.0)
        print("  %5d°   %6.2f mag   %11.0f   %8.2f   %15d   %5.1f min"
              % (h, ext, s, foton.snr_pose(s, c, 9, 0.4, 3.0), n, n * 8 / 60))
    print()
    print("  ⚠️ O coeficiente 0,20 mag por massa de ar é um valor de referência para um")
    print("  sítio limpo na banda V; num sítio com aerossóis é maior. Mede-se")
    print("  fotografando a mesma estrela a alturas diferentes na mesma noite — que é")
    print("  o exercício E3 desta lição.")


# ═══════════════════════════════════════════════════════════ 9
@seccao(9, "O projeto, de ponta a ponta (lição 9)")
def s9():
    t0 = time.time()
    cam = Camara()
    ses = Sessao(cam, semente=99)
    campo = Campo(semente=99).povoar(120).acrescentar(256, 256, 1200.0)
    rng = np.random.default_rng(99)
    n = 40
    # A pose 0 é a referência do alinhamento: é ela que define a grelha final, e
    # por isso não leva deslocamento. ⚠️ Com a pose 0 também deslocada, a estrela de
    # teste deixa de estar em (256, 256) na pilha — e medir lá inflaciona a FWHM por
    # causa da distância ao centro, não por causa do alinhamento. Apanhado na Fase 3.
    luzes = [ses.pose(campo, 8.0, 12.0)]
    luzes += [ses.pose(campo, 8.0, 12.0,
                       desloc=(rng.uniform(-6, 6), rng.uniform(-6, 6)))
              for _ in range(n - 1)]
    zeros = [ses.zero_bruto() for _ in range(16)]
    escuros = [ses.escuro_bruto(8.0) for _ in range(16)]
    planos = [ses.plano_bruto(7000.0) for _ in range(16)]

    g, r = medir.ganho_e_leitura(planos[0], planos[1], zeros[0], zeros[1])
    zero_m = pilha.mestre(zeros, "media")
    escuro_m = pilha.mestre(escuros, "media")
    plano_m = pilha.mestre(planos)
    cals = [pilha.calibrar(l, zero_m, escuro_m, plano_m, 8.0, 8.0) for l in luzes]
    al_i, _ = pilha.alinhar(cals, metodo="inteiro")
    al_b, _ = pilha.alinhar(cals, metodo="bilinear")
    emp = pilha.empilhar(al_i, "sigma")
    emp_b = pilha.empilhar(al_b, "sigma")

    # 🔴 Mede-se onde a estrela está, não onde devia estar: o centroide primeiro.
    cx, cy = pilha.centroide(emp, 256, 256, raio=5)
    uma = medir.fotometria(cals[0], *pilha.centroide(cals[0], 256, 256, raio=5),
                           ganho_e_adu=g)
    pil = medir.fotometria(emp, cx, cy, ganho_e_adu=g, n_poses=n)
    bx, by = pilha.centroide(emp_b, 256, 256, raio=5)
    pil_b = medir.fotometria(emp_b, bx, by, ganho_e_adu=g, n_poses=n)
    cab("O relatório, tal como a lição 9 o pede")
    medir.relatorio([
        ["grandeza", "previsto", "medido", "diferença"],
        ["escala (″/px)", "%.2f" % foton.escala_arcsec_px(FOCAL, PASSO),
         "%.2f" % foton.escala_arcsec_px(FOCAL, PASSO), "por construção"],
        ["ganho (e⁻/ADU)", "%.2f" % cam.ganho_e_adu, "%.3f" % g,
         "%+.1f %%" % (100 * (g / cam.ganho_e_adu - 1))],
        ["leitura (e⁻)", "%.2f" % cam.leitura_e, "%.2f" % r,
         "%+.1f %%" % (100 * (r / cam.leitura_e - 1))],
        ["escuro (e⁻/px/s)", "%.3f" % cam.escuro_e_s,
         "%.3f" % medir.escuro_por_segundo(escuro_m, zero_m, 8.0, g),
         "⚠️ 8 s não chegam (§4)"],
        ["FWHM na pilha (px)", "2.69", "%.2f" % medir.fwhm(emp, cx, cy),
         "alinhada ao píxel inteiro"],
        ["FWHM, alinhada por interpolação", "2.69", "%.2f" % medir.fwhm(emp_b, bx, by),
         "a interpolação alarga"],
        ["céu (mag/arcsec²)", "19.00",
         "%.2f" % medir.brilho_ceu(float(np.median(emp)), 8.0, g, FOCAL, FNUM, PASSO),
         "⚠️ +0,35 da normalização (§7)"],
        ["SNR de uma pose", "—", "%.2f" % uma["snr"], ""],
        ["SNR da pilha de %d" % n, "%.2f" % (uma["snr"] * math.sqrt(n)),
         "%.2f" % pil["snr"],
         "%+.1f %%" % (100 * (pil["snr"] / (uma["snr"] * math.sqrt(n)) - 1))],
        ["… alinhada por interpolação", "%.2f" % (uma["snr"] * math.sqrt(n)),
         "%.2f" % pil_b["snr"],
         "%+.1f %% ⚠️" % (100 * (pil_b["snr"] / (uma["snr"] * math.sqrt(n)) - 1))],
    ])
    print()
    print("  🔴 As duas últimas linhas são o resultado do curso. Alinhada ao píxel")
    print("  inteiro, a pilha chega ao √N previsto a menos de uns poucos por cento —")
    print("  é o que se espera de %d poses iguais numa noite estável simulada." % n)
    print("  Alinhada por interpolação, a medição dá **mais** do que √N, o que é")
    print("  impossível: a interpolação correlacionou o ruído e o anel passou a medir")
    print("  menos do que há. A mesma interpolação alargou a FWHM, e é aí que se vê.")
    print("  Numa noite tua, com transparência a variar, o número desce — quanto,")
    print("  está medido em §5.")
    print()
    print("  (corrido em %.1f s)" % (time.time() - t0))


def main():
    pedidas = [int(a) for a in sys.argv[1:] if a.isdigit()]
    for n in sorted(SECCOES):
        if pedidas and n not in pedidas:
            continue
        titulo, f = SECCOES[n]
        print()
        print()
        print("═" * 74)
        print("  §%d  %s" % (n, titulo))
        print("═" * 74)
        f()
    print()


if __name__ == "__main__":
    main()
