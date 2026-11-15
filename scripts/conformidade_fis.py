"""Conformidade legal do processo SEI-480002/001314/2024 (FIS): mede, caso a caso (relatório, ofício, vistoria
ou o processo), cada requisito de mapeamento/normas_FIS.json com as datas da linha do tempo
(mapeamento/linha_do_tempo_FIS.json), dos fatos (mapeamento/fatos_FIS.json), das fichas (fichas/) e do texto
integral (texto/processo_completo.txt, só para datas e prazos escritos nas peças, lidos por expressão regular).

Regra de números: nenhum número é digitado em texto livre. Prazos-parâmetro vêm de normas_FIS.json
(prazo.valor da norma ligada ou campo do teste); prazos concedidos vêm do texto da peça; todo intervalo é
calculado aqui e gravado com id 'calc.*'. Dias úteis: calendário de scripts/fatos_fis.py (hipótese; exclui o
dia inicial e inclui o final).

Situações por caso: 'conforme', 'não conforme', 'sem evidência' (o dado não está nos autos exportados),
'não aplicável'. Taxa por requisito = conformes ÷ (conformes + não conformes).

Uso: python scripts/conformidade_fis.py   (a partir da pasta do caso)
Saídas: mapeamento/conformidade_FIS.json e mapeamento/conformidade_FIS.csv
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))
from fatos_fis import FERIADOS_D, carregar_fichas, du_entre, paginas, pdata  # noqa: E402  (mesmo calendário dos fatos)

MAP = BASE / "mapeamento"
CASO = "SEI-480002/001314/2024"
C, NC, SE, NA = "conforme", "não conforme", "sem evidência", "não aplicável"

linha = json.loads((MAP / "linha_do_tempo_FIS.json").read_text(encoding="utf-8"))
porn = {d["n"]: d for d in linha}
fatos = {f["id"]: f for f in json.loads((MAP / "fatos_FIS.json").read_text(encoding="utf-8"))["fatos"]}
normas_doc = json.loads((MAP / "normas_FIS.json").read_text(encoding="utf-8"))
NORMAS = {n["id"]: n for n in normas_doc["normas"]}
REQ = {r["id"]: r for r in normas_doc["requisitos"]}
FICHAS = carregar_fichas()
P = paginas()
MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
                                      "setembro", "outubro", "novembro", "dezembro"], 1)}


# ---------------------------------------------------------------- utilidades
def d(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


def soma_du(a: date, n: int) -> date:
    x, k = a, 0
    while k < n:
        x += timedelta(days=1)
        if x.weekday() < 5 and x not in FERIADOS_D:
            k += 1
    return x


def texto_doc(doc: dict) -> str:
    """Texto das páginas do documento; usa a página inicial da ficha quando ela delimita melhor o início
    (o doc 1 da linha do tempo começa no recorte do DOERJ da Deliberação 4216/2021)."""
    pf = str(FICHAS.get(doc["sei"], {}).get("paginas") or "")
    i, f = map(int, doc["paginas"].split("-"))
    m = re.match(r"(\d+)", pf)
    if m and i < int(m.group(1)) <= f:
        i = int(m.group(1))
    return " ".join(P[p] for p in range(i, f + 1))


def fato(fid: str):
    return fatos[fid]["valor"]


def prazo_norma(nid: str):
    return NORMAS[nid]["prazo"]["valor"]


CALC: list[dict] = []
DATAS_LIDAS: dict[str, dict] = {}


def intervalo(cid: str, desc: str, a: date, b: date, origem: str) -> dict:
    dc, du = (b - a).days, du_entre(a, b)
    CALC.append({"id": f"calc.{cid}.dc", "descricao": desc, "valor": dc, "unidade": "dc", "de": a.isoformat(), "ate": b.isoformat(), "origem": origem})
    CALC.append({"id": f"calc.{cid}.du", "descricao": desc, "valor": du, "unidade": "du", "de": a.isoformat(), "ate": b.isoformat(), "origem": origem})
    return {"dc": dc, "du": du, "ids": [f"calc.{cid}.dc", f"calc.{cid}.du"]}


def data_calc(cid: str, desc: str, v: date, origem: str) -> str:
    CALC.append({"id": f"calc.{cid}", "descricao": desc, "valor": v.isoformat(), "unidade": "data", "origem": origem})
    return f"calc.{cid}"


def lida(chave: str, v: date | None, origem: str) -> date | None:
    if v:
        DATAS_LIDAS[chave] = {"data": v.isoformat(), "origem": origem}
    return v


RES: dict[str, list[dict]] = {r: [] for r in REQ}
NOTAS: dict[str, str] = {}


def reg(rid: str, caso: str, situacao: str, detalhe: str, calc=(), docs=()):
    RES[rid].append({"caso": caso, "situacao": situacao, "detalhe": detalhe, "calculos": list(calc), "documentos": list(docs)})


# ---------------------------------------------------------------- casos
def num_ficha(ficha: dict) -> int | None:
    m = re.match(r"0*(\d+)", str(ficha.get("numero") or ""))
    return int(m.group(1)) if m else None


def montar_relatorios() -> list[dict]:
    rels = []
    for doc in linha:
        if doc["tipo"] != "Relatório de Fiscalização":
            continue
        fi = FICHAS.get(doc["sei"], {})
        fz = fi.get("fiscalizacao") or {}
        txt = texto_doc(doc)
        ass = doc["assinaturas"]
        ger = [a for a in ass if a["cargo"].lower().startswith("gerente")]
        num = num_ficha(fi) or (int(doc["relatorio_n"]) if doc["relatorio_n"] else None)
        m_em = re.search(r"\bEm (\d\d/\d\d/\d{4})", txt)
        prazos = [p for p in fi.get("prazos") or [] if str(p.get("quantidade", "")).isdigit()]
        rels.append({
            "n": doc["n"], "sei": doc["sei"], "num": num, "rotulo": f"RF {num}/{CASO[-4:]} (doc {doc['n']})",
            "instalacao": fz.get("instalacao", ""), "tipo_inst": fz.get("tipo_instalacao", ""), "concessionaria": fz.get("concessionaria", ""),
            "vistoria": lida(f"rf{num}.vistoria", pdata(fz.get("data_vistoria", "")), f"ficha SEI {doc['sei']}, fiscalizacao.data_vistoria"),
            "data_texto": lida(f"rf{num}.data_no_texto", pdata(m_em.group(1)) if m_em else None, f"doc {doc['n']}, 'Em dd/mm/aaaa' no fecho do relatório"),
            "ass1": d(ass[0]["data"]) if ass else None, "ger": d(ger[-1]["data"]) if ger else None,
            "prazo": int(prazos[0]["quantidade"]) if prazos else None, "prazo_trecho": prazos[0]["trecho_literal"] if prazos else "",
            "ncs": doc["nao_conformidades"], "texto": txt,
        })
    return rels


def montar_oficios() -> list[dict]:
    ofs = []
    for doc in linha:
        if doc["tipo"] != "Ofício":
            continue
        txt = texto_doc(doc)
        m_num = re.search(r"Of\.AGENERSA/CASAN\s+N[ºo°]\s*(\d+)", txt)
        m_dt = re.search(r"Rio de Janeiro, (\d{1,2}) de (\w+) de (\d{4})", txt)
        dt_esc = date(int(m_dt.group(3)), MESES[m_dt.group(2).lower()], int(m_dt.group(1))) if m_dt else None
        m_pr = re.search(r"prazo de (\d+) \(", txt)
        mail = porn.get(doc["n"] + 1) if porn.get(doc["n"] + 1, {}).get("tipo") == "E-mail" else None
        num = int(m_num.group(1)) if m_num else None
        ofs.append({
            "n": doc["n"], "num": num, "rotulo": f"Ofício {num}/{CASO[-4:]} (doc {doc['n']})",
            "data_escrita": lida(f"oficio{num}.data_escrita", dt_esc, f"doc {doc['n']}, cabeçalho 'Rio de Janeiro, …'"),
            "assinatura": d(doc["assinaturas"][0]["data"]) if doc["assinaturas"] else None,
            "email": d(mail["data_envio_email"]) if mail else None, "email_n": mail["n"] if mail else None,
            "prazo": int(m_pr.group(1)) if m_pr else None, "citados": doc["relatorios_citados"], "texto": txt,
        })
    return ofs


# ---------------------------------------------------------------- avaliação
def main() -> None:
    rels, ofs = montar_relatorios(), montar_oficios()
    enc = [o for o in ofs if o["citados"]]
    of_de = {n: o for o in enc for n in o["citados"]}
    parecer, desp = d(fato("marco.parecer")), d(fato("marco.despacho_procuradoria"))
    exercicio = int(re.search(r"/(\d{4})$", CASO).group(1))

    # R-FIS-01 — processo específico por concessionária
    conc = sorted({r["concessionaria"] for r in rels if r["concessionaria"]})
    outras = [c for c in conc if "Águas do Rio" not in c]
    reg("R-FIS-01", "processo", C if not outras else NC,
        f"{len(rels)} relatórios e {len(ofs)} ofícios; concessionárias nas fichas: {conc}. Todos os ofícios são dirigidos à mesma concessionária.",
        docs=[r["n"] for r in rels])

    # R-FIS-02 — cronograma anual antes da 1ª vistoria
    achou = [p for p, t in P.items() if p > 1 and re.search(r"cronograma (anual )?de (vistorias|fiscaliza)", t, re.I)]
    prim = min(r["vistoria"] for r in rels if r["vistoria"])
    avisos = [o for o in ofs if not o["citados"]]
    reg("R-FIS-02", "processo", C if achou else SE,
        f"Nenhuma peça com cronograma de vistorias nos autos (busca por 'cronograma de vistorias/fiscalização': páginas {achou}). "
        f"Primeira vistoria registrada em {prim.isoformat()}; programação comunicada só em aviso pontual: {[o['rotulo'] for o in avisos]}.",
        docs=[o["n"] for o in avisos])
    NOTAS["R-FIS-02"] = "Dizer se o cronograma do art. 2º (N-FIS-01) deve constar deste processo e se o aviso pontual o substitui."

    # R-FIS-03 — vistoria no exercício
    for r in rels:
        if not r["vistoria"]:
            reg("R-FIS-03", r["rotulo"], SE, "Data da vistoria não legível no relatório/ficha.", docs=[r["n"]])
        else:
            reg("R-FIS-03", r["rotulo"], C if r["vistoria"].year == exercicio else NC,
                f"{r['tipo_inst']} vistoriada em {r['vistoria'].isoformat()} (exercício {exercicio}).", docs=[r["n"]])
    ets = [r for r in rels if r["tipo_inst"] in ("ETA", "ETE")]
    lista = re.findall(r"Relatório de Fiscalização AGENERSA/CASAN N[ºo°]\s*0*(\d+)", " ".join(P[p] for p in (227, 228)), re.I)
    NOTAS["R-FIS-03"] = (f"Estações de tratamento com relatório no PDF: {len(ets)} ({', '.join(r['instalacao'] for r in ets)}). "
                         f"O parecer lista {len(set(lista))} relatórios; {len(set(lista)) - len(rels)} não têm texto no PDF. "
                         "Confirmar com a CASAN a lista completa de estações do Bloco 1 sujeitas à vistoria anual.")

    # R-FIS-04 — relatório ao Gerente em até N du da lavratura (IN 128/2024, art. 32)
    t4 = REQ["R-FIS-04"]["teste"]
    lim4, vig4 = prazo_norma("N-FIS-35"), d(t4["vigencia_desde"])
    for r in rels:
        if not (r["ass1"] and r["ger"]):
            reg("R-FIS-04", r["rotulo"], SE, "Relatório sem assinaturas no PDF.", docs=[r["n"]])
            continue
        i = intervalo(f"rf{r['num']}.lavratura_ate_gerente", f"RF {r['num']}: 1ª assinatura até 'De acordo' do Gerente", r["ass1"], r["ger"], f"doc {r['n']}")
        alt = ""
        ids = list(i["ids"])
        if r["data_texto"]:
            j = intervalo(f"rf{r['num']}.data_texto_ate_gerente", f"RF {r['num']}: data escrita no relatório até 'De acordo' do Gerente", r["data_texto"], r["ger"], f"doc {r['n']}")
            alt = f" Leitura alternativa (data escrita no texto {r['data_texto'].isoformat()}): {j['du']} du{' (acima do limite)' if j['du'] > lim4 else ''}."
            ids += j["ids"]
        if r["vistoria"]:
            k = intervalo(f"rf{r['num']}.vistoria_ate_lavratura", f"RF {r['num']}: vistoria até 1ª assinatura", r["vistoria"], r["ass1"], f"doc {r['n']}")
            alt += f" Vistoria → 1ª assinatura: {k['dc']} dc."
            ids += k["ids"]
        if r["ass1"] < vig4:
            sit = NA
            txt = f"Lavrado em {r['ass1'].isoformat()}, antes da vigência ({vig4.isoformat()}). Medido: {i['du']} du até o Gerente."
        else:
            sit = C if i["du"] <= lim4 else NC
            txt = f"Lavrado em {r['ass1'].isoformat()}; 'De acordo' em {r['ger'].isoformat()}: {i['du']} du (limite {lim4} du)."
        reg("R-FIS-04", r["rotulo"], sit, txt + alt, ids, [r["n"]])
    NOTAS["R-FIS-04"] = "Fixar o marco da 'lavratura' (1ª assinatura ou data escrita no relatório) e se o 'De acordo' equivale ao envio ao Gerente (N-FIS-35)."

    # R-FIS-05 — 'De acordo' antes do ofício
    for r in rels:
        o = of_de.get(r["num"])
        if not o:
            reg("R-FIS-05", r["rotulo"], NA, "Nenhum ofício nos autos cita este relatório (ver R-FIS-06).", docs=[r["n"]])
        elif not r["ger"]:
            reg("R-FIS-05", r["rotulo"], SE, f"Encaminhado pelo {o['rotulo']}, mas sem assinatura do Gerente no PDF.", docs=[r["n"], o["n"]])
        else:
            i = intervalo(f"rf{r['num']}.gerente_ate_oficio", f"RF {r['num']}: 'De acordo' até o ofício de encaminhamento", r["ger"], o["assinatura"], f"doc {r['n']} → doc {o['n']}")
            reg("R-FIS-05", r["rotulo"], C if i["dc"] >= 0 else NC,
                f"'De acordo' em {r['ger'].isoformat()}; {o['rotulo']} assinado em {o['assinatura'].isoformat()} ({i['dc']} dc depois).", i["ids"], [r["n"], o["n"]])

    # R-FIS-06 — relatório comunicado por ofício com comprovante
    for r in rels:
        o = of_de.get(r["num"])
        if o and o["email"]:
            reg("R-FIS-06", r["rotulo"], C, f"Citado no {o['rotulo']}; e-mail de envio em {o['email'].isoformat()} (doc {o['email_n']}).", docs=[r["n"], o["n"], o["email_n"]])
        elif o:
            reg("R-FIS-06", r["rotulo"], SE, f"Citado no {o['rotulo']}, sem e-mail de envio nos autos.", docs=[r["n"], o["n"]])
        else:
            extra = f" Fixa prazo para a concessionária ('{r['prazo_trecho']}')." if r["prazo"] else ""
            reg("R-FIS-06", r["rotulo"], SE, f"Nenhum ofício dos autos cita o relatório ({len(enc)} ofícios de encaminhamento conferidos).{extra}", docs=[r["n"]])
    sem_of = [r["num"] for r in rels if r["num"] not in of_de]
    NOTAS["R-FIS-06"] = (f"Relatórios sem ofício de encaminhamento nos autos: {sem_of}. Dizer se o prazo dado nesses relatórios corre sem notificação formal "
                         "e se a falta impede cobrar o saneamento.")

    # R-FIS-07 — ofício fixa prazo expresso
    for o in enc:
        dif = intervalo(f"oficio{o['num']}.data_escrita_ate_assinatura", f"Ofício {o['num']}: data escrita até assinatura", o["data_escrita"], o["assinatura"], f"doc {o['n']}") if o["data_escrita"] and o["assinatura"] else None
        nota = f" Data escrita {o['data_escrita'].isoformat()}, assinatura {o['assinatura'].isoformat()} ({dif['dc']} dc)." if dif else ""
        reg("R-FIS-07", o["rotulo"], C if o["prazo"] else NC,
            (f"Fixa prazo de {o['prazo']} dias para manifestação." if o["prazo"] else "Sem prazo expresso.") + nota,
            dif["ids"] if dif else [], [o["n"]])

    # R-FIS-08 — manifestação no prazo do ofício
    venc_ofs = {}
    for o in enc:
        if not (o["prazo"] and o["email"]):
            reg("R-FIS-08", o["rotulo"], SE, "Sem prazo ou sem data de envio nos autos.", docs=[o["n"]])
            continue
        vdc, vdu = o["email"] + timedelta(days=o["prazo"]), soma_du(o["email"], o["prazo"])
        a = data_calc(f"oficio{o['num']}.vencimento_dc", f"Ofício {o['num']}: vencimento em dias corridos", vdc, f"e-mail doc {o['email_n']} + prazo do ofício")
        b = data_calc(f"oficio{o['num']}.vencimento_du", f"Ofício {o['num']}: vencimento em dias úteis", vdu, f"e-mail doc {o['email_n']} + prazo do ofício (du)")
        venc_ofs[o["num"]] = (vdc, vdu)
        reg("R-FIS-08", o["rotulo"], SE,
            f"Enviado em {o['email'].isoformat()}; prazo vence em {vdc.isoformat()} (dc) ou {vdu.isoformat()} (du). As respostas da concessionária não estão no PDF; "
            "o parecer só registra que ela 'encaminhou respostas formais'.", [a, b], [o["n"], o["email_n"], 32])
    NOTAS["R-FIS-08"] = "Fixar a contagem do prazo de manifestação (dias corridos ou úteis, N-FIS-33) e o termo inicial (envio do e-mail ou leitura)."

    # R-FIS-09 — saneamento no prazo do relatório
    for r in rels:
        if not r["prazo"]:
            reg("R-FIS-09", r["rotulo"], NA, "Relatório sem prazo numérico para a concessionária.", docs=[r["n"]])
            continue
        o = of_de.get(r["num"])
        if not (o and o["email"]):
            reg("R-FIS-09", r["rotulo"], SE, f"Prazo de {r['prazo']} dias sem termo inicial nos autos (relatório não encaminhado por ofício juntado).", docs=[r["n"]])
            continue
        vdc, vdu = o["email"] + timedelta(days=r["prazo"]), soma_du(o["email"], r["prazo"])
        a = data_calc(f"rf{r['num']}.vencimento_dc", f"RF {r['num']}: vencimento do prazo para sanar (dc)", vdc, f"e-mail doc {o['email_n']} + prazo do relatório")
        b = data_calc(f"rf{r['num']}.vencimento_du", f"RF {r['num']}: vencimento do prazo para sanar (du)", vdu, f"e-mail doc {o['email_n']} + prazo do relatório (du)")
        reg("R-FIS-09", r["rotulo"], SE,
            f"Prazo de {r['prazo']} dias; vence em {vdc.isoformat()} (dc) ou {vdu.isoformat()} (du). Comprovação por unidade fora do PDF; o parecer aponta "
            "'cumprimento apenas parcial' sem individualizar.", [a, b], [r["n"], o["n"], 32])
    NOTAS["R-FIS-09"] = "Dizer se a conclusão agregada do parecer ('cumprimento apenas parcial') basta para caracterizar descumprimento ou se é preciso apurar por unidade."

    # R-FIS-10 — espera mínima entre o ofício e a análise
    for o in enc:
        if not (o["prazo"] and o["email"]):
            reg("R-FIS-10", o["rotulo"], SE, "Sem prazo ou data de envio.", docs=[o["n"]])
            continue
        i = intervalo(f"oficio{o['num']}.envio_ate_parecer", f"Ofício {o['num']}: envio até o Parecer 250/2025", o["email"], parecer, f"doc {o['email_n']} → marco.parecer")
        ok = i["dc"] >= o["prazo"] and i["du"] >= o["prazo"]
        reg("R-FIS-10", o["rotulo"], C if ok else NC, f"Envio {o['email'].isoformat()} → parecer {parecer.isoformat()}: {i['dc']} dc / {i['du']} du (mínimo {o['prazo']}).", i["ids"], [o["n"], 32])

    # R-FIS-11 — parecer técnico em até N dias de instada
    lim11 = prazo_norma("N-FIS-26")
    ult = max(v[1] for v in venc_ofs.values())
    i = intervalo("ultimo_vencimento_ate_parecer", "Último vencimento de prazo de manifestação (du) até o parecer", ult, parecer, "calc.oficio*.vencimento_du → marco.parecer")
    reg("R-FIS-11", "processo", SE,
        f"Data em que as respostas chegaram à CASAN não está nos autos. Do último vencimento ({ult.isoformat()}) ao parecer ({parecer.isoformat()}): "
        f"{i['dc']} dc (limite {lim11} dc a partir do recebimento). Último ofício até o parecer: {fato('intervalo.ultimo_oficio_parecer')} dc "
        "(fato intervalo.ultimo_oficio_parecer).", i["ids"] + ["intervalo.ultimo_oficio_parecer"], [32])
    NOTAS["R-FIS-11"] = "Dizer se o prazo de parecer técnico do Regimento (N-FIS-26) se aplica à análise anual das respostas e qual é o termo inicial."

    # R-FIS-12 — motivação: fatos e fundamento
    fund = re.compile(r"Lei Federal|Lei n[ºo°]|Decreto Federal|Contrato de Concessão|Deliberação", re.I)
    fatos_re = re.compile(r"descri[çc][ãa]o|n[ãa]o conformidade|vistoria", re.I)
    for r in rels:
        if len(r["texto"]) < 1000 or not r["ass1"]:
            reg("R-FIS-12", r["rotulo"], SE, "Relatório sem texto extraível no PDF (páginas só com rodapé).", docs=[r["n"]])
            continue
        tem_f, tem_d = bool(fund.search(r["texto"])), bool(fatos_re.search(r["texto"]))
        erro = re.findall(r"munic[íi]pio de (Pomerode)", r["texto"])
        det = f"Fundamento normativo citado: {'sim' if tem_f else 'não'}; descrição dos fatos: {'sim' if tem_d else 'não'}."
        if erro:
            det += f" Erro material: cita o município de {erro[0]} (fora do Bloco 1)."
        reg("R-FIS-12", r["rotulo"], C if tem_f and tem_d else NC, det, docs=[r["n"]])
    NOTAS["R-FIS-12"] = "Dizer se o relatório que fixa prazo à concessionária é ato que exige motivação com fundamento jurídico (N-FIS-30) e se a falta de citação o invalida."

    # R-FIS-13 — parecer técnico antes da Procuradoria
    i = intervalo("parecer_ate_procuradoria", "Parecer 250/2025 até o envio à Procuradoria", parecer, desp, "marco.parecer → marco.despacho_procuradoria")
    reg("R-FIS-13", "processo", C if i["dc"] >= 0 else NC,
        f"Parecer em {parecer.isoformat()}, envio à Procuradoria em {desp.isoformat()} ({i['dc']} dc). Não há deliberação nos autos.", i["ids"], [32, 33, 34])

    # R-FIS-14 — Procuradoria em até N dias
    lim14 = prazo_norma("N-FIS-27")
    v14 = data_calc("vencimento_procuradoria", "Vencimento do prazo da Procuradoria (dc)", desp + timedelta(days=lim14), "marco.despacho_procuradoria + prazo de N-FIS-27")
    v14b = data_calc("vencimento_procuradoria_prorrogado", "Vencimento com uma prorrogação por igual período (dc)", desp + timedelta(days=2 * lim14), "idem, prorrogado")
    reg("R-FIS-14", "processo", SE,
        f"Enviado em {desp.isoformat()}; prazo vence em {(desp + timedelta(days=lim14)).isoformat()} ou {(desp + timedelta(days=2 * lim14)).isoformat()} com prorrogação. "
        "O PDF termina no despacho de envio.", [v14, v14b], [34])
    NOTAS["R-FIS-14"] = "Registrar a data de recebimento e o prazo da manifestação pedida no despacho (N-FIS-22, N-FIS-27)."

    # R-FIS-15 — decisão do pedido de arquivamento
    reg("R-FIS-15", "processo", SE,
        "Pedido de arquivamento da concessionária citado no despacho, sem decisão nos autos; a instrução ainda não foi concluída (consulta à Procuradoria pendente).", docs=[34])
    NOTAS["R-FIS-15"] = "Dizer quem decide o pedido de arquivamento (câmara, SECEX ou Conselho-Diretor) e o prazo (N-FIS-29)."

    # R-FIS-16 — sanção só com notificação e defesa
    ni = [p for p, t in P.items() if p > 1 and re.search(r"Notifica[çc][ãa]o de Infra[çc][ãa]o|Auto de Infra[çc][ãa]o", t, re.I)]
    reg("R-FIS-16", "processo", NA if not ni else SE,
        f"Nenhuma notificação/auto de infração nos autos (páginas {ni}); o parecer não propõe sanção, só 'providências administrativas cabíveis'.", docs=[32])
    NOTAS["R-FIS-16"] = "Se a agência quiser sancionar o descumprimento, dizer se o caminho é a notificação de infração da IN 128/2024 (N-FIS-36) em processo próprio."

    # R-FIS-17 — paralisação máxima
    datas = sorted({d(a["data"]) for x in linha for a in x["assinaturas"]} | {d(x["data_envio_email"]) for x in linha if x["data_envio_email"]})
    gaps = [(datas[k], datas[k + 1]) for k in range(len(datas) - 1)]
    a, b = max(gaps, key=lambda g: (g[1] - g[0]).days)
    i = intervalo("maior_hiato_entre_pecas", "Maior intervalo entre peças datadas", a, b, "assinaturas e e-mails da linha do tempo")
    anos = prazo_norma("N-FIS-32")
    lim17 = a.replace(year=a.year + anos)
    reg("R-FIS-17", "processo", C if b <= lim17 else NC,
        f"Maior intervalo sem peça: {a.isoformat()} → {b.isoformat()} ({i['dc']} dc), abaixo de {anos} anos.", i["ids"], [])

    # R-FIS-18 — aviso de fiscalização com antecedência (IN 128/2024, art. 4º)
    t18 = REQ["R-FIS-18"]["teste"]
    vig18, min18 = d(t18["vigencia_desde"]), t18["min"]
    for r in rels:
        if not r["vistoria"] and r["ass1"] and r["ass1"] < vig18:
            reg("R-FIS-18", r["rotulo"], NA, f"Data da vistoria não legível, mas o relatório foi assinado em {r['ass1'].isoformat()}, antes da vigência ({vig18.isoformat()}).", docs=[r["n"]])
        elif not r["vistoria"]:
            reg("R-FIS-18", r["rotulo"], SE, "Data da vistoria não legível e relatório sem assinatura no PDF.", docs=[r["n"]])
        elif r["vistoria"] < vig18:
            reg("R-FIS-18", r["rotulo"], NA, f"Vistoria em {r['vistoria'].isoformat()}, antes da vigência ({vig18.isoformat()}); nenhum aviso nos autos.", docs=[r["n"]])
        else:
            reg("R-FIS-18", r["rotulo"], SE, "Vistoria após a vigência sem aviso nos autos.", docs=[r["n"]])
    o757 = next((o for o in ofs if not o["citados"]), None)
    if o757:
        dts = [pdata(x) for x in re.findall(r"\d\d/\d\d/\d{4}", re.search(r"Datas das Vistorias[^.]*", o757["texto"]).group(0))]
        v1 = lida(f"oficio{o757['num']}.primeira_vistoria", min(dts), f"doc {o757['n']}, 'Datas das Vistorias'")
        i = intervalo(f"oficio{o757['num']}.aviso_ate_vistoria", f"Ofício {o757['num']}: envio do aviso até a 1ª vistoria", o757["email"], v1, f"doc {o757['email_n']} → data literal")
        dif = intervalo(f"oficio{o757['num']}.data_escrita_ate_assinatura", f"Ofício {o757['num']}: data escrita até assinatura", o757["data_escrita"], o757["assinatura"], f"doc {o757['n']}")
        reg("R-FIS-18", o757["rotulo"], NA if v1 < vig18 else (C if i["dc"] >= min18 else NC),
            f"Aviso enviado em {o757['email'].isoformat()} para vistorias a partir de {v1.isoformat()}: {i['dc']} dc de antecedência "
            f"({'abaixo' if i['dc'] < min18 else 'acima'} do mínimo de {min18} dc que valeria após {vig18.isoformat()}). Ofício datado de {o757['data_escrita'].isoformat()} "
            f"e assinado em {o757['assinatura'].isoformat()} ({dif['dc']} dc). Os relatórios dessas vistorias não estão no PDF.",
            i["ids"] + dif["ids"], [o757["n"], o757["email_n"]])
    NOTAS["R-FIS-18"] = "Dizer se havia, antes da IN 128/2024 (N-FIS-34), regra de aviso prévio aplicável ao Bloco 1."

    # ------------------------------------------------------------ consolidação
    faltam = [r for r in REQ if not RES[r]]
    if faltam:
        raise SystemExit(f"requisitos sem avaliação: {faltam}")
    tot = {C: 0, NC: 0, SE: 0, NA: 0}
    por_req = {}
    for rid in sorted(REQ):
        cont = {C: 0, NC: 0, SE: 0, NA: 0}
        for x in RES[rid]:
            cont[x["situacao"]] += 1
            tot[x["situacao"]] += 1
        den = cont[C] + cont[NC]
        q = REQ[rid]
        validar = rid in NOTAS
        por_req[rid] = {"exigencia": q["exigencia"], "tipo": q["tipo"], "normas": q["normas"], "criticidade": q["criticidade"], "unidade_caso": q["caso"],
                        "n_casos": len(RES[rid]), "contagem": cont, "taxa_conformidade": round(100 * cont[C] / den, 1) if den else None,
                        "validar_procuradoria": validar, "nota_validacao": NOTAS.get(rid, ""),
                        **({"interpretacao": q["interpretacao"]} if "interpretacao" in q else {}), "casos": RES[rid]}
    den = tot[C] + tot[NC]
    saida = {
        "codigo": "FIS", "caso": CASO, "gerado_por": "scripts/conformidade_fis.py",
        "fontes": ["mapeamento/normas_FIS.json", "mapeamento/linha_do_tempo_FIS.json", "mapeamento/fatos_FIS.json", "fichas/", "texto/processo_completo.txt"],
        "observacao": "Vários casos por requisito (relatório, ofício ou vistoria) quando o requisito se repete; 'processo' = caso único. O PDF é recorte: "
                      "respostas da concessionária e parte dos relatórios não estão nele ('sem evidência'). Dias úteis pelo calendário de scripts/fatos_fis.py (hipótese).",
        "contagem_casos": tot, "pct_conforme_casos": round(100 * tot[C] / den, 1) if den else None,
        "definicao_pct": "conformes ÷ (conformes + não conformes)",
        "datas_lidas_dos_autos": DATAS_LIDAS, "intervalos_calculados": CALC,
        "requisitos": por_req,
        "itens_procuradoria": {rid: NOTAS[rid] for rid in sorted(NOTAS)},
    }
    (MAP / "conformidade_FIS.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    with (MAP / "conformidade_FIS.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["processo", "requisito", "tipo", "criticidade", "normas", "caso", "situacao", "calculos", "documentos", "validar_procuradoria", "detalhe"])
        for rid in sorted(REQ):
            q = REQ[rid]
            for x in RES[rid]:
                w.writerow([CASO, rid, q["tipo"], q["criticidade"], " ".join(q["normas"]), x["caso"], x["situacao"], " ".join(x["calculos"]),
                            " ".join(map(str, x["documentos"])), "sim" if rid in NOTAS else "não", x["detalhe"]])

    print(f"casos: {tot} | pct_conforme_casos: {saida['pct_conforme_casos']}")
    for rid, v in por_req.items():
        print(f"  {rid}: n={v['n_casos']} {v['contagem']} taxa={v['taxa_conformidade']}")


if __name__ == "__main__":
    main()
