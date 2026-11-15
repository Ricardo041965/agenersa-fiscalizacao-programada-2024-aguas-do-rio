"""Priorização da automação aplicada ao FIS (capítulo 11 do método, adaptado a um processo com vários casos internos).

Lê os artefatos do FIS (fatos, casos, avaliação, vínculos, fichas, normas, conformidade) e a matriz do repositório
(parâmetros e linha do P06), mede os critérios da matriz com proxies declarados e calcula custo × retorno em três
cenários. Grava mapeamento/priorizacao_FIS.json. Rode desta pasta do processo: python scripts/priorizacao_fis.py

Diferenças em relação a scripts/priorizacao_automacao.py do repositório (todas declaradas no JSON):
- sem fichas com horas: as horas por peça vêm das fichas da coorte P06 (mesma agência, mesmo tipo), hipótese;
- unidade de caso = relatório de fiscalização (o processo anual é um só);
- texto padrão medido pela recorrência das não conformidades (categorias), não por composicao_texto.
"""
from __future__ import annotations

import glob
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
MAP = AQUI / "mapeamento"
REPO = AQUI.parent.parent / "mapeamento-processos-sei"
F4 = REPO / "saida" / "fase4"

CENARIOS = ["conservador", "esperado", "otimista"]
FATOR = {"conservador": "piso", "esperado": "esperado", "otimista": "teto"}

# Categorias de não conformidade (primeira que casa). Julgamento declarado; a régua é o texto da ficha.
CATEGORIAS_NC = [
    ("sinalização de risco elétrico", r"choque|risco el|advert|perigo"),
    ("registros de manutenção no local", r"registro.{0,40}manuten|manuten.{0,40}registr"),
    ("licença e documentos", r"licen|prontuario|atestado"),
    ("identificação da unidade", r"identifica"),
    ("acesso não restrito", r"acesso|restrit|nao autorizad"),
    ("iluminação", r"ilumina"),
    ("ventilação e circulação de ar", r"ventila|circulacao de ar"),
    ("falta de bomba reserva", r"reserva|apenas (uma|duas) bomba|sem conjuntos motor"),
    ("vazamento e infiltração", r"vazament|infiltra"),
    ("gradeamento", r"grade"),
    ("instalação elétrica", r"eletric|fiacao|fios|disjuntor|painel|quadro|canaleta"),
    ("equipamento inoperante", r"inoperant|fora de operac|sem operac|fora de funcionamento|em manutencao"),
    ("guarda-corpo, tampa e segurança", r"guarda|tampa|extintor|cerca|fechamento"),
    ("conservação e corrosão", r"corros|ferrug|oxid|conserva|manutencao|sujidade|residuo|inserv|assoreamento"),
    ("espaço para operação", r"espaco|livre circulacao"),
]


def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def categoria(nc: str) -> str:
    t = sem_acento(nc)
    for nome, rx in CATEGORIAS_NC:
        if re.search(rx, t):
            return nome
    return "outras"


def nota(v, cortes):
    return None if v is None else 1 + sum(v >= c for c in cortes)


def ler(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    fatos = {f["id"]: f["valor"] for f in ler(MAP / "fatos_FIS.json")["fatos"]}
    casos = ler(MAP / "casos_FIS.json")
    fatos.update({f["id"]: f["valor"] for f in casos["fatos"]})
    av = ler(MAP / "avaliacao_FIS.json")["atividades"]
    vinc = ler(MAP / "vinculos_FIS.json")["atividades"]
    normas = ler(MAP / "normas_FIS.json")
    conf = ler(MAP / "conformidade_FIS.json")
    fichas = []
    for p in sorted(glob.glob(str(AQUI / "fichas" / "fichas_parte*.json"))):
        fichas += ler(Path(p))
    matriz = ler(F4 / "matriz_automacao.json")
    par = matriz["parametros"]
    p06 = next(c for c in matriz["codigos"] if c["codigo"] == "P06")

    # ---------- âncoras de horas (coorte P06, hipótese) ----------
    s = p06["sinais"]
    h_analise = s["horas_fichas"] * s["frac_horas_analise"] / s["pecas_analise"]
    h_apoio = s["horas_fichas"] * (1 - s["frac_horas_analise"]) / (s["pecas"] - s["pecas_analise"])
    casos_p06 = ler(REPO / "saida" / "fase2" / "casos_P06.json")["casos"]
    h_t3_p06 = sum((o["horas_piso"] + o["horas_teto"]) / 2 for c in casos_p06 for o in c["ocorrencias"]
                   if o["atividade"] == "t3")
    h_parecer = h_t3_p06 / len(casos_p06)
    hc = p06["horas_caso"]
    escala = {k: hc[k] / hc["esperado"] for k in CENARIOS}

    # ---------- peças por atividade no ano ----------
    sei_tipo = {f["sei"]: f["tipo"] for f in fichas}
    rel_ano = fatos["contagem.relatorios_citados_parecer"]
    pecas = {}
    for a, v in sorted(vinc.items()):
        docs = [d.split(":")[1] for d in v["docs"]]
        n_rel = sum(sei_tipo.get(d, "").startswith("Relatório") for d in docs)
        n_par = sum(sei_tipo.get(d, "").startswith("Parecer") for d in docs)
        n_apoio = len(docs) - n_rel - n_par
        pecas[a] = dict(relatorios=rel_ano if n_rel else 0, pareceres=n_par, apoio=n_apoio)
    horas_ativ = {}
    for a, p in pecas.items():
        horas_ativ[a] = {k: escala[k] * (p["relatorios"] * h_analise + p["pareceres"] * h_parecer
                                         + p["apoio"] * h_apoio) for k in CENARIOS}
    potencial = {a: v["potencial_ia"] for a, v in av.items()}
    tot_esp = sum(h["esperado"] for h in horas_ativ.values())
    h_an_esp = sum(escala["esperado"] * (p["relatorios"] * h_analise + p["pareceres"] * h_parecer)
                   for p in pecas.values())

    # ---------- critérios ----------
    rel_fichas = [f for f in fichas if f["acao_no_processo"] == "vistoria_relatorio" and f.get("fiscalizacao")
                  and f["fiscalizacao"].get("tipo_instalacao")]
    parecer = [f for f in fichas if f["tipo"].startswith("Parecer")]
    pecas_an = rel_fichas + parecer

    def txt(f):
        return sem_acento(" ".join([f.get("resumo", ""), f.get("indicios_esforco", ""),
                                    f.get("retrabalho_ou_problema", "")]))
    estrut = [bool(re.search(r"mca|medi[cd]|pressao|vazao|l/s|telemetria|checklist|itens vistoriados", txt(f)))
              for f in pecas_an]
    nao_estrut = [bool(re.search(r"foto|anexo|resposta|cronograma", txt(f))) for f in pecas_an]
    norma_sub = [any("48.209" not in n["norma"] for n in f["normas_citadas"]) for f in pecas_an]
    checklist = [bool(re.search(r"checklist|check-list|itens vistoriados|lista de verifica", txt(f)))
                 for f in pecas_an]

    ncs = [(f["sei"], nc) for f in rel_fichas for nc in f["fiscalizacao"]["nao_conformidades"]]
    cat_rel = defaultdict(set)
    cat_n = Counter()
    for sei, nc in ncs:
        c = categoria(nc)
        cat_rel[c].add(sei)
        cat_n[c] += 1
    recorrentes = {c for c, r in cat_rel.items() if len(r) >= 3 and c != "outras"}
    frac_nc_recorrente = sum(cat_n[c] for c in recorrentes) / len(ncs)

    caminho_freq = max(fatos["casos.variante.sem_oficio_de_encaminhamento_nos_autos"],
                       fatos["casos.variante.com_oficio_de_encaminhamento_nos_autos"]) / fatos["casos.total"]
    n_caminhos = len({c["variante"] for c in casos["casos"]})
    variabilidade = n_caminhos / fatos["casos.total"]

    metricas = dict(
        volume_processo=p06["volume"]["estimado"],
        volume_relatorio=rel_ano,
        analise=h_an_esp / tot_esp,
        dados=(sum(estrut) / len(pecas_an) + sum(nao_estrut) / len(pecas_an)) / 2,
        regras=(sum(norma_sub) / len(pecas_an) + sum(checklist) / len(pecas_an)) / 2,
        padrao=(frac_nc_recorrente + caminho_freq) / 2,
        completude=sum(h["esperado"] for a, h in horas_ativ.items() if potencial.get(a) == "alto") / tot_esp,
    )
    crit = par["criterios"]
    notas = {c: nota(metricas[c], crit[c][1]) for c in ("analise", "dados", "regras", "padrao", "completude")}
    notas["volume_processo"] = nota(metricas["volume_processo"], crit["volume"][1])
    notas["volume_relatorio"] = nota(metricas["volume_relatorio"], crit["volume"][1])

    def composta(nv):
        return round((crit["volume"][0] * nv + sum(crit[c][0] * notas[c] for c in
                                                   ("analise", "dados", "regras", "padrao", "completude"))) / 5, 1)

    # ---------- custo × retorno ----------
    autom = sorted(a for a, p in potencial.items() if p in ("alto", "médio"))
    caps = sorted({t for a in autom for t in av[a].get("tipos_ia") or []})
    config = len(autom) * par["horas_config_atividade"] * (1 + par["variabilidade_fator"] * variabilidade)
    h_isolado = par["horas_plataforma"] + sum(par["horas_capacidade"][c] for c in caps) + config
    ch = par["custo_hora_servidor"]
    chars = len((AQUI / "texto" / "processo_completo.txt").read_text(encoding="utf-8"))
    mchar_ano = chars / 1e6 * rel_ano / fatos["contagem.relatorios_no_pdf"]
    cen = {}
    for i, k in enumerate(CENARIOS):
        fr = par["fracao_automatizavel"]
        h_tot = sum(h[k] for h in horas_ativ.values())
        h_lib = sum(h[k] * fr[potencial.get(a, "baixo")][i] for a, h in horas_ativ.items())
        fator = par["fator_custo_total"][FATOR[k]]
        valid = par["casos_validacao"] * par["horas_validacao_caso"] * ch * fator
        constr = h_isolado * par["custo_hora_dev"][i] + valid
        incr = config * par["custo_hora_dev"][i] + valid
        ret = h_lib * ch * fator
        llm = mchar_ano * par["preco_llm_mchar"][i]
        c_ano, c_ano_i = par["manutencao_anual"] * constr + llm, par["manutencao_anual"] * incr + llm
        pb = (lambda c, ca: round(c / (ret - ca), 1) if ret > ca else None)
        cen[k] = dict(horas_ano_total=round(h_tot, 1), fracao_automatizavel=round(h_lib / h_tot, 3),
                      horas_liberadas_ano=round(h_lib, 1), retorno_ano=round(ret), custo_construcao=round(constr),
                      custo_incremental=round(incr), custo_llm_ano=round(llm, 2), custo_ano=round(c_ano),
                      liquido_ano=round(ret - c_ano), liquido_incremental_ano=round(ret - c_ano_i),
                      payback_anos=pb(constr, c_ano), payback_incremental_anos=pb(incr, c_ano_i),
                      saldo_5_anos=round(par["horizonte_anos"] * (ret - c_ano) - constr),
                      saldo_5_anos_incremental=round(par["horizonte_anos"] * (ret - c_ano_i) - incr),
                      relatorios_ano_para_empatar_incremental=(
                          round(c_ano_i / (ret / rel_ano), 1) if ret else None),
                      relatorios_ano_para_cobrir_custo_ano_isolado=(
                          round(c_ano / (ret / rel_ano), 1) if ret else None),
                      relatorios_ano_payback_5_anos_isolado=(
                          round((c_ano + constr / par["horizonte_anos"]) / (ret / rel_ano), 1) if ret else None),
                      retorno_por_relatorio=round(ret / rel_ano, 1))

    reqs = normas["requisitos"]
    out = dict(
        codigo="FIS",
        gerado_por="scripts/priorizacao_fis.py",
        hipotese=True,
        nota="Medição dos critérios da matriz do capítulo 11 com proxies declarados; horas e premissas de custo são "
             "hipótese até calibração com a CASAN. Unidade de caso: relatório de fiscalização.",
        ancoras_horas=dict(
            fonte="saida/fase4/matriz_automacao.json (P06.sinais, P06.horas_caso) e saida/fase2/casos_P06.json (t3)",
            horas_por_peca_analise_P06=round(h_analise, 2), horas_por_peca_apoio_P06=round(h_apoio, 2),
            horas_parecer_tecnico_por_caso_P06_t3=round(h_parecer, 2),
            escala_cenarios={k: round(v, 3) for k, v in escala.items()}, hipotese=True),
        pecas_ano_por_atividade=pecas,
        horas_ano_por_atividade={a: {k: round(v, 1) for k, v in h.items()} for a, h in sorted(horas_ativ.items())},
        sinais=dict(
            pecas_analise=len(pecas_an), relatorios_com_texto=len(rel_fichas),
            frac_estruturado=round(sum(estrut) / len(pecas_an), 3),
            frac_nao_estruturado=round(sum(nao_estrut) / len(pecas_an), 3),
            frac_norma_substantiva=round(sum(norma_sub) / len(pecas_an), 3),
            frac_checklist=round(sum(checklist) / len(pecas_an), 3),
            nao_conformidades=len(ncs),
            categorias_nc={c: dict(itens=cat_n[c], relatorios=len(cat_rel[c])) for c in
                           sorted(cat_n, key=lambda c: (-cat_n[c], c))},
            categorias_recorrentes=sorted(recorrentes),
            frac_nc_em_categoria_recorrente=round(frac_nc_recorrente, 3),
            caminho_mais_frequente=round(caminho_freq, 3), caminhos_distintos=n_caminhos,
            variabilidade=round(variabilidade, 3),
            requisitos=len(reqs), requisitos_teste_computavel=sum(r["teste"]["tipo"] != "manual" for r in reqs),
            normas=len(normas["normas"]),
            normas_com_texto_nos_autos=sum(not n["situacao_trecho"].startswith("obter") for n in normas["normas"]),
            pct_conforme_casos=conf["pct_conforme_casos"],
            casos_sem_evidencia=conf["contagem_casos"]["sem evidência"],
            mchar_ano=round(mchar_ano, 3)),
        metricas={k: round(v, 3) for k, v in metricas.items()},
        notas=notas,
        nota_composta=dict(unidade_processo=composta(notas["volume_processo"]),
                           unidade_relatorio=composta(notas["volume_relatorio"]),
                           # dados, regras e padrão medidos aqui com instrumento diferente do repositório: leitura
                           # conservadora usa as notas do P06 nesses três critérios
                           conservadora_unidade_processo=round((crit["volume"][0] * notas["volume_processo"]
                               + crit["analise"][0] * notas["analise"] + crit["completude"][0] * notas["completude"]
                               + sum(crit[c][0] * p06["notas"][c] for c in ("dados", "regras", "padrao"))) / 5, 1),
                           conservadora_unidade_relatorio=round((crit["volume"][0] * notas["volume_relatorio"]
                               + crit["analise"][0] * notas["analise"] + crit["completude"][0] * notas["completude"]
                               + sum(crit[c][0] * p06["notas"][c] for c in ("dados", "regras", "padrao"))) / 5, 1)),
        portoes=dict(nota_volume_processo=notas["volume_processo"] >= par["portoes"]["nota_volume"],
                     nota_volume_relatorio=notas["volume_relatorio"] >= par["portoes"]["nota_volume"],
                     nota_regras=notas["regras"] >= par["portoes"]["nota_regras"],
                     casos=fatos["casos.total"] >= par["portoes"]["casos_coorte"],
                     volume_medido_com_revocacao=False),
        atividades_automatizaveis=autom, capacidades=caps,
        horas_dev=dict(isolado=round(h_isolado, 1), incremental=round(config, 1)),
        cenarios=cen,
        p06=dict(nota_composta=p06["nota_composta"], notas=p06["notas"], metricas=p06["metricas"],
                 prioridade=p06["prioridade"], cenarios=p06["cenarios"]),
    )
    (MAP / "priorizacao_FIS.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("metricas", "notas", "nota_composta", "portoes", "horas_dev")},
                     ensure_ascii=False))
    for k, v in cen.items():
        print(k, v)


if __name__ == "__main__":
    main()
