"""Trava de ancoragem da avaliação AS-IS do FIS (SEI-480002/001314/2024).

Mesmas checagens de `mapeamento-processos-sei/scripts/validar_avaliacao.py` (que só lê `saida/bpmn/` do repositório),
adaptadas à estrutura desta pasta:
  - fatos = mapeamento/fatos_FIS.json + fatos de mapeamento/casos_FIS.json (ids únicos);
  - "ficha" = fichas/fichas_parte*.json; datas aceitas = fatos de data, datas dos casos e datas escritas nas fichas;
  - todo bloco com número precisa de "fatos_usados" (ou fatos_<bloco>) com ids existentes;
  - todo id de fato escrito no texto tem que existir e estar na lista de fatos do bloco;
  - número seguido de du, dc, dias, dias úteis ou dias corridos tem que ser o valor de um fato citado no bloco;
  - demais números: valor de fato citado ou número presente nas fichas;
  - ficam de fora identificadores (RF, doc, Ofício, Parecer, Deliberação, SEI...), datas, ordinais e anos;
  - frase com "mediana" diz de quê (relatórios, casos, lotes);
  - "posse"/"permanência" de unidade só em frase que a negue (não há trilha de andamentos);
  - campos obrigatórios e rótulos da especificação; toda tarefa do modelo em "atividades"; 4 a 7 oportunidades.

Uso: python scripts/validar_avaliacao_fis.py [--carimbar]   (a partir da pasta do caso)"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MAP = BASE / "mapeamento"

RE_ID = re.compile(r"(?:Parecer|Pareceres|Of[ií]cios?|NA|Delibera[cç][aã]o|Deliberações|Voto|Relat[oó]rios?|Lei|Decreto|IN|"
                   r"Instru[cç][aã]o Normativa|art\.?|arts\.?|Resolu[cç][aã]o|Carta|Processo|SEI|n[ºo°.]|Nota Técnica|"
                   r"Despacho|Contrato|Cl[aá]usula|Ata|Bloco|RF|docs?|ID)\s*[\w./-]*\d[\w./-]*", re.I)
RE_SIGLA = re.compile(r"\b[A-Za-zÀ-ú]+[-/]\d[\w/-]*|\b[A-Z]{2,}\d+\b")
RE_DATA = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}/\d{4}|\b(?:19|20)\d{2}\b|\d+\s*[ºª°]")
RE_DATA_COMPLETA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
RE_NUM = re.compile(r"\d+(?:[.,]\d+)*")
RE_TEMPO = r"(du\b|dc\b|dias úteis|dias corridos|dias\b)"

VALOR = {"agrega valor", "necessária sem valor", "não agrega valor"}
NIVEL = {"alto", "médio", "baixo"}
SEVER = {"alta", "média", "baixa"}
CATEG = {"IA", "Lean", "IA + Lean"}
LEAN = {"Espera", "Defeitos/retrabalho", "Superprocessamento", "Transporte", "Estoque", "Movimentação",
        "Superprodução", "Talento não aproveitado"}
TIPOS_IA = {"extração de dados de documentos", "classificação e triagem", "sumarização e linha do tempo",
            "redação assistida de minuta", "cálculo e conferência automática", "verificação de conformidade",
            "monitoramento de prazos e alertas", "busca de precedentes e normas", "automação de tramitação (RPA no SEI)",
            "painel e indicadores"}


def canon(n) -> str:
    n = str(n)
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", n):
        n = n.replace(".", "")
    n = n.replace(",", ".")
    if "." in n:
        n = n.rstrip("0").rstrip(".")
    return n.lstrip("0") or "0"


def carregar_fatos() -> dict[str, dict]:
    fatos: dict[str, dict] = {}
    for arq in (MAP / "fatos_FIS.json", MAP / "casos_FIS.json"):
        for f in json.loads(arq.read_text(encoding="utf-8"))["fatos"]:
            if f["id"] in fatos:
                raise SystemExit(f"id de fato repetido: {f['id']} ({arq.name})")
            fatos[f["id"]] = f
    return fatos


def carregar_fichas() -> list:
    out = []
    for arq in sorted((BASE / "fichas").glob("fichas_parte*.json")):
        out += json.loads(arq.read_text(encoding="utf-8"))
    return out


def datas_conhecidas(fatos: dict, fichas: list) -> set[str]:
    out = {str(f["valor"]) for f in fatos.values() if f.get("unidade") == "data"}
    casos = json.loads((MAP / "casos_FIS.json").read_text(encoding="utf-8"))["casos"]
    for c in casos:
        out |= {v for v in c["datas"].values() if v}
    for d, m, y in RE_DATA_COMPLETA.findall(json.dumps(fichas, ensure_ascii=False)):
        out.add(f"{y}-{int(m):02d}-{int(d):02d}")
    return out


def blocos(av: dict):
    for k in ("sintese", "leitura_metricas", "variabilidade"):
        yield k, av.get(k, ""), av.get(f"fatos_{k}", [])
    g = av.get("gargalo") or {}
    yield "gargalo", f"{g.get('onde', '')} {g.get('evidencia', '')}", g.get("fatos_usados", [])
    for i, w in enumerate(av.get("desperdicios", [])):
        yield f"desperdicios[{i}]", w.get("evidencia", ""), w.get("fatos_usados", [])
    for i, o in enumerate(av.get("oportunidades", [])):
        yield (f"oportunidades[{i}]", f"{o.get('titulo', '')} {o.get('descricao', '')} {o.get('ganho_esperado', '')} "
               f"{o.get('prerequisitos', '')} {o.get('riscos', '')}", o.get("fatos_usados", []))
    for t, a in (av.get("atividades") or {}).items():
        yield (f"atividades.{t}", " ".join(str(a.get(c, "")) for c in ("justificativa_valor", "aplicacao_ia", "ganho_esperado",
                                                                       "controle_humano", "melhoria_lean")),
               a.get("fatos_usados", []))
    for i, e in enumerate((av.get("vsm") or {}).get("etapas", [])):
        yield f"vsm.etapas[{i}]", f"{e.get('trecho', '')} {e.get('evidencia', '')}", e.get("fatos_usados", [])
    for i, r in enumerate(av.get("riscos", [])):
        yield f"riscos[{i}]", f"{r.get('risco', '')} {r.get('evidencia', '')}", r.get("fatos_usados", [])
    yield "indicadores_sugeridos", " ".join(av.get("indicadores_sugeridos", [])), []
    yield "perguntas_validacao", " ".join(av.get("perguntas_validacao", [])), []


def checar_estrutura(av: dict, tarefas: list[str]) -> list[str]:
    e = []
    for k in ("codigo", "sintese", "fatos_sintese", "leitura_metricas", "fatos_leitura_metricas", "gargalo",
              "variabilidade", "fatos_variabilidade", "desperdicios", "atividades", "oportunidades",
              "indicadores_sugeridos", "perguntas_validacao", "riscos", "vsm"):
        if not av.get(k):
            e.append(f"campo obrigatório ausente ou vazio: {k}")
    g = av.get("gargalo") or {}
    for k in ("onde", "evidencia", "atividades", "fatos_usados"):
        if k not in g:
            e.append(f"gargalo sem {k}")
    for i, w in enumerate(av.get("desperdicios", [])):
        for k in ("tipo", "evidencia", "atividades", "severidade", "fatos_usados"):
            if k not in w:
                e.append(f"desperdicios[{i}] sem {k}")
        if w.get("tipo") not in LEAN:
            e.append(f"desperdicios[{i}]: tipo fora dos 8 desperdícios Lean: {w.get('tipo')}")
        if w.get("severidade") not in SEVER:
            e.append(f"desperdicios[{i}]: severidade inválida")
    for t, a in (av.get("atividades") or {}).items():
        for k in ("valor", "justificativa_valor", "potencial_ia", "tipos_ia", "aplicacao_ia", "ganho_esperado",
                  "controle_humano", "melhoria_lean", "fatos_usados"):
            if k not in a:
                e.append(f"atividades.{t} sem {k}")
        if a.get("valor") not in VALOR:
            e.append(f"atividades.{t}: valor inválido")
        if a.get("potencial_ia") not in NIVEL:
            e.append(f"atividades.{t}: potencial_ia inválido")
        for x in a.get("tipos_ia", []):
            if x not in TIPOS_IA:
                e.append(f"atividades.{t}: tipo de IA fora da lista: {x}")
    ops = av.get("oportunidades", [])
    if not 4 <= len(ops) <= 7:
        e.append(f"oportunidades: {len(ops)} (a especificação pede 4 a 7)")
    for i, o in enumerate(ops):
        for k in ("titulo", "categoria", "descricao", "atividades", "ganho_esperado", "impacto", "esforco",
                  "prerequisitos", "riscos", "fatos_usados"):
            if k not in o:
                e.append(f"oportunidades[{i}] sem {k}")
        if o.get("categoria") not in CATEG or o.get("impacto") not in NIVEL or o.get("esforco") not in NIVEL:
            e.append(f"oportunidades[{i}]: categoria/impacto/esforço inválido")
    todas = set(tarefas)
    for nome, lista in [("gargalo", g.get("atividades", []))] + \
            [(f"desperdicios[{i}]", w.get("atividades", [])) for i, w in enumerate(av.get("desperdicios", []))] + \
            [(f"oportunidades[{i}]", o.get("atividades", [])) for i, o in enumerate(ops)] + \
            [(f"riscos[{i}]", r.get("atividades", [])) for i, r in enumerate(av.get("riscos", []))]:
        fora = [t for t in lista if t not in todas]
        if fora:
            e.append(f"{nome}: atividades inexistentes no modelo {fora}")
    faltam = [t for t in tarefas if t not in (av.get("atividades") or {})]
    if faltam:
        e.append(f"tarefas do modelo sem entrada em atividades: {faltam}")
    extras = sorted(set(av.get("atividades") or {}) - todas)
    if extras:
        e.append(f"atividades que não existem no modelo: {extras}")
    return e


def checar_numeros(av: dict, fatos: dict, ficha_nums: set[str], datas: set[str]) -> tuple[list[str], int]:
    erros, n_num = [], 0
    ids_ord = sorted(fatos, key=len, reverse=True)
    re_ids = re.compile("|".join(re.escape(i) for i in ids_ord))
    re_id_like = re.compile(r"\b(?:casos|lotes|of\d|oficios|oficio\d|contagem|intervalo|marco|ciclo|rel\w*)\.[\w.\-]+")
    for nome, texto, usados in blocos(av):
        usados = usados or []
        inexistentes = [u for u in usados if u not in fatos]
        if inexistentes:
            erros.append(f"{nome}: fatos_usados inexistentes {inexistentes}")
        # ids escritos no texto: existem e estão listados no bloco
        citados = re_ids.findall(texto)
        for c in citados:
            if c not in usados:
                erros.append(f"{nome}: id {c} citado no texto e ausente de fatos_usados")
        sem_ids = re_ids.sub(" ", texto)
        for resto in re_id_like.findall(sem_ids):
            erros.append(f"{nome}: id inexistente no texto: {resto}")
        valores = {canon(fatos[u]["valor"]) for u in usados if u in fatos}
        for d, m, y in RE_DATA_COMPLETA.findall(texto):
            if f"{y}-{int(m):02d}-{int(d):02d}" not in datas:
                erros.append(f"{nome}: data {d}/{m}/{y} sem lastro nos fatos, casos ou fichas")
        for frase in re.split(r"(?<=[.;])\s+", sem_ids):
            if re.search(r"mediana", frase, re.I) and not re.search(r"relatório|caso|lote", frase, re.I):
                erros.append(f"{nome}: mediana sem dizer de quê: {frase[:90]}")
            if re.search(r"\b(posse|permanência)\b", frase, re.I) and not re.search(r"\b(sem|não|nenhuma)\b", frase, re.I):
                erros.append(f"{nome}: conclusão apoiada em posse/permanência de unidade: {frase[:90]}")
        sem_tarefas = re.sub(r"\b[tsefg]\d+\b", " ", sem_ids)  # ids de elementos do modelo (t2, e1, g1...)
        limpo = RE_DATA.sub(" ", RE_SIGLA.sub(" ", RE_ID.sub(" ", sem_tarefas)))
        for m_ in re.finditer(r"(\d+(?:[.,]\d+)*)\s*" + RE_TEMPO + "?", limpo):
            n, tempo = m_.group(1), m_.group(2)
            n_num += 1
            if not usados:
                erros.append(f"{nome}: número {n} sem fatos_usados")
                continue
            c = canon(n)
            if tempo and c not in valores:
                erros.append(f"{nome}: {n} {tempo} não é valor de fato citado")
            elif not tempo and c not in valores and c not in ficha_nums:
                erros.append(f"{nome}: {n} não está nos fatos citados nem nas fichas")
        # Referência estrita: números escritos antes de um parêntese com ids (desde o parêntese anterior) ou dentro
        # dele têm que ser o valor de um dos fatos desse parêntese — o número "bate" com o fato que o acompanha.
        anterior = 0
        for g in re.finditer(r"\(([^()]*)\)", texto):
            ids_g = re_ids.findall(g.group(1))
            if not ids_g:
                continue
            trecho = texto[anterior:g.start()] + " " + re_ids.sub(" ", g.group(1))
            anterior = g.end()
            vals_g = {canon(fatos[i]["valor"]) for i in ids_g}
            trecho = re.sub(r"\b[tsefg]\d+\b", " ", trecho)
            trecho = RE_DATA.sub(" ", RE_SIGLA.sub(" ", RE_ID.sub(" ", trecho)))
            for m_ in RE_NUM.finditer(trecho):
                if canon(m_.group(0)) not in vals_g:
                    erros.append(f"{nome}: {m_.group(0)} não bate com o fato que o acompanha {ids_g}")
    return erros, n_num


def sha_fatos(fatos: dict) -> str:
    base = json.dumps(sorted((i, str(f["valor"])) for i, f in fatos.items()), ensure_ascii=False)
    return hashlib.sha256(base.encode()).hexdigest()[:16]


def main() -> None:
    arq = MAP / "avaliacao_FIS.json"
    av = json.loads(arq.read_text(encoding="utf-8"))
    fatos = carregar_fatos()
    fichas = carregar_fichas()
    ficha_nums = {canon(x) for x in RE_NUM.findall(json.dumps(fichas, ensure_ascii=False))}
    mod = json.loads((MAP / "modelo_FIS.json").read_text(encoding="utf-8"))
    tarefas = [e["id"] for e in mod["elementos"] if e["tipo"] == "tarefa"]
    erros = checar_estrutura(av, tarefas)
    e2, n_num = checar_numeros(av, fatos, ficha_nums, datas_conhecidas(fatos, fichas))
    erros += e2
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", json.dumps(av, ensure_ascii=False)):
        erros.append("e-mail de pessoa no texto")
    print(f"FIS: {len(erros)} problema(s); {n_num} números conferidos; {len(fatos)} fatos disponíveis")
    for x in erros:
        print("  ", x)
    if not erros and "--carimbar" in sys.argv:
        av["validado_contra"] = {"fatos_sha": sha_fatos(fatos), "fatos": ["mapeamento/fatos_FIS.json", "mapeamento/casos_FIS.json"],
                                 "validador": "scripts/validar_avaliacao_fis.py",
                                 "data": datetime.now().strftime("%Y-%m-%d %H:%M")}
        arq.write_text(json.dumps(av, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("carimbado")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
