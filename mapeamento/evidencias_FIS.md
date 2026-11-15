# Evidências — FIS Fiscalizações programadas 2024 da CASAN nas unidades da Águas do Rio – Bloco 1

Processo: SEI-480002/001314/2024 (AGENERSA/RJ). Tipo equivalente ao **P06 – Fiscalização técnica de campo** do
repositório `mapeamento-processos-sei`.

**Vários casos dentro de um processo.** Cada Relatório de Fiscalização é tratado como um caso do subprocesso
vistoria → relatório → revisão/assinaturas → "De acordo" do Gerente → ofício à concessionária → e-mail de envio, o
que permite mediana, mínimo e máximo entre casos (`casos.total`). A etapa seguinte (análise das respostas e parecer
anual) tem um só caso. Com poucos casos por variante, as medianas são ordem de grandeza, não padrão.

Fontes: fichas por documento (`fichas/fichas_parte1..6.json`), linha do tempo e fatos de `scripts/fatos_fis.py`
(`mapeamento/linha_do_tempo_FIS.json`, `mapeamento/fatos_FIS.json`) e casos de `scripts/casos_fis.py`
(`mapeamento/casos_FIS.json`, `casos_FIS.csv`). Todo número citado é o valor de um fato, indicado pelo id (prefixos
`casos.`, `lotes.`, `of<k>.`, `oficios.` em `casos_FIS.json`; os demais em `fatos_FIS.json`). Números de documento,
de relatório (RF), de ofício e de SEI são identificadores. Nomes de pessoas omitidos: usa-se a função. Dias úteis
pelo calendário RJ de `scripts/fatos_fis.py` (hipótese: pontos facultativos não conferidos).

## Gatilho e escopo

- **Gatilho normativo:** Deliberação AGENERSA 4216/2021 do Conselho-Diretor (recorte do Diário Oficial na página 1
  do PDF, sem SEI próprio), que determina processo regulatório específico por concessionária, com cronograma e
  vistorias anuais nas estações de tratamento. O Parecer CASAN 250/2025 declara que as fiscalizações atendem a essa
  deliberação.
- **Escopo anual × autos exportados:** o parecer lista `contagem.relatorios_citados_parecer` relatórios; o PDF traz
  `contagem.relatorios_no_pdf` documentos do tipo relatório, um deles (RF 227, doc 31) sem texto nem assinatura
  (`casos.variante.sem_texto_nem_assinatura_no_pdf`). Respostas da concessionária, a manifestação dela ao parecer e a
  reiteração da CASAN são citadas no despacho final (doc 34), mas não estão no PDF.

## Sequência de atividades observada

1. **Programar e agendar a vistoria** (CASAN → concessionária). Só um ofício de agendamento nos autos
   (`oficios.agendamento`): Ofício 757/2024 (doc 20), assinado pelo Gerente da Câmara de Saneamento e enviado por
   e-mail pela Assistente/CASAN, pede agendamento de vistoria técnica em unidades de Cambuci e Miracema em
   `of3.vistorias_agendadas_dias` dias seguidos. Antecedência entre o envio e a 1ª vistoria:
   `of3.antecedencia_agendamento_du` du. Cronograma anual não consta dos autos.
2. **Realizar a vistoria em campo** (equipe técnica da CASAN; ao menos parte dos relatórios identifica os representantes
   da concessionária presentes). Data da vistoria vem da ficha; relatórios sem data de vistoria:
   `casos.sem_vistoria_datada`.
3. **Redigir o relatório de fiscalização** (Especialistas em Regulação, Engenheiros ou Assistentes da CASAN). Modelo
   padronizado: identificação, descrição dos fatos com fotos, não conformidades, recomendações e checklist. Vistoria
   até a 1ª assinatura: mediana `casos.vistoria_1a_assinatura.mediana_du` du (mín.
   `casos.vistoria_1a_assinatura.min_du`, máx. `casos.vistoria_1a_assinatura.max_du`; n
   `casos.vistoria_1a_assinatura.n`). Esse intervalo mistura redação e fila — não se separa sem andamentos do SEI. A
   data escrita no relatório fica perto da 1ª assinatura (`casos.redacao_1a_assinatura.mediana_du` du de mediana), o
   que sugere que o texto é datado quando fica pronto, não no dia da vistoria.
4. **Revisar e colher assinaturas** (elaboradores, Assistente e/ou Assessor da CASAN). Mediana de
   `casos.assinaturas.mediana` assinaturas por relatório (máx. `casos.assinaturas.max`), em
   `casos.dias_com_assinatura.mediana` dias distintos (máx. `casos.dias_com_assinatura.max`). Há
   `casos.cadeias_distintas` cadeias diferentes de cargos signatários (tabela gerada abaixo): a ordem
   elaboração → revisão → aprovação não é fixa.
5. **Aprovar ("De acordo") o relatório** (Gerente da Câmara de Saneamento). 1ª assinatura até o "De acordo": mediana
   `casos.revisao_aprovacao.mediana_du` du (máx. `casos.revisao_aprovacao.max_du`); só a espera pela assinatura do
   Gerente após a última assinatura técnica: mediana `casos.ultima_tecnica_aprovacao.mediana_du` du (máx.
   `casos.ultima_tecnica_aprovacao.max_du`). A aprovação é feita **em lote**: `lotes.aprovacao.n` dias de
   "De acordo", com mediana de `lotes.aprovacao.tamanho_mediana` relatórios por lote (máx.
   `lotes.aprovacao.tamanho_max`).
6. **Oficiar a concessionária** (Gerente da Câmara de Saneamento). Ofício de encaminhamento lista vários relatórios
   (`oficios.encaminhamento` ofícios nos autos) e pede manifestação sobre as recomendações em prazo único
   (`oficios.prazo_resposta_unico` dias, sem dizer se úteis ou corridos). "De acordo" até o ofício: mediana
   `casos.aprovacao_oficio.mediana_du` du (máx. `casos.aprovacao_oficio.max_du`; n `casos.aprovacao_oficio.n`).
7. **Enviar por e-mail pelo SEI** (Assistente/CASAN, remetente "não responda" do SEI, para a área regulatória da
   concessionária). Ofício até o e-mail: mediana `casos.oficio_email.mediana_du` du (máx.
   `casos.oficio_email.max_du`). Ciclo completo vistoria → e-mail: mediana `casos.vistoria_email.mediana_du` du
   (mín. `casos.vistoria_email.min_du`, máx. `casos.vistoria_email.max_du`; n `casos.vistoria_email.n`).
8. **Aguardar e receber a manifestação da concessionária** (terceiro). Respostas fora dos autos: tempo de terceiros
   **indeterminado** (não se separa de processo parado).
9. **Analisar as providências e emitir parecer consolidado anual** (Especialista em Regulação elabora, Gerente da
   Câmara Técnica de Saneamento dá "De acordo"): Parecer CASAN 250/2025 (doc 32), que conclui pelo atendimento
   parcial. Do último ofício ao parecer: `intervalo.ultimo_oficio_parecer_du` du (`intervalo.ultimo_oficio_parecer`
   dc).
10. **Encaminhar à SECEX** (Assistente da CASAN, doc 33, no mesmo dia do parecer — `marco.parecer`).
11. **(fora dos autos)** Concessionária se manifesta sobre o parecer, contesta o escopo da fiscalização e pede
    arquivamento; a CASAN reitera o parecer (relato do doc 34).
12. **Encaminhar à Procuradoria** (Assessora da SECEX, doc 34) para analisar os fundamentos jurídicos da
    fiscalização. Parecer até esse envio: `intervalo.parecer_procuradoria` dc; primeira assinatura de relatório até a
    última peça: `intervalo.total_aberto` dc. Processo aberto.

## Atores e unidades (siglas do processo)

| Ator / unidade | Papel observado | Documentos (n da linha do tempo) |
|---|---|---|
| Conselho-Diretor da AGENERSA | deliberação que determina as vistorias anuais (gatilho) | recorte na página 1 |
| CASAN (Câmara Técnica de Saneamento) — Especialistas em Regulação, Engenheiros | vistoria, redação e assinatura dos relatórios; elaboração do parecer anual | 1–3, 6–13, 16–19, 22–28, 31, 32 |
| CASAN — Assistente | assinatura de relatórios (elaboração ou revisão), envio dos e-mails, despacho à SECEX | relatórios acima; 5, 15, 21, 30, 33 |
| CASAN — Assessor | assinatura intermediária dos relatórios a partir do 2º lote | 6–13, 16–19, 22–28 |
| CASAN — Gerente da Câmara de Saneamento | "De acordo" dos relatórios e do parecer; assina todos os ofícios | todos os relatórios assinados; 4, 14, 20, 29, 32 |
| SECEX — Assessora | encaminha à Procuradoria após a reiteração do parecer | 34 |
| Procuradoria | destinatária final (análise jurídica dos fundamentos) | — (sem peça nos autos) |
| Concessionária Águas do Rio – Bloco 1 (Diretor Presidente; área regulatória) | acompanha a vistoria; destinatária dos ofícios; manifestações fora dos autos | — |

## Evidências por etapa

| Etapa | Unidade / função | Documentos (n — SEI) | Fatos | Observações |
|---|---|---|---|---|
| Agendar vistoria | CASAN / Gerente; Assistente | 20 — 82718456 (Ofício 757/2024); 21 — 82834832 (e-mail) | `of3.antecedencia_agendamento_du`, `of3.texto_assinatura_dc` | Ofício datado no texto antes da assinatura; enviado "para conhecimento", sem prazo. |
| Vistoria + relatório | CASAN / Especialistas em Regulação, Engenheiros, Assistentes | 1–3, 6–13, 16–19, 22–28 (SEI na tabela gerada) | `casos.vistoria_1a_assinatura.*`, `casos.redacao_1a_assinatura.*`, `casos.nao_conformidades.*` | Não conformidades por relatório nas fichas; `casos.nao_conformidades.sem_nc` relatórios sem nenhuma (obra de reforma). |
| Revisão / assinaturas | CASAN / Assistente, Assessor | mesmos | `casos.assinaturas.*`, `casos.dias_com_assinatura.*`, `casos.cadeias_distintas` | Assessor só aparece a partir do lote de RF 052–059. |
| "De acordo" | CASAN / Gerente | mesmos | `casos.revisao_aprovacao.*`, `casos.ultima_tecnica_aprovacao.*`, `lotes.aprovacao.*` | Maiores esperas nos lotes RF 010–012 e RF 155–158. |
| Ofício de encaminhamento | CASAN / Gerente | 4 — 74141761 (Ofício 349/2024); 14 — 80501066 (Ofício 682/2024); 29 — 87188346 (Ofício 946/2024) | `of1.*`, `of2.*`, `of4.*`, `casos.aprovacao_oficio.*`, `oficios.prazo_resposta_unico` | Ofícios 349 e 682 citam relatórios ausentes do PDF (`of1.relatorios_citados` × `of1.relatorios_no_pdf`; `of2.relatorios_citados` × `of2.relatorios_no_pdf`). |
| E-mail de envio | CASAN / Assistente | 5 — 74179603; 15 — 80626379; 30 — 87308946 | `casos.oficio_email.*`, `oficio1.envio_email_dc`, `oficio2.envio_email_dc`, `oficio4.envio_email_dc` | Envio pelo próprio SEI. |
| Resposta da concessionária | Concessionária | — | — | Fora dos autos; tempo indeterminado. |
| Parecer consolidado | CASAN / Especialista em Regulação; Gerente | 32 — 104033188 (Parecer 250/2025) | `marco.parecer`, `intervalo.ultimo_oficio_parecer_du` | Um parecer para o ano inteiro, não por relatório. |
| Encaminhar à SECEX | CASAN / Assistente | 33 — 104117825 | `marco.parecer` | Mesmo dia do parecer. |
| Encaminhar à Procuradoria | SECEX / Assessora | 34 — 117907053 | `marco.despacho_procuradoria`, `intervalo.parecer_procuradoria` | Menciona manifestação da concessionária e reiteração da CASAN não juntadas ao PDF. |

## Decisões e variantes observadas

- **Lote ou relatório isolado.** Relatórios são aprovados e oficiados em lote (`lotes.aprovacao.*`); os lotes
  de RF 159 e de RF 153 têm um só relatório (lista em `lotes_aprovacao` de `casos_FIS.json`). Decisão implícita: quando juntar relatórios suficientes para um ofício.
- **Com ofício nos autos × sem ofício nos autos.** `casos.variante.com_oficio_de_encaminhamento_nos_autos` relatórios
  aparecem citados num ofício dos autos; `casos.variante.sem_oficio_de_encaminhamento_nos_autos` não (RF 052, 056,
  059, 065, 070, 073, 090, 153, 155–158), embora constem da lista do parecer anual. Ou o encaminhamento ocorreu em
  peça não exportada, ou não ocorreu. Os RF 155–158 receberam o "De acordo" depois do Ofício 682.
- **Relatório com ou sem prazo para sanar.** `casos.com_prazo_para_sanar` relatórios fixam prazo no próprio texto
  (ficha); os demais deixam o prazo só para o ofício.
- **Ofício de encaminhamento × ofício de agendamento** (`oficios.encaminhamento`, `oficios.agendamento`).
- **Cadeia de assinaturas variável** (`casos.cadeias_distintas`): o elaborador pode ser Especialista, Engenheiro ou
  Assistente; Assessor e Assistente aparecem em posições diferentes.
- **Desfecho da análise anual:** atendimento parcial → manifestação da concessionária → reiteração da CASAN →
  Procuradoria. Não há, nos autos, notificação sancionatória nem relatoria no Conselho-Diretor.

## Sinais de retrabalho, espera e erro (das fichas e dos casos)

- **Relatório muito defasado da vistoria:** RF 017 (ETE São Gonçalo, doc 28) é o máximo de
  `casos.vistoria_1a_assinatura.max_du` — vistoria no início do ano, assinatura no lote de novembro.
- **Possível duplicidade:** RF 209 e RF 259 (docs 23 e 24) têm a mesma instalação (EEE Parafuso, obra de reforma) e a
  mesma data de vistoria.
- **Data no texto diferente da assinatura nos ofícios** (`of3.texto_assinatura_dc`, `of4.texto_assinatura_dc`).
- **Numeração de relatórios fora da ordem das vistorias** (ex.: RF 017 assinado com os RF 2xx) e relatório com
  número em formato diferente no parecer (RF 065 sem ano).
- **Reiteração de não conformidades** entre relatórios de unidades parecidas (fichas de RF 010–012: falta de
  identificação e de motobomba reserva).
- **Relatório sem texto no PDF** (RF 227, doc 31): só cabeçalho/rodapé por página.
- **Número do relatório não detectado no texto** em 5 documentos (docs 1, 2, 8, 9 e 12): em `fatos_FIS.json` os
  fatos por relatório deles usam o nº SEI no id (`relSEI<nº SEI>.*`, corrigido em 14/11/2026; antes saíam ids
  repetidos). Este documento cita os ids por caso de `casos_FIS.json`, que usa o número da ficha.

## Comparação qualitativa com a coorte P06 do repositório

Base: `mapeamento-processos-sei/saida/bpmn/evidencias_P06.md` (participação das unidades, transições e casos típico e
crítico da AGENERSA). Comparação só de forma; os números do P06 ficam naquele arquivo.

- **Unidade técnica.** No P06 a fiscalização de campo é feita, na maioria dos processos, pela CAENE (energia); a
  CASAN aparece numa minoria. O FIS é inteiramente da CASAN até o parecer anual — é um exemplo do ramo de saneamento
  pouco representado na coorte.
- **Granularidade.** No P06 cada processo tende a ter um relatório (às vezes com termo de notificação) e segue, em boa
  parte, para relatoria e deliberação; no FIS um processo anual reúne `contagem.relatorios_citados_parecer`
  relatórios, cada um com seu mini-ciclo, e um único parecer
  consolidado no fim. Os tempos do FIS são, portanto, por relatório (casos) e não por processo.
- **Caminho depois do relatório.** P06: relatório → SCEXEC → PROC → relator (CONS-xx) → razões finais → voto e
  deliberação. FIS: relatório → ofício com prazo à concessionária → parecer de atendimento → SECEX → Procuradoria;
  ainda não houve relatoria nem deliberação. O trecho final (secretaria → Procuradoria) coincide com o início do
  caminho sancionatório do P06.
- **Onde está a espera.** No P06 as esperas dominantes estão nas filas entre unidades (secretaria, Procuradoria,
  relatoria), medidas pela posse. No FIS, dentro da CASAN, o maior trecho é vistoria → 1ª assinatura
  (`casos.vistoria_1a_assinatura.mediana_du`) frente a revisão (`casos.revisao_aprovacao.mediana_du`) e
  encaminhamento (`casos.aprovacao_oficio.mediana_du`); fora dela, o trecho mais longo é último ofício → parecer
  (`intervalo.ultimo_oficio_parecer_du`). Sem andamentos do SEI, não é possível repartir por posse como no P06.
- **Comunicação.** Nos dois, o ofício à concessionária vai por e-mail do SEI; no P06 aparece também diligência a
  terceiros (Corpo de Bombeiros, INEA), ausente no FIS.
- **Siglas.** O despacho do FIS usa "SECEX"; a trilha do P06 usa "SCEXEC". Provavelmente a mesma Secretaria
  Executiva (a validar).

## Perguntas a validar (com a CASAN, a SECEX e a Procuradoria)

1. Onde estão os ofícios de encaminhamento dos RF 052, 056, 059, 065, 070, 073, 090, 153 e 155–158, e os relatórios
   citados nos Ofícios 349 e 682 que não estão no PDF? Há outro processo ou documento restrito?
2. Entre a vistoria e a 1ª assinatura, quanto é redação e quanto é fila? Há meta interna de prazo para o relatório?
3. Qual o papel de cada assinatura (Assistente, Assessor): revisão técnica, revisão formal ou ciência? Existe ordem
   prevista "elaborado / revisado / de acordo"?
4. Qual o critério para fechar um lote de aprovação e de ofício (número de relatórios, mês, campanha)?
5. O prazo de resposta do ofício é em dias corridos ou úteis? Por que alguns relatórios fixam prazo e outros não?
6. As respostas da concessionária são analisadas relatório a relatório ou só no parecer anual? Onde são juntadas?
7. Existe cronograma anual de vistorias (exigido pela Deliberação 4216/2021)? Qual antecedência mínima de aviso à
   concessionária? O Ofício 757 trata de municípios do Bloco 1?
8. Por que o RF 017 foi assinado tantos meses depois da vistoria? Os RF 209 e 259 são duplicados ou etapas da obra?
9. O RF 227 tem texto no SEI original (o PDF só traz imagem)?
10. SECEX e SCEXEC são a mesma unidade? O que se espera da Procuradoria: parecer sobre o escopo da fiscalização ou
    início de processo sancionatório (caminho do P06)?
11. Os pontos facultativos do RJ em 2024–2025 alteram os dias úteis calculados?

## Tabelas geradas pelos scripts

<!-- inicio:casos_fis -->
<!-- gerado por scripts/casos_fis.py a partir de mapeamento/casos_FIS.json; não editar à mão -->

### Casos (um por relatório)

| caso | doc | instalação | variante | vistoria | 1ª assin. | De acordo | ofício (nº) | e-mail | assin. | NC |
|---|---|---|---|---|---|---|---|---|---|---|
| RF010 | 1 | EEAT Praça Paris - Glória (estação elevatória de água) | com ofício de encaminhamento nos autos | 2024-01-18 | 2024-03-07 | 2024-04-29 | 2024-05-08 (349) | 2024-05-08 | 6 | 5 |
| RF011 | 2 | Estação Elevatória de Água Tratada Barão de Guaratiba (EEAT Barão de Guaratiba) | com ofício de encaminhamento nos autos | 2024-01-18 | 2024-03-07 | 2024-04-29 | 2024-05-08 (349) | 2024-05-08 | 6 | 2 |
| RF012 | 3 | EEAT Cisterna do Aterro (estação elevatória de água) | com ofício de encaminhamento nos autos | — | 2024-03-07 | 2024-04-29 | 2024-05-08 (349) | 2024-05-08 | 6 | 4 |
| RF056 | 6 | EEE 34 - Cantagalo (Estação Elevatória de Esgoto Cantagalo) | sem ofício de encaminhamento nos autos | 2024-04-04 | 2024-05-10 | 2024-05-24 | — | — | 4 | 9 |
| RF052 | 7 | EEE São Conrado (EEE49) | sem ofício de encaminhamento nos autos | 2024-04-02 | 2024-05-10 | 2024-05-24 | — | — | 5 | 4 |
| RF059 | 8 | EEE 30 - Captação em Tempo Seco Cantagalo | sem ofício de encaminhamento nos autos | 2024-04-04 | 2024-05-10 | 2024-05-24 | — | — | 4 | 6 |
| RF070 | 9 | EEE Aquarela do Brasil (EEE 96) | sem ofício de encaminhamento nos autos | 2024-04-02 | 2024-06-04 | 2024-06-10 | — | — | 5 | 6 |
| RF073 | 10 | EEE Parafuso | sem ofício de encaminhamento nos autos | 2024-04-10 | 2024-06-03 | 2024-06-10 | — | — | 5 | 6 |
| RF065 | 11 | EEE Leblon (EEE 51) | sem ofício de encaminhamento nos autos | 2024-04-16 | 2024-06-06 | 2024-06-10 | — | — | 5 | 8 |
| RF090 | 12 | EEE 16 / André Azevedo (Hipica) | sem ofício de encaminhamento nos autos | 2024-04-10 | 2024-06-06 | 2024-06-10 | — | — | 5 | 4 |
| RF159 | 13 | EEAT Ojuara | com ofício de encaminhamento nos autos | 2024-06-26 | 2024-08-02 | 2024-08-06 | 2024-08-07 (682) | 2024-08-08 | 5 | 3 |
| RF155 | 16 | EEAT 791 - Canal | sem ofício de encaminhamento nos autos | 2024-07-16 | 2024-08-09 | 2024-09-24 | — | — | 4 | 9 |
| RF156 | 17 | EEAT 790 - Mageense | sem ofício de encaminhamento nos autos | 2024-07-16 | 2024-08-09 | 2024-09-24 | — | — | 4 | 6 |
| RF157 | 18 | EEAT 792 - Presídio I | sem ofício de encaminhamento nos autos | 2024-07-16 | 2024-08-09 | 2024-09-24 | — | — | 4 | 6 |
| RF158 | 19 | EEAT 794 - Meu Boi | sem ofício de encaminhamento nos autos | 2024-07-16 | 2024-08-09 | 2024-09-24 | — | — | 4 | 9 |
| RF153 | 22 | ETA Magé (Sistema Roncador) | sem ofício de encaminhamento nos autos | 2024-07-16 | 2024-09-11 | 2024-09-17 | — | — | 4 | 2 |
| RF259 | 23 | EEE Parafuso (obra de reforma) | com ofício de encaminhamento nos autos | 2024-08-14 | 2024-11-06 | 2024-11-08 | 2024-11-11 (946) | 2024-11-11 | 3 | 0 |
| RF209 | 24 | EEE Parafuso (obra de reforma) | com ofício de encaminhamento nos autos | 2024-08-14 | 2024-11-06 | 2024-11-08 | 2024-11-11 (946) | 2024-11-11 | 3 | 0 |
| RF212 | 25 | EEE Mário Quintão | com ofício de encaminhamento nos autos | 2024-08-20 | 2024-11-06 | 2024-11-08 | 2024-11-11 (946) | 2024-11-11 | 3 | 5 |
| RF213 | 26 | EEE Frederico Marques | com ofício de encaminhamento nos autos | 2024-08-20 | 2024-11-06 | 2024-11-08 | 2024-11-11 (946) | 2024-11-11 | 3 | 5 |
| RF214 | 27 | EEE Piscinão | com ofício de encaminhamento nos autos | 2024-08-20 | 2024-11-06 | 2024-11-08 | 2024-11-11 (946) | 2024-11-11 | 3 | 3 |
| RF017 | 28 | ETE São Gonçalo | com ofício de encaminhamento nos autos | 2024-03-06 | 2024-11-07 | 2024-11-08 | 2024-11-11 (946) | 2024-11-11 | 3 | 11 |
| RF227 | 31 |  | sem texto nem assinatura no PDF | — | — | — | — | — | 0 | 0 |

### Intervalos entre casos (fatos `casos.<intervalo>.<estatística>_<dc|du>`)

| intervalo (id) | n | mediana dc | mín dc | máx dc | mediana du | mín du | máx du |
|---|---|---|---|---|---|---|---|
| Vistoria até a 1ª assinatura do relatório (redação + espera) (`vistoria_1a_assinatura`) | 21 | 51 | 24 | 246 | 34 | 18 | 171 |
| Data escrita no relatório até a 1ª assinatura (`redacao_1a_assinatura`) | 22 | 1.0 | 0 | 13 | 1.0 | 0 | 8 |
| 1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas) (`revisao_aprovacao`) | 22 | 6.5 | 1 | 53 | 4.5 | 1 | 35 |
| Última assinatura antes do Gerente até o 'De acordo' (`ultima_tecnica_aprovacao`) | 22 | 4.0 | 0 | 28 | 2.0 | 0 | 20 |
| Vistoria até o 'De acordo' do Gerente (`vistoria_aprovacao`) | 21 | 70 | 41 | 247 | 50 | 29 | 172 |
| 'De acordo' até a assinatura do ofício de encaminhamento (`aprovacao_oficio`) | 10 | 3.0 | 1 | 9 | 1.0 | 1 | 6 |
| Assinatura do ofício até o envio do e-mail pelo SEI (`oficio_email`) | 10 | 0.0 | 0 | 1 | 0.0 | 0 | 1 |
| Vistoria até o envio à concessionária (ciclo completo) (`vistoria_email`) | 9 | 89 | 43 | 250 | 62 | 31 | 173 |

### Ofícios

| doc | ofício | finalidade | data no texto | assinatura | e-mail | relatórios citados | prazo (dias) |
|---|---|---|---|---|---|---|---|
| 4 | 349/2024 | encaminhar relatórios | 2024-05-08 | 2024-05-08 | 2024-05-08 | 10, 11, 12, 33, 34, 38, 46, 47, 48, 53, 54, 55 | 30 |
| 14 | 682/2024 | encaminhar relatórios | 2024-08-07 | 2024-08-07 | 2024-08-08 | 111, 123, 134, 135, 159 | 30 |
| 20 | 757/2024 | agendar vistoria | 2024-09-06 | 2024-09-09 | 2024-09-09 | — | — |
| 29 | 946/2024 | encaminhar relatórios | 2024-11-08 | 2024-11-11 | 2024-11-11 | 17, 209, 212, 213, 214, 259 | 30 |

### Cadeias de assinatura (cargos, na ordem)

| cadeia | relatórios |
|---|---|
| Assistente → Assessor → Gerente | 6 |
| Especialista em Regulação → Assessor → Gerente | 5 |
| Especialista em Regulação → Assessor → Especialista em Regulação → Gerente | 4 |
| Especialista em Regulação → Assistente → Gerente | 3 |
| Especialista em Regulação → Assistente → Assessor → Gerente | 1 |
| Assessor → Especialista em Regulação → Assistente → Especialista em Regulação → Gerente | 1 |
| Especialista em Regulação → Assistente → Assessor → Especialista em Regulação → Gerente | 1 |
| Assistente → Assessor → Assistente → Gerente | 1 |

### Fatos dos casos

| id | descrição | valor | unidade | definição |
|---|---|---|---|---|
| `casos.vistoria_1a_assinatura.mediana_dc` | Vistoria até a 1ª assinatura do relatório (redação + espera) — mediana entre casos | 51 | dc | vistoria → assinatura_1; 21 relatórios com os dois marcos |
| `casos.vistoria_1a_assinatura.min_dc` | Vistoria até a 1ª assinatura do relatório (redação + espera) — min entre casos | 24 | dc | vistoria → assinatura_1; 21 relatórios com os dois marcos |
| `casos.vistoria_1a_assinatura.max_dc` | Vistoria até a 1ª assinatura do relatório (redação + espera) — max entre casos | 246 | dc | vistoria → assinatura_1; 21 relatórios com os dois marcos |
| `casos.vistoria_1a_assinatura.n` | Vistoria até a 1ª assinatura do relatório (redação + espera) — relatórios com os dois marcos | 21 | relatórios | vistoria e assinatura_1 datados |
| `casos.vistoria_1a_assinatura.mediana_du` | Vistoria até a 1ª assinatura do relatório (redação + espera) — mediana entre casos | 34 | du | vistoria → assinatura_1; 21 relatórios com os dois marcos |
| `casos.vistoria_1a_assinatura.min_du` | Vistoria até a 1ª assinatura do relatório (redação + espera) — min entre casos | 18 | du | vistoria → assinatura_1; 21 relatórios com os dois marcos |
| `casos.vistoria_1a_assinatura.max_du` | Vistoria até a 1ª assinatura do relatório (redação + espera) — max entre casos | 171 | du | vistoria → assinatura_1; 21 relatórios com os dois marcos |
| `casos.redacao_1a_assinatura.mediana_dc` | Data escrita no relatório até a 1ª assinatura — mediana entre casos | 1.0 | dc | data_texto → assinatura_1; 22 relatórios com os dois marcos |
| `casos.redacao_1a_assinatura.min_dc` | Data escrita no relatório até a 1ª assinatura — min entre casos | 0 | dc | data_texto → assinatura_1; 22 relatórios com os dois marcos |
| `casos.redacao_1a_assinatura.max_dc` | Data escrita no relatório até a 1ª assinatura — max entre casos | 13 | dc | data_texto → assinatura_1; 22 relatórios com os dois marcos |
| `casos.redacao_1a_assinatura.n` | Data escrita no relatório até a 1ª assinatura — relatórios com os dois marcos | 22 | relatórios | data_texto e assinatura_1 datados |
| `casos.redacao_1a_assinatura.mediana_du` | Data escrita no relatório até a 1ª assinatura — mediana entre casos | 1.0 | du | data_texto → assinatura_1; 22 relatórios com os dois marcos |
| `casos.redacao_1a_assinatura.min_du` | Data escrita no relatório até a 1ª assinatura — min entre casos | 0 | du | data_texto → assinatura_1; 22 relatórios com os dois marcos |
| `casos.redacao_1a_assinatura.max_du` | Data escrita no relatório até a 1ª assinatura — max entre casos | 8 | du | data_texto → assinatura_1; 22 relatórios com os dois marcos |
| `casos.revisao_aprovacao.mediana_dc` | 1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas) — mediana entre casos | 6.5 | dc | assinatura_1 → aprovacao; 22 relatórios com os dois marcos |
| `casos.revisao_aprovacao.min_dc` | 1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas) — min entre casos | 1 | dc | assinatura_1 → aprovacao; 22 relatórios com os dois marcos |
| `casos.revisao_aprovacao.max_dc` | 1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas) — max entre casos | 53 | dc | assinatura_1 → aprovacao; 22 relatórios com os dois marcos |
| `casos.revisao_aprovacao.n` | 1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas) — relatórios com os dois marcos | 22 | relatórios | assinatura_1 e aprovacao datados |
| `casos.revisao_aprovacao.mediana_du` | 1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas) — mediana entre casos | 4.5 | du | assinatura_1 → aprovacao; 22 relatórios com os dois marcos |
| `casos.revisao_aprovacao.min_du` | 1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas) — min entre casos | 1 | du | assinatura_1 → aprovacao; 22 relatórios com os dois marcos |
| `casos.revisao_aprovacao.max_du` | 1ª assinatura até o 'De acordo' do Gerente (revisão e assinaturas) — max entre casos | 35 | du | assinatura_1 → aprovacao; 22 relatórios com os dois marcos |
| `casos.ultima_tecnica_aprovacao.mediana_dc` | Última assinatura antes do Gerente até o 'De acordo' — mediana entre casos | 4.0 | dc | assinatura_pre_gerente → aprovacao; 22 relatórios com os dois marcos |
| `casos.ultima_tecnica_aprovacao.min_dc` | Última assinatura antes do Gerente até o 'De acordo' — min entre casos | 0 | dc | assinatura_pre_gerente → aprovacao; 22 relatórios com os dois marcos |
| `casos.ultima_tecnica_aprovacao.max_dc` | Última assinatura antes do Gerente até o 'De acordo' — max entre casos | 28 | dc | assinatura_pre_gerente → aprovacao; 22 relatórios com os dois marcos |
| `casos.ultima_tecnica_aprovacao.n` | Última assinatura antes do Gerente até o 'De acordo' — relatórios com os dois marcos | 22 | relatórios | assinatura_pre_gerente e aprovacao datados |
| `casos.ultima_tecnica_aprovacao.mediana_du` | Última assinatura antes do Gerente até o 'De acordo' — mediana entre casos | 2.0 | du | assinatura_pre_gerente → aprovacao; 22 relatórios com os dois marcos |
| `casos.ultima_tecnica_aprovacao.min_du` | Última assinatura antes do Gerente até o 'De acordo' — min entre casos | 0 | du | assinatura_pre_gerente → aprovacao; 22 relatórios com os dois marcos |
| `casos.ultima_tecnica_aprovacao.max_du` | Última assinatura antes do Gerente até o 'De acordo' — max entre casos | 20 | du | assinatura_pre_gerente → aprovacao; 22 relatórios com os dois marcos |
| `casos.vistoria_aprovacao.mediana_dc` | Vistoria até o 'De acordo' do Gerente — mediana entre casos | 70 | dc | vistoria → aprovacao; 21 relatórios com os dois marcos |
| `casos.vistoria_aprovacao.min_dc` | Vistoria até o 'De acordo' do Gerente — min entre casos | 41 | dc | vistoria → aprovacao; 21 relatórios com os dois marcos |
| `casos.vistoria_aprovacao.max_dc` | Vistoria até o 'De acordo' do Gerente — max entre casos | 247 | dc | vistoria → aprovacao; 21 relatórios com os dois marcos |
| `casos.vistoria_aprovacao.n` | Vistoria até o 'De acordo' do Gerente — relatórios com os dois marcos | 21 | relatórios | vistoria e aprovacao datados |
| `casos.vistoria_aprovacao.mediana_du` | Vistoria até o 'De acordo' do Gerente — mediana entre casos | 50 | du | vistoria → aprovacao; 21 relatórios com os dois marcos |
| `casos.vistoria_aprovacao.min_du` | Vistoria até o 'De acordo' do Gerente — min entre casos | 29 | du | vistoria → aprovacao; 21 relatórios com os dois marcos |
| `casos.vistoria_aprovacao.max_du` | Vistoria até o 'De acordo' do Gerente — max entre casos | 172 | du | vistoria → aprovacao; 21 relatórios com os dois marcos |
| `casos.aprovacao_oficio.mediana_dc` | 'De acordo' até a assinatura do ofício de encaminhamento — mediana entre casos | 3.0 | dc | aprovacao → oficio; 10 relatórios com os dois marcos |
| `casos.aprovacao_oficio.min_dc` | 'De acordo' até a assinatura do ofício de encaminhamento — min entre casos | 1 | dc | aprovacao → oficio; 10 relatórios com os dois marcos |
| `casos.aprovacao_oficio.max_dc` | 'De acordo' até a assinatura do ofício de encaminhamento — max entre casos | 9 | dc | aprovacao → oficio; 10 relatórios com os dois marcos |
| `casos.aprovacao_oficio.n` | 'De acordo' até a assinatura do ofício de encaminhamento — relatórios com os dois marcos | 10 | relatórios | aprovacao e oficio datados |
| `casos.aprovacao_oficio.mediana_du` | 'De acordo' até a assinatura do ofício de encaminhamento — mediana entre casos | 1.0 | du | aprovacao → oficio; 10 relatórios com os dois marcos |
| `casos.aprovacao_oficio.min_du` | 'De acordo' até a assinatura do ofício de encaminhamento — min entre casos | 1 | du | aprovacao → oficio; 10 relatórios com os dois marcos |
| `casos.aprovacao_oficio.max_du` | 'De acordo' até a assinatura do ofício de encaminhamento — max entre casos | 6 | du | aprovacao → oficio; 10 relatórios com os dois marcos |
| `casos.oficio_email.mediana_dc` | Assinatura do ofício até o envio do e-mail pelo SEI — mediana entre casos | 0.0 | dc | oficio → email; 10 relatórios com os dois marcos |
| `casos.oficio_email.min_dc` | Assinatura do ofício até o envio do e-mail pelo SEI — min entre casos | 0 | dc | oficio → email; 10 relatórios com os dois marcos |
| `casos.oficio_email.max_dc` | Assinatura do ofício até o envio do e-mail pelo SEI — max entre casos | 1 | dc | oficio → email; 10 relatórios com os dois marcos |
| `casos.oficio_email.n` | Assinatura do ofício até o envio do e-mail pelo SEI — relatórios com os dois marcos | 10 | relatórios | oficio e email datados |
| `casos.oficio_email.mediana_du` | Assinatura do ofício até o envio do e-mail pelo SEI — mediana entre casos | 0.0 | du | oficio → email; 10 relatórios com os dois marcos |
| `casos.oficio_email.min_du` | Assinatura do ofício até o envio do e-mail pelo SEI — min entre casos | 0 | du | oficio → email; 10 relatórios com os dois marcos |
| `casos.oficio_email.max_du` | Assinatura do ofício até o envio do e-mail pelo SEI — max entre casos | 1 | du | oficio → email; 10 relatórios com os dois marcos |
| `casos.vistoria_email.mediana_dc` | Vistoria até o envio à concessionária (ciclo completo) — mediana entre casos | 89 | dc | vistoria → email; 9 relatórios com os dois marcos |
| `casos.vistoria_email.min_dc` | Vistoria até o envio à concessionária (ciclo completo) — min entre casos | 43 | dc | vistoria → email; 9 relatórios com os dois marcos |
| `casos.vistoria_email.max_dc` | Vistoria até o envio à concessionária (ciclo completo) — max entre casos | 250 | dc | vistoria → email; 9 relatórios com os dois marcos |
| `casos.vistoria_email.n` | Vistoria até o envio à concessionária (ciclo completo) — relatórios com os dois marcos | 9 | relatórios | vistoria e email datados |
| `casos.vistoria_email.mediana_du` | Vistoria até o envio à concessionária (ciclo completo) — mediana entre casos | 62 | du | vistoria → email; 9 relatórios com os dois marcos |
| `casos.vistoria_email.min_du` | Vistoria até o envio à concessionária (ciclo completo) — min entre casos | 31 | du | vistoria → email; 9 relatórios com os dois marcos |
| `casos.vistoria_email.max_du` | Vistoria até o envio à concessionária (ciclo completo) — max entre casos | 173 | du | vistoria → email; 9 relatórios com os dois marcos |
| `casos.total` | Relatórios de fiscalização tratados como casos | 23 | relatórios | documentos do tipo Relatório de Fiscalização na linha do tempo |
| `casos.variante.com_oficio_de_encaminhamento_nos_autos` | Relatórios — com ofício de encaminhamento nos autos | 10 | relatórios |  |
| `casos.variante.sem_oficio_de_encaminhamento_nos_autos` | Relatórios — sem ofício de encaminhamento nos autos | 12 | relatórios |  |
| `casos.variante.sem_texto_nem_assinatura_no_pdf` | Relatórios — sem texto nem assinatura no PDF | 1 | relatórios |  |
| `casos.assinaturas.mediana` | Assinaturas eletrônicas por relatório — mediana | 4.0 | assinaturas | 22 relatórios assinados |
| `casos.assinaturas.max` | Assinaturas eletrônicas por relatório — máximo | 6 | assinaturas |  |
| `casos.dias_com_assinatura.mediana` | Dias distintos com assinatura por relatório — mediana | 3.0 | dias | rodadas de assinatura |
| `casos.dias_com_assinatura.max` | Dias distintos com assinatura por relatório — máximo | 4 | dias |  |
| `casos.cadeias_distintas` | Cadeias de cargos signatários distintas | 8 | cadeias | sequência de cargos na ordem das assinaturas, sem repetição consecutiva |
| `casos.sem_vistoria_datada` | Relatórios sem data de vistoria na ficha | 2 | relatórios |  |
| `casos.com_prazo_para_sanar` | Relatórios que fixam prazo para sanar (ficha) | 10 | relatórios | fiscalizacao.prazo_para_sanar |
| `casos.nao_conformidades.mediana` | Não conformidades por relatório — mediana | 5.0 | itens | 22 relatórios assinados (fichas) |
| `casos.nao_conformidades.max` | Não conformidades por relatório — máximo | 11 | itens |  |
| `casos.nao_conformidades.sem_nc` | Relatórios sem não conformidade listada | 2 | relatórios |  |
| `lotes.aprovacao.n` | Dias distintos de 'De acordo' do Gerente (lotes de aprovação) | 7 | lotes | relatórios aprovados no mesmo dia formam um lote |
| `lotes.aprovacao.tamanho_mediana` | Relatórios por lote de aprovação — mediana | 3 | relatórios |  |
| `lotes.aprovacao.tamanho_max` | Relatórios por lote de aprovação — máximo | 6 | relatórios |  |
| `of1.finalidade_encaminhar` | Ofício 349/2024: encaminha relatórios (1) ou agenda vistoria (0) | 1 | indicador | relatórios citados no texto |
| `of1.relatorios_citados` | Ofício 349/2024: relatórios citados | 12 | relatórios |  |
| `of1.relatorios_no_pdf` | Ofício 349/2024: relatórios citados com texto no PDF | 3 | relatórios |  |
| `of1.texto_assinatura_dc` | Ofício 349/2024: data escrita até a assinatura | 0 | dc | data da assinatura − data do cabeçalho |
| `of1.texto_assinatura_du` | Ofício 349/2024: data escrita até a assinatura (du) | 0 | du | calendário RJ (hipótese) |
| `of2.finalidade_encaminhar` | Ofício 682/2024: encaminha relatórios (1) ou agenda vistoria (0) | 1 | indicador | relatórios citados no texto |
| `of2.relatorios_citados` | Ofício 682/2024: relatórios citados | 5 | relatórios |  |
| `of2.relatorios_no_pdf` | Ofício 682/2024: relatórios citados com texto no PDF | 1 | relatórios |  |
| `of2.texto_assinatura_dc` | Ofício 682/2024: data escrita até a assinatura | 0 | dc | data da assinatura − data do cabeçalho |
| `of2.texto_assinatura_du` | Ofício 682/2024: data escrita até a assinatura (du) | 0 | du | calendário RJ (hipótese) |
| `of3.finalidade_encaminhar` | Ofício 757/2024: encaminha relatórios (1) ou agenda vistoria (0) | 0 | indicador | relatórios citados no texto |
| `of3.texto_assinatura_dc` | Ofício 757/2024: data escrita até a assinatura | 3 | dc | data da assinatura − data do cabeçalho |
| `of3.texto_assinatura_du` | Ofício 757/2024: data escrita até a assinatura (du) | 1 | du | calendário RJ (hipótese) |
| `of3.vistorias_agendadas_dias` | Ofício 757/2024: dias de vistoria agendados | 3 | dias | trecho 'Datas das Vistorias' |
| `of3.antecedencia_agendamento_dc` | Ofício 757/2024: envio do e-mail até a 1ª vistoria agendada | 1 | dc | 1ª data agendada − data do e-mail |
| `of3.antecedencia_agendamento_du` | Ofício 757/2024: envio do e-mail até a 1ª vistoria agendada (du) | 1 | du | calendário RJ (hipótese) |
| `of4.finalidade_encaminhar` | Ofício 946/2024: encaminha relatórios (1) ou agenda vistoria (0) | 1 | indicador | relatórios citados no texto |
| `of4.relatorios_citados` | Ofício 946/2024: relatórios citados | 6 | relatórios |  |
| `of4.relatorios_no_pdf` | Ofício 946/2024: relatórios citados com texto no PDF | 6 | relatórios |  |
| `of4.texto_assinatura_dc` | Ofício 946/2024: data escrita até a assinatura | 3 | dc | data da assinatura − data do cabeçalho |
| `of4.texto_assinatura_du` | Ofício 946/2024: data escrita até a assinatura (du) | 1 | du | calendário RJ (hipótese) |
| `oficios.encaminhamento` | Ofícios de encaminhamento de relatórios nos autos | 3 | ofícios |  |
| `oficios.agendamento` | Ofícios de agendamento de vistoria nos autos | 1 | ofícios |  |
| `oficios.prazo_resposta_unico` | Prazo de resposta dado em todos os ofícios de encaminhamento | 30 | dias | trecho 'prazo de N (...) dias'; não diz se úteis ou corridos |
<!-- fim:casos_fis -->
