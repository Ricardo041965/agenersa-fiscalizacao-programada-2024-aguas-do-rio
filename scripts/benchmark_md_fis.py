"""Gera BENCHMARKING_FIS.md a partir de benchmark_FIS.json, benchmark_verificacao_FIS.json e fatos_FIS.json."""
import json, sys, statistics

M = sys.argv[1].rstrip('/') + '/'
b = json.load(open(M + 'benchmark_FIS.json', encoding='utf-8'))
v = json.load(open(M + 'benchmark_verificacao_FIS.json', encoding='utf-8'))
fatos = json.load(open(M + 'fatos_FIS.json', encoding='utf-8'))['fatos']
F = {}
for f in fatos:
    F.setdefault(f['id'], f['valor'])
def fv(i):
    return F[i]

vist = [f['valor'] for f in fatos if f['id'].endswith('.vistoria_aprov_dc')]
vist_med = statistics.median(vist)
of_rel = [F[k] for k in sorted(F) if k.startswith('oficio') and k.endswith('.relatorios')]

FASE = {1: 'Ajuste do fluxo', 2: 'Automação de regras e dados', 3: 'Automação com IA', 4: 'Controles, indicadores e metas'}
CAM = {'cientifica': 'científica', 'oficial': 'oficial'}
NIV = {'avaliacao_quantitativa': 'avaliação quantitativa', 'quase_experimental': 'quase-experimental',
       'estudo_de_caso': 'estudo de caso', 'revisao_sistematica': 'revisão sistemática', 'relato_oficial': 'relato oficial'}
casos = b['casos']
C = {c['id']: c for c in casos}
nc = sum(c['fonte']['camada'] == 'cientifica' for c in casos)
no = len(casos) - nc
re_ = [c for c in casos if not c['id'].startswith('B-FIS')]
nv = [c for c in casos if c['id'].startswith('B-FIS')]
r = v['resumo']

L = []
L.append('# Benchmarking do processo FIS — fiscalizações programadas da CASAN (SEI-480002/001314/2024)\n')
L.append('Casos de estado da arte, no Brasil e no exterior, que orientam a melhoria das fiscalizações programadas anuais da '
         'Câmara Técnica de Saneamento (CASAN) da AGENERSA nas unidades da Águas do Rio – Bloco 1 (vistoria → relatório com não '
         'conformidades → ofício com prazo para plano de ação → parecer anual → Procuradoria). Mesma regra do benchmarking do '
         'curso: prática aplicada por órgão identificado, com resultado medido ou avaliado, em duas camadas que não se misturam '
         '(**científica**: revisada por pares, tese ou dissertação com DOI ou handle; **oficial**: documento de regulador). '
         'Cada caso traz trecho literal da fonte, reaberta em 14/11/2026.\n')
L.append(f'- **Casos:** {len(casos)} ({nc} científicos, {no} oficiais; {round(100*nc/len(casos))}% científicos, meta ≥ 60%).')
L.append(f'- **Reaproveitados** da família de fiscalização do P06 (`saida/fase3/benchmark/fiscalizacao.json`): {len(re_)}, com o veredito da verificação independente do repositório; só atividades-alvo e aplicabilidade foram reescritas para o FIS.')
L.append(f'- **Novos**, pesquisados na web: {len(nv)}. Conferência independente (reabertura por script + auditor que não fez a busca): {r["novos_ok"]} sem ressalva, {r["novos_corrigidos"]} corrigidos, {r["excluidos"]} excluídos; {r["trechos_achados_reabertura"]} de {len(nv)} trechos achados na fonte reaberta. Detalhe em `benchmark_verificacao_FIS.json`.')
fases = {k: sum(k in c['fase_melhoria'] for c in casos) for k in FASE}
L.append('- **Por fase:** ' + '; '.join(f'{FASE[k]} {n}' for k, n in fases.items()) + '.\n')

L.append('## Gargalos prováveis do FIS\n')
L.append('Hipóteses do mapeamento AS-IS, a validar com a CASAN. Números de `fatos_FIS.json` (id entre parênteses).\n')
L.append(f'- **G1 — Demora entre a vistoria e a aprovação do relatório.** Da vistoria ao "De acordo" do gerente, a mediana é de {str(vist_med).replace(".", ",")} dias corridos nos {len(vist)} relatórios com as duas datas (fatos `rel*.vistoria_aprov_dc`, mediana calculada por este gerador), com máximo de {max(vist)} dias (`rel17.vistoria_aprov_dc`); já da primeira assinatura à aprovação a mediana é de {str(fv("ciclo.elab_aprov_mediana_dc")).replace(".", ",")} dias (`ciclo.elab_aprov_mediana_dc`). O tempo longo está antes da assinatura: na redação do relatório.')
L.append(f'- **G2 — Envio em lote por ofício.** Os relatórios saem em ofícios de lote ({", ".join(str(x) for x in of_rel)} relatórios por ofício: `oficio*.relatorios`), com espera de até {fv("oficio1.espera_max_dc")} dias entre a aprovação e o ofício (`oficio1.espera_max_dc`), e há relatórios aprovados que não aparecem em nenhum ofício dos autos (pergunta de validação do modelo).')
L.append(f'- **G3 — Parecer anual único.** O Parecer CASAN 250/2025 analisa de uma vez {fv("contagem.relatorios_citados_parecer")} relatórios (`contagem.relatorios_citados_parecer`), {fv("intervalo.ultimo_oficio_parecer")} dias corridos depois do último ofício (`intervalo.ultimo_oficio_parecer`); a consequência de cada não conformidade só aparece nele, e a contestação levou o processo à Procuradoria (`marco.despacho_procuradoria`).')
L.append(f'- **G4 — Respostas da concessionária fora dos autos.** Cada ofício dá {fv("oficio1.prazo_resposta")} dias para plano de ação (`oficio1.prazo_resposta`), mas as respostas e cronogramas não estão no processo (LEIA-ME, limites); não há registro por não conformidade ({fv("contagem.nao_conformidades_total")} itens nos relatórios do PDF: `contagem.nao_conformidades_total`).\n')

L.append('## Práticas por gargalo\n')
G = {
 'G1': ('Demora entre vistoria e relatório', [
   ('B-FIS-01', 'Fiscalização remota na Arsae-MG: tempo médio até o relatório caiu de 135,6 para 75,9 dias (44%), com perda de achados nas unidades operacionais. Para o FIS: verificação remota só da parte documental e das vistorias de retorno; elevatórias, ETAs e ETEs seguem presenciais.'),
   ('B-FIS-02', 'Diagnóstico Lean: a redação do relatório tomou de um terço à metade do tempo de inspeção e só 42% do tempo agregou valor. Método para medir onde está o G1 antes de mudar.'),
   ('B-fiscalizacao-12', 'Fiscais com estilos diferentes em casos comparáveis: justifica lista de verificação por tipo de unidade e critérios fixos de classificação e prazo, que também encurtam a redação.'),
   ('B-fiscalizacao-03', 'Alertas automáticos dirigindo a vistoria: base para usar telemetria e ocorrências da concessionária como gatilho.'),
 ]),
 'G2': ('Envio em lote por ofício', [
   ('B-FIS-03', 'Relatório eletrônico via web do regulado ao regulador, com efeito positivo sobre a conformidade (o primeiro sistema, mal desenhado, piorou). Para o FIS: envio de cada relatório assim que aprovado, por canal eletrônico com ciência registrada, sem esperar o lote.'),
   ('B-fiscalizacao-14', 'ANEEL: alertas automáticos e planos de melhoria acompanhados resolvem parte das não conformidades sem processo sancionador.'),
 ]),
 'G3': ('Parecer anual único sobre ~42 relatórios', [
   ('B-fiscalizacao-07', 'Escalada dinâmica para reincidentes: eliminar a escalada elevaria o dano em 164%. Para o FIS: regra escrita de escalada por item vencido, aplicada durante o ano, em vez do juízo anual único.'),
   ('B-fiscalizacao-11', 'Contrapeso: a pirâmide responsiva só funciona se a escalada acontecer de fato e for previsível.'),
   ('B-FIS-06', 'Environment Agency: métricas fixas, anuais e publicadas para empresas de água e esgoto; autonotificação em 82% em 2022, a melhor desde 2011, mas só 48% nos incidentes graves.'),
   ('B-FIS-05', 'Publicação comparada do desempenho (sunshine) elevou a produtividade das empresas de água neerlandesas.'),
   ('B-fiscalizacao-13', 'Divulgação das violações ao usuário reduziu as violações de água entre 30% e 44%.'),
   ('B-fiscalizacao-08', 'Divulgação de infrações: efeito de um comunicado equivalente a 210 inspeções.'),
   ('B-fiscalizacao-10', 'Medir a fiscalização pelo efeito (resolução e reincidência), não pelo número de relatórios.'),
   ('B-fiscalizacao-01', 'Seleção de alvos por dados: com restrições, dobra as violações achadas. Para o plano de vistorias do ano seguinte.'),
   ('B-fiscalizacao-02', 'Seleção pela maior redução esperada de dano: até o dobro do resultado com a mesma equipe.'),
   ('B-fiscalizacao-04', 'Priorização por algoritmo antecipou em 7,5 dias a constatação de violações críticas.'),
   ('B-fiscalizacao-06', 'Rating de risco pelo histórico de conformidade (precisão de 61% a 66% nos 10% e 5% de maior risco).'),
 ]),
 'G4': ('Respostas da concessionária fora dos autos', [
   ('B-FIS-04', 'Plano de segurança da água obrigatório, do prestador, acompanhado pela autoridade: não conformidade reduzida de forma significativa. Para o FIS: plano de ação único e permanente por unidade, atualizado a cada vistoria e juntado ao processo.'),
   ('B-FIS-03', 'Resposta estruturada em formulário eletrônico por não conformidade (item, providência, prazo, evidência).'),
   ('B-FIS-06', 'Autonotificação como métrica: ônus de informar com o prestador, com conferência independente.'),
   ('B-fiscalizacao-14', 'Plano de melhoria acordado e acompanhado: queda de 41% em dois anos nas falhas de causa desconhecida na transmissão.'),
 ]),
}
for g, (titulo, itens) in G.items():
    L.append(f'### {g} — {titulo}\n')
    L.append('| Caso | Prática | Evidência | Ligação com o FIS |')
    L.append('|---|---|---|---|')
    for cid, txt in itens:
        c = C[cid]
        L.append(f"| {cid} | {c['pratica']} | {NIV[c['nivel_evidencia']]}, {CAM[c['fonte']['camada']]} | {txt} |")
    L.append('')

L.append('## Casos\n')
L.append('| Caso | Prática | Contexto | Resultado | Evidência | Fases | Gargalos |')
L.append('|---|---|---|---|---|---|---|')
for c in casos:
    ctx = c['contexto']
    L.append(f"| {c['id']} | {c['pratica']} | {ctx['orgao']} ({ctx['pais']}, {ctx['periodo']}) | {c['resultado_reportado']} | "
             f"{NIV[c['nivel_evidencia']]}, {CAM[c['fonte']['camada']]} | {', '.join(map(str, c['fase_melhoria']))} | {', '.join(c.get('gargalos_FIS', []))} |")
L.append('')

L.append('### Aplicação ao FIS\n')
for c in casos:
    p = f" Parâmetro: {c['parametro_ganho']}" if c.get('parametro_ganho') else ''
    L.append(f"- **{c['id']}** ({', '.join(c['atividades_alvo'])}) — {c['aplicabilidade']}{p}")
L.append('')
L.append('Parâmetros de casos de outro setor, ferramenta ou país são **teto, não meta**; o cenário do TO-BE fica abaixo e a transferência é explicada.\n')

L.append('### Lacunas\n')
for x in b['lacunas']:
    L.append(f'- {x}')
L.append('')

L.append('### Fontes\n')
for c in casos:
    f = c['fonte']
    link = f"https://doi.org/{f['doi']}" if f['doi'] else f['url']
    L.append(f"- {c['id']}: {f['autores']} ({f['ano']}). {f['titulo']}. *{f['veiculo']}*. {link} Trecho: “{f['trecho']}”")
L.append('')
open(M + 'BENCHMARKING_FIS.md', 'w', encoding='utf-8').write('\n'.join(L))
print('ok', len(L))
