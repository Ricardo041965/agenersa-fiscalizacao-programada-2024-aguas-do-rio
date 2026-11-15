"""Gera o relatório gerencial em PDF do mapeamento FIS.

Todos os números vêm dos arquivos de mapeamento/ (fatos, casos, resultado do TO-BE, conformidade, controles,
priorização); o texto não digita números. Os diagramas BPMN são exportados como SVG dos visualizadores em
mapeamento/bpmn*/index.html (bpmn-js carregado da CDN; precisa de rede). PDF impresso com Playwright (Chromium).

Uso (a partir da pasta do processo):  python scripts/gerar_relatorio_pdf.py
Saída: relatorio/Relatorio_Mapeamento_Fiscalizacoes_2024.pdf (e o .html usado para imprimir)
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent.parent
MAP = BASE / "mapeamento"
OUT = BASE / "relatorio"


def carregar(nome):
    return json.loads((MAP / nome).read_text(encoding="utf-8"))


fatos_fis = carregar("fatos_FIS.json")
casos = carregar("casos_FIS.json")
res = carregar("resultado_tobe_FIS.json")
conf = carregar("conformidade_FIS.json")
normas = carregar("normas_FIS.json")
melh = carregar("melhorias_FIS.json")
ctrl = carregar("controles_FIS.json")
bench = carregar("benchmark_FIS.json")
aval = carregar("avaliacao_FIS.json")
prio = carregar("priorizacao_FIS.json")

FATOS = {}
for fonte in (fatos_fis, casos, res):
    for f in fonte.get("fatos", []):
        FATOS[f["id"]] = f["valor"]


def num(v, casas=1):
    if isinstance(v, (int,)) or (isinstance(v, float) and v.is_integer()):
        return f"{int(v):,}".replace(",", ".")
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def F(fid, casas=1):
    if fid not in FATOS:
        raise KeyError(f"fato ausente: {fid}")
    return num(FATOS[fid], casas)


E = html.escape
_ID = r"(?:[a-zA-Z][\w\-]*\.[\w\.\-]+|lb\.[\w\.\-]+)"


def limpa(txt: str) -> str:
    """Tira do texto as referências internas a ids de fatos e nomes de arquivos."""
    t = re.sub(r"\s*\((?:" + _ID + r")(?:\s*[;,]\s*" + _ID + r")*\)", "", txt)
    t = re.sub(r"\s*\(fato\s+" + _ID + r"\)", "", t)
    t = re.sub(r"`?[\w\-]+_FIS\.(json|md|csv)`?", "os registros do mapeamento", t)
    t = re.sub(r"\b(t|g|e|s)(\d{1,2})\b(?=[\s,;:.)])", lambda m: m.group(0), t)
    return t


# ---------------------------------------------------------------- diagramas
def exportar_svgs():
    svgs = {}
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1600, "height": 1000})
        for chave, arq in (("asis", MAP / "bpmn" / "index.html"), ("tobe", MAP / "bpmn_tobe" / "index.html")):
            pg.goto(arq.as_uri())
            pg.wait_for_selector(".djs-container svg", timeout=60000)
            svgs[chave] = pg.evaluate("async () => (await viewer.saveSVG()).svg")
        nav.close()
    return svgs


# ---------------------------------------------------------------- blocos
def tabela(cab, linhas, cls=""):
    h = "".join(f"<th>{E(c)}</th>" for c in cab)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def lb(ciclo, k="mediana"):
    return res["linha_base"][ciclo][k]


def fase(f, cen, ciclo, k="mediana"):
    return res["fases"][str(f)][cen][ciclo][k]


def ganho(f, cen, ciclo):
    base = lb(ciclo)
    return 100 * (base - fase(f, cen, ciclo)) / base


def montar_html(svgs):
    hoje = dt.date.today().strftime("%d/%m/%Y")
    cc = conf["contagem_casos"]
    n_req = len(normas["requisitos"])
    n_bench = len(bench["casos"])
    n_cient = sum(1 for c in bench["casos"] if c["fonte"].get("camada") == "cientifica")
    n_melh = len(melh["melhorias"])
    por_fase = {f: [m for m in melh["melhorias"] if str(m["fase"]) == f] for f in ("1", "2", "3")}
    nc = prio["nota_composta"]

    # ---- tempos AS-IS
    tempos = [
        ("Vistoria → 1ª assinatura do relatório (redação e espera)",
         f"{F('casos.vistoria_1a_assinatura.mediana_du')} du", f"{F('casos.vistoria_1a_assinatura.min_du')} a {F('casos.vistoria_1a_assinatura.max_du')} du",
         F('casos.vistoria_1a_assinatura.n')),
        ("1ª assinatura → “De acordo” do Gerente",
         f"{F('casos.revisao_aprovacao.mediana_du')} du", f"até {F('casos.revisao_aprovacao.max_du')} du", F('casos.revisao_aprovacao.n')),
        ("“De acordo” → ofício à concessionária",
         f"{F('casos.aprovacao_oficio.mediana_du')} du", f"até {F('casos.aprovacao_oficio.max_du')} du", F('casos.aprovacao_oficio.n')),
        ("Ciclo completo: vistoria → e-mail à concessionária",
         f"{F('casos.vistoria_email.mediana_du')} du", f"{F('casos.vistoria_email.min_du')} a {F('casos.vistoria_email.max_du')} du",
         F('casos.vistoria_email.n')),
        ("Último ofício → parecer anual consolidado", f"{F('intervalo.ultimo_oficio_parecer_du')} du", "caso único", "1"),
        ("Vistoria → parecer, por relatório", f"{num(lb('ate_parecer'))} du",
         f"{num(lb('ate_parecer','min'))} a {num(lb('ate_parecer','max'))} du", num(lb('ate_parecer', 'n'))),
    ]

    # ---- desperdícios
    desp = "".join(
        f"<li><b>{E(d['tipo'])}</b> ({E(d.get('severidade',''))}): {E(limpa(d['evidencia']))}</li>"
        for d in aval["desperdicios"])

    # ---- conformidade
    linhas_conf = []
    for rid, r in conf["requisitos"].items():
        cont = r["contagem"]
        taxa = r.get("taxa_conformidade")
        situ = (f"{num(taxa)}% ({cont['conforme']} de {cont['conforme'] + cont['não conforme']})"
                if taxa is not None else ("sem evidência nos autos" if cont.get("sem evidência") else "não aplicável"))
        linhas_conf.append([E(rid), E(limpa(r["exigencia"])), E(r.get("criticidade", "")), situ])
    itens_proc = "".join(f"<li>{E(limpa(v))}</li>" for v in conf["itens_procuradoria"].values())

    # ---- benchmarking
    linhas_b = []
    for c in bench["casos"]:
        ctx = c.get("contexto", {})
        linhas_b.append([E(c["pratica"]), E(f"{ctx.get('orgao','')} ({ctx.get('pais','')})"),
                         E(limpa(c.get("resultado_reportado", ""))[:260]), E(c["fonte"].get("camada", ""))])

    # ---- melhorias
    def tab_melh(f):
        return tabela(["Id", "Melhoria", "Efeito esperado (hipótese)"],
                      [[E(m["id"]), "<b>" + E(m["titulo"]) + "</b><br><span class='mut'>" + E(limpa(m["descricao"]))[:420] + "</span>",
                        E(limpa(m.get("efeito_esperado", "")))] for m in por_fase[f]], "small")

    # ---- simulação
    linhas_sim = [["Situação atual", "—", f"{num(lb('vistoria_email'))}", "—", f"{num(lb('ate_parecer'))}", "—"]]
    for f in (1, 2, 3):
        for cen in ("conservador", "esperado", "otimista"):
            linhas_sim.append([f"Fase {f}", cen, num(fase(f, cen, "vistoria_email")), f"{num(ganho(f, cen, 'vistoria_email'))}%",
                               num(fase(f, cen, "ate_parecer")), f"{num(ganho(f, cen, 'ate_parecer'))}%"])

    # ---- indicadores
    linhas_ind = []
    for i in ctrl["indicadores"]:
        lbv = i.get("linha_base") or {}
        base = f"{num(lbv['valor']) if isinstance(lbv.get('valor'), (int, float)) else E(str(lbv.get('valor', '—')))} {E(lbv.get('unidade', ''))}"
        metas = {m["fase"]: m for m in i.get("metas", [])}

        def mt(f):
            m = metas.get(f)
            if not m:
                return "—"
            v = m.get("valor")
            return (num(v) if isinstance(v, (int, float)) else E(str(v))) + " " + E(m.get("unidade", ""))
        linhas_ind.append([E(i["id"]), E(i["nome"]), base, mt(1), mt(2), mt(3), E(i.get("responsavel", ""))])

    controles = "".join(f"<li><b>{E(c['id'])}</b> — {E(limpa(c.get('nome') or c.get('controle') or c.get('descricao','')))}"
                        f"{(' <span class=mut>(' + E(c['responsavel']) + ')</span>') if c.get('responsavel') else ''}</li>"
                        for c in ctrl["controles_internos"])

    perguntas = aval.get("perguntas_validacao") or []
    gar = aval["gargalo"]

    css = """
    @page { size: A4; margin: 18mm 16mm 18mm 16mm; }
    @page paisagem { size: A4 landscape; margin: 12mm; }
    body { font: 10.5pt/1.45 'Segoe UI', Calibri, Arial, sans-serif; color:#1d1d1f; }
    h1 { font-size: 22pt; color:#1f4e79; margin:0 0 6mm; }
    h2 { font-size: 15pt; color:#1f4e79; border-bottom: 2px solid #1f4e79; padding-bottom:2mm; margin: 8mm 0 4mm; break-after: avoid; }
    h3 { font-size: 12pt; color:#1f4e79; margin: 5mm 0 2mm; break-after: avoid; }
    p { margin: 0 0 3mm; text-align: justify; }
    table { border-collapse: collapse; width: 100%; margin: 2mm 0 5mm; font-size: 9pt; }
    th { background:#1f4e79; color:#fff; text-align:left; padding: 1.6mm 2mm; }
    td { border-bottom: 1px solid #d0d4d9; padding: 1.6mm 2mm; vertical-align: top; }
    tr { break-inside: avoid; }
    table.small { font-size: 8.4pt; }
    td:first-child { white-space: nowrap; }
    .mut { color:#5f6368; }
    .capa { height: 245mm; display:flex; flex-direction:column; justify-content:center; break-after: page; }
    .capa .sub { font-size: 13pt; color:#5f6368; margin-bottom: 14mm; }
    .capa .meta { font-size: 10pt; color:#5f6368; border-top:1px solid #d0d4d9; padding-top:4mm; }
    .kpis { display:grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; margin: 4mm 0 6mm; }
    .kpi { border:1px solid #d0d4d9; border-left: 4px solid #1f4e79; padding: 3mm; break-inside: avoid; }
    .kpi .v { font-size: 18pt; font-weight: 700; color:#1f4e79; }
    .kpi .l { font-size: 8.8pt; color:#5f6368; }
    .aviso { background:#fff8e1; border-left:4px solid #b58105; padding: 3mm 4mm; margin: 3mm 0 5mm; font-size: 9.5pt; }
    .diag { page: paisagem; break-before: page; break-after: page; }
    .diag svg { width: 100%; height: auto; max-height: 165mm; }
    .quebra { break-before: page; }
    ul { margin: 0 0 3mm 5mm; padding-left: 4mm; } li { margin-bottom: 1.4mm; }
    """

    secoes = f"""
<div class="capa">
  <h1>Mapeamento e proposta de melhoria do processo de fiscalizações programadas de saneamento</h1>
  <div class="sub">Estudo de caso: fiscalizações programadas de 2024 da Câmara Técnica de Saneamento (CASAN/AGENERSA-RJ)
  nas unidades da concessionária Águas do Rio – Bloco 1<br>Processo SEI-480002/001314/2024</div>
  <div class="meta">Relatório gerencial · {hoje}<br>Aplicação da metodologia de mapeamento de processos a partir dos autos do SEI
  (fases 0 a 4: base documental, AS-IS, conformidade legal, benchmarking, TO-BE e priorização da automação).
  Documento de trabalho: as metas e ganhos são hipóteses a validar com a unidade dona do processo.</div>
</div>

<h2>1. Sumário executivo</h2>
<p>O processo analisado reúne, em um único expediente SEI, as vistorias anuais da CASAN em estações elevatórias,
ETAs e ETEs de uma concessionária de saneamento, os relatórios de fiscalização, os ofícios de encaminhamento, o parecer
anual sobre as providências da concessionária e o envio à Procuradoria após a contestação. Cada relatório foi tratado
como um caso do subprocesso vistoria → relatório → aprovação → ofício, o que permitiu medir tempos com medianas.</p>
<div class="kpis">
  <div class="kpi"><div class="v">{F('casos.total')}</div><div class="l">relatórios de fiscalização analisados (de {F('contagem.relatorios_citados_parecer')} citados no parecer anual)</div></div>
  <div class="kpi"><div class="v">{F('casos.vistoria_email.mediana_du')} du</div><div class="l">mediana da vistoria ao envio do relatório à concessionária</div></div>
  <div class="kpi"><div class="v">{F('casos.vistoria_1a_assinatura.mediana_du')} du</div><div class="l">mediana da vistoria à 1ª assinatura do relatório — gargalo provável</div></div>
  <div class="kpi"><div class="v">{F('intervalo.ultimo_oficio_parecer_du')} du</div><div class="l">do último ofício ao parecer anual consolidado</div></div>
  <div class="kpi"><div class="v">{num(conf['pct_conforme_casos'])}%</div><div class="l">dos casos verificáveis conformes aos {n_req} requisitos legais levantados</div></div>
  <div class="kpi"><div class="v">{num(fase(1,'esperado','vistoria_email'))} du</div><div class="l">ciclo vistoria → envio projetado já na fase 1 (cenário esperado), sem tecnologia nova</div></div>
</div>
<p><b>Principais achados.</b> (1) O maior tempo do ciclo está entre a vistoria e a primeira assinatura do relatório,
trecho controlável pela própria CASAN; há indícios de relatórios prontos aguardando assinatura. (2) Os relatórios são
aprovados e enviados em lotes ({F('lotes.aprovacao.n')} lotes no ano), com {F('casos.cadeias_distintas')} cadeias de
assinatura diferentes. (3) {F('casos.variante.sem_oficio_de_encaminhamento_nos_autos')} relatórios aprovados não têm ofício
de encaminhamento nos autos exportados. (4) A análise das respostas da concessionária fica concentrada em um parecer
anual único, emitido muito depois do fim dos prazos. (5) O prazo de resposta dos ofícios ({F('oficios.prazo_resposta_unico')}
dias) não diz se é contado em dias úteis ou corridos.</p>
<p><b>Proposta.</b> {n_melh} melhorias em três fases cumulativas — organizacionais rápidas, estruturantes (rito e padrão
técnico) e digitais — que, no cenário esperado, reduzem a mediana do ciclo vistoria → envio de
{num(lb('vistoria_email'))} para {num(fase(3,'esperado','vistoria_email'))} dias úteis e do ciclo vistoria → análise da
resposta de {num(lb('ate_parecer'))} para {num(fase(3,'esperado','ate_parecer'))} dias úteis, sem encurtar o prazo
concedido à concessionária.</p>
<p><b>Decisões pedidas à gestão.</b> Validar o gargalo e as metas internas com a CASAN; submeter à Procuradoria os
pontos de interpretação legal listados na seção 5; medir o volume anual de relatórios de fiscalização de todas as
concessionárias, que define se o processo justifica automação dedicada.</p>
<div class="aviso"><b>Limites.</b> O PDF exportado é um recorte dos autos: as respostas da concessionária e parte dos
relatórios e ofícios não constam. Não há trilha de andamentos do SEI, então não se mede com qual unidade o processo
estava nem horas de trabalho. Dias úteis pelo calendário do RJ (pontos facultativos não conferidos). Todo efeito de
melhoria é hipótese até validação com a unidade.</div>

<h2 class="quebra">2. Objeto e método</h2>
<p>A análise partiu exclusivamente dos documentos do processo ({F('contagem.documentos')} documentos,
{F('contagem.paginas')} páginas): de cada documento extraiu-se data, unidade, função do signatário, ação no processo,
não conformidades, prazos e normas citadas. As datas das assinaturas eletrônicas formam a linha do tempo; os tempos são
calculados por rotina reprodutível. O fluxo foi modelado em BPMN, avaliado pelos critérios Lean (desperdícios), mapa de
fluxo de valor e teoria das restrições (gargalo), confrontado com os requisitos legais e com práticas de outros
reguladores, e então redesenhado (TO-BE) e simulado em três cenários.</p>
<p>O processo é do mesmo tipo do processo de referência “fiscalização técnica de campo” da metodologia, o que permitiu
comparar resultados e reaproveitar casos de benchmarking já verificados.</p>

<h2>3. Como o processo funciona hoje (AS-IS)</h2>
<ol>
<li>O Conselho-Diretor determina vistorias anuais por concessionária; a CASAN agenda as vistorias com a concessionária.</li>
<li>A equipe de fiscalização vistoria a unidade e redige o relatório (checklist, fotos, não conformidades e recomendações).</li>
<li>O relatório recebe até {F('casos.assinaturas.max')} assinaturas, em cadeias de cargos variáveis, até o “De acordo” do Gerente.</li>
<li>Relatórios aprovados seguem em lote, por ofício com prazo de resposta, enviado por e-mail pelo SEI.</li>
<li>As respostas da concessionária chegam fora do processo exportado; a CASAN as analisa em um parecer anual único,
encaminhado à Secretaria Executiva para ciência da concessionária.</li>
<li>A concessionária contestou o escopo; a CASAN reiterou o parecer e a Secretaria Executiva enviou o processo à
Procuradoria (fim do recorte).</li>
</ol>
<h3>Tempos medidos (dias úteis)</h3>
{tabela(["Trecho", "Mediana", "Faixa", "Relatórios"], tempos)}
<p class="mut">Não conformidades registradas nos relatórios do PDF: {F('contagem.nao_conformidades_total')}.
Relatórios sem ofício de encaminhamento nos autos: {F('casos.variante.sem_oficio_de_encaminhamento_nos_autos')}
(contra {F('casos.variante.com_oficio_de_encaminhamento_nos_autos')} com ofício).</p>

<div class="diag"><h2>Diagrama do processo atual (AS-IS)</h2>{svgs['asis']}</div>

<h2>4. Gargalo e desperdícios</h2>
<p><b>Gargalo declarado (hipótese a validar):</b> {E(limpa(gar.get('onde','')))}</p>
<p>Decompondo o trecho com a data de fecho escrita no texto do relatório: da vistoria ao fecho do texto, mediana de
{F('lb.vistoria_fecho.mediana_du')} du; do fecho à primeira assinatura, mediana de {F('lb.fecho_1a_assinatura.mediana_du')} du —
indício de texto pronto aguardando assinatura.</p>
<h3>Desperdícios identificados</h3>
<ul>{desp}</ul>

<h2 class="quebra">5. Conformidade legal</h2>
<p>Foram levantados {n_req} requisitos (Deliberação AGENERSA 4216/2021, instrução normativa de fiscalização, lei estadual
de processo administrativo, regimento, contrato de concessão e outros). Os trechos transcritos nos autos foram conferidos
contra o texto do processo; as normas apenas citadas estão marcadas para obtenção do texto integral. Nos casos com dado
suficiente: {cc['conforme']} conformes, {cc['não conforme']} não conformes, {cc['sem evidência']} sem evidência nos autos e
{cc['não aplicável']} não aplicáveis.</p>
{tabela(["Requisito", "Exigência", "Criticidade", "Situação no caso"], linhas_conf, "small")}
<h3>Pontos para a Procuradoria</h3>
<ul>{itens_proc}</ul>

<h2 class="quebra">6. Benchmarking</h2>
<p>{n_bench} práticas de outros reguladores e estudos, {n_cient} delas de fonte científica, todas com trecho literal
conferido na fonte. Resultados de outros contextos são tratados como teto, não como meta.</p>
{tabela(["Prática", "Onde", "Resultado reportado", "Fonte"], linhas_b, "small")}

<h2 class="quebra">7. Processo proposto (TO-BE)</h2>
<p>O TO-BE mantém todas as decisões humanas e o prazo concedido à concessionária. Muda: cronograma anual e aviso de
fiscalização com antecedência mínima; checklist por tipo de unidade e relatório em modelo padrão com meta interna;
conferência de forma antes da assinatura; aprovação em fluxo contínuo, sem lotes; ofício gerado no “De acordo” com prazo
e unidade de contagem expressos; análise das respostas relatório a relatório, com regra escrita de escalada e painel de
pendências; parecer anual apenas de consolidação; e tese-padrão para contestações de escopo.</p>
<h3>Fase 1 — rápidas (organização, sem norma nova nem tecnologia)</h3>{tab_melh('1')}
<h3>Fase 2 — estruturantes (rito, norma interna, padrão técnico)</h3>{tab_melh('2')}
<h3>Fase 3 — digitais e automação (sempre com conferência humana)</h3>{tab_melh('3')}

<div class="diag"><h2>Diagrama do processo proposto (TO-BE)</h2>{svgs['tobe']}</div>

<h2>8. Simulação dos ganhos</h2>
<p>Cada relatório foi refeito com os efeitos de cada fase, em três cenários. O prazo concedido à concessionária é
preservado em todas as fases. Mediana por relatório, em dias úteis, e redução sobre a situação atual:</p>
{tabela(["Fase", "Cenário", "Vistoria → envio", "Redução", "Vistoria → análise da resposta", "Redução"], linhas_sim)}
<div class="aviso">O ganho no ciclo vistoria → envio depende sobretudo da meta interna da fase 1 (M-FIS-01): sem ela, a
mediana piora {F('sens.M-FIS-01.vistoria_email_mediana_du')} du. O ganho no ciclo até a análise vem da mudança de rito
(análise por relatório em vez de parecer anual) e depende de capacidade da equipe, não medida. Reduções acima de 60%
exigem revisão dos parâmetros com a CASAN antes de virar meta. Com poucos relatórios por ciclo, os percentuais são
ordem de grandeza.</div>

<h2 class="quebra">9. Indicadores, metas e controles</h2>
<p>Metas do cenário esperado por fase. Indicadores de qualidade acompanham os de prazo, para que a meta de tempo não
empurre relatório incompleto para a assinatura.</p>
{tabela(["Id", "Indicador", "Situação atual", "Fase 1", "Fase 2", "Fase 3", "Responsável"], linhas_ind, "small")}
<h3>Controles internos propostos</h3>
<ul>{controles}</ul>

<h2>10. Prioridade de automação</h2>
<p>Pelos critérios da matriz de priorização (volume, padronização, regras explícitas, dados estruturados, risco e ganho no
gargalo), o processo obtém nota conservadora de {num(nc['conservadora_unidade_processo'])} contado por processo e de
{num(nc['conservadora_unidade_relatorio'])} contado por relatório: fica em “reavaliar com dados”. O conteúdo é muito
repetitivo — as não conformidades se concentram em poucas categorias recorrentes —, o que favorece checklist digital e
redação assistida do relatório. Contudo, com o volume de um só bloco de concessão, o retorno estimado em horas não cobre o
custo de um sistema dedicado; a decisão depende do volume anual de relatórios de todas as concessionárias.
Sequência sugerida: (1) controle de prazos e rastreabilidade (fila de assinatura, conferência aprovado × oficiado,
prazo de resposta alertado); (2) checklist digital e redação assistida; (3) acompanhamento das respostas e consolidação
do parecer.</p>
<p class="mut">Horas e custos usados na priorização são hipótese, emprestados de processo semelhante, até calibração com a CASAN.</p>

<h2>11. Pendências de validação e próximos passos</h2>
<ol>
<li><b>CASAN (dona do processo):</b> validar o gargalo e a hipótese de relatório pronto aguardando assinatura; aceitar ou
ajustar a meta interna (M-FIS-01), o checklist por tipo de unidade (M-FIS-07) e a análise das respostas por relatório
(M-FIS-08/M-FIS-14); confirmar a capacidade da equipe.</li>
<li><b>CASAN e planejamento:</b> aceitar ou ajustar as metas e os responsáveis pelos alertas.</li>
<li><b>Procuradoria:</b> unidade de contagem e termo inicial do prazo dos ofícios; prazo de análise das respostas;
prazos-padrão por gravidade; exigência de fundamento normativo no relatório; regra de escalada e procedimento
sancionatório; tese-padrão sobre o escopo; cronograma anual exigido pela Deliberação 4216/2021.</li>
<li><b>Controle interno:</b> aceitar os testes de auditoria contínua.</li>
<li><b>Gestão e TI:</b> acesso de leitura aos andamentos do SEI para o painel de prazos; medição do volume anual de
relatórios de todas as concessionárias; decisão sobre o painel público de não conformidades.</li>
</ol>
{('<h3>Perguntas de validação</h3><ol>' + ''.join(f'<li>{E(limpa(q if isinstance(q,str) else q.get("pergunta", str(q))))}</li>' for q in perguntas) + '</ol>') if perguntas else ''}
"""
    return f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><title>Mapeamento — Fiscalizações programadas 2024</title><style>{css}</style></head><body>{secoes}</body></html>"


def main():
    OUT.mkdir(exist_ok=True)
    svgs = exportar_svgs()
    for k in svgs:  # remove dimensões fixas para o SVG escalar na página
        svgs[k] = re.sub(r'<svg([^>]*?)\swidth="[^"]*"\sheight="[^"]*"', r'<svg\1', svgs[k], count=1)
    doc = montar_html(svgs)
    # IA só aparece como solução proposta no TO-BE; o relatório não fala de como foi produzido nem de caminhos locais
    proibidos = re.findall(r"\b(?:Claude|C:\\\\|_FIS\.json)\b", doc)
    sobras = re.findall(r"\b(?:casos|lb|tobe|sens|intervalo|contagem)\.[a-z_]+\.[\w.]+", re.sub(r"<[^>]+>", " ", doc))
    if proibidos or sobras:
        print("ATENÇÃO, termos a revisar:", set(proibidos), set(sobras))
    arq_html = OUT / "relatorio_FIS.html"
    arq_html.write_text(doc, encoding="utf-8")
    pdf = OUT / "Relatorio_Mapeamento_Fiscalizacoes_2024.pdf"
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page()
        pg.goto(arq_html.as_uri())
        pg.pdf(path=str(pdf), format="A4", print_background=True, prefer_css_page_size=True,
               display_header_footer=True, header_template="<span></span>",
               footer_template="<div style='font-size:8px;width:100%;text-align:center;color:#777'>"
                               "Mapeamento — Fiscalizações programadas 2024 · página <span class='pageNumber'></span> de "
                               "<span class='totalPages'></span></div>")
        nav.close()
    print(pdf)


if __name__ == "__main__":
    main()
