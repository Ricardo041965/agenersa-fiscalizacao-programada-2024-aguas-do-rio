"""Casos do subprocesso de fiscalização programada no processo FIS (SEI-480002/001314/2024, AGENERSA/RJ).

Etapa determinística: cada Relatório de Fiscalização dos autos é um caso do subprocesso
    vistoria -> relatório (1ª assinatura) -> revisão/assinaturas -> "De acordo" do Gerente da CASAN
    -> ofício de encaminhamento à concessionária -> e-mail de envio pelo SEI.
Para cada caso calcula datas e intervalos em dias corridos (dc) e úteis (du, calendário RJ de
scripts/fatos_fis.py, hipótese) e, entre os casos, n, mediana, mínimo e máximo. Também descreve os ofícios
(lote, prazo, data do texto x assinatura) e o ofício de agendamento de vistoria.

Entradas: mapeamento/linha_do_tempo_FIS.json (gerado por fatos_fis.py), fichas/fichas_parte*.json e o texto
integral (para o ofício de agendamento). Rode antes: python scripts/fatos_fis.py

Saídas: mapeamento/casos_FIS.json, mapeamento/casos_FIS.csv e, se mapeamento/evidencias_FIS.md existir com os
marcadores <!-- inicio:casos_fis --> / <!-- fim:casos_fis -->, as tabelas entre eles (nunca editar à mão).

Uso: python scripts/casos_fis.py   (a partir da pasta do caso)
"""
from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))
from fatos_fis import CASO, carregar_fichas, du_entre, paginas, pdata  # noqa: E402

MAP = BASE / "mapeamento"
CODIGO = "FIS"
TIPO_RF = "Relatório de Fiscalização"
MESES = {m: i for i, m in enumerate(
    ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
     "novembro", "dezembro"], 1)}

# Intervalos medidos por caso: (id, descrição, marco inicial, marco final)
INTERVALOS = [
    ("vistoria_1a_assinatura", "Vistoria até a 1ª assinatura do relatório (redação + espera)", "vistoria", "assinatura_1"),
    ("redacao_1a_assinatura", "Data escrita no relatório até a 1ª assinatura", "data_texto", "assinatura_1"),
    ("revisao_aprovacao", "1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas)", "assinatura_1", "aprovacao"),
    ("ultima_tecnica_aprovacao", "Última assinatura antes do Gerente até o 'De acordo'", "assinatura_pre_gerente", "aprovacao"),
    ("vistoria_aprovacao", "Vistoria até o 'De acordo' do Gerente", "vistoria", "aprovacao"),
    ("aprovacao_oficio", "'De acordo' até a assinatura do ofício de encaminhamento", "aprovacao", "oficio"),
    ("oficio_email", "Assinatura do ofício até o envio do e-mail pelo SEI", "oficio", "email"),
    ("vistoria_email", "Vistoria até o envio à concessionária (ciclo completo)", "vistoria", "email"),
]


def num(s) -> int | None:
    m = re.search(r"(\d+)", str(s or ""))
    return int(m.group(1)) if m else None


def data_extenso(txt: str) -> date | None:
    m = re.search(r"Rio de Janeiro, (\d{1,2})(?: de)? (\w+) de (\d{4})", txt)
    if not m or m.group(2).lower() not in MESES:
        return None
    return date(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1)))


def iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def resumo(vals: list[int]) -> dict:
    if not vals:
        return {"n": 0, "mediana": None, "min": None, "max": None}
    return {"n": len(vals), "mediana": statistics.median(vals), "min": min(vals), "max": max(vals)}


def cadeia(assinaturas: list[dict]) -> str:
    seq = []
    for a in assinaturas:
        c = a["cargo"].strip()
        if not seq or seq[-1] != c:
            seq.append(c)
    return " → ".join(seq)


def main() -> None:
    lt = json.loads((MAP / "linha_do_tempo_FIS.json").read_text(encoding="utf-8"))
    fichas = carregar_fichas()
    P = paginas()
    oficios = [d for d in lt if d["tipo"] == "Ofício"]
    emails = {d["n"]: d for d in lt if d["tipo"] == "E-mail"}

    # --- ofícios: classificação, datas e lote
    info_of = []
    for k, o in enumerate(oficios, 1):
        ini, fim = map(int, o["paginas"].split("-"))
        txt = " ".join(P[p] for p in range(ini, fim + 1))
        f = fichas.get(o["sei"], {})
        mail = emails.get(o["n"] + 1)
        ass = date.fromisoformat(o["assinaturas"][0]["data"])
        datas_vist = [pdata(x) for x in re.findall(r"\d\d/\d\d/\d{4}", (re.search(
            r"Datas das Vistorias[^\d]*([\d/ ,e]+)", txt) or [None, ""])[1])]
        prazo = re.search(r"prazo de (\d+) \((\w+)\) dias", txt)
        info_of.append({
            "ordem": k, "doc_n": o["n"], "sei": o["sei"], "numero": num(f.get("numero")) or num(
                (re.search(r"Of\.AGENERSA/CASAN N[ºo°]\s*(\d+)", txt) or [None, ""])[1]),
            "finalidade": "encaminhar relatórios" if o["relatorios_citados"] else "agendar vistoria",
            "data_texto": iso(data_extenso(txt)), "assinatura": ass.isoformat(),
            "email": mail["data_envio_email"] if mail else None, "email_doc_n": mail["n"] if mail else None,
            "relatorios_citados": o["relatorios_citados"],
            "prazo_resposta_dias": int(prazo.group(1)) if prazo else None,
            "datas_vistoria_agendada": [iso(d) for d in datas_vist if d],
        })
    of_de_rel = {}
    for o in info_of:
        for r in o["relatorios_citados"]:
            of_de_rel.setdefault(r, o)

    # --- casos: um por relatório
    casos = []
    for d in lt:
        if d["tipo"] != TIPO_RF:
            continue
        f = fichas.get(d["sei"], {})
        fisc = f.get("fiscalizacao") or {}
        nrel = num(f.get("numero")) or num(d.get("relatorio_n"))
        ass = d["assinaturas"]
        ger = [a for a in ass if a["cargo"].lower().startswith("gerente")]
        pre = [a for a in ass if not a["cargo"].lower().startswith("gerente")]
        o = of_de_rel.get(nrel)
        m = {
            "vistoria": pdata(fisc.get("data_vistoria", "")),
            "data_texto": pdata(f.get("data_documento", "")),
            "assinatura_1": date.fromisoformat(ass[0]["data"]) if ass else None,
            "assinatura_pre_gerente": date.fromisoformat(pre[-1]["data"]) if pre and ger else None,
            "aprovacao": date.fromisoformat(ger[-1]["data"]) if ger else None,
            "oficio": date.fromisoformat(o["assinatura"]) if o else None,
            "email": date.fromisoformat(o["email"]) if o and o["email"] else None,
        }
        if not ass:
            variante = "sem texto nem assinatura no PDF"
        elif o:
            variante = "com ofício de encaminhamento nos autos"
        else:
            variante = "sem ofício de encaminhamento nos autos"
        iv = {}
        for iid, _, a, b in INTERVALOS:
            if m[a] and m[b]:
                iv[iid] = {"dc": (m[b] - m[a]).days, "du": du_entre(m[a], m[b])}
        casos.append({
            "id": f"RF{nrel:03d}" if nrel else f"doc{d['n']}",
            "relatorio": f"{nrel}/2024" if nrel else None,
            "doc_n": d["n"], "sei": d["sei"], "paginas": d["paginas"],
            "instalacao": fisc.get("instalacao") or d.get("instalacao") or "",
            "tipo_instalacao": fisc.get("tipo_instalacao", ""),
            "variante": variante,
            "datas": {k: iso(v) for k, v in m.items()},
            "oficio_numero": o["numero"] if o else None, "oficio_doc_n": o["doc_n"] if o else None,
            "n_assinaturas": len(ass), "dias_com_assinatura": len({a["data"] for a in ass}),
            "cadeia_assinaturas": cadeia(ass),
            "nao_conformidades": len(fisc.get("nao_conformidades") or []),
            "prazo_para_sanar_no_relatorio": bool((fisc.get("prazo_para_sanar") or "").strip()),
            "intervalos": iv,
        })

    # --- estatísticas entre casos e fatos citáveis
    fatos = []

    def fato(fid, desc, valor, unidade, definicao, origem="casos"):
        fatos.append({"id": fid, "caso": CASO, "descricao": desc, "valor": valor, "unidade": unidade,
                      "definicao": definicao, "origem": origem})

    estat = {}
    for iid, desc, a, b in INTERVALOS:
        for u in ("dc", "du"):
            vals = [c["intervalos"][iid][u] for c in casos if iid in c["intervalos"]]
            r = resumo(vals)
            estat[f"{iid}.{u}"] = r
            if not r["n"]:
                continue
            for k in ("mediana", "min", "max"):
                fato(f"casos.{iid}.{k}_{u}", f"{desc} — {k} entre casos", r[k], u,
                     f"{a} → {b}; {r['n']} relatórios com os dois marcos", "casos_FIS.json")
            if u == "dc":
                fato(f"casos.{iid}.n", f"{desc} — relatórios com os dois marcos", r["n"], "relatórios",
                     f"{a} e {b} datados", "casos_FIS.json")

    fato("casos.total", "Relatórios de fiscalização tratados como casos", len(casos), "relatórios",
         "documentos do tipo Relatório de Fiscalização na linha do tempo", "linha_do_tempo_FIS.json")
    for v, n in sorted(Counter(c["variante"] for c in casos).items()):
        slug = re.sub(r"[^a-z]+", "_", v.lower().replace("ç", "c").replace("í", "i").replace("ó", "o")).strip("_")
        fato(f"casos.variante.{slug}", f"Relatórios — {v}", n, "relatórios", "", "casos_FIS.json")
    assinados = [c for c in casos if c["n_assinaturas"]]
    fato("casos.assinaturas.mediana", "Assinaturas eletrônicas por relatório — mediana",
         statistics.median(c["n_assinaturas"] for c in assinados), "assinaturas", f"{len(assinados)} relatórios assinados")
    fato("casos.assinaturas.max", "Assinaturas eletrônicas por relatório — máximo",
         max(c["n_assinaturas"] for c in assinados), "assinaturas", "")
    fato("casos.dias_com_assinatura.mediana", "Dias distintos com assinatura por relatório — mediana",
         statistics.median(c["dias_com_assinatura"] for c in assinados), "dias", "rodadas de assinatura")
    fato("casos.dias_com_assinatura.max", "Dias distintos com assinatura por relatório — máximo",
         max(c["dias_com_assinatura"] for c in assinados), "dias", "")
    cad = Counter(c["cadeia_assinaturas"] for c in assinados)
    fato("casos.cadeias_distintas", "Cadeias de cargos signatários distintas", len(cad), "cadeias",
         "sequência de cargos na ordem das assinaturas, sem repetição consecutiva")
    fato("casos.sem_vistoria_datada", "Relatórios sem data de vistoria na ficha",
         sum(1 for c in casos if not c["datas"]["vistoria"]), "relatórios", "")
    fato("casos.com_prazo_para_sanar", "Relatórios que fixam prazo para sanar (ficha)",
         sum(1 for c in casos if c["prazo_para_sanar_no_relatorio"]), "relatórios", "fiscalizacao.prazo_para_sanar")
    nc = [c["nao_conformidades"] for c in assinados]
    fato("casos.nao_conformidades.mediana", "Não conformidades por relatório — mediana", statistics.median(nc), "itens",
         f"{len(nc)} relatórios assinados (fichas)")
    fato("casos.nao_conformidades.max", "Não conformidades por relatório — máximo", max(nc), "itens", "")
    fato("casos.nao_conformidades.sem_nc", "Relatórios sem não conformidade listada", nc.count(0), "relatórios", "")

    # lotes de aprovação: relatórios com o mesmo dia de "De acordo"
    lotes = defaultdict(list)
    for c in assinados:
        if c["datas"]["aprovacao"]:
            lotes[c["datas"]["aprovacao"]].append(c["id"])
    tam = [len(v) for v in lotes.values()]
    fato("lotes.aprovacao.n", "Dias distintos de 'De acordo' do Gerente (lotes de aprovação)", len(lotes), "lotes",
         "relatórios aprovados no mesmo dia formam um lote")
    fato("lotes.aprovacao.tamanho_mediana", "Relatórios por lote de aprovação — mediana", statistics.median(tam),
         "relatórios", "")
    fato("lotes.aprovacao.tamanho_max", "Relatórios por lote de aprovação — máximo", max(tam), "relatórios", "")

    # ofícios
    for o in info_of:
        k = o["ordem"]
        no_pdf = [c for c in casos if c["oficio_doc_n"] == o["doc_n"]]
        fato(f"of{k}.finalidade_encaminhar", f"Ofício {o['numero']}/2024: encaminha relatórios (1) ou agenda vistoria (0)",
             int(o["finalidade"] == "encaminhar relatórios"), "indicador", "relatórios citados no texto",
             f"doc {o['doc_n']} (SEI {o['sei']})")
        if o["relatorios_citados"]:
            fato(f"of{k}.relatorios_citados", f"Ofício {o['numero']}/2024: relatórios citados", len(o["relatorios_citados"]),
                 "relatórios", "", f"doc {o['doc_n']}")
            fato(f"of{k}.relatorios_no_pdf", f"Ofício {o['numero']}/2024: relatórios citados com texto no PDF", len(no_pdf),
                 "relatórios", "", f"doc {o['doc_n']}")
        if o["data_texto"]:
            dt = date.fromisoformat(o["data_texto"])
            da = date.fromisoformat(o["assinatura"])
            fato(f"of{k}.texto_assinatura_dc", f"Ofício {o['numero']}/2024: data escrita até a assinatura", (da - dt).days,
                 "dc", "data da assinatura − data do cabeçalho", f"doc {o['doc_n']}")
            fato(f"of{k}.texto_assinatura_du", f"Ofício {o['numero']}/2024: data escrita até a assinatura (du)",
                 du_entre(dt, da), "du", "calendário RJ (hipótese)", f"doc {o['doc_n']}")
        if o["datas_vistoria_agendada"]:
            da = date.fromisoformat(o["assinatura"])
            v1 = date.fromisoformat(o["datas_vistoria_agendada"][0])
            de = date.fromisoformat(o["email"]) if o["email"] else da
            fato(f"of{k}.vistorias_agendadas_dias", f"Ofício {o['numero']}/2024: dias de vistoria agendados",
                 len(o["datas_vistoria_agendada"]), "dias", "trecho 'Datas das Vistorias'", f"doc {o['doc_n']}")
            fato(f"of{k}.antecedencia_agendamento_dc", f"Ofício {o['numero']}/2024: envio do e-mail até a 1ª vistoria agendada",
                 (v1 - de).days, "dc", "1ª data agendada − data do e-mail", f"docs {o['doc_n']}, {o['email_doc_n']}")
            fato(f"of{k}.antecedencia_agendamento_du", f"Ofício {o['numero']}/2024: envio do e-mail até a 1ª vistoria agendada (du)",
                 du_entre(de, v1), "du", "calendário RJ (hipótese)", f"docs {o['doc_n']}, {o['email_doc_n']}")
    fato("oficios.encaminhamento", "Ofícios de encaminhamento de relatórios nos autos",
         sum(o["finalidade"] == "encaminhar relatórios" for o in info_of), "ofícios", "")
    fato("oficios.agendamento", "Ofícios de agendamento de vistoria nos autos",
         sum(o["finalidade"] == "agendar vistoria" for o in info_of), "ofícios", "")
    pz = sorted({o["prazo_resposta_dias"] for o in info_of if o["prazo_resposta_dias"]})
    if len(pz) == 1:
        fato("oficios.prazo_resposta_unico", "Prazo de resposta dado em todos os ofícios de encaminhamento", pz[0], "dias",
             "trecho 'prazo de N (...) dias'; não diz se úteis ou corridos")

    # --- casos no formato da metodologia (ocorrências por atividade)
    def ocorrencias(c):
        dd = {k: (date.fromisoformat(v) if v else None) for k, v in c["datas"].items()}
        seq = [("a1_vistoria", dd["vistoria"], dd["vistoria"]),
               ("a2_elaborar_relatorio", dd["assinatura_1"], dd["assinatura_1"]),
               ("a3_revisar_aprovar", dd["assinatura_1"], dd["aprovacao"]),
               ("a4_oficiar_concessionaria", dd["oficio"], dd["oficio"]),
               ("a5_enviar_email", dd["email"], dd["email"])]
        out, fim_ant = [], None
        for at, ini, fim in seq:
            if not ini or not fim:
                continue
            esp = 0 if fim_ant is None or ini <= fim_ant else du_entre(fim_ant, ini)
            out.append({"atividade": at, "inicio": ini.isoformat(), "fim": fim.isoformat(),
                        "espera_antes_du": float(esp), "execucao_du": float(du_entre(ini, fim)),
                        "espera_antes_por_unidade": {}, "espera_antes_terceiros_du": None,
                        "horas_piso": None, "horas_teto": None})
            fim_ant = max(fim_ant, fim) if fim_ant else fim
        return out

    for c in casos:
        c["ocorrencias"] = ocorrencias(c)

    out = {
        "codigo": CODIGO, "caso": CASO,
        "observacao": ("Vários casos dentro de um processo: cada Relatório de Fiscalização é um caso do subprocesso "
                       "vistoria → relatório → revisão/assinaturas → 'De acordo' → ofício → e-mail. Datas: vistoria e data "
                       "escrita vêm das fichas; assinaturas e e-mails, do texto do PDF (linha_do_tempo_FIS.json). "
                       "A atividade a2 mede só a 1ª assinatura: o intervalo vistoria → 1ª assinatura mistura redação e "
                       "espera. Dias úteis pelo calendário RJ de scripts/fatos_fis.py (hipótese). Posse, horas e espera de "
                       "terceiros não medidas (sem andamentos do SEI; resposta da concessionária fora dos autos): ficam "
                       "nulas. Relatórios sem ofício nos autos não têm a4/a5: o encaminhamento pode estar em ofício não "
                       "exportado."),
        "definicoes": {"dc": "dias corridos", "du": "dias úteis, calendário RJ (hipótese)",
                       "intervalos": {i: f"{d} ({a} → {b})" for i, d, a, b in INTERVALOS}},
        "estatisticas": estat,
        "lotes_aprovacao": dict(sorted(lotes.items())),
        "cadeias_assinatura": dict(cad.most_common()),
        "oficios": info_of,
        "casos": casos,
        "fatos": fatos,
    }
    (MAP / "casos_FIS.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    cols = ["id", "relatorio", "doc_n", "sei", "instalacao", "tipo_instalacao", "variante", "oficio_numero",
            "n_assinaturas", "dias_com_assinatura", "cadeia_assinaturas", "nao_conformidades"]
    cols_d = list(casos[0]["datas"].keys())
    with (MAP / "casos_FIS.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(cols + [f"data_{k}" for k in cols_d] + [f"{i}_{u}" for i, *_ in INTERVALOS for u in ("dc", "du")])
        for c in casos:
            w.writerow([c[k] for k in cols] + [c["datas"][k] or "" for k in cols_d] +
                       [c["intervalos"].get(i, {}).get(u, "") for i, *_ in INTERVALOS for u in ("dc", "du")])

    atualizar_evidencias(out)
    print(f"{len(casos)} casos, {len(info_of)} ofícios, {len(fatos)} fatos")
    for f in fatos:
        print(f"  {f['id']}: {f['valor']} {f['unidade']}")


def atualizar_evidencias(out: dict) -> None:
    arq = MAP / "evidencias_FIS.md"
    if not arq.exists():
        return
    t = arq.read_text(encoding="utf-8")
    ini, fim = "<!-- inicio:casos_fis -->", "<!-- fim:casos_fis -->"
    if ini not in t or fim not in t:
        return
    md = ["", "<!-- gerado por scripts/casos_fis.py a partir de mapeamento/casos_FIS.json; não editar à mão -->", "",
          "### Casos (um por relatório)", "",
          "| caso | doc | instalação | variante | vistoria | 1ª assin. | De acordo | ofício (nº) | e-mail | assin. | NC |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in out["casos"]:
        d = c["datas"]
        md.append(f"| {c['id']} | {c['doc_n']} | {c['instalacao']} | {c['variante']} | {d['vistoria'] or '—'} | "
                  f"{d['assinatura_1'] or '—'} | {d['aprovacao'] or '—'} | "
                  f"{(d['oficio'] + ' (' + str(c['oficio_numero']) + ')') if d['oficio'] else '—'} | {d['email'] or '—'} | "
                  f"{c['n_assinaturas']} | {c['nao_conformidades']} |")
    md += ["", "### Intervalos entre casos (fatos `casos.<intervalo>.<estatística>_<dc|du>`)", "",
           "| intervalo (id) | n | mediana dc | mín dc | máx dc | mediana du | mín du | máx du |",
           "|---|---|---|---|---|---|---|---|"]
    for i, desc in ((i, d) for i, d, *_ in INTERVALOS):
        a, b = out["estatisticas"][f"{i}.dc"], out["estatisticas"][f"{i}.du"]
        md.append(f"| {desc} (`{i}`) | {a['n']} | {a['mediana']} | {a['min']} | {a['max']} | {b['mediana']} | "
                  f"{b['min']} | {b['max']} |")
    md += ["", "### Ofícios", "",
           "| doc | ofício | finalidade | data no texto | assinatura | e-mail | relatórios citados | prazo (dias) |",
           "|---|---|---|---|---|---|---|---|"]
    for o in out["oficios"]:
        md.append(f"| {o['doc_n']} | {o['numero']}/2024 | {o['finalidade']} | {o['data_texto']} | {o['assinatura']} | "
                  f"{o['email']} | {', '.join(map(str, o['relatorios_citados'])) or '—'} | {o['prazo_resposta_dias'] or '—'} |")
    md += ["", "### Cadeias de assinatura (cargos, na ordem)", "", "| cadeia | relatórios |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in out["cadeias_assinatura"].items()]
    md += ["", "### Fatos dos casos", "", "| id | descrição | valor | unidade | definição |", "|---|---|---|---|---|"]
    md += [f"| `{f['id']}` | {f['descricao']} | {f['valor']} | {f['unidade']} | {f['definicao']} |" for f in out["fatos"]]
    md.append("")
    a, b = t.index(ini) + len(ini), t.index(fim)
    arq.write_text(t[:a] + "\n".join(md) + t[b:], encoding="utf-8")


if __name__ == "__main__":
    main()
