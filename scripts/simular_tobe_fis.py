"""Linha de base congelada e simulação do TO-BE do processo FIS (SEI-480002/001314/2024, AGENERSA/RJ).

Adaptação de mapeamento-processos-sei/scripts/linha_base.py e simular_tobe.py a um processo com vários casos internos
(um caso por relatório de fiscalização). Só biblioteca padrão; determinístico (mesma entrada, mesma saída, sem data
de execução gravada).

Ciclos medidos em cada relatório (dias úteis, calendário RJ de scripts/fatos_fis.py, hipótese):
  - vistoria → e-mail de envio à concessionária (relatórios com os dois marcos nos autos);
  - vistoria → "De acordo" do Gerente (complementar: mais relatórios têm os dois marcos);
  - vistoria → parecer (análise da resposta do relatório): no AS-IS, a data do Parecer CASAN 250/2025 (marco.parecer),
    único para o ano; no TO-BE, a análise da resposta de cada relatório.
Ocorrências a1 a a5 vêm de mapeamento/casos_FIS.json. A ocorrência a6_analisar_resposta é montada aqui: espera do
último marco do relatório (e-mail; sem e-mail nos autos, o "De acordo") até o parecer. Parte protegida dessa espera
(tempo da concessionária, intocável por teto ou redução): prazo do ofício lido como dias úteis (a leitura mais longa,
oficios.prazo_resposta_unico; contagem pendente na Procuradoria, R-FIS-08) + 5 du de margem, como a regra de espera de
terceiros da metodologia. Fases cumulativas: a fase f aplica as melhorias de fase ≤ f, em ordem (fase, id).

Portões antes de simular (param a execução): fatos, requisitos, benchmark e atividades citados existem; sem benchmark →
hipótese; cenários monotônicos; fase 3 com controle humano; nenhum teto ou redução sobre a parte protegida; a fase 0
reproduz os fatos de casos_FIS.json; a linha de base gravada tem o mesmo carimbo das entradas atuais.

Saídas: mapeamento/linha_base_FIS.json e mapeamento/resultado_tobe_FIS.json

Uso (a partir da pasta do caso):  python scripts/simular_tobe_fis.py [--congelar]
  --congelar  regrava a linha de base quando as entradas mudaram (só depois de revisar a mudança)."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fatos_fis import FERIADOS, du_entre  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
MAP = BASE / "mapeamento"
CENARIOS = ("conservador", "esperado", "otimista")
MARGEM_TERCEIROS_DU = 5
LIMITE_R04_DU = 5  # R-FIS-04: 5 dias úteis da lavratura (1ª assinatura) ao Gerente
A2, A3, A4, A5, A6 = ("a2_elaborar_relatorio", "a3_revisar_aprovar", "a4_oficiar_concessionaria", "a5_enviar_email",
                      "a6_analisar_resposta")
OCORRENCIAS_VALIDAS = {"a1_vistoria", A2, A3, A4, A5, A6}
TIPOS = {"teto_espera", "teto_execucao", "reduz_espera_pct", "qualitativo"}
COMPONENTES = (A2, A3, A4, "a6_agencia")
CICLOS = {"vistoria_email": "Vistoria → e-mail de envio à concessionária",
          "vistoria_aprovacao": "Vistoria → 'De acordo' do Gerente",
          "ate_parecer": "Vistoria → parecer (análise da resposta do relatório)"}


def ler(nome: str):
    return json.loads((MAP / nome).read_text(encoding="utf-8"))


# ----------------------------------------------------------------------------------------------- estatística
def percentil(v: list[float], p: float) -> float:
    s = sorted(v)
    k = (len(s) - 1) * p
    f = math.floor(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def dist(v: list[float]) -> dict | None:
    if not v:
        return None
    return dict(n=len(v), media=round(sum(v) / len(v), 1), mediana=round(percentil(v, 0.5), 1),
                q1=round(percentil(v, 0.25), 1), q3=round(percentil(v, 0.75), 1), min=round(min(v), 1),
                max=round(max(v), 1))


# ----------------------------------------------------------------------------------------------- linha de base
def montar_casos(casos_json: dict, parecer: date, prazo_du: int) -> list[dict]:
    """Casos com as ocorrências a1-a5 de casos_FIS.json e a ocorrência a6 montada até o parecer."""
    out = []
    for c in casos_json["casos"]:
        if not c["ocorrencias"]:
            continue
        d = c["datas"]
        oc = [dict(atividade=o["atividade"], inicio=o["inicio"], espera_antes_du=float(o["espera_antes_du"]),
                   execucao_du=float(o["execucao_du"]),
                   espera_antes_terceiros_du=float(o.get("espera_antes_terceiros_du") or 0.0)) for o in c["ocorrencias"]]
        if d.get("aprovacao"):
            ultimo = d.get("email") or d["aprovacao"]
            esp = float(du_entre(date.fromisoformat(ultimo), parecer))
            oc.append(dict(atividade=A6, inicio=parecer.isoformat(), espera_antes_du=esp, execucao_du=0.0,
                           espera_antes_terceiros_du=min(esp, float(prazo_du + MARGEM_TERCEIROS_DU)),
                           marco_inicio_protegido="e-mail do ofício" if d.get("email") else
                           "'De acordo' (hipótese: envio no mesmo dia; ofício fora dos autos)"))
        out.append(dict(id=c["id"], relatorio=c["relatorio"], tipo_instalacao=c["tipo_instalacao"],
                        variante=c["variante"], vistoria=d.get("vistoria"), aprovacao=d.get("aprovacao"),
                        email=d.get("email"), ocorrencias=oc))
    return out


def soma(caso: dict, ate: set[str]) -> float:
    return sum(o["espera_antes_du"] + o["execucao_du"] for o in caso["ocorrencias"] if o["atividade"] in ate)


def medir(caso: dict) -> dict:
    ats = {o["atividade"] for o in caso["ocorrencias"]}
    m = {}
    tem_v = bool(caso["vistoria"])
    if tem_v and caso["email"]:
        m["vistoria_email"] = soma(caso, {"a1_vistoria", A2, A3, A4, A5})
    if tem_v and caso["aprovacao"]:
        m["vistoria_aprovacao"] = soma(caso, {"a1_vistoria", A2, A3})
        m["ate_parecer"] = soma(caso, OCORRENCIAS_VALIDAS)
    if A3 in ats:
        m["r04"] = next(o["execucao_du"] for o in caso["ocorrencias"] if o["atividade"] == A3) <= LIMITE_R04_DU
    for a in (A2, A3, A4, A6):
        o = next((o for o in caso["ocorrencias"] if o["atividade"] == a), None)
        if o and tem_v:
            m[a] = o["execucao_du"] if a == A3 else o["espera_antes_du"]
            if a == A6:
                m["a6_agencia"] = o["espera_antes_du"] - o["espera_antes_terceiros_du"]
                m["a6_protegida"] = o["espera_antes_terceiros_du"]
    return m


def resumir(medidas: list[dict]) -> dict:
    r = {k: dist([m[k] for m in medidas if k in m]) for k in CICLOS}
    r["componentes"] = {k: dist([m[k] for m in medidas if k in m]) for k in (A2, A3, A4, A6, "a6_agencia", "a6_protegida")}
    v = [m["r04"] for m in medidas if "r04" in m]
    r["conformidade_temporal"] = {"R-FIS-04": dict(n=len(v), conformes=sum(v), pct=round(100 * sum(v) / len(v), 1))}
    return r


def linha_base(congelar: bool) -> tuple[dict, list[dict]]:
    bruto = (MAP / "casos_FIS.json").read_text(encoding="utf-8")
    casos_json = json.loads(bruto)
    fatos_casos = {f["id"]: f["valor"] for f in casos_json["fatos"]}
    fatos_proc = {f["id"]: f["valor"] for f in ler("fatos_FIS.json")["fatos"]}
    parecer = date.fromisoformat(fatos_proc["marco.parecer"])
    prazo = int(fatos_casos["oficios.prazo_resposta_unico"])
    param = dict(parecer=parecer.isoformat(), prazo_resposta_du=prazo, margem_terceiros_du=MARGEM_TERCEIROS_DU,
                 limite_r04_du=LIMITE_R04_DU, feriados=sorted(FERIADOS))
    datas_texto = ler("conformidade_FIS.json")["datas_lidas_dos_autos"]
    carimbo = hashlib.sha256(json.dumps([bruto, param, datas_texto], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    casos = montar_casos(casos_json, parecer, prazo)
    medidas = [medir(c) for c in casos]
    # decomposição do gargalo (a2): vistoria → data do fecho do texto ("Em dd/mm/aaaa") → 1ª assinatura
    v_fecho, fecho_ass = [], []
    for x in casos_json["casos"]:
        chave = "rf" + str(int(x["relatorio"].split("/")[0])) if x.get("relatorio") else None
        fecho = (datas_texto.get(f"{chave}.data_no_texto") or {}).get("data") if chave else None
        d = x["datas"]
        if fecho and d.get("vistoria") and d.get("assinatura_1"):
            v_fecho.append(du_entre(date.fromisoformat(d["vistoria"]), date.fromisoformat(fecho)))
            fecho_ass.append(du_entre(date.fromisoformat(fecho), date.fromisoformat(d["assinatura_1"])))
    # fase 0 reproduz o AS-IS: mesmos valores de casos_FIS.json e da data do parecer
    problemas = []
    for c, m in zip(casos, medidas):
        orig = next(x for x in casos_json["casos"] if x["id"] == c["id"])["intervalos"]
        for k, ik in (("vistoria_email", "vistoria_email"), ("vistoria_aprovacao", "vistoria_aprovacao")):
            if k in m and orig.get(ik) and m[k] != orig[ik]["du"]:
                problemas.append(f"{c['id']}: {k} {m[k]} ≠ {orig[ik]['du']} (casos_FIS.json)")
        if "ate_parecer" in m:
            ref = du_entre(date.fromisoformat(c["vistoria"]), parecer)
            if m["ate_parecer"] != ref:
                problemas.append(f"{c['id']}: ate_parecer {m['ate_parecer']} ≠ {ref} (vistoria → parecer)")
    r = resumir(medidas)
    r["decomposicao_a2"] = dict(
        nota="Data do fecho do texto lida em conformidade_FIS.json (datas_lidas_dos_autos); relatórios com vistoria, "
             "fecho e 1ª assinatura datados. Indício de texto pronto aguardando assinatura, a confirmar com a CASAN.",
        vistoria_fecho=dist(v_fecho), fecho_1a_assinatura=dist(fecho_ass))
    for k, fid in (("vistoria_email", "casos.vistoria_email.mediana_du"),
                   ("vistoria_aprovacao", "casos.vistoria_aprovacao.mediana_du")):
        if r[k]["mediana"] != fatos_casos[fid]:
            problemas.append(f"mediana {k} {r[k]['mediana']} ≠ {fid} {fatos_casos[fid]}")
    if r["componentes"][A2]["mediana"] != fatos_casos["casos.vistoria_1a_assinatura.mediana_du"]:
        problemas.append("mediana a2 ≠ casos.vistoria_1a_assinatura.mediana_du")
    if problemas:
        sys.exit("PORTÃO fase 0 (não reproduz o AS-IS):\n  " + "\n  ".join(problemas))
    lb = dict(codigo="FIS", caso=casos_json["caso"],
              descricao="Linha de base AS-IS congelada por código: referência de todo resultado do TO-BE do FIS.",
              entradas=dict(casos="mapeamento/casos_FIS.json", datas_do_fecho="mapeamento/conformidade_FIS.json",
                            sha256_casos=hashlib.sha256(bruto.encode()).hexdigest(),
                            marco_parecer="fatos_FIS.json: marco.parecer",
                            prazo_resposta="casos_FIS.json: oficios.prazo_resposta_unico"),
              parametros=param, carimbo=carimbo,
              ciclos=CICLOS, casos_com_ocorrencias=len(casos), por_ciclo=r,
              por_caso=[dict(id=c["id"], relatorio=c["relatorio"], tipo_instalacao=c["tipo_instalacao"],
                             variante=c["variante"], **{k: v for k, v in m.items() if k != "r04"},
                             r04_conforme=m.get("r04")) for c, m in zip(casos, medidas)],
              horas_custo=None,
              ressalvas=["Horas de trabalho e custo não medidos (sem andamentos do SEI nem fichas de esforço): nenhum "
                         "total anual em horas, FTE ou R$ é calculado; qualquer valor desse tipo é hipótese a levantar.",
                         "Dias úteis pelo calendário RJ de scripts/fatos_fis.py (pontos facultativos não conferidos).",
                         "Recorte dos autos: 23 relatórios no PDF contra 42 no parecer; os sem ofício nos autos não entram "
                         "no ciclo vistoria → e-mail.",
                         "R-FIS-04 vale desde 01/10/2024; a conformidade aqui é contrafactual (regra aplicada a todos os "
                         "relatórios do ano), diferente da medida em conformidade_FIS.json (só no período de vigência).",
                         "No ciclo até o parecer, a parte protegida é hipótese de leitura do prazo (30 du + 5 du)."])
    arq = MAP / "linha_base_FIS.json"
    if arq.exists() and not congelar:
        antigo = json.loads(arq.read_text(encoding="utf-8"))
        if antigo.get("carimbo") != carimbo:
            sys.exit("PORTÃO linha de base: as entradas mudaram desde o congelamento (carimbo diferente). Revise a "
                     "mudança em casos_FIS.json e rode de novo com --congelar.")
    else:
        arq.write_text(json.dumps(lb, ensure_ascii=False, indent=1), encoding="utf-8")
    return lb, casos


# ----------------------------------------------------------------------------------------------- validação
def validar(mel: list[dict]) -> list[str]:
    fatos = {f["id"] for f in ler("fatos_FIS.json")["fatos"]} | {f["id"] for f in ler("casos_FIS.json")["fatos"]}
    reqs = {r["id"]: r for r in ler("normas_FIS.json")["requisitos"]}
    bench = {c["id"] for c in ler("benchmark_FIS.json")["casos"]}
    asis = {e["id"] for e in ler("modelo_FIS.json")["elementos"]}
    arq_tobe = MAP / "modelo_tobe_FIS.json"
    tobe = {e["id"] for e in json.loads(arq_tobe.read_text(encoding="utf-8"))["elementos"]} if arq_tobe.exists() else None
    p = []
    ids = [m["id"] for m in mel]
    if len(ids) != len(set(ids)):
        p.append("ids de melhoria duplicados")
    for m in mel:
        i = m["id"]
        if m["fase"] not in (1, 2, 3):
            p.append(f"{i}: fase inválida")
        if not m.get("fatos"):
            p.append(f"{i}: sem fato")
        p += [f"{i}: fato inexistente {f}" for f in m.get("fatos", []) if f not in fatos]
        p += [f"{i}: requisito inexistente {r}" for r in m.get("requisitos", []) + m.get("prazo_protegido", []) if r not in reqs]
        p += [f"{i}: benchmark inexistente {b}" for b in m.get("benchmark", []) if b not in bench]
        if not m.get("benchmark") and not m.get("hipotese"):
            p.append(f"{i}: sem benchmark e sem hipotese=true")
        p += [f"{i}: atividade AS-IS inexistente {a}" for a in m.get("atividades", []) if a not in asis]
        if tobe is not None:
            p += [f"{i}: atividade TO-BE inexistente {a}" for a in m.get("atividades_tobe", []) if a not in tobe]
        if not m.get("premissa"):
            p.append(f"{i}: sem premissa explícita")
        if m["fase"] == 3 and (not m.get("controle_humano") or m["controle_humano"].startswith("só na fase")):
            p.append(f"{i}: fase 3 sem controle humano")
        ef = m["efeito"]
        if ef["tipo"] not in TIPOS:
            p.append(f"{i}: tipo de efeito desconhecido {ef['tipo']}")
            continue
        if ef["tipo"] == "qualitativo":
            continue
        p += [f"{i}: ocorrência inexistente {a}" for a in ef["atividades"] if a not in OCORRENCIAS_VALIDAS]
        c = ef["cenarios"]
        if ef["tipo"].startswith("teto"):
            if not c["conservador"] >= c["esperado"] >= c["otimista"] >= 0:
                p.append(f"{i}: cenários de teto fora de ordem (conservador ≥ esperado ≥ otimista)")
        elif not 0 <= c["conservador"] <= c["esperado"] <= c["otimista"] < 100:
            p.append(f"{i}: cenários de redução fora de ordem (conservador ≤ esperado ≤ otimista)")
        if ef["tipo"] == "reduz_espera_pct" and A6 in ef["atividades"]:
            p.append(f"{i}: redução percentual na espera de a6 atingiria o prazo protegido (R-FIS-10); use teto")
        if A6 in ef["atividades"] and "R-FIS-10" not in m.get("prazo_protegido", []):
            p.append(f"{i}: efeito em a6 sem declarar R-FIS-10 em prazo_protegido")
    return p


# ----------------------------------------------------------------------------------------------- simulação
def aplicar(caso: dict, ef: dict, valor: float) -> None:
    t, ativ = ef["tipo"], set(ef.get("atividades") or [])
    for o in caso["ocorrencias"]:
        if o["atividade"] not in ativ:
            continue
        terc = min(o["espera_antes_terceiros_du"], o["espera_antes_du"])  # tempo da concessionária: intocável
        if t == "teto_espera":
            o["espera_antes_du"] = terc + min(o["espera_antes_du"] - terc, valor)
        elif t == "reduz_espera_pct":
            o["espera_antes_du"] = terc + (o["espera_antes_du"] - terc) * (1 - valor / 100)
        elif t == "teto_execucao":
            o["execucao_du"] = min(o["execucao_du"], valor)
        else:
            raise ValueError(t)


def simular(casos: list[dict], mel: list[dict], fase: int, cenario: str) -> list[dict]:
    out = []
    ativas = sorted((m for m in mel if m["fase"] <= fase and m["efeito"]["tipo"] != "qualitativo"),
                    key=lambda m: (m["fase"], m["id"]))
    for c in casos:
        c = copy.deepcopy(c)
        for m in ativas:
            aplicar(c, m["efeito"], float(m["efeito"]["cenarios"][cenario]))
        protegido_ok = all(o["espera_antes_du"] >= o["espera_antes_terceiros_du"] for o in c["ocorrencias"])
        mm = medir(c)
        mm["protegido_ok"] = protegido_ok
        out.append(mm)
    return out


def ganho(base: float, novo: float) -> float:
    return round(100 * (1 - novo / base), 1) if base else 0.0


def sensibilidade(casos: list[dict], mel: list[dict]) -> dict:
    f = max(m["fase"] for m in mel)
    sim = [m for m in mel if m["efeito"]["tipo"] != "qualitativo"]

    def res(ms):
        r = resumir(ms)
        return {k: (r[k]["mediana"], r[k]["media"]) for k in ("vistoria_email", "ate_parecer")}
    todos = res(simular(casos, mel, f, "esperado"))
    linhas = []
    for m in sim:
        sem = res(simular(casos, [x for x in mel if x is not m], f, "esperado"))
        linhas.append(dict(melhoria=m["id"], fase=m["fase"],
                           vistoria_email_mediana_du=round(sem["vistoria_email"][0] - todos["vistoria_email"][0], 1),
                           vistoria_email_media_du=round(sem["vistoria_email"][1] - todos["vistoria_email"][1], 1),
                           ate_parecer_mediana_du=round(sem["ate_parecer"][0] - todos["ate_parecer"][0], 1),
                           ate_parecer_media_du=round(sem["ate_parecer"][1] - todos["ate_parecer"][1], 1)))
    linhas.sort(key=lambda d: (-(d["ate_parecer_media_du"] + d["vistoria_email_media_du"]), d["melhoria"]))
    return dict(fase=f, cenario="esperado", leitura="quanto pioram as medianas e médias (du) se a melhoria for retirada",
                sem_cada_melhoria=linhas)


def fatos_planos(res: dict) -> list[dict]:
    """Números citáveis do resultado, um id por valor (princípio de ancoragem)."""
    out = []

    def add(fid, valor, unidade, desc):
        out.append(dict(id=fid, valor=valor, unidade=unidade, descricao=desc))
    for k, nome in CICLOS.items():
        d = res["linha_base"][k]
        for est in ("n", "mediana", "q1", "q3", "media", "min", "max"):
            add(f"lb.{k}.{est}" + ("" if est == "n" else "_du"), d[est], "relatórios" if est == "n" else "du",
                f"Linha de base — {nome}: {est}")
    for k, d in res["decomposicao_a2"].items():
        if isinstance(d, dict):
            for est in ("n", "mediana", "q1", "q3", "min", "max"):
                add(f"lb.{k}.{est}" + ("" if est == "n" else "_du"), d[est], "relatórios" if est == "n" else "du",
                    f"Linha de base — decomposição de a2 ({k}): {est}")
    for a in COMPONENTES:
        d = res["linha_base"]["componentes"][a]
        for est in ("n", "mediana", "q1", "q3", "max"):
            add(f"lb.componente.{a}.{est}" + ("" if est == "n" else "_du"), d[est], "relatórios" if est == "n" else "du",
                f"Linha de base — {a}: {est}")
    c = res["linha_base"]["conformidade_temporal"]["R-FIS-04"]
    add("lb.R-FIS-04.pct", c["pct"], "%", "Linha de base — R-FIS-04 aplicado a todos os relatórios (contrafactual)")
    for f, por in res["fases"].items():
        for cen, r in por.items():
            for k, nome in CICLOS.items():
                add(f"tobe.f{f}.{cen}.{k}.mediana_du", r[k]["mediana"], "du", f"Fase {f}, {cen} — {nome}: mediana")
                add(f"tobe.f{f}.{cen}.{k}.media_du", r[k]["media"], "du", f"Fase {f}, {cen} — {nome}: média")
                add(f"tobe.f{f}.{cen}.{k}.ganho_mediana_pct", r["ganho_mediana_pct"][k], "%",
                    f"Fase {f}, {cen} — {nome}: ganho da mediana sobre a linha de base")
            for a in COMPONENTES:
                add(f"tobe.f{f}.{cen}.componente.{a}.mediana_du", r["componentes"][a]["mediana"], "du",
                    f"Fase {f}, {cen} — {a}: mediana entre os relatórios")
            add(f"tobe.f{f}.{cen}.R-FIS-04.pct", r["conformidade_temporal"]["R-FIS-04"]["pct"], "%",
                f"Fase {f}, {cen} — R-FIS-04 aplicado a todos os relatórios")
    for s in res["sensibilidade"]["sem_cada_melhoria"]:
        for k in ("vistoria_email_mediana_du", "ate_parecer_mediana_du", "ate_parecer_media_du", "vistoria_email_media_du"):
            add(f"sens.{s['melhoria']}.{k}", s[k], "du", f"Sensibilidade — piora sem {s['melhoria']} ({k})")
    return out


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    congelar = "--congelar" in sys.argv[1:]
    mel_json = ler("melhorias_FIS.json")
    mel = mel_json["melhorias"]
    prob = validar(mel)
    if prob:
        sys.exit("PORTÃO validação das melhorias:\n  " + "\n  ".join(prob))
    lb, casos = linha_base(congelar)
    b0 = [medir(c) for c in casos]
    base = resumir(b0)
    res = dict(codigo="FIS", caso=lb["caso"], carimbo_linha_base=lb["carimbo"], ciclos=CICLOS,
               casos_com_ocorrencias=len(casos),
               melhorias_simuladas=[m["id"] for m in mel if m["efeito"]["tipo"] != "qualitativo"],
               melhorias_qualitativas=[m["id"] for m in mel if m["efeito"]["tipo"] == "qualitativo"],
               linha_base=base, decomposicao_a2=lb["por_ciclo"]["decomposicao_a2"], fases={})
    for f in sorted({m["fase"] for m in mel}):
        res["fases"][str(f)] = {}
        for cen in CENARIOS:
            ms = simular(casos, mel, f, cen)
            r = resumir(ms)
            r["ganho_mediana_pct"] = {k: ganho(base[k]["mediana"], r[k]["mediana"]) for k in CICLOS}
            r["ganho_media_pct"] = {k: ganho(base[k]["media"], r[k]["media"]) for k in CICLOS}
            r["prazo_protegido_preservado"] = all(m["protegido_ok"] for m in ms)
            res["fases"][str(f)][cen] = r
    res["sensibilidade"] = sensibilidade(casos, mel)
    res["checagens"] = dict(
        prazo_protegido_preservado_em_todas_as_fases=all(r["prazo_protegido_preservado"]
                                                        for por in res["fases"].values() for r in por.values()),
        fase0_reproduz_casos=True,
        nota="R-FIS-10 (prazo mínimo entre o envio e o parecer) e R-FIS-07 (prazo concedido) ficam fora do corte: a "
             "parte protegida da espera de a6 nunca é reduzida. R-FIS-11 (15 dias da última resposta ao parecer) não é "
             "simulável: as datas das respostas não estão nos autos.")
    res["leitura_critica"] = [
        f"Fase {f}, {cen}: ganho de {r['ganho_mediana_pct'][k]}% na mediana do ciclo '{CICLOS[k]}' (acima de 60%: "
        "revisar o parâmetro e validar com a CASAN)"
        for f, por in res["fases"].items() for cen, r in por.items() for k in CICLOS
        if cen == "esperado" and r["ganho_mediana_pct"][k] > 60]
    res["ressalvas"] = lb["ressalvas"] + [
        "Medianas com 9 relatórios (vistoria → e-mail) e 21 (demais ciclos) são instáveis: tratar os percentuais como "
        "ordem de grandeza.",
        "No AS-IS o ciclo até o parecer é dominado pela espera do parecer anual único; o ganho do TO-BE nesse ciclo vem "
        "da mudança de rito (análise por relatório), não de produtividade, e depende de capacidade da equipe a validar."]
    res["fatos"] = fatos_planos(res)
    (MAP / "resultado_tobe_FIS.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("linha de base", lb["carimbo"][:12], "| casos", len(casos),
          {k: (base[k]["n"], base[k]["mediana"]) for k in CICLOS}, "| R-FIS-04", base["conformidade_temporal"]["R-FIS-04"]["pct"])
    for f, por in res["fases"].items():
        for cen in CENARIOS:
            r = por[cen]
            print(f"fase {f} {cen:11s}", {k: (r[k]["mediana"], r["ganho_mediana_pct"][k]) for k in CICLOS},
                  "R-FIS-04", r["conformidade_temporal"]["R-FIS-04"]["pct"])
    print("sensibilidade:", [(s["melhoria"], s["vistoria_email_mediana_du"], s["ate_parecer_mediana_du"])
                             for s in res["sensibilidade"]["sem_cada_melhoria"]])
    if res["leitura_critica"]:
        print("leitura crítica:", *res["leitura_critica"], sep="\n  ")


if __name__ == "__main__":
    main()
