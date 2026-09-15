/* ------------------------------------------------------------------
   professor — comportamento base.
   FONTE ÚNICA: modelo/base.js. Editar aqui e correr  python3 sincronizar.py
   (ver DECISOES.md D-005). Tudo o que usa localStorage está em try/catch:
   em modo privado o acesso ATIRA, não devolve null (DECISOES.md D-006).
   A página tem de funcionar inteira sem JS e sem armazenamento.
   ------------------------------------------------------------------ */
(function () {
  "use strict";

  var guardar = function (chave, valor) {
    try { window.localStorage.setItem(chave, valor); } catch (e) { /* sem armazenamento: segue */ }
  };
  var ler = function (chave) {
    try { return window.localStorage.getItem(chave); } catch (e) { return null; }
  };
  var hoje = function () { return new Date().toISOString().slice(0, 10); };
  // O slug sai do caminho da própria página, para o aviso dizer onde colar de
  // verdade em vez de "<slug>" — que já foi copiado à letra mais do que uma vez.
  var slug = function () {
    var m = /docs\/([^/]+)\//.exec(document.body.dataset.pagina || "");
    return m ? m[1] : "<slug>";
  };

  /* ---------- tema: sistema -> claro -> escuro -> sistema ---------- */

  var ROTULOS = { sistema: "Tema: sistema", claro: "Tema: claro", escuro: "Tema: escuro" };
  var SEGUINTE = { sistema: "claro", claro: "escuro", escuro: "sistema" };

  function aplicarTema(tema) {
    var raiz = document.documentElement;
    if (tema === "sistema") { raiz.removeAttribute("data-tema"); }
    else { raiz.setAttribute("data-tema", tema); }
    var b = document.querySelector("[data-alternar-tema]");
    if (b) {
      b.textContent = ROTULOS[tema];
      b.setAttribute("aria-label", ROTULOS[tema] + ". Carrega para mudar para " + ROTULOS[SEGUINTE[tema]].toLowerCase() + ".");
    }
  }

  var temaAtual = ler("professor:tema") || "sistema";
  if (!ROTULOS[temaAtual]) { temaAtual = "sistema"; }
  aplicarTema(temaAtual);

  document.addEventListener("click", function (ev) {
    var b = ev.target.closest && ev.target.closest("[data-alternar-tema]");
    if (!b) { return; }
    temaAtual = SEGUINTE[temaAtual];
    aplicarTema(temaAtual);
    guardar("professor:tema", temaAtual);
  });

  /* ---------- índice lateral ---------- */

  function prepararIndice() {
    var botao = document.querySelector(".alternar-indice");
    var indice = document.querySelector(".indice");
    if (!botao || !indice) { return; }

    // Sem JS o índice fica aberto (o HTML traz aria-expanded="true"): é a
    // degradação correta. Só aqui, com JS a correr, é que se colapsa no telemóvel.
    var estreito = window.matchMedia("(max-width: 949px)");
    function ajustar() {
      if (estreito.matches) { indice.hidden = true; botao.setAttribute("aria-expanded", "false"); }
      else { indice.hidden = false; botao.setAttribute("aria-expanded", "true"); }
    }
    ajustar();
    if (estreito.addEventListener) { estreito.addEventListener("change", ajustar); }

    botao.addEventListener("click", function () {
      var aberto = botao.getAttribute("aria-expanded") === "true";
      botao.setAttribute("aria-expanded", String(!aberto));
      indice.hidden = aberto;
    });
    indice.addEventListener("click", function (ev) {
      if (ev.target.tagName === "A" && estreito.matches) {
        botao.setAttribute("aria-expanded", "false");
        indice.hidden = true;
      }
    });

    var ligacoes = Array.prototype.slice.call(indice.querySelectorAll('a[href^="#"]'));
    if (!ligacoes.length || !window.IntersectionObserver) { return; }
    var porId = {};
    var alvos = [];
    ligacoes.forEach(function (a) {
      var el = document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)));
      if (el) { porId[el.id] = a; alvos.push(el); }
    });
    var visiveis = {};
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) { visiveis[e.target.id] = e.isIntersecting; });
      var activo = null;
      alvos.forEach(function (el) { if (visiveis[el.id] && !activo) { activo = el.id; } });
      ligacoes.forEach(function (a) { a.removeAttribute("aria-current"); });
      if (activo && porId[activo]) { porId[activo].setAttribute("aria-current", "true"); }
    }, { rootMargin: "-70px 0px -65% 0px" });
    alvos.forEach(function (el) { obs.observe(el); });
  }

  /* ---------- blocos roláveis acessíveis por teclado ---------- */

  function prepararRolaveis() {
    Array.prototype.forEach.call(document.querySelectorAll("pre"), function (pre) {
      if (pre.scrollWidth > pre.clientWidth + 1 && !pre.hasAttribute("tabindex")) {
        pre.setAttribute("tabindex", "0");
        pre.setAttribute("role", "region");
        pre.setAttribute("aria-label", pre.getAttribute("data-rotulo") || "Bloco de código, rolável na horizontal");
      }
    });
  }

  /* ---------- quiz ---------- */

  function chaveQuiz(quiz) { return "professor:quiz:" + (quiz.dataset.quiz || location.pathname); }

  function corrigirPergunta(pergunta, revelarTudo) {
    var escolhida = pergunta.querySelector("input[type=radio]:checked");
    var acertou = false;
    Array.prototype.forEach.call(pergunta.querySelectorAll("li.opcao"), function (li) {
      var input = li.querySelector("input[type=radio]");
      var expl = li.querySelector(".explicacao");
      var certa = input.dataset.certa === "true";
      li.classList.remove("certa", "errada");
      if (expl) { expl.hidden = true; }
      if (!escolhida) { return; }
      var foiEsta = input === escolhida;
      if (certa) { acertou = acertou || foiEsta; }
      if (foiEsta || certa || revelarTudo) {
        li.classList.add(certa ? "certa" : "errada");
        if (expl) { expl.hidden = false; }
      }
    });
    return { respondida: !!escolhida, acertou: acertou,
             texto: escolhida ? escolhida.parentNode.querySelector(".rotulo").textContent.trim() : null };
  }

  function prepararQuiz(quiz) {
    var perguntas = Array.prototype.slice.call(quiz.querySelectorAll("li.pergunta"));
    var saida = quiz.querySelector(".resultado");

    var estado = null;
    try { estado = JSON.parse(ler(chaveQuiz(quiz)) || "null"); } catch (e) { estado = null; }
    if (estado) {
      perguntas.forEach(function (p, i) {
        var v = estado[i];
        if (!v) { return; }
        var input = p.querySelector('input[type=radio][value="' + v + '"]');
        if (input) { input.checked = true; }
      });
    }

    function verificar() {
      var certas = 0, respondidas = 0, guarda = [];
      perguntas.forEach(function (p) {
        var r = corrigirPergunta(p, false);
        if (r.respondida) { respondidas++; }
        if (r.acertou) { certas++; }
        var esc = p.querySelector("input[type=radio]:checked");
        guarda.push(esc ? esc.value : null);
      });
      quiz.dataset.certas = certas;
      quiz.dataset.total = perguntas.length;
      if (saida) {
        saida.textContent = respondidas < perguntas.length
          ? "Faltam " + (perguntas.length - respondidas) + " de " + perguntas.length + ". Corrigi as que respondeste: " + certas + " certas."
          : certas + " em " + perguntas.length + " certas." + (certas === perguntas.length
              ? " Lê à mesma as explicações das opções que não escolheste."
              : " Lê a explicação de cada opção — é lá que está o que faltava perceber.");
      }
      guardar(chaveQuiz(quiz), JSON.stringify(guarda));
    }

    var bv = quiz.querySelector("[data-verificar]");
    if (bv) { bv.addEventListener("click", verificar); }

    var bl = quiz.querySelector("[data-limpar]");
    if (bl) {
      bl.addEventListener("click", function () {
        perguntas.forEach(function (p) {
          Array.prototype.forEach.call(p.querySelectorAll("input[type=radio]"), function (i) { i.checked = false; });
          Array.prototype.forEach.call(p.querySelectorAll("li.opcao"), function (li) { li.classList.remove("certa", "errada"); });
          Array.prototype.forEach.call(p.querySelectorAll(".explicacao"), function (e) { e.hidden = true; });
        });
        delete quiz.dataset.certas;
        if (saida) { saida.textContent = ""; }
        guardar(chaveQuiz(quiz), "null");
      });
    }
  }

  /* ---------- respostas abertas ---------- */

  function prepararAbertas() {
    Array.prototype.forEach.call(document.querySelectorAll("textarea[data-pergunta]"), function (ta) {
      var chave = "professor:aberta:" + (document.body.dataset.pagina || location.pathname) + ":" + ta.dataset.pergunta;
      var antes = ler(chave);
      if (antes && !ta.value) { ta.value = antes; }
      ta.addEventListener("input", function () { guardar(chave, ta.value); });
    });
  }

  /* ---------- gerar a entrega em Markdown ---------- */

  function construirMarkdown() {
    var titulo = (document.querySelector("h1") || {}).textContent || document.title;
    var linhas = ["# " + titulo.trim(), "", "- **Data:** " + hoje(), "- **Página:** `" + (document.body.dataset.pagina || "") + "`", ""];

    var quizzes = Array.prototype.slice.call(document.querySelectorAll(".quiz"));
    if (quizzes.length) {
      linhas.push("## Quiz", "");
      quizzes.forEach(function (quiz) {
        var perguntas = Array.prototype.slice.call(quiz.querySelectorAll("li.pergunta"));
        var certas = 0, feito = false;
        var detalhe = [];
        perguntas.forEach(function (p, i) {
          var esc = p.querySelector("input[type=radio]:checked");
          var enun = (p.querySelector(".enunciado") || {}).textContent || "";
          if (!esc) { detalhe.push((i + 1) + ". _sem resposta_ — " + enun.trim()); return; }
          feito = true;
          var certa = esc.dataset.certa === "true";
          if (certa) { certas++; }
          var rotulo = esc.parentNode.querySelector(".rotulo").textContent.trim();
          detalhe.push((i + 1) + ". " + (certa ? "✅" : "❌") + " escolhi «" + rotulo + "» — " + enun.trim());
        });
        linhas.push("**Resultado: " + certas + "/" + perguntas.length + "**" + (feito ? "" : " (por responder)"), "");
        linhas = linhas.concat(detalhe, [""]);
      });
    }

    var abertas = Array.prototype.slice.call(document.querySelectorAll("textarea[data-pergunta]"));
    if (abertas.length) {
      linhas.push("## Respostas abertas", "");
      abertas.forEach(function (ta) {
        linhas.push("### " + (ta.dataset.pergunta || "Pergunta"), "");
        var v = ta.value.trim();
        linhas.push(v || "_(por responder)_", "");
      });
    }

    linhas.push("---", "", "> Colar em `topicos/" + slug() + "/respostas/" + hoje() + ".md` e correr `/corrigir " + slug() + "`.", "");
    return linhas.join("\n");
  }

  function prepararCopia() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-copiar-respostas]"), function (botao) {
      var aviso = document.querySelector(".aviso-copia");
      botao.addEventListener("click", function () {
        var md = construirMarkdown();
        function falhou() {
          // Sem clipboard (http, permissão negada): mostra o texto para copiar à mão.
          var cx = document.querySelector("[data-saida-markdown]");
          if (cx) {
            cx.hidden = false;
            cx.value = md;
            cx.focus();
            cx.select();
          }
          if (aviso) { aviso.hidden = false; aviso.textContent = "Não consegui usar a área de transferência. O texto está na caixa abaixo — copia-o à mão."; }
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(md).then(function () {
            if (aviso) { aviso.hidden = false; aviso.textContent = "Copiado. Cola em topicos/" + slug() + "/respostas/" + hoje() + ".md"; }
          }, falhou);
        } else { falhou(); }
      });
    });
  }

  /* ---------- pesquisa do catálogo ---------- */

  function prepararPesquisa() {
    var campo = document.querySelector("[data-pesquisa]");
    if (!campo) { return; }
    var cartoes = Array.prototype.slice.call(document.querySelectorAll("[data-pesquisavel]"));
    var caixaRes = document.querySelector("[data-resultados]");
    var contador = document.querySelector("[data-contagem]");
    var vazio = document.querySelector("[data-sem-resultados]");
    var indice = window.INDICE_PESQUISA || [];
    campo.hidden = false;

    // Sem acentos e sem maiúsculas: procurar "indices" tem de encontrar "índices".
    function normalizar(s) {
      return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }
    cartoes.forEach(function (el) {
      el.dataset.chave = normalizar(el.textContent + " " + (el.dataset.pesquisavel || ""));
    });
    indice.forEach(function (pag) {
      pag._t = normalizar(pag.t);
      pag.s.forEach(function (sec) {
        sec._h = normalizar(sec.h);
        sec._d = normalizar(sec.d || "");
        sec._k = normalizar(sec.k || "");
      });
    });

    function escapar(s) {
      return s.replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    }

    function procurar(q) {
      // Todos os termos têm de aparecer (E, não OU): "indice composto" não deve
      // devolver tudo o que fala de índices.
      var termos = q.split(/\s+/).filter(Boolean);
      var achados = [];

      indice.forEach(function (pag) {
        pag.s.forEach(function (sec) {
          var pontos = 0, todos = true;
          for (var i = 0; i < termos.length; i++) {
            var t = termos[i], p = 0;
            // Onde o termo aparece vale mais do que quantas vezes aparece:
            // no título da secção é sobre isso; na prosa é só menção.
            if (sec._h.indexOf(t) !== -1) { p = 100; }
            else if (sec._d.indexOf(t) !== -1) { p = 30; }
            else if (pag._t.indexOf(t) !== -1) { p = 12; }
            else if (sec._k.indexOf(t) !== -1) { p = 4; }
            if (!p) { todos = false; break; }
            pontos += p;
          }
          if (todos) { achados.push({ pagina: pag, seccao: sec, pontos: pontos }); }
        });
      });

      achados.sort(function (a, b) {
        if (b.pontos !== a.pontos) { return b.pontos - a.pontos; }
        return a.pagina.p < b.pagina.p ? -1 : 1;   // empate: por ordem das lições
      });
      return achados;
    }

    function filtrar() {
      var bruto = campo.value.trim();
      var q = normalizar(bruto);

      if (!q) {
        cartoes.forEach(function (el) { el.hidden = false; });
        if (caixaRes) { caixaRes.hidden = true; caixaRes.innerHTML = ""; }
        if (vazio) { vazio.hidden = true; }
        if (contador) {
          contador.textContent = cartoes.length + (cartoes.length === 1 ? " tópico" : " tópicos");
        }
        return;
      }

      var visiveis = 0;
      cartoes.forEach(function (el) {
        var mostra = el.dataset.chave.indexOf(q) !== -1;
        el.hidden = !mostra;
        if (mostra) { visiveis++; }
      });

      var achados = procurar(q);
      if (caixaRes) {
        if (achados.length) {
          // Agrupado por página: onze secções da mesma lição em fila não são
          // onze resultados, são um resultado com ruído à volta.
          var porPagina = [], vistas = {};
          achados.forEach(function (a) {
            var k = a.pagina.p;
            if (!vistas[k]) { vistas[k] = { pagina: a.pagina, seccoes: [] }; porPagina.push(vistas[k]); }
            if (vistas[k].seccoes.length < 3) { vistas[k].seccoes.push(a.seccao); }
          });

          var html = ['<h3 class="res-titulo">Dentro das lições</h3><ul class="resultados">'];
          porPagina.slice(0, 6).forEach(function (g) {
            html.push('<li><a href="' + escapar(g.pagina.p) + "#" + escapar(g.seccoes[0].id) + '">' +
                      escapar(g.pagina.t) + "</a><span class=\"res-pagina\">" +
                      g.seccoes.map(function (s) {
                        return '<a class="res-sec" href="' + escapar(g.pagina.p) + "#" +
                               escapar(s.id) + '">' + escapar(s.h) + "</a>";
                      }).join(" · ") + "</span></li>");
          });
          html.push("</ul>");
          if (porPagina.length > 6) {
            html.push('<p class="verificado">e mais ' + (porPagina.length - 6) +
                      " páginas — afina a pesquisa com uma segunda palavra.</p>");
          }
          caixaRes.innerHTML = html.join("");
          caixaRes.hidden = false;
          caixaRes.dataset.paginas = porPagina.length;
        } else {
          caixaRes.hidden = true;
          caixaRes.innerHTML = "";
          caixaRes.dataset.paginas = 0;
        }
      }

      if (contador) {
        var partes = [];
        if (visiveis) { partes.push(visiveis + (visiveis === 1 ? " tópico" : " tópicos")); }
        var np = caixaRes ? Number(caixaRes.dataset.paginas || 0) : 0;
        if (np) { partes.push(np + (np === 1 ? " página" : " páginas") + " com " +
                              achados.length + (achados.length === 1 ? " secção" : " secções")); }
        contador.textContent = partes.length ? partes.join(" · ") : "nada encontrado";
      }
      if (vazio) { vazio.hidden = !(visiveis === 0 && achados.length === 0); }
    }

    campo.addEventListener("input", filtrar);
    filtrar();
  }

  /* ---------- arranque ---------- */

  function arrancar() {
    prepararIndice();
    prepararRolaveis();
    Array.prototype.forEach.call(document.querySelectorAll(".quiz"), prepararQuiz);
    prepararAbertas();
    prepararCopia();
    prepararPesquisa();
  }

  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", arrancar); }
  else { arrancar(); }
})();
