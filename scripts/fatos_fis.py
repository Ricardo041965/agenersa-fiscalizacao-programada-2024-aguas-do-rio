"""Fatos do processo SEI-480002/001314/2024 (AGENERSA/RJ — Fiscalizações Programadas 2024, Águas do Rio Bloco 1).

Etapa determinística do método (fase 1, "fatos"): lê o texto integral extraído do PDF e as fichas por
documento e calcula a linha do tempo, os intervalos entre marcos (dias corridos e úteis) e as contagens.
Nenhum número dos relatórios deve ser digitado à mão: cite o id do fato gravado em mapeamento/fatos_FIS.json.

Saídas: mapeamento/fatos_FIS.json, mapeamento/linha_do_tempo_FIS.json, texto/indice_documentos.md

Uso: python scripts/fatos_fis.py   (a partir da pasta do caso)
"""
from __future__ import annotations

import json
import re
import statistics
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CODIGO = "FIS"
CASO = "SEI-480002/001314/2024"

# Fronteiras dos documentos (última página de cada um), conferidas à mão contra os rodapés "SEI nº".
FIM_DOCS = [12, 18, 27, 29, 30, 38, 47, 54, 62, 75, 87, 100, 107, 109, 110, 117, 125, 130, 137, 139, 140,
            147, 154, 160, 167, 174, 179, 197, 199, 200, 226, 231, 232, 233]

# Feriados nacionais, estaduais (RJ) e municipais (Rio de Janeiro). Hipótese: pontos facultativos do
# Executivo fluminense de 2024/2025 não foram conferidos.
FERIADOS = {
    "2024-01-01", "2024-01-20", "2024-02-12", "2024-02-13", "2024-03-29", "2024-04-21", "2024-04-23",
    "2024-05-01", "2024-05-30", "2024-09-07", "2024-10-12", "2024-10-28", "2024-11-02", "2024-11-15",
    "2024-11-20", "2024-12-25",
    "2025-01-01", "2025-01-20", "2025-03-03", "2025-03-04", "2025-04-18", "2025-04-21", "2025-04-23",
    "2025-05-01", "2025-06-19", "2025-09-07", "2025-10-12", "2025-10-28", "2025-11-02", "2025-11-15",
    "2025-11-20", "2025-12-25",
}
FERIADOS_D = {date.fromisoformat(f) for f in FERIADOS}
RE_ASS = re.compile(r"Documento assinado eletronicamente por [^,]+, ([^,]+?), em (\d\d/\d\d/\d{4}), às (\d\d:\d\d)")


def du_entre(a: date, b: date) -> int:
    if b < a:
        return -du_entre(b, a)
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5 and d not in FERIADOS_D:
            n += 1
    return n


def pdata(s: str) -> date | None:
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    return date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def paginas() -> dict[int, str]:
    t = (BASE / "texto" / "processo_completo.txt").read_text(encoding="utf-8")
    pg = re.split(r"\n===== PÁGINA (\d+) =====\n", t)[1:]
    return {int(pg[i]): " ".join(pg[i + 1].split()) for i in range(0, len(pg), 2)}


def tipo_doc(corpo: str, primeira: str) -> str:
    if primeira.startswith("E-mail -"):
        return "E-mail"
    if "Ofício - NA" in corpo or "Of.AGENERSA/CASAN" in corpo:
        return "Ofício"
    if "PARECER Nº" in corpo[:600]:
        return "Parecer"
    if "Despacho de Encaminhamento" in corpo:
        return "Despacho"
    return "Relatório de Fiscalização"


def num_relatorio(txt: str) -> str | None:
    m = re.search(r"Relatório de Fiscalização AGENERSA/CASAN [Nn][ºo°]\s*0*(\d+)", txt)
    return m.group(1) if m else None


def carregar_fichas() -> dict[str, dict]:
    out = {}
    for arq in sorted((BASE / "fichas").glob("fichas_parte*.json")):
        for f in json.loads(arq.read_text(encoding="utf-8")):
            out.setdefault(str(f.get("sei", "")).strip(), f)
    return out


def main() -> None:
    P = paginas()
    fichas = carregar_fichas()
    docs, ini = [], 1
    for fim in FIM_DOCS:
        corpo = " ".join(P[p] for p in range(ini, fim + 1))
        em = re.match(r"E-mail - (\d+)", P[ini])
        seis = re.findall(r"SEI n[ºo°]\s*(\d{7,})", corpo)
        hdr = re.findall(r"\((\d{8,9})\) SEI SEI-480002", corpo)
        sei = em.group(1) if em else (seis[-1] if seis else (hdr[0] if hdr else "?"))
        tp = tipo_doc(corpo, P[ini])
        ass = [{"cargo": c, "data": pdata(d).isoformat(), "hora": h} for c, d, h in RE_ASS.findall(corpo)]
        env = re.search(r"Data de Envio: (\d\d/\d\d/\d{4})", corpo)
        ficha = fichas.get(sei, {})
        fisc = ficha.get("fiscalizacao") or {}
        d = {
            "n": len(docs) + 1, "sei": sei, "tipo": tp, "paginas": f"{ini}-{fim}",
            "relatorio_n": num_relatorio(corpo[:3000]) if tp == "Relatório de Fiscalização" else None,
            "instalacao": fisc.get("instalacao", ""),
            "data_vistoria": (pdata(fisc.get("data_vistoria", "")) or None),
            "assinaturas": ass,
            "data_envio_email": pdata(env.group(1)).isoformat() if env else None,
            "relatorios_citados": sorted({int(x) for x in re.findall(
                r"Relatório de Fiscalização AGENERSA/CASAN [Nn][ºo°]\s*0*(\d+)", corpo)}) if tp == "Ofício" else [],
            "nao_conformidades": len(fisc.get("nao_conformidades") or []),
        }
        if d["data_vistoria"]:
            d["data_vistoria"] = d["data_vistoria"].isoformat()
        docs.append(d)
        ini = fim + 1

    # --- índice legível
    linhas = ["| # | Tipo | Nº relatório | Instalação | SEI | Páginas | 1ª assinatura | Última assinatura |",
              "|---|---|---|---|---|---|---|---|"]
    for d in docs:
        a = d["assinaturas"]
        linhas.append(f"| {d['n']} | {d['tipo']} | {d['relatorio_n'] or ''} | {d['instalacao']} | {d['sei']} | "
                      f"{d['paginas']} | {a[0]['data'] if a else (d['data_envio_email'] or '')} | {a[-1]['data'] if a else ''} |")
    (BASE / "texto" / "indice_documentos.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    fatos = []

    def fato(fid, desc, valor, unidade, definicao, origem):
        fatos.append({"id": fid, "caso": CASO, "descricao": desc, "valor": valor, "unidade": unidade,
                      "definicao": definicao, "origem": origem})

    rels = [d for d in docs if d["tipo"] == "Relatório de Fiscalização" and d["assinaturas"]]
    oficios = [d for d in docs if d["tipo"] == "Ofício"]
    emails = [d for d in docs if d["tipo"] == "E-mail"]
    parecer = next(d for d in docs if d["tipo"] == "Parecer")
    despachos = [d for d in docs if d["tipo"] == "Despacho"]

    fato("contagem.documentos", "Documentos no PDF exportado", len(docs), "documentos", "fronteiras FIM_DOCS", "PDF")
    fato("contagem.paginas", "Páginas do PDF", max(P), "páginas", "", "PDF")
    for tp in ["Relatório de Fiscalização", "Ofício", "E-mail", "Parecer", "Despacho"]:
        fato(f"contagem.{tp.split()[0].lower()}", f"Documentos do tipo {tp}", sum(d['tipo'] == tp for d in docs),
             "documentos", "classificação por padrão de texto", "PDF")
    citados = re.findall(r"Relatório de Fiscalização AGENERSA/CASAN N[ºo°]\s*0*(\d+)", " ".join(
        P[p] for p in range(227, 229)), flags=re.I)
    fato("contagem.relatorios_citados_parecer", "Relatórios listados no Parecer 250/2025 (escopo anual)",
         len(set(citados)), "relatórios", "lista do item I do parecer", f"doc {parecer['n']} (SEI {parecer['sei']})")
    fato("contagem.relatorios_no_pdf", "Relatórios de fiscalização com texto no PDF", len(
        [d for d in docs if d["tipo"] == "Relatório de Fiscalização"]), "relatórios", "", "PDF")

    # --- ciclo interno de cada relatório: elaboração (1ª assinatura) -> aprovação (assinatura do Gerente)
    ciclos = []
    for d in rels:
        a0 = date.fromisoformat(d["assinaturas"][0]["data"])
        ger = [x for x in d["assinaturas"] if x["cargo"].lower().startswith("gerente")]
        af = date.fromisoformat((ger[-1] if ger else d["assinaturas"][-1])["data"])
        ciclos.append((d, a0, af))
        # Id único: número do relatório quando detectado no texto; senão o nº SEI do documento (nunca "relNone").
        rid = f"rel{d['relatorio_n']}" if d["relatorio_n"] else f"relSEI{d['sei']}"
        rot = f"RF {d['relatorio_n']}" if d["relatorio_n"] else f"RF (SEI {d['sei']}, nº não detectado no texto)"
        fato(f"{rid}.elab_aprov_dc", f"{rot}: 1ª assinatura até 'De acordo' do Gerente",
             (af - a0).days, "dc", "data da assinatura do Gerente − data da 1ª assinatura", f"doc {d['n']} (SEI {d['sei']})")
        fato(f"{rid}.assinaturas", f"{rot}: nº de assinaturas eletrônicas",
             len(d["assinaturas"]), "assinaturas", "", f"doc {d['n']} (SEI {d['sei']})")
        if d["data_vistoria"]:
            v = date.fromisoformat(d["data_vistoria"])
            fato(f"{rid}.vistoria_aprov_dc", f"{rot}: vistoria até aprovação",
                 (af - v).days, "dc", "data do 'De acordo' − data da vistoria (ficha)", f"doc {d['n']} (SEI {d['sei']})")
    vals = [(af - a0).days for _, a0, af in ciclos]
    fato("ciclo.elab_aprov_mediana_dc", "Mediana: 1ª assinatura do relatório até aprovação do Gerente",
         statistics.median(vals), "dc", f"{len(vals)} relatórios com assinatura no PDF", "rel*.elab_aprov_dc")
    fato("ciclo.elab_aprov_max_dc", "Máximo: 1ª assinatura até aprovação", max(vals), "dc", "", "rel*.elab_aprov_dc")
    fato("ciclo.assinaturas_mediana", "Mediana de assinaturas por relatório",
         statistics.median([len(d["assinaturas"]) for d in rels]), "assinaturas", "", "rel*.assinaturas")

    # --- ofícios de encaminhamento: aprovação do último relatório do lote -> ofício -> e-mail
    por_num = {int(d["relatorio_n"]): (d, af) for d, _, af in ciclos if d["relatorio_n"]}
    for k, o in enumerate(oficios, 1):
        do = date.fromisoformat(o["assinaturas"][0]["data"])
        mail = next((e for e in emails if e["n"] == o["n"] + 1), None)
        fato(f"oficio{k}.data", f"Ofício de encaminhamento {k} à concessionária", do.isoformat(), "data",
             "assinatura do Gerente", f"doc {o['n']} (SEI {o['sei']})")
        fato(f"oficio{k}.relatorios", f"Ofício {k}: relatórios encaminhados", len(o["relatorios_citados"]),
             "relatórios", "números citados no ofício", f"doc {o['n']} (SEI {o['sei']})")
        if mail and mail["data_envio_email"]:
            fato(f"oficio{k}.envio_email_dc", f"Ofício {k}: assinatura até envio por e-mail",
                 (date.fromisoformat(mail["data_envio_email"]) - do).days, "dc", "", f"doc {mail['n']} (SEI {mail['sei']})")
        no_pdf = [por_num[n] for n in o["relatorios_citados"] if n in por_num]
        if no_pdf:
            esperas = [(do - af).days for _, af in no_pdf]
            fato(f"oficio{k}.espera_max_dc", f"Ofício {k}: maior espera entre aprovação de um relatório do lote e o ofício",
                 max(esperas), "dc", "data do ofício − data do 'De acordo' (só relatórios presentes no PDF)",
                 f"doc {o['n']}")
            fato(f"oficio{k}.espera_min_dc", f"Ofício {k}: menor espera entre aprovação e ofício", min(esperas), "dc",
                 "", f"doc {o['n']}")
        m = re.search(r"prazo de (\d+) \((\w+)\) dias", " ".join(P[p] for p in range(*map(int, o["paginas"].split("-")))) + " " + P[int(o["paginas"].split("-")[1])])
        if m:
            fato(f"oficio{k}.prazo_resposta", f"Ofício {k}: prazo dado à concessionária", int(m.group(1)), "dias",
                 "trecho 'prazo de N (...) dias' do ofício", f"doc {o['n']}")

    # --- marcos globais
    primeiro = min(a0 for _, a0, _ in ciclos)
    ultimo_of = date.fromisoformat(oficios[-1]["assinaturas"][0]["data"])
    dp = date.fromisoformat(parecer["assinaturas"][-1]["data"])
    dfim = date.fromisoformat(despachos[-1]["assinaturas"][-1]["data"])
    fato("marco.primeiro_relatorio", "Marco: 1ª assinatura de relatório no PDF", primeiro.isoformat(), "data", "", "rels")
    fato("marco.ultimo_oficio", "Marco: último ofício de encaminhamento", ultimo_of.isoformat(), "data", "", f"doc {oficios[-1]['n']}")
    fato("marco.parecer", "Marco: Parecer CASAN 250/2025 (análise das respostas)", dp.isoformat(), "data", "",
         f"doc {parecer['n']} (SEI {parecer['sei']})")
    fato("marco.despacho_procuradoria", "Marco: envio à Procuradoria (última peça)", dfim.isoformat(), "data", "",
         f"doc {despachos[-1]['n']} (SEI {despachos[-1]['sei']})")
    fato("intervalo.ultimo_oficio_parecer", "Último ofício até o parecer de análise das respostas", (dp - ultimo_of).days,
         "dc", "", "marco.ultimo_oficio → marco.parecer")
    fato("intervalo.ultimo_oficio_parecer_du", "Último ofício até o parecer (dias úteis)", du_entre(ultimo_of, dp), "du",
         "calendário RJ (hipótese)", "idem")
    fato("intervalo.parecer_procuradoria", "Parecer até envio à Procuradoria", (dfim - dp).days, "dc", "",
         "marco.parecer → marco.despacho_procuradoria")
    fato("intervalo.total_aberto", "Duração até a última peça (processo ainda aberto)", (dfim - primeiro).days, "dc", "",
         "marco.primeiro_relatorio → marco.despacho_procuradoria")
    nc = [d["nao_conformidades"] for d in docs if d["tipo"] == "Relatório de Fiscalização" and d["instalacao"]]
    if nc:
        fato("contagem.nao_conformidades_total", "Não conformidades listadas nos relatórios do PDF (fichas)", sum(nc),
             "itens", "soma de fiscalizacao.nao_conformidades nas fichas", "fichas/")

    repetidos = sorted({f["id"] for f in fatos if sum(g["id"] == f["id"] for g in fatos) > 1})
    if repetidos:
        raise SystemExit(f"ids de fatos repetidos: {repetidos}")

    out = {"codigo": CODIGO, "caso": CASO,
           "definicoes": {"dc": "dias corridos", "du": "dias úteis, calendário RJ em scripts/fatos_fis.py (hipótese)",
                          "observacao": "PDF é recorte do processo: 24 dos relatórios citados no Parecer 250/2025 têm texto; "
                                        "respostas da concessionária não constam. Sem trilha de andamentos do SEI."},
           "fatos": fatos}
    (BASE / "mapeamento" / "fatos_FIS.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (BASE / "mapeamento" / "linha_do_tempo_FIS.json").write_text(json.dumps(docs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(docs)} documentos, {len(fatos)} fatos")
    for f in fatos:
        if not f["id"].startswith("rel"):
            print(f"  {f['id']}: {f['valor']} {f['unidade']}")


if __name__ == "__main__":
    main()
