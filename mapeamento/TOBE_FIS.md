# Fiscalizações programadas 2024 da Águas do Rio – Bloco 1 — proposta de TO-BE

Processo de referência: SEI-480002/001314/2024 (AGENERSA/RJ, Câmara Técnica de Saneamento — CASAN). Código do
processo: FIS. Mesmo tipo do P06 (fiscalização técnica de campo) do repositório da metodologia.

**Leitura obrigatória.** Esta proposta parte de um único processo anual, com um caso por relatório de fiscalização
(23 relatórios no PDF, casos.total) e um único caso de análise das respostas (o parecer anual). Os
autos exportados são um recorte: 23 relatórios com texto no PDF contra
42 listados no parecer (contagem.relatorios_no_pdf;
contagem.relatorios_citados_parecer). O TO-BE foi simulado reaplicando a linha do tempo de cada relatório, mas
**todo parâmetro de melhoria é hipótese** a validar com a CASAN, e as medianas de 9 a 21 relatórios são ordem de
grandeza. **Horas de trabalho e custo não foram medidos nem simulados**: qualquer número desse tipo é hipótese (os da
seção 9 vêm de `priorizacao_FIS.md`, com horas emprestadas da coorte P06). Entre parênteses vai o id do fato, do
requisito legal, do caso de benchmark, da melhoria ou do valor calculado (`lb.*`, `tobe.*`, `sens.*` em
`resultado_tobe_FIS.json`).

## 1. Como o processo funciona hoje (AS-IS)

1. O Conselho-Diretor determina vistorias anuais por concessionária; a CASAN agenda as vistorias com a concessionária.
2. A equipe de fiscalização vistoria a unidade (elevatória de água ou esgoto, ETA, ETE) e redige o relatório, com
   checklist, fotos, não conformidades e recomendações.
3. O relatório recebe até 6 assinaturas (casos.assinaturas.max), em cadeias de cargos que
   variam, até o "De acordo" do Gerente.
4. Relatórios aprovados seguem em lote, por ofício com prazo de resposta, enviado por e-mail pelo SEI.
5. As respostas e cronogramas da concessionária chegam fora do processo exportado; a CASAN os analisa num parecer
   anual único, que vai à SECEX para ciência da concessionária.
6. A concessionária contestou o escopo da fiscalização; a CASAN reiterou o parecer e a SECEX enviou o processo à
   Procuradoria (fim do recorte).

| Medida | Valor | Fato |
|---|---|---|
| Ciclo do relatório, da vistoria ao e-mail à concessionária | mediana de 62 du em 9 relatórios, de 31 a 173 du | casos.vistoria_email.mediana_du; casos.vistoria_email.n; casos.vistoria_email.min_du; casos.vistoria_email.max_du |
| Vistoria → 1ª assinatura do relatório | mediana de 34 du em 21 relatórios, de 18 a 171 du | casos.vistoria_1a_assinatura.mediana_du; .n; .min_du; .max_du |
| 1ª assinatura → "De acordo" | mediana de 4,5 du, máximo de 35 du | casos.revisao_aprovacao.mediana_du; .max_du |
| "De acordo" → ofício (relatórios oficiados nos autos) | mediana de 1 du, máximo de 6 du | casos.aprovacao_oficio.mediana_du; .max_du |
| Último ofício → parecer anual | 159 du | intervalo.ultimo_oficio_parecer_du |
| Vistoria → parecer, por relatório (linha de base congelada) | mediana de 256 du em 21 relatórios | lb.ate_parecer.mediana_du; lb.ate_parecer.n |
| Parecer → envio à Procuradoria | 118 dias corridos | intervalo.parecer_procuradoria |
| Relatórios sem ofício de encaminhamento nos autos | 12 (contra 10 com ofício) | casos.variante.sem_oficio_de_encaminhamento_nos_autos; casos.variante.com_oficio_de_encaminhamento_nos_autos |
| Lotes de aprovação no ano; cadeias de assinatura distintas | 7 lotes; 8 cadeias | lotes.aprovacao.n; casos.cadeias_distintas |
| Não conformidades nos relatórios do PDF | 113 | contagem.nao_conformidades_total |
| Prazo de resposta nos ofícios | 30 dias, sem dizer se úteis ou corridos | oficios.prazo_resposta_unico |

Dias úteis pelo calendário do RJ de `scripts/fatos_fis.py` (hipótese: pontos facultativos não conferidos).

## 2. Onde está o gargalo

**Principal: da vistoria à 1ª assinatura do relatório (t2).** É o maior trecho do ciclo interno
(casos.vistoria_1a_assinatura.mediana_du) e é controlável pela própria CASAN. A linha de base decompõe o trecho com a
data do fecho do texto ("Em dd/mm/aaaa", lida em `conformidade_FIS.json`): da vistoria ao fecho, mediana de
12 du; do fecho à 1ª assinatura, mediana de 17 du,
nos 21 relatórios com as três datas (lb.vistoria_fecho.mediana_du; lb.fecho_1a_assinatura.mediana_du;
lb.vistoria_fecho.n). É indício de texto pronto aguardando assinatura — hipótese a confirmar com a CASAN, que define o
quanto a fase 1 pode ganhar sem tecnologia. O caso extremo é o RF 017: 247 dias corridos da
vistoria ao "De acordo" (rel17.vistoria_aprov_dc).

**Restrição secundária: a análise das respostas concentrada num parecer anual (t5).** O parecer saiu
159 du depois do último ofício (intervalo.ultimo_oficio_parecer_du); para cada
relatório, o tempo do fim do prazo protegido da concessionária até o parecer tem mediana de
162 du (lb.componente.a6_agencia.mediana_du). É um só caso e inclui o prazo da
concessionária, por isso não foi declarado gargalo principal na avaliação.

**Outros desperdícios (avaliacao_FIS.json):** estoque de relatórios aprovados à espera do lote
(lotes.aprovacao.n); superprocessamento na cadeia de assinaturas (mediana de 4
assinaturas por relatório, casos.assinaturas.mediana); defeitos de forma (datas divergentes, texto de modelo de outro
município ou sistema, 2 relatórios sem vistoria datada, casos.sem_vistoria_datada);
encaminhamento não rastreável (casos.variante.sem_oficio_de_encaminhamento_nos_autos).

## 3. Conformidade legal

96,2% dos casos verificáveis estão conformes (75 conformes,
3 não conformes, 35 sem evidência; `conformidade_FIS.json`).
O que pesa no TO-BE:

| Requisito | Exigência | Situação no caso | Tratamento no TO-BE |
|---|---|---|---|
| R-FIS-04 | Relatório ao Gerente em até 5 du da lavratura (IN 128/2024, desde 01/10/2024) | Conforme nos relatórios do período de vigência; aplicado a todo o ano, 54,5% (lb.R-FIS-04.pct) | M-FIS-02; meta simulada no I-FIS-04 |
| R-FIS-06 | Relatório com não conformidade comunicado por ofício com comprovante | 12 relatórios sem evidência nos autos | M-FIS-03, M-FIS-13; I-FIS-05 |
| R-FIS-07, R-FIS-08 | Prazo expresso no ofício; resposta no prazo | Prazo de 30 dias sem unidade; respostas fora dos autos | M-FIS-03, M-FIS-06; **prazo protegido** |
| R-FIS-09, R-FIS-11 | Saneamento no prazo; parecer em 15 dias das respostas | Sem evidência | M-FIS-04, M-FIS-08, M-FIS-14; I-FIS-08, I-FIS-12 |
| R-FIS-10 | Entre o envio e o parecer decorre ao menos o prazo concedido | Conforme | **Protegido**: a simulação nunca reduz esse tempo |
| R-FIS-12 | Relatório com fatos e fundamento normativo | 86,4% (RF 10, RF 11 e RF 12 sem fundamento) | M-FIS-05, M-FIS-15; I-FIS-09 |
| R-FIS-02, R-FIS-18 | Cronograma antes da 1ª vistoria; aviso com 48 horas | Sem evidência; aviso de 1 du no único ofício de agendamento (of3.antecedencia_agendamento_du) | M-FIS-09; I-FIS-13 |
| R-FIS-16 | Sanção só com notificação e defesa prévia | Não aplicável no recorte | C-FIS-06 na regra de escalada (M-FIS-10) |

Itens para a Procuradoria estão em `conformidade_FIS.json` (`itens_procuradoria`) e na seção 10.

## 4. Benchmarking usado

Casos de `benchmark_FIS.json` (detalhe em `BENCHMARKING_FIS.md`). Resultado de outro setor ou desenho é **teto, não
meta**: os cenários esperados ficam abaixo e a transferência está justificada em cada melhoria.

| Tema | Casos | Uso |
|---|---|---|
| Tempo até o relatório | B-FIS-01 (fiscalização remota de saneamento em MG, redução média de 44% no tempo até o relatório); B-FIS-02 (diagnóstico Lean: redação é a etapa longa) | Sustentam M-FIS-01, M-FIS-07, M-FIS-15 |
| Padronização entre fiscais | B-fiscalizacao-12 | M-FIS-02, M-FIS-05, M-FIS-07 |
| Acompanhamento contínuo e planos de ação | B-fiscalizacao-14 (ANEEL), B-FIS-04 (plano de segurança da água) | M-FIS-03, M-FIS-04, M-FIS-08, M-FIS-12, M-FIS-13 |
| Resposta eletrônica do regulado | B-FIS-03, B-fiscalizacao-06 | M-FIS-06, M-FIS-14 |
| Escalada previsível | B-fiscalizacao-07, B-fiscalizacao-11 | M-FIS-10, M-FIS-11 |
| Priorização por risco | B-fiscalizacao-01, -02, -04, -06 | M-FIS-16 |
| Divulgação | B-fiscalizacao-13, B-FIS-05, B-fiscalizacao-08 | M-FIS-17 |

Lacuna registrada no benchmarking: não se achou regulador brasileiro de saneamento com redução medida do tempo de
emissão do relatório por aplicativo de campo, nem prazo padronizado por gravidade com efeito medido.

## 5. O processo proposto (TO-BE)

O TO-BE mantém todas as decisões humanas e o prazo concedido à concessionária. O que muda:

- cronograma anual juntado ao processo e aviso de fiscalização por modelo, com antecedência mínima (t1, t2);
- vistoria com checklist digital por tipo de unidade e relatório no modelo padrão, com meta interna e minuta
  assistida revista pela equipe (t3, t4);
- checagem automática de forma antes da assinatura (t5, nova);
- "De acordo" em fluxo contínuo, sem lote, com cadeia elaborado / revisado / de acordo (t6);
- ofício gerado no "De acordo", com prazo e unidade de contagem expressos e conferência aprovado × oficiado (t7);
- resposta da concessionária por não conformidade, analisada relatório a relatório em prazo interno (t8), com regra
  escrita de escalada (g1, t9) e painel de pendências (t10, novo);
- parecer anual só de consolidação (t11); contestação respondida pela tese-padrão, e só questão jurídica nova vai à
  Procuradoria (t13 a t15).

Correspondência com o AS-IS: t1→t1 e t2; t2→t3 e t4; t3→t6; t4→t7; g1→g1 e t9; t5→t8 e t11; t6→t12; t7→t13;
t8→t14; t9→t15; t5 e t10 do TO-BE são novas (`modelo_tobe_FIS.json`, `correspondencia_asis_tobe`).

Diagrama: `bpmn_tobe/FISTOBE.bpmn` e visualizador `bpmn_tobe/index.html`, gerados por `gerar_bpmn.py` do repositório
da metodologia a partir de `bpmn_tobe/modelo_FISTOBE.json` (cópia de `modelo_tobe_FIS.json`). `checar_bpmn.py`: 0 seta
atravessando elemento, 0 sobreposição, 0 cruzamento e 0 rótulo sobreposto.

## 6. Melhorias por fase

As fases são cumulativas. Nenhuma melhoria encurta o prazo concedido à concessionária (R-FIS-07, R-FIS-08,
R-FIS-10) nem o aviso prévio da vistoria (R-FIS-18). Todas são `hipotese: true`; a faixa é o efeito simulado por
cenário (conservador / esperado / otimista), e a premissa de cada uma está em `melhorias_FIS.json`.

### Fase 1 — rápidas (organização, sem norma nova nem tecnologia)

| Id | Melhoria | Ataca | Requisitos | Benchmark | Efeito simulado |
|---|---|---|---|---|---|
| M-FIS-01 | Meta interna da vistoria ao relatório assinado, com fila visível | Gargalo t2 (espera) | R-FIS-03, R-FIS-04, R-FIS-12 | B-FIS-02, B-FIS-01 | Teto de 30 / 25 / 18 du na vistoria → 1ª assinatura |
| M-FIS-02 | Aprovação em fluxo contínuo, cadeia elaborado / revisado / de acordo | Estoque e superprocessamento (t3) | R-FIS-04, R-FIS-05 | B-fiscalizacao-12, B-FIS-02 | Teto de 10 / 5 / 3 du da 1ª assinatura ao "De acordo" |
| M-FIS-03 | Ofício no dia útil seguinte ao "De acordo", com prazo e unidade expressos | Estoque; encaminhamento não rastreável (t4) | R-FIS-05 a R-FIS-08, R-FIS-10 | B-fiscalizacao-14 | Teto de 3 / 1 / 0 du do "De acordo" ao ofício |
| M-FIS-04 | Análise das respostas por ofício, sem esperar o parecer anual | Restrição secundária (t5) | R-FIS-09 a R-FIS-11, R-FIS-13 | B-fiscalizacao-14, B-fiscalizacao-07 | Teto de 60 / 40 / 25 du depois do prazo protegido |
| M-FIS-05 | Modelo de relatório com fundamento normativo e conferência de forma | Defeitos (t2, t3) | R-FIS-12, R-FIS-03 | B-fiscalizacao-12 | Qualitativo (I-FIS-09, I-FIS-10) |
| M-FIS-06 | Respostas da concessionária juntadas ao processo, com data de protocolo | Rastreabilidade (t5) | R-FIS-08, R-FIS-09, R-FIS-11 | B-FIS-03 | Qualitativo (I-FIS-11) |

### Fase 2 — estruturantes (rito, norma interna, padrão técnico)

| Id | Melhoria | Ataca | Requisitos | Benchmark | Efeito simulado |
|---|---|---|---|---|---|
| M-FIS-07 | Checklist e modelo por tipo de unidade, com gravidade e prazo-padrão | Gargalo t2; talento não aproveitado | R-FIS-09, R-FIS-12 | B-fiscalizacao-12, B-FIS-02, B-FIS-01 | Redução de 15% / 25% / 35% no tempo restante da vistoria → 1ª assinatura |
| M-FIS-08 | Análise contínua por relatório com prazo interno; parecer anual só de consolidação | Restrição secundária (t5) | R-FIS-09 a R-FIS-11, R-FIS-13 | B-fiscalizacao-14, B-FIS-04 | Teto de 40 / 20 / 12 du depois do prazo protegido |
| M-FIS-09 | Cronograma anual juntado e Aviso de Fiscalização com antecedência mínima | Defeito de rito (t1) | R-FIS-02, R-FIS-03, R-FIS-18 | B-fiscalizacao-02 | Qualitativo (I-FIS-13) |
| M-FIS-10 | Regra escrita de escalada para não conformidade não sanada | Consequência só no parecer anual | R-FIS-09, R-FIS-16 | B-fiscalizacao-07, B-fiscalizacao-11 | Qualitativo (I-FIS-12) |
| M-FIS-11 | Tese-padrão sobre o escopo, aprovada com a Procuradoria | Contestação e envio à Procuradoria (t7 a t9) | R-FIS-13 a R-FIS-15 | B-fiscalizacao-11 | Qualitativo (I-FIS-15) |

### Fase 3 — digitais e automação (com IA sob controle humano)

| Id | Melhoria | Controle humano (resumo) | Efeito simulado |
|---|---|---|---|
| M-FIS-12 | Painel de prazos com alertas sobre o SEI | Gerente decide cada alerta; regra de dias úteis conferida (Q-FIS-04) | Qualitativo: sustenta os tetos das fases 1 e 2 (sem contagem dupla) |
| M-FIS-13 | Ofício e e-mail gerados no "De acordo", conferência aprovado × oficiado | Gerente assina; lista conferida em 100% dos ofícios (Q-FIS-04) | Teto de 1 / 0 / 0 du do "De acordo" ao ofício e ao e-mail |
| M-FIS-14 | Formulário eletrônico de resposta por não conformidade e extração assistida | 100% dos campos extraídos conferidos; juízo sempre do analista (Q-FIS-02) | Teto de 30 / 15 / 8 du depois do prazo protegido |
| M-FIS-15 | Checklist digital em campo, minuta assistida do relatório e checagem de forma | Equipe revê 100% da minuta contra fotos e checklist; assinatura bloqueada com pendência (Q-FIS-01) | Redução de 10% / 20% / 30%, líquida da revisão |
| M-FIS-16 | Priorização das vistorias por risco | Gerente aprova o cronograma; cobertura legal fora do modelo (Q-FIS-03) | Qualitativo (efetividade) |
| M-FIS-17 | Painel público das não conformidades por unidade | CASAN valida 100% dos itens novos (Q-FIS-05) | Qualitativo (efetividade) |

## 7. Simulação

**Linha de base congelada** em `linha_base_FIS.json`, gerada por `scripts/simular_tobe_fis.py` a partir de
`casos_FIS.json` (carimbo sha-256 `577e10af35ddc978…`, conferido a cada execução; o resultado guarda o mesmo carimbo).
A fase 0 reproduz os fatos do AS-IS (portão do script). Cada relatório é refeito com os efeitos de cada fase, em três
cenários. O ciclo até o parecer protege, por relatório, o prazo do ofício lido como 30 du mais 5 du de margem (a
leitura mais longa, enquanto a Procuradoria não fixa a contagem): esse tempo nunca é reduzido (checagem
`prazo_protegido_preservado_em_todas_as_fases` = verdadeiro).

Mediana por relatório, em dias úteis, e ganho sobre a linha de base (`resultado_tobe_FIS.json`, ids
`tobe.f<fase>.<cenário>.<ciclo>.mediana_du` e `.ganho_mediana_pct`):

| Fase | Cenário | Vistoria → e-mail (n = 9) | Ganho | Vistoria → parecer (n = 21) | Ganho |
|---|---|---|---|---|---|
| Linha de base | — | 62 | — | 256 | — |
| 1 | conservador | 33 | 46,8% | 128 | 50% |
| 1 | esperado | 28 | 54,8% | 103 | 59,8% |
| 1 | otimista | 20 | 67,7% | 81 | 68,4% |
| 2 | conservador | 28,5 | 54% | 103,5 | 59,6% |
| 2 | esperado | 21,8 | 64,8% | 76,8 | 70% |
| 2 | otimista | 13,7 | 77,9% | 61,7 | 75,9% |
| 3 | conservador | 25,9 | 58,2% | 91 | 64,5% |
| 3 | esperado | 17 | 72,6% | 67 | 73,8% |
| 3 | otimista | 10,2 | 83,5% | 54,2 | 78,8% |

Vistoria → "De acordo" (n = 21), cenário esperado: de 50 du
na linha de base para 27, 20,8
e 17 du nas fases 1, 2 e 3 (lb.vistoria_aprovacao.mediana_du;
tobe.f1.esperado.vistoria_aprovacao.mediana_du; tobe.f2.esperado.vistoria_aprovacao.mediana_du;
tobe.f3.esperado.vistoria_aprovacao.mediana_du).

**R-FIS-04 aplicado a todos os relatórios** (contrafactual): de 54,5% para
100% no esperado e no otimista já na fase 1; no conservador fica em
54,5% em todas as fases (lb.R-FIS-04.pct; tobe.f1.esperado.R-FIS-04.pct;
tobe.f3.conservador.R-FIS-04.pct), porque o teto conservador da M-FIS-02 é de 10 du.

**Sensibilidade** (fase 3, esperado; quanto a mediana piora sem cada melhoria, `sensibilidade` no resultado):
sem M-FIS-01, +18 du no ciclo vistoria → e-mail e
+7,8 du no ciclo até o parecer (sens.M-FIS-01.vistoria_email_mediana_du;
sens.M-FIS-01.ate_parecer_mediana_du); sem M-FIS-07, +5 du e
+5 du; sem M-FIS-14, +5 du no ciclo até o
parecer (sens.M-FIS-07.vistoria_email_mediana_du; sens.M-FIS-07.ate_parecer_mediana_du;
sens.M-FIS-14.ate_parecer_mediana_du). M-FIS-03, M-FIS-04 e M-FIS-08 dão zero na fase 3 porque M-FIS-13 e M-FIS-14
baixam os mesmos tetos; na fase em que entram, são elas que produzem o ganho.

**Leitura crítica.**

- O ganho no ciclo vistoria → e-mail **depende sobretudo de uma melhoria** (M-FIS-01, meta interna da fase 1): é a
  primeira a validar com a CASAN. Ela só se sustenta se a decomposição do gargalo (texto pronto aguardando assinatura)
  se confirmar.
- O ganho no ciclo até o parecer vem da **mudança de rito** (análise por relatório em vez de parecer anual), não de
  produtividade; depende de capacidade da equipe, que não foi medida.
- No cenário esperado, os ganhos passam de 60% a partir da fase 2 nos dois ciclos e já perto disso na fase 1 no ciclo
  até o parecer (`leitura_critica` no resultado): pela regra da metodologia, pedem revisão do parâmetro e conversa com a
  unidade antes de virar meta.
- Com 9 relatórios no ciclo vistoria → e-mail, um relatório a mais ou a menos muda a mediana: percentuais são ordem de
  grandeza.
- Não há ganho simulado em horas nem em reais: horas não foram medidas no FIS.

## 8. Indicadores, metas e controles

Metas do cenário esperado, com origem conferível (`controles_FIS.json`); as do conservador estão no resultado.

| Id | Indicador | Linha de base | Fase 1 | Fase 2 | Fase 3 | Origem da meta |
|---|---|---|---|---|---|---|
| I-FIS-01 | Vistoria → 1ª assinatura (mediana, du) | 34 (casos.vistoria_1a_assinatura.mediana_du) | 25 | 18,8 | 15 | simulação |
| I-FIS-02 | Vistoria → e-mail (mediana, du) | 62 (casos.vistoria_email.mediana_du) | 28 | 21,8 | 17 | simulação |
| I-FIS-03 | Vistoria → "De acordo" (mediana, du) | 50 (casos.vistoria_aprovacao.mediana_du) | 27 | 20,8 | 17 | simulação |
| I-FIS-04 | "De acordo" em até 5 du da 1ª assinatura (%) | 100 no período de vigência; 54,5 no ano (lb.R-FIS-04.pct) | 100 | 100 | 100 | simulação; exigência legal R-FIS-04 |
| I-FIS-05 | Relatórios aprovados sem ofício no processo | 12 (casos.variante.sem_oficio_de_encaminhamento_nos_autos) | 0 | 0 | 0 | norma R-FIS-06 |
| I-FIS-06 | "De acordo" → ofício (mediana, du) | 1 (casos.aprovacao_oficio.mediana_du) | 1 | 1 | 0 | simulação |
| I-FIS-07 | Vistoria → análise da resposta (mediana, du) | 256 (lb.ate_parecer.mediana_du) | 103 | 76,8 | 67 | simulação; R-FIS-10 protegido |
| I-FIS-08 | Fim do prazo protegido → análise (mediana, du) | 162 (lb.componente.a6_agencia.mediana_du) | 40 | 20 | 15 | simulação; referência R-FIS-11 |
| I-FIS-09 | Relatórios com fundamento normativo (%) | 86,4 (conformidade_FIS.json) | 100 | 100 | 100 | norma R-FIS-12 |
| I-FIS-10 | Relatórios assinados com defeito de forma | 2 sem vistoria datada (casos.sem_vistoria_datada) | 0 sem vistoria datada | — | nenhum com pendência (proposto) | norma R-FIS-03; proposto (M-FIS-15) |
| I-FIS-11 | Ofícios com resposta juntada e datada (%) | 0 de 3 (conformidade_FIS.json, R-FIS-08) | 100 | 100 | 100 | norma R-FIS-08 |
| I-FIS-12 | Não conformidades com estado registrado e sanadas no prazo | 113 itens sem estado por item (contagem.nao_conformidades_total) | — | 100% com estado | medido e publicado | norma R-FIS-09; benchmark B-fiscalizacao-14 (teto) |
| I-FIS-13 | Cronograma e aviso de fiscalização | aviso com 1 du (of3.antecedencia_agendamento_du) | — | cronograma e 100% dos avisos com 48 h | 100% das estações vistoriadas | normas R-FIS-18, R-FIS-03 |
| I-FIS-14 | Assinaturas por relatório (mediana) | 4 (casos.assinaturas.mediana) | 3 papéis (proposto) | — | — | proposto (M-FIS-02) |
| I-FIS-15 | Envios à Procuradoria e prazo da manifestação | 118 dc do parecer ao envio (intervalo.parecer_procuradoria) | — | 15 dias, prorrogáveis | — | norma R-FIS-14 |

I-FIS-09 a I-FIS-12 são indicadores de qualidade e efetividade, ao lado dos de prazo: meta de prazo sozinha empurra o
relatório incompleto para a assinatura.

**Controles internos (C-FIS-01 a C-FIS-09), com responsável:** bloqueio da assinatura sem conferência de forma
(Gerência da CASAN; R-FIS-03, R-FIS-12); ofício só com prazo, unidade e lista conferida (Gerente; R-FIS-05 a
R-FIS-08); conferência semanal aprovado × oficiado (R-FIS-06); nenhuma conclusão de descumprimento antes do fim do
prazo concedido (R-FIS-07, R-FIS-10); revisão semanal da fila de prazos (Gerente; R-FIS-04, R-FIS-11, R-FIS-17);
escalada que proponha penalidade só por processo sancionatório com defesa prévia (R-FIS-16); cronograma e aviso
(R-FIS-02, R-FIS-18); envio à Procuradoria só depois do parecer e com questão nova (SECEX; R-FIS-13, R-FIS-14);
publicação só de item validado (R-FIS-09).

**Controles de qualidade da IA e das rotinas:** Q-FIS-01 (minuta do relatório: 100% das não conformidades conferidas
contra fotos e checklist), Q-FIS-02 (extração das respostas: 100% dos campos conferidos contra a página de origem),
Q-FIS-03 (modelo de risco: acerto comparado com vistorias escolhidas ao acaso), Q-FIS-04 (painel e ofício gerado),
Q-FIS-05 (painel público). Toda melhoria de fase 3 tem pelo menos um.

**Auditoria contínua:** A-FIS-01, A-FIS-02 e A-FIS-03 do programa de auditoria de `normas_FIS.json` passam a rodar
automaticamente; A-FIS-04 (fase jurídica) segue manual.

## 9. Prioridade de automação (resumo de `priorizacao_FIS.md`)

O documento de priorização, feito em paralelo, chega a quatro pontos:

- Pela régua da metodologia, o FIS fica como **"próxima onda"** contado por processo (nota conservadora de
  62, igual ao P06) e como **"reavaliar com dados"** contado por relatório (nota conservadora de
  72), porque o volume de relatórios por ano da agência não foi medido (`priorizacao_FIS.json`:
  nota_composta.conservadora_unidade_processo; nota_composta.conservadora_unidade_relatorio).
- **1ª onda proposta: controle de prazos e rastreabilidade** (data da vistoria, fila de assinatura, conferência
  aprovado × oficiado, prazo de resposta contado e alertado) — corresponde às melhorias M-FIS-12 e M-FIS-13 deste TO-BE
  e às fases 1 e 2 que as sustentam. Depois: checklist digital e redação assistida (M-FIS-07, M-FIS-15), acompanhamento
  das respostas (M-FIS-14) e dossiê para contestação.
- O retorno em horas (hipótese, com horas emprestadas do P06) não paga o FIS isolado com um só bloco; sobre a
  plataforma de outro tipo, paga-se no limite no esperado. O ganho de prazo deste TO-BE fica fora desse retorno.
- Decisão pedida à gestão: medir os relatórios de fiscalização programada por ano de todas as concessionárias.

## 10. Pendências de validação e PARADAS

**PARADAS humanas (nada aqui vira meta antes delas):**

1. **CASAN (dona do processo):** validar as melhorias de maior peso na sensibilidade — M-FIS-01 (meta interna), M-FIS-07
   (checklist por tipo de unidade) e M-FIS-14/M-FIS-08 (análise por relatório) — e todas as faixas, que são hipótese;
   confirmar a decomposição do gargalo (texto pronto aguardando assinatura) e a capacidade para analisar as respostas
   ao longo do ano.
2. **CASAN e área de planejamento:** aceitar ou ajustar as metas de `controles_FIS.json` e os destinatários dos alertas.
3. **Procuradoria:** unidade de contagem e termo inicial do prazo dos ofícios (R-FIS-08); aplicação do art. 27, III,
   do Regimento à análise das respostas (R-FIS-11); prazos-padrão por gravidade (R-FIS-09); exigência de motivação no
   relatório (R-FIS-12); regra de escalada e procedimento sancionatório (R-FIS-16); tese-padrão sobre o escopo
   (M-FIS-11); cronograma do art. 2º da Deliberação 4216/2021 (R-FIS-02).
4. **Controle interno:** aceitar os testes de auditoria contínua A-FIS-01 a A-FIS-03.
5. **Gestão e TI:** acesso de leitura aos andamentos do SEI para o painel (M-FIS-12); serviço de IA aprovado para as
   melhorias M-FIS-14 e M-FIS-15; decisão do Conselho-Diretor sobre o painel público (M-FIS-17).

**Perguntas de validação** (também em `modelo_tobe_FIS.json`):

1. Qual meta interna da vistoria à 1ª assinatura a CASAN aceita, e quanto do intervalo atual é texto pronto
   aguardando assinatura?
2. O que cada assinatura (Assistente, Assessor, Especialista) confere hoje? A cadeia elaborado / revisado / de acordo
   cobre o controle necessário?
3. A equipe tem capacidade para analisar as respostas por relatório ao longo do ano?
4. A concessionária pode ser obrigada a responder em formulário eletrônico por não conformidade?
5. Quem decide a vistoria de retorno e quando a pendência vira proposta de notificação de infração?
6. Onde estão os ofícios dos 12 relatórios sem encaminhamento
   nos autos (casos.variante.sem_oficio_de_encaminhamento_nos_autos), e as respostas da concessionária?
7. O prazo de resposta é em dias úteis ou corridos, contado do e-mail ou da leitura?
8. Há acesso de leitura aos andamentos do SEI para o painel?

**Limites que valem para tudo:** recorte dos autos (respostas, manifestação e reiteração fora do PDF); sem trilha de
andamentos do SEI (redação e fila não se separam por unidade); horas e custo não medidos; dias úteis pelo calendário
RJ (hipótese); a parte protegida do ciclo até o parecer é hipótese de leitura do prazo.

Arquivos: `melhorias_FIS.json`, `linha_base_FIS.json`, `resultado_tobe_FIS.json` (via `scripts/simular_tobe_fis.py`),
`modelo_tobe_FIS.json`, `bpmn_tobe/`, `controles_FIS.json`, `priorizacao_FIS.md`.
