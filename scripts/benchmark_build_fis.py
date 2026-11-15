import json, copy, sys, os

REPO = sys.argv[1]   # mapeamento-processos-sei
OUT = sys.argv[2]    # .../SEI_480002_001314_2024/mapeamento/benchmark_FIS.json

src = json.load(open(os.path.join(REPO, 'saida/fase3/benchmark/fiscalizacao.json'), encoding='utf-8'))
by_id = {c['id']: c for c in src['casos']}

# Casos reaproveitados: resultado, métrica, fonte e parâmetro de ganho mantidos como verificados no repositório;
# atividades-alvo e aplicabilidade reescritas para o processo FIS.
reuso = {
 'B-fiscalizacao-01': (['FIS:t1', 'FIS:t2'], [2, 3], ['G3'],
   'O Parecer CASAN 250/2025 consolida 42 relatórios (fato contagem.relatorios_citados_parecer) num único ano, sem critério de prioridade explícito. As não conformidades já registradas nos relatórios (fato contagem.nao_conformidades_total) são o histórico que um modelo de risco usaria para escolher as unidades da vistoria programada seguinte, mantendo um mínimo de vistoria para todas, como no desenho com restrições do estudo.'),
 'B-fiscalizacao-02': (['FIS:t1'], [2, 3], ['G3'],
   'O ganho vem de escolher melhor quais elevatórias, ETAs e ETEs vistoriar, não de vistoriar mais. Serve ao plano anual da CASAN: priorizar unidades com maior dano esperado (por exemplo, ETEs com não conformidade de tratamento) em vez de cobrir o rol por calendário.'),
 'B-fiscalizacao-03': (['FIS:t1', 'FIS:t2'], [2], ['G1', 'G3'],
   'Fiscalização disparada por alerta, e não por calendário. O análogo no FIS é usar dados que a concessionária já gera (telemetria de elevatórias, extravasamentos, paradas de bomba, análises de efluente) para mandar a vistoria direto à unidade em alerta, em vez de esperar o ciclo anual. Transferência pela prática, não pelo setor.'),
 'B-fiscalizacao-04': (['FIS:t1', 'FIS:t2'], [3], ['G3'],
   'Mostra o ganho de antecipar a constatação sem aumentar a equipe. No FIS, ordenar a agenda de vistorias pelo risco antecipa o achado nas unidades críticas e encurta o tempo de exposição ao problema, que hoje só é consolidado no parecer anual.'),
 'B-fiscalizacao-06': (['FIS:t1', 'FIS:t5'], [2, 3, 4], ['G3', 'G4'],
   'O histórico de conformidade por unidade é o melhor preditor do risco e já está nos relatórios do processo, mas em texto livre, como o relatório da OCDE registra também em Trento. Estruturar as não conformidades por unidade e prazo (fato contagem.nao_conformidades_total) é pré-requisito tanto para o rating de risco quanto para acompanhar as respostas da concessionária.'),
 'B-fiscalizacao-07': (['FIS:t5', 'FIS:t7', 'FIS:t8'], [2, 4], ['G3', 'G4'],
   'Fundamenta uma regra objetiva de escalada no lugar do juízo anual único: não conformidade não resolvida no prazo do ofício (fato oficio1.prazo_resposta) muda o status da unidade, encurta o intervalo até a vistoria de retorno e leva a notificação formal. No FIS a consequência do descumprimento só aparece no parecer anual, depois de um intervalo longo (fato intervalo.ultimo_oficio_parecer).'),
 'B-fiscalizacao-08': (['FIS:t5', 'FIS:t6'], [1, 4], ['G3'],
   'O parecer anual não é divulgado de forma ativa. Publicar, por unidade, as não conformidades e o seu estado (aberta, em plano, resolvida) multiplica o efeito de cada vistoria sem novas visitas.'),
 'B-fiscalizacao-10': (['FIS:t5'], [4], ['G3'],
   'Justifica medir a fiscalização da CASAN pelo efeito (não conformidades resolvidas no prazo, reincidência na mesma unidade) e não pelo número de relatórios emitidos, o que exige registrar as respostas da concessionária por item.'),
 'B-fiscalizacao-11': (['FIS:t5', 'FIS:t7', 'FIS:t8'], [1], ['G3'],
   'Contrapeso: a pirâmide responsiva só funciona se a escalada de fato acontecer e for previsível. No FIS, a contestação da concessionária levou o processo à Procuradoria (fato marco.despacho_procuradoria); escrever a regra de escalada (prazo, reincidência, quando notificar) antes da vistoria reduz a margem de contestação do parecer.'),
 'B-fiscalizacao-12': (['FIS:t2', 'FIS:t3', 'FIS:t5'], [2, 4], ['G1', 'G3'],
   'Justifica padronizar o relatório de vistoria (lista de verificação por tipo de unidade: elevatória, ETA, ETE) com critério explícito de classificação da não conformidade e de prazo, o que encurta a redação, reduz a variação entre fiscais e facilita a consolidação no parecer.'),
 'B-fiscalizacao-13': (['FIS:t5', 'FIS:t6'], [4], ['G3', 'G4'],
   'Caso de saneamento: indicadores de conformidade publicados ao usuário funcionam como fiscalização complementar. Para o FIS, um painel por unidade com as não conformidades e as providências da concessionária daria visibilidade contínua ao que hoje só aparece no parecer anual.'),
 'B-fiscalizacao-14': (['FIS:t4', 'FIS:t5', 'FIS:t7'], [1, 2, 4], ['G2', 'G3', 'G4'],
   'Regulador brasileiro sob o mesmo marco legal: alertas automáticos e planos de melhoria acompanhados resolvem parte das não conformidades sem processo sancionador. No FIS, o ofício já pede plano de ação com prazo (fato oficio1.prazo_resposta), mas as respostas não estão nos autos e o acompanhamento é anual; o plano acompanhado por item e por marco é a contrapartida direta.'),
}

casos = []
for cid, (alvo, fases, gargalos, aplic) in reuso.items():
    c = copy.deepcopy(by_id[cid])
    c['origem'] = 'reaproveitado: mapeamento-processos-sei/saida/fase3/benchmark/fiscalizacao.json (verificação em saida/fase3/benchmark/verificacao.json)'
    c['atividades_alvo'] = alvo
    c['fase_melhoria'] = sorted(set(fases) & set(c['fase_melhoria'])) or c['fase_melhoria']
    c['gargalos_FIS'] = gargalos
    c['aplicabilidade'] = aplic
    casos.append(c)

V = '2026-11-14'
novos = [
 {
  'id': 'B-FIS-01',
  'pratica': 'Fiscalização remota de sistemas de água e esgoto com relatório produzido sem deslocamento',
  'descricao': 'A Arsae-MG passou a fiscalizar remotamente os sistemas de abastecimento de água e de esgotamento sanitário em 2020 (pandemia), com coleta de informações e evidências enviadas pelo prestador no lugar da viagem a campo. O estudo compara 91 relatórios presenciais (2019) com 94 remotos (2020) quanto ao número de não conformidades, à produtividade e ao tempo entre o recebimento da demanda e o envio do relatório.',
  'contexto': {'pais': 'Brasil', 'orgao': 'Agência Reguladora de Serviços de Abastecimento de Água e de Esgotamento Sanitário do Estado de Minas Gerais (Arsae-MG)', 'setor': 'saneamento (água e esgoto)', 'periodo': '2019 (presencial) x 2020 (remota)'},
  'resultado_reportado': 'O tempo médio de atendimento às demandas caiu de 135,6 dias na fiscalização presencial para 75,9 dias na remota (redução de 44%), com número semelhante de relatórios (91 e 94). Em contrapartida, as não conformidades sobre unidades operacionais (elevatórias, ETAs, ETEs) caíram de 46% para 19% do total nos relatórios de água, o que os autores atribuem à visão incompleta das unidades na fiscalização remota.',
  'metrica': {'nome': 'tempo médio entre o recebimento da demanda e o envio do relatório de fiscalização', 'antes': 135.6, 'depois': 75.9, 'unidade': 'dias corridos', 'variacao_pct': -44.0},
  'fonte': {'camada': 'cientifica', 'autores': 'Francis Anthony Cristófaro Warrener; Lucas Marques Pessoa; Uende Aparecida Figueiredo Gomes', 'ano': 2024,
            'titulo': 'Análise comparativa entre a fiscalização remota e presencial dos sistemas de abastecimento de água e de esgotamento sanitário de Minas Gerais: uma análise dos impactos da pandemia de covid-19',
            'veiculo': 'Revista DAE, v. 72, n. 246, p. 1-11', 'doi': '10.36659/dae.2024.058', 'url': 'https://doi.org/10.36659/dae.2024.058',
            'trecho': 'Houve uma redução no tempo médio de atendimento às demandas na fiscalização presencial (135,6 dias), quando comparado à fiscalização remota (75,9 dias).',
            'verificado_em': 'https://www.revistadae.com.br/artigos/artigo_edicao_246_n_2242.pdf', 'data_verificacao': V},
  'nivel_evidencia': 'estudo_de_caso',
  'fase_melhoria': [1, 2],
  'atividades_alvo': ['FIS:t2', 'FIS:t3', 'FIS:t4'],
  'gargalos_FIS': ['G1'],
  'aplicabilidade': 'É o caso mais próximo do FIS: regulador estadual de saneamento, relatório de fiscalização operacional com não conformidades a resolver pelo prestador, processo no SEI. Mostra que tirar a viagem e o trabalho de escritório do caminho crítico encurta o tempo até o relatório. Não serve para substituir a vistoria presencial de elevatórias e estações, justamente onde o estudo perdeu achados; serve para as verificações documentais (licenças, laudos, cronogramas) e para as vistorias de retorno.',
  'parametro_ganho': 'Teto: redução de cerca de 44% no tempo entre a demanda e o envio do relatório quando a verificação é remota; aplicável só à parte documental ou de retorno, com perda de achados em unidades operacionais se usada no lugar da vistoria presencial.',
  'limitacoes': 'Comparação antes e depois em anos diferentes (2019 x 2020), sem grupo de controle, com a pandemia afetando também o prestador; o tempo medido inclui fiscalizações por demanda, não só as programadas.',
 },
 {
  'id': 'B-FIS-02',
  'pratica': 'Diagnóstico Lean do tempo de inspeção de campo, com a redação do relatório como etapa medida',
  'descricao': 'Dissertação que cronometrou, por acompanhamento direto, cada etapa da inspeção de rotina de 26 pontes (preparação, deslocamento, inspeção, desmobilização e redação do relatório) e classificou as atividades em que agregam valor, necessárias sem valor e desperdício, tendo como produto o relatório aprovado pelo dono da obra.',
  'contexto': {'pais': 'Estados Unidos', 'orgao': 'Programa de inspeção de rotina de pontes (Delaware), estudado na University of Delaware', 'setor': 'infraestrutura (inspeção de pontes)', 'periodo': 'publicado em 2017'},
  'resultado_reportado': 'Deslocamento, inspeção e redação do relatório consumiram cada um cerca de um terço da duração total; somando o tempo declarado pelos inspetores, a redação do relatório chegou à metade. Só 42% do tempo total agregou valor ao produto final, o relatório aprovado.',
  'metrica': {'nome': 'fração do tempo de inspeção que agrega valor ao relatório aprovado', 'antes': None, 'depois': 42, 'unidade': '%', 'variacao_pct': None},
  'fonte': {'camada': 'cientifica', 'autores': 'Emal Masoud', 'ano': 2017, 'titulo': 'Application of Lean philosophy to routine inspection of bridges',
            'veiculo': 'Dissertação, University of Delaware (UDSpace)', 'doi': '10.58088/y7dz-t902', 'url': 'http://udspace.udel.edu/handle/19716/23121',
            'trecho': 'only 42% of total time spent on routine inspection of bridges was found to add value to the final output, an owner approved bridge inspection report.',
            'verificado_em': 'https://api.openalex.org/works/doi:10.58088/y7dz-t902', 'data_verificacao': V},
  'nivel_evidencia': 'estudo_de_caso',
  'fase_melhoria': [1],
  'atividades_alvo': ['FIS:t2', 'FIS:t3'],
  'gargalos_FIS': ['G1'],
  'aplicabilidade': 'Dá método e ordem de grandeza para o gargalo G1: no FIS, o tempo entre a vistoria e a aprovação do relatório (fatos rel*.vistoria_aprov_dc) é muito maior que o tempo entre a primeira assinatura e a aprovação (fato ciclo.elab_aprov_mediana_dc), o que aponta a redação como a etapa longa. Cronometrar a redação dos relatórios da CASAN pelo mesmo método mostraria quanto é desperdício (retranscrição de anotações, montagem de fotos, reescrita de itens repetidos).',
  'parametro_ganho': None,
  'limitacoes': 'Diagnóstico sem intervenção: mede o desperdício, não o ganho de uma mudança. Setor diferente (pontes), 26 inspeções acompanhadas.',
 },
 {
  'id': 'B-FIS-03',
  'pratica': 'Relatório eletrônico (via web) das medições do regulado ao regulador',
  'descricao': 'Avaliação, com dados de Ohio de 1996 a 2009, do efeito do relatório eletrônico de monitoramento de descargas (DMR) exigido dos titulares de licença do Clean Water Act, entre eles estações de tratamento de esgoto. Ohio adotou um software de relatório eletrônico em 2000 e um sistema via web em 2008; o estudo usa modelos logit com tendência temporal e efeitos fixos por licenciado.',
  'contexto': {'pais': 'Estados Unidos', 'orgao': 'Ohio Environmental Protection Agency (programa NPDES do Clean Water Act)', 'setor': 'efluentes e esgoto', 'periodo': 'anos fiscais de 1996 a 2009'},
  'resultado_reportado': 'O primeiro sistema (software) teve efeito negativo significativo sobre a conformidade e o sistema via web teve efeito positivo significativo; o autor conclui que o relatório eletrônico ajuda o regulador a identificar violações com mais precisão e dá dados mais completos à agência e ao público.',
  'metrica': {'nome': 'efeito do sistema de relatório via web sobre a conformidade', 'antes': None, 'depois': None, 'unidade': 'qualitativo (significância estatística)', 'variacao_pct': None},
  'fonte': {'camada': 'cientifica', 'autores': 'Gregory B. Siedschlag', 'ano': 2011, 'titulo': 'The effect of electronic reporting of discharge monitoring reports on Clean Water Act compliance in Ohio',
            'veiculo': 'Dissertação (Master of Public Policy), Georgetown University', 'doi': '', 'url': 'http://hdl.handle.net/10822/553916',
            'trecho': 'Results indicate a significant negative effect on compliance from the first system and a significant positive effect from the second.',
            'verificado_em': 'https://api.openalex.org/works/W850999971', 'data_verificacao': V},
  'nivel_evidencia': 'quase_experimental',
  'fase_melhoria': [2],
  'atividades_alvo': ['FIS:t4', 'FIS:t5'],
  'gargalos_FIS': ['G2', 'G4'],
  'aplicabilidade': 'Responde ao gargalo G4: no FIS as respostas e os cronogramas da concessionária não estão nos autos, e o parecer anual teve de reconstituí-los. Um formulário eletrônico de resposta por não conformidade (item, providência, prazo, evidência), recebido no SEI ou em sistema integrado, deixa a resposta rastreável e comparável. O resultado misto alerta que o desenho importa: o primeiro sistema piorou a conformidade.',
  'parametro_ganho': None,
  'limitacoes': 'Dissertação de mestrado, um Estado, sem número de efeito no resumo; o repositório da Georgetown exige verificação de navegador, e o trecho foi lido no registro do OpenAlex.',
 },
 {
  'id': 'B-FIS-04',
  'pratica': 'Plano de segurança da água obrigatório, elaborado pelo prestador e auditado pela autoridade',
  'descricao': 'A Islândia foi um dos primeiros países a tornar obrigatório o plano de segurança da água (WSP): o prestador identifica riscos e define barreiras e ações corretivas, e a autoridade sanitária acompanha. O estudo compara mais de uma década de dados de vigilância da qualidade da água e de diarreia antes e depois da implantação.',
  'contexto': {'pais': 'Islândia', 'orgao': 'Autoridades sanitárias da Islândia e prestadores de abastecimento de água', 'setor': 'abastecimento de água', 'periodo': 'mais de uma década de dados; publicado em 2012'},
  'resultado_reportado': 'Depois da implantação do plano, a não conformidade regulatória e a contagem de bactérias heterotróficas caíram de forma significativa (p < 0,001), e a população atendida por sistemas com plano teve 14% menos probabilidade de casos clínicos de diarreia.',
  'metrica': {'nome': 'probabilidade de casos clínicos de diarreia na população atendida com plano', 'antes': None, 'depois': None, 'unidade': '%', 'variacao_pct': -14},
  'fonte': {'camada': 'cientifica', 'autores': 'María J. Gunnarsdóttir; Sigurdur Magnus Gardarsson; Mark Elliott; Guðrún Sigmundsdóttir; Jamie Bartram', 'ano': 2012,
            'titulo': 'Benefits of Water Safety Plans: Microbiology, Compliance, and Public Health', 'veiculo': 'Environmental Science & Technology, v. 46, n. 14, p. 7782-7789',
            'doi': '10.1021/es300372h', 'url': 'https://doi.org/10.1021/es300372h',
            'trecho': 'noncompliance was also significantly reduced (p < 0.001 in both cases). A significant decrease in incidence of diarrhea was detected where a WSP was implemented',
            'verificado_em': 'https://api.openalex.org/works/doi:10.1021/es300372h', 'data_verificacao': V},
  'nivel_evidencia': 'quase_experimental',
  'fase_melhoria': [1, 4],
  'atividades_alvo': ['FIS:t4', 'FIS:t5'],
  'gargalos_FIS': ['G3', 'G4'],
  'aplicabilidade': 'Inverte a lógica do FIS: em vez de o regulador listar não conformidades e esperar respostas avulsas, o prestador mantém um plano formal de riscos e ações por unidade, que o regulador audita. Para a Águas do Rio, o plano de ação exigido nos ofícios poderia ser um plano único e permanente por unidade (elevatória, ETA, ETE), atualizado a cada vistoria, o que substitui a reconstituição anual feita no parecer.',
  'parametro_ganho': 'Redução significativa da não conformidade regulatória depois da adoção do plano obrigatório (sem percentual no resumo); efeito de saúde de 14% menos casos de diarreia como resultado final, não transferível como meta de processo.',
  'limitacoes': 'Abastecimento de água, não esgoto; antes e depois sem aleatorização. O plano é do prestador; o efeito do acompanhamento pelo regulador não é isolado.',
 },
 {
  'id': 'B-FIS-05',
  'pratica': 'Regulação por exposição (sunshine): publicação comparada do desempenho dos prestadores',
  'descricao': 'Nos Países Baixos, as empresas de água potável passaram a ter o desempenho publicado em benchmarking comparativo, sem regulação formal de preços. O estudo decompõe a variação do lucro e da produtividade antes e depois da introdução da publicação, com medidas de eficiência não paramétricas robustas.',
  'contexto': {'pais': 'Países Baixos', 'orgao': 'Empresas de água potável neerlandesas (benchmarking setorial publicado)', 'setor': 'abastecimento de água', 'periodo': 'antes e depois da introdução da publicação; publicado em 2009'},
  'resultado_reportado': 'A publicação comparada do desempenho foi eficaz para elevar a produtividade das empresas públicas de água e trouxe redução moderada das tarifas, mas os lucros econômicos persistentes indicam que não basta, sozinha, para alinhar preços e custos no longo prazo.',
  'metrica': {'nome': 'produtividade das empresas de água', 'antes': None, 'depois': None, 'unidade': 'qualitativo', 'variacao_pct': None},
  'fonte': {'camada': 'cientifica', 'autores': 'Kristof De Witte; David S. Saal', 'ano': 2009,
            'titulo': 'Is a little sunshine all we need? On the impact of sunshine regulation on profits, productivity and prices in the Dutch drinking water sector',
            'veiculo': 'Journal of Regulatory Economics, v. 37, n. 3, p. 219-242', 'doi': '10.1007/s11149-009-9112-5', 'url': 'https://doi.org/10.1007/s11149-009-9112-5',
            'trecho': 'sunshine regulation was effective in improving the productivity of publicly organised services. Nevertheless, while sunshine regulation did bring about a moderate reduction in water prices',
            'verificado_em': 'https://api.openalex.org/works/doi:10.1007/s11149-009-9112-5', 'data_verificacao': V},
  'nivel_evidencia': 'avaliacao_quantitativa',
  'fase_melhoria': [4],
  'atividades_alvo': ['FIS:t5', 'FIS:t6'],
  'gargalos_FIS': ['G3'],
  'aplicabilidade': 'Mostra que publicar o desempenho já move o prestador, sem sanção. No FIS, o parecer anual sobre 42 relatórios (fato contagem.relatorios_citados_parecer) poderia virar um painel publicado por unidade e por tipo de não conformidade, atualizado a cada vistoria e resposta; o parecer deixaria de ser a primeira e única visão de conjunto. Mede produtividade e preço, não conformidade técnica: a transferência é pelo mecanismo.',
  'parametro_ganho': None,
  'limitacoes': 'Mede eficiência econômica, não conformidade de instalações; contexto de empresas públicas neerlandesas; sem número no resumo.',
 },
 {
  'id': 'B-FIS-06',
  'pratica': 'Avaliação anual de desempenho ambiental das empresas de água e esgoto com autonotificação de incidentes (EPA)',
  'descricao': 'A Environment Agency da Inglaterra avalia desde 2011 as empresas de água e esgoto por um conjunto fixo de métricas com metas em semáforo (incidentes de poluição por 10 mil km de rede, incidentes graves, conformidade das licenças de estações, autonotificação de incidentes) e publica uma classificação em estrelas por empresa.',
  'contexto': {'pais': 'Reino Unido (Inglaterra)', 'orgao': 'Environment Agency', 'setor': 'água e esgoto', 'periodo': '2011-2022'},
  'resultado_reportado': 'Em 2022 a autonotificação de incidentes de poluição pelas empresas chegou a 82%, a melhor desde o início da avaliação em 2011, e a conformidade das estações de tratamento de água atingiu o maior nível; mas só 48% dos incidentes graves foram autonotificados e o total de incidentes de esgoto continuou alto.',
  'metrica': {'nome': 'incidentes de poluição autonotificados pelas empresas', 'antes': None, 'depois': 82, 'unidade': '%', 'variacao_pct': None},
  'fonte': {'camada': 'oficial', 'autores': 'Environment Agency', 'ano': 2023, 'titulo': 'Water and sewerage companies in England: environmental performance report 2022',
            'veiculo': 'GOV.UK', 'doi': '',
            'url': 'https://www.gov.uk/government/publications/water-and-sewerage-companies-in-england-environmental-performance-report-2022/water-and-sewerage-companies-in-england-environmental-performance-report-2022',
            'trecho': 'We have seen that the EPA can motivate water companies to achieve better performance – both self-reporting and WTW compliance were at their highest levels ever in 2022.',
            'verificado_em': 'https://www.gov.uk/government/publications/water-and-sewerage-companies-in-england-environmental-performance-report-2022/water-and-sewerage-companies-in-england-environmental-performance-report-2022', 'data_verificacao': V},
  'nivel_evidencia': 'relato_oficial',
  'fase_melhoria': [4],
  'atividades_alvo': ['FIS:t5'],
  'gargalos_FIS': ['G3', 'G4'],
  'aplicabilidade': 'Modelo de indicador fixo, anual e publicado, aplicado a empresas de água e esgoto: substitui o juízo qualitativo único por métricas comparáveis entre anos, e a autonotificação transfere ao prestador o ônus de informar. Para o FIS, a métrica análoga é a fração das não conformidades com resposta e plano registrados no prazo do ofício.',
  'parametro_ganho': None,
  'limitacoes': 'Relato do próprio regulador; os incidentes graves e os de esgoto não melhoraram, e relatórios posteriores mostram piora. A autonotificação de incidentes graves (48%) segue baixa, o que exige conferência independente.',
 },
]
casos.extend(novos)

out = {
 'familia': 'fiscalizacao_FIS',
 'processos': ['FIS'],
 'processo_sei': 'SEI-480002/001314/2024 (AGENERSA/RJ, CASAN, Águas do Rio – Bloco 1)',
 'pergunta': 'Que práticas documentadas de fiscalização técnica de saneamento e de inspeção regulatória, com resultado medido, encurtam o tempo entre a vistoria e o relatório, substituem o envio em lote e a análise anual única por acompanhamento contínuo das não conformidades e trazem as respostas do prestador para dentro do processo?',
 'gargalos': {
   'G1': 'Demora entre a vistoria e a aprovação do relatório (fatos rel*.vistoria_aprov_dc; ciclo.elab_aprov_mediana_dc)',
   'G2': 'Envio dos relatórios em lote por ofício, com espera entre a aprovação e o ofício e relatórios fora dos ofícios dos autos (fatos oficio*.relatorios, oficio*.espera_max_dc)',
   'G3': 'Parecer anual único sobre o conjunto de relatórios do ano (fatos contagem.relatorios_citados_parecer, intervalo.ultimo_oficio_parecer)',
   'G4': 'Ausência das respostas e cronogramas da concessionária nos autos (LEIA-ME, limites; evento e1 do modelo)'
 },
 'estrategia_busca': [
   'Reaproveitamento: saida/fase3/benchmark/fiscalizacao.json (família do P06), 12 dos 15 casos; fora B-fiscalizacao-05 (concurso de algoritmo), 09 (gasodutos) e 15 (deliberação da diretoria, etapa que o FIS não tem).',
   'OpenAlex API (works?search=): "sunshine regulation water utilities Portugal performance", "water safety plans benefits compliance Iceland", "sunshine regulation drinking water benchmarking Netherlands efficiency", "wastewater treatment plants inspections effect compliance municipal Clean Water Act", "electronic reporting discharge monitoring compliance effect", "fiscalização remota Arsae-MG", "mobile tablet electronic inspection form environmental health inspectors time savings evaluation", "inspection report completion time paper versus electronic inspectors", "risk-based inspection drinking water regulator audit frequency compliance".',
   'Crossref (api.crossref.org/works/<doi>) e DataCite (api.datacite.org/dois/<doi>) para conferir DOI e metadados.',
   'WebSearch e WebFetch/curl: ARSAE-MG fiscalização baseada em risco; ERSAR indicador de água segura; Environment Agency Environmental Performance Assessment; Drinking Water Inspectorate legal instruments; aplicativo de fiscalização em campo de agências de saneamento.'
 ],
 'casos': casos,
 'lacunas': [
   'ERSAR (Portugal): o indicador de água segura (de cerca de 50% em 1993 para 99%) só foi achado em notícias e em figura sem valores no PENSAAR 2020; a página oficial da ERSAR não abriu (404). Ficou de fora.',
   'Drinking Water Inspectorate (Reino Unido): os programas de melhoria juridicamente vinculantes (notices e undertakings) com marcos, relatórios de encerramento e portal de acompanhamento de marcos (2024) são o modelo mais próximo de plano de ação com prazo padronizado, mas as páginas lidas trazem só contagens de instrumentos, sem resultado medido. Ficou de fora; vale como referência de desenho.',
   'Gray, Shadbegian e Wolverton (NBER Working Paper 35525, 2026) acharam, por diferenças em diferenças, mais completude dos relatórios, menos descargas e inspeções mais bem dirigidas depois do relatório online com auditoria automática de efluentes; é working paper, não revisado por pares, e ficou fora das duas camadas.',
   'Aplicativo de campo ou relatório digital de vistoria em regulador de saneamento brasileiro com redução medida do tempo de emissão do relatório: não encontrado. Há o aplicativo de fiscalização da APAC (apresentação no Progestão/ANA) e relatórios remotos da AGR-GO, sem medição de prazo.',
   'ARSESP, ADASA e AGR-GO: fiscalização baseada em risco ou por indicadores com resultado medido em fonte verificável não encontrada.',
   'Prazo padronizado de resposta a não conformidade (por gravidade) com efeito medido sobre o tempo de correção: não encontrado.',
   'Ofwat: os relatórios de desempenho tratam de compromissos de desempenho e incentivos tarifários, não de fiscalização de unidades; não incluídos.'
 ]
}
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(len(casos), sum(c['fonte']['camada'] == 'cientifica' for c in casos))
