# Priorização da automação — FIS (fiscalizações programadas anuais de saneamento)

**Proposta para decisão da gestão.** Estudo de caso único (SEI-480002/001314/2024, AGENERSA/RJ, fiscalizações
programadas 2024 da CASAN na Águas do Rio – Bloco 1), lido com os critérios da matriz do capítulo 11 do método e
posicionado contra o P06 e os demais tipos de `saida/fase4/matriz_automacao.csv`. Fatos citados pelo id de
`fatos_FIS.json` e `casos_FIS.json`; números calculados aqui, pelo campo de `priorizacao_FIS.json` (gerado por
`scripts/priorizacao_fis.py`, determinístico). **Horas, frações automatizáveis e premissas de custo são hipótese até
a calibração com a CASAN.** A escolha do piloto é da gestão; este documento é insumo.

## Síntese

1. **O FIS é o mesmo tipo do P06, mas na unidade certa o volume muda de patamar.** Contado por processo, herda o
   volume do P06 (`metricas.volume_processo`, nota 2) e fica abaixo do portão. Contado por relatório, que é a unidade
   que se repete e que o sistema produziria, são 42 relatórios no ano só para um bloco
   (contagem.relatorios_citados_parecer), nota 4 (`notas.volume_relatorio`), acima do portão.
2. **Pela regra do método, a classificação é "reavaliar com dados"**: os 42 relatórios são contagem de um processo,
   não volume da agência medido com revocação (`portoes.volume_medido_com_revocacao`). Medir os relatórios por ano de
   todas as concessionárias é o primeiro passo.
3. **Conteúdo muito repetitivo:** 90,3% das 113 não conformidades caem em 13 categorias que se repetem em 3 ou mais
   relatórios (`sinais.frac_nc_em_categoria_recorrente`; contagem.nao_conformidades_total), e há checklist em 78% das
   peças de análise (`sinais.frac_checklist`). É o terreno de redação assistida e verificação automática.
4. **Atividade-alvo:** vistoria → relatório (t2), que é o gargalo (mediana de 34 du da vistoria à 1ª assinatura,
   casos.vistoria_1a_assinatura.mediana_du) e concentra 90% das horas estimadas
   (`horas_ano_por_atividade.t2.esperado` sobre `cenarios.esperado.horas_ano_total`).
5. **Custo × retorno (hipótese):** isolado, o FIS não se paga em nenhum cenário com um só bloco; sobre a plataforma
   construída para outro tipo (P01), paga-se no esperado no limite (`cenarios.esperado.payback_incremental_anos`) e
   bem no otimista (`cenarios.otimista.payback_incremental_anos`). O retorno escala com o número de relatórios por
   ano da agência, ainda não medido.

## 1. Critérios medidos

Mesmos critérios, pesos e réguas da matriz (`matriz_automacao.json: parametros.criterios`). O FIS não tem fichas com
horas e composição de texto como a coorte do repositório; três critérios foram medidos com **instrumento diferente**
(marcados "proxy") e por isso valem como indicação, não como nota comparável 1:1.

| Critério (peso) | Medida no FIS | Valor | Nota FIS | Nota P06 | Fonte e ressalva |
|---|---|---|---|---|---|
| Volume (25%) — por processo | Um processo anual por concessionária (N-FIS-01, R-FIS-01); volume do tipo = o do P06 | 7,6 proc./ano | 2 | 2 | `metricas.volume_processo` = P06 `volume.estimado` |
| Volume (25%) — por relatório | Relatórios do ano listados no parecer anual, um bloco | 42 | 4 | — | contagem.relatorios_citados_parecer; régua calibrada para processos: leitura de sensibilidade |
| Foco em análise (15%) | Horas estimadas de relatórios e parecer ÷ horas do processo | 0,965 | 5 | 5 | `metricas.analise`; horas por peça do P06 (hipótese) |
| Dados estruturados e não estruturados (15%) — proxy | Média: peças de análise com medição/checklist (0,913) e com fotos, anexos ou respostas (1,0) | 0,957 | 5 | 3 | `sinais.frac_estruturado`, `sinais.frac_nao_estruturado`; busca em texto da ficha |
| Regras claras (20%) — proxy | Média: peças que citam norma substantiva (0,87) e com checklist como padrão de teste (0,783) | 0,826 | 4 | 3 | `sinais.frac_norma_substantiva`, `sinais.frac_checklist`; a citação é genérica (lei, CONAMA, ABNT) e 3 relatórios falham na motivação (conformidade_FIS.json, R-FIS-12) |
| Padronização (15%) — proxy | Média: NC em categoria recorrente (0,903) e caminho mais frequente (0,522) | 0,712 | 5 | 2 | `sinais.frac_nc_em_categoria_recorrente`; casos.variante.sem_oficio_de_encaminhamento_nos_autos ÷ casos.total |
| Completude (10%) | Horas em atividades de potencial alto ÷ horas totais | 0,99 | 5 | 5 | `metricas.completude`; t2, t4, t5 alto (avaliacao_FIS.json) |

**Nota composta:** 81,0 por processo e 91,0 por relatório (`nota_composta.unidade_processo`,
`nota_composta.unidade_relatorio`). **Leitura conservadora**, com as notas do P06 nos três critérios proxy: 62,0 por
processo (igual ao P06) e 72,0 por relatório (`nota_composta.conservadora_unidade_processo`,
`nota_composta.conservadora_unidade_relatorio`). A leitura conservadora é a que se deve usar para comparar.

### Sinais que a matriz não pontua, mas que pesam na escolha

| Sinal | Medida | Fonte |
|---|---|---|
| Repetitividade do conteúdo | 113 não conformidades, mediana de 5 por relatório e máximo de 11; as mais repetidas: conservação e corrosão (15 itens em 10 relatórios), identificação da unidade (10 em 10), registros de manutenção no local (10 em 10), sinalização de risco elétrico (9 em 8), falta de bomba reserva (7 em 7) | contagem.nao_conformidades_total; casos.nao_conformidades.mediana; casos.nao_conformidades.max; `sinais.categorias_nc` |
| Defeitos de modelo | Texto de modelo citando outro município (RF 212, RF 213, RF 214) e outro sistema (RF 017); datas internas divergentes em 13 relatórios | avaliacao_FIS.json, desperdícios (fichas) |
| Cadeia de assinaturas | Mediana de 4 assinaturas por relatório, máximo de 6, em 8 cadeias distintas de cargos; 7 lotes de aprovação no ano | casos.assinaturas.mediana; casos.assinaturas.max; casos.cadeias_distintas; lotes.aprovacao.n |
| Regras explícitas | 18 requisitos, 17 com teste computável; mas só 15 de 36 normas com texto nos autos | `sinais.requisitos_teste_computavel`; `sinais.normas_com_texto_nos_autos` |
| Conformidade medida | 96,2% conforme nos casos com evidência, com 35 casos sem evidência | conformidade_FIS.json: pct_conforme_casos, contagem_casos |
| Risco jurídico | Escopo da fiscalização contestado e pedido de arquivamento na Procuradoria; 12 relatórios sem ofício de encaminhamento nos autos; prazo de 30 dias sem dizer se úteis ou corridos | doc 34 (despacho); casos.variante.sem_oficio_de_encaminhamento_nos_autos; oficios.prazo_resposta_unico |
| Variabilidade do fluxo | 3 caminhos em 23 relatórios: fluxo estável, o que reduz o custo de configuração | `sinais.caminhos_distintos`; `sinais.variabilidade` |

## 2. Posição na matriz

| Código | Processo | Nota | Volume | Regras | Prioridade (matriz) | Saldo 5 anos esperado (R$) |
|---|---|---|---|---|---|---|
| P01 | Reajuste tarifário anual | 80,0 | 5 | 3 | piloto | 7.672 |
| P21 | Apuração de ocorrência de usuário | 66,0 | 4 | 3 | candidato a piloto | −140.125 |
| P04 | Homologação de planos de investimento | 66,0 | 2 | 4 | próxima onda | −280.768 |
| P08 | Monitoramento de metas e IDG | 65,0 | 3 | 4 | reavaliar com dados | −217.788 |
| P35 | Interrupções e crises de abastecimento | 63,0 | 3 | 3 | reavaliar com dados | −277.823 |
| P06 | Fiscalização técnica de campo | 62,0 | 2 | 3 | próxima onda | −212.121 |
| **FIS** (por processo, conservadora) | Fiscalização programada anual | 62,0 | 2 | 3 | **próxima onda**, como o P06 | −202.568 |
| **FIS** (por relatório, conservadora) | idem, unidade relatório | 72,0 | 4 | 3 | **reavaliar com dados** (volume de um bloco, sem revocação) | −202.568 |

Fontes: `matriz_automacao.csv` (linhas do repositório); `priorizacao_FIS.json` (nota_composta, notas,
cenarios.esperado.saldo_5_anos). O saldo do FIS é o de um só bloco.

**Leitura.** O FIS é a etapa pré-sancionatória do P06: a coorte P06 do repositório é feita de processos que chegaram
à deliberação (vistoria, parecer técnico, parecer jurídico, relatoria), enquanto o FIS é o programa anual de vistorias
que alimenta essa cadeia. Na unidade relatório, ele passa nos portões de nota de volume, de regras e de casos, com o fluxo mais estável
(`sinais.variabilidade`) e o conteúdo mais repetitivo da carteira. Não vira candidato a piloto por falta de volume
medido na agência. Se o total de relatórios por ano de todas as concessionárias confirmar o patamar, a nota
conservadora (72,0) o põe em segundo lugar, atrás do P01 (80,0) e à frente do P21 (66,0).

## 3. Ganho de tempo no gargalo (fora do retorno em reais)

O retorno da seção 6 conta só horas de trabalho. O ganho que mais importa para a regulação é de prazo, e não entra
no cálculo (capítulo 11, seção 5):

| Trecho | Hoje | O que o sistema ataca | Fonte |
|---|---|---|---|
| Vistoria → 1ª assinatura (t2) | Mediana de 34 du, de 18 a 171 du, em 21 relatórios | Minuta pronta a partir do checklist e das fotos; alerta de relatório sem assinatura; quanto é redação e quanto é fila, a medir | casos.vistoria_1a_assinatura.mediana_du; .min_du; .max_du; .n |
| 1ª assinatura → "De acordo" (t3) | Mediana de 4,5 du, máximo de 35 du | Fila com contagem de dias e checagem de forma antes do Gerente | casos.revisao_aprovacao.mediana_du; .max_du |
| "De acordo" → ofício (t4) | Mediana de 1 du nos oficiados, mas 12 relatórios sem ofício nos autos | Ofício gerado na aprovação e conferência aprovado × oficiado | casos.aprovacao_oficio.mediana_du; casos.variante.sem_oficio_de_encaminhamento_nos_autos |
| Ciclo vistoria → e-mail | Mediana de 62 du em 9 relatórios | Soma dos efeitos acima | casos.vistoria_email.mediana_du; .n |
| Último ofício → parecer anual (t5) | 159 du, com prazo de 30 dias da concessionária dentro | Análise de cada resposta quando chega e parecer gerado do painel | intervalo.ultimo_oficio_parecer_du; oficios.prazo_resposta_unico |

O prazo de resposta da concessionária (30 dias) é tempo de terceiros e não é ganho.

## 4. Atividades candidatas

Potencial e tipos de IA da avaliação AS-IS (`avaliacao_FIS.json`); horas estimadas (hipótese) de
`horas_ano_por_atividade`, cenário esperado.

| Atividade | Potencial | Horas/ano (esp.) | O que o sistema faz | Humano no laço |
|---|---|---|---|---|
| **t2 Vistoriar e elaborar relatório** | alto | 155,6 | Checklist digital por tipo de unidade (EEE, EEAT, ETA, ETE) preenchido em campo, fotos legendadas; **redação assistida do relatório** no modelo da CASAN com as não conformidades da biblioteca de categorias; verificação de datas, unidade, município e trechos de modelo não ajustados; busca de NC já apontadas na mesma unidade; alerta de relatório sem assinatura | Constatação em campo, juízo de gravidade e prazo, assinatura |
| **t5 Analisar providências e emitir parecer anual** | alto | 12,0 | Extração das providências, prazos e cronogramas de cada resposta, por não conformidade; painel de pendências por unidade; **consolidação automática da minuta do parecer anual** a partir do painel | Juízo de atendimento e conclusão do parecer |
| **t4 Encaminhar lote por ofício** | alto | 3,6 | Ofício e e-mail gerados no "De acordo"; conferência aprovado × oficiado; **controle de prazos de resposta** com contagem e alerta de vencimento | Assinatura do Gerente; prazo definido pela CASAN |
| t3 Aprovar relatório | médio | 0 (assinatura na mesma peça) | Fila de aprovação com dias úteis; checagem de forma antes do Gerente; cadeia de assinaturas padronizada | Aprovação |
| t1 Agendar vistorias | médio | 1,2 | Ofício de agendamento a partir do cronograma anual e do cadastro de ativos; alerta de antecedência (R-FIS-18) | Cronograma e assinatura |
| t7, t8, t9 Contestação e Procuradoria | médio | 0,6 (só t8 tem peça nos autos) | Dossiê com linha do tempo, separação de argumentos novos e localização de cláusulas e normas sobre o escopo | Tese jurídica e decisão |
| t6 Ciência do parecer | baixo | 0 (peça fora dos autos) | Comunicação e registro de ciência pelo SEI | Assinatura |

**Ordem sugerida das funções (ondas):**

1. **Controle de prazos e rastreabilidade** (t2, t3, t4, t5): data da vistoria registrada, fila de assinatura,
   conferência aprovado × oficiado, prazo de resposta contado e alertado. Baixo risco (alerta, não decide), sem
   modelo de linguagem, ataca os 12 relatórios sem ofício nos autos e o gargalo de espera.
2. **Checklist digital e redação assistida do relatório** (t2), com verificação de forma. Maior volume de horas e
   maior repetitividade; pré-requisito: modelo oficial e checklist por tipo de unidade.
3. **Acompanhamento das respostas e parecer anual consolidado** (t5). Pré-requisito: respostas juntadas ao processo.
4. **Dossiê para contestação** (t7 a t9), quando houver volume de contestações.

## 5. Capacidades transversais reaproveitáveis

O FIS usa 8 das 10 capacidades da carteira (`capacidades`), as mesmas 8 do P06. Nenhuma é exclusiva dele: todas já
são usadas por 8 a 11 tipos (`capacidades_transversais.csv`). Por isso o custo que conta é o incremental.

| Capacidade | Tipos que já usam | Horas/ano por hora de construção na carteira | Uso no FIS |
|---|---|---|---|
| Sumarização e linha do tempo | 11 | 78,06 | t5, t7, t8, t9 |
| Redação assistida de minuta | 11 | 56,34 | t1, t2, t4, t7 (relatório, ofícios) |
| Busca de precedentes e normas | 10 | 50,15 | t7, t9 |
| Monitoramento de prazos e alertas | 11 | 37,87 | t1, t2, t3, t5 |
| Verificação de conformidade | 10 | 31,79 | t2, t3, t4 |
| Automação de tramitação (RPA no SEI) | 11 | 14,38 | t1, t4, t8 |
| Extração de dados de documentos | 11 | 14,29 | t2, t5 |
| Painel e indicadores | 8 | 2,9 | t5 |

O FIS acrescenta à plataforma dois ativos próprios, reaproveitáveis por P06 e N01: a **biblioteca de categorias de
não conformidade** (15 categorias e um grupo "outras", `sinais.categorias_nc`) e o **cadastro de unidades** por tipo de instalação.

## 6. Custo × retorno — hipótese até calibração

Fórmulas e premissas do capítulo 11 (`matriz_automacao.json: parametros`). Diferença declarada: sem horas medidas
no FIS, as horas por peça vêm da coorte P06 (3,70 h por peça de análise, 0,61 h por peça de apoio, 11,39 h por
parecer técnico, `ancoras_horas`), aplicadas a 42 relatórios, 1 parecer anual e às peças de apoio dos autos
(`pecas_ano_por_atividade`); os cenários escalam essas horas como o piso e o teto do P06
(`ancoras_horas.escala_cenarios`). Volume: um bloco.

| Cenário | Horas/ano do processo | Fração automatizável | Horas liberadas/ano | Retorno/ano (R$) | Construção isolada (R$) | Incremental (R$) | Custo/ano isolado (R$) | Payback isolado | Payback incremental | Saldo 5 anos incremental (R$) |
|---|---|---|---|---|---|---|---|---|---|---|
| Conservador | 101,0 | 0,397 | 40,1 | 1.313 | 165.719 | 31.959 | 33.149 | não se paga | não se paga | −57.376 |
| Esperado | 173,1 | 0,597 | 103,3 | 5.406 | 114.792 | 23.592 | 22.961 | não se paga | 34,5 anos | −20.168 |
| Otimista | 245,1 | 0,796 | 195,2 | 14.045 | 78.753 | 17.953 | 15.751 | não se paga | 1,7 ano | 34.313 |

Fonte: `priorizacao_FIS.json: cenarios.<cenário>` (horas_ano_total, fracao_automatizavel, horas_liberadas_ano,
retorno_ano, custo_construcao, custo_incremental, custo_ano, payback_anos, payback_incremental_anos,
saldo_5_anos_incremental). Horas de desenvolvimento: 744,3 isolado e 136,3 incremental (`horas_dev`). Leitura de
documentos pelo modelo de linguagem: abaixo de R$ 5 por ano em todos os cenários (`cenarios.<cenário>.custo_llm_ano`).

**Faixa (hipótese até calibração):** retorno de R$ 1,3 mil a R$ 14,0 mil por ano para um bloco; construção isolada de
R$ 79 mil a R$ 166 mil, ou de R$ 18 mil a R$ 32 mil sobre a plataforma de outro tipo.

**Ponto de equilíbrio em relatórios por ano** (o número a medir na agência):

| Cenário | Retorno por relatório (R$) | Relatórios/ano para pagar o custo anual incremental | Para pagar o custo anual isolado | Para payback isolado em 5 anos |
|---|---|---|---|---|
| Conservador | 31,3 | 204,6 | 1.060,3 | 2.120,4 |
| Esperado | 128,7 | 36,7 | 178,4 | 356,8 |
| Otimista | 334,4 | 10,7 | 47,1 | 94,2 |

Fonte: `cenarios.<cenário>.retorno_por_relatorio`, `relatorios_ano_para_empatar_incremental`,
`relatorios_ano_para_cobrir_custo_ano_isolado`, `relatorios_ano_payback_5_anos_isolado`.

**Leitura.** No cenário esperado, os 42 relatórios de um bloco já cobrem o custo anual incremental; o FIS isolado só
se paga em 5 anos com algo como 357 relatórios por ano, o que exigiria o programa de todas as concessionárias
reguladas. O que **não** está no retorno: a redução do gargalo de 34 du, a rastreabilidade dos ofícios, a prova mais
robusta numa contestação (defeitos de forma e motivação) e a conformidade dos prazos.

## 7. Insumos para especificar o sistema

| Artefato do FIS | Vira, no sistema | Situação |
|---|---|---|
| `modelo_FIS.json` (9 tarefas com gatilho e saída, 2 decisões) | Casos de uso: gatilho → entrada → regra → saída | 7 perguntas de validação abertas |
| `avaliacao_FIS.json` (potencial e tipos de IA por atividade) | Escopo de cada caso de uso e capacidade usada | Classificação alto/médio/baixo sem verificação independente |
| `fichas/` e `casos_FIS.json` (23 relatórios, datas, cadeias, NC) | Campos do relatório estruturado; conjunto de aceite rotulado | 1 relatório sem texto; 19 relatórios do ano fora do PDF |
| `sinais.categorias_nc` (15 categorias e "outras", 113 itens) | Biblioteca de não conformidades e de recomendações-padrão | Categorias por regra de texto; validar com a CASAN |
| `normas_FIS.json` (18 requisitos, 17 com teste computável) | Verificações automáticas: prazo de envio ao Gerente (R-FIS-04), ordem aprovação ≤ ofício (R-FIS-05), ofício por relatório (R-FIS-06), prazo expresso (R-FIS-07), aviso prévio (R-FIS-18) | 21 normas sem texto nos autos; 12 itens para a Procuradoria (conformidade_FIS.json, itens_procuradoria) |
| `conformidade_FIS.json` (96,2% conforme, 35 sem evidência) | Linha de base para medir o efeito | Respostas da concessionária fora dos autos |
| `fatos_FIS.json` e `casos_FIS.json` (intervalos por relatório) | Linha de base de prazo: indicadores do painel | Dias úteis pelo calendário RJ (hipótese) |
| Melhorias e TO-BE (em elaboração em paralelo) | Regras de humano no laço e controles | Pendente |

Requisitos mínimos já visíveis: data da vistoria como campo obrigatório; numeração única do relatório; um relatório
por vistoria (caso RF 209 e RF 259); prazo de resposta com tipo de contagem (úteis ou corridos); juntada das respostas
da concessionária no próprio processo.

## 8. Limites

- **Um processo, um bloco.** 23 relatórios com texto no PDF contra 42 listados no parecer
  (contagem.relatorios_no_pdf; contagem.relatorios_citados_parecer). Mediana com 21 a 23 casos: aceitável, mas de um
  só processo.
- **Horas não medidas.** Todas as horas vêm da coorte P06 e são hipótese, a calibrar com os servidores da CASAN. Sem
  andamentos do SEI, redação e fila não se separam no gargalo.
- **Proxies.** Dados, regras e padronização foram medidos por busca em texto das fichas e por categorias de NC; a
  citação de normas nos relatórios é genérica. Por isso a nota comparável é a conservadora.
- **Unidade de volume.** A régua de volume foi calibrada para processos; a nota por relatório é sensibilidade.
- **Retorno conta só horas.** Prazo, conformidade e risco jurídico ficam fora, como manda o método.

## Decisão pedida

1. Medir os relatórios de fiscalização programada por ano de todas as concessionárias de saneamento (e, se houver, de
   outras câmaras), para fechar o volume na unidade relatório.
2. Aprovar a 1ª onda (controle de prazos e rastreabilidade) como extensão do P06 sobre a plataforma do piloto, ou
   indicar outra função.
3. Validar com a CASAN as categorias de não conformidade, o checklist por tipo de unidade e as horas por relatório.
