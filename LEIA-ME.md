# Mapeamento: Fiscalizações Programadas 2024 — Águas do Rio Bloco 1 (SEI-480002/001314/2024, AGENERSA/RJ)

Aplicação da metodologia do curso (repositório `mapeamento-processos-sei`, clonado em `../../mapeamento-processos-sei`)
a um único processo SEI da AGENERSA/RJ, indicado como exemplo por um colega: as fiscalizações programadas de 2024
da Câmara Técnica de Saneamento (CASAN) nas unidades da concessionária Águas do Rio – Bloco 1 (estações
elevatórias de água e esgoto, ETAs e ETEs), até o envio à Procuradoria em 03/11/2025. Código nos artefatos: **FIS**.

O processo é do mesmo tipo que o **P06 – Fiscalização técnica de campo** do repositório (mesma agência), o que
permite comparar o caso com a coorte P06 em todas as etapas.

Fonte: o PDF exportado do SEI (233 páginas, 34 documentos). `texto/` contém nomes e e-mails de pessoas e **não vai
para o git** (`.gitignore`). Para refazer, extraia de novo o texto do PDF (PyMuPDF, uma marca `===== PÁGINA N =====`
por página) em `texto/processo_completo.txt`.

## Pastas, na ordem do trabalho

| Pasta | O que tem | Etapa do método |
|---|---|---|
| `texto/` | Texto integral extraído do PDF, índice dos 34 documentos e o texto dividido em 6 partes | Coleta (adaptada: PDF no lugar da Pesquisa Pública) |
| `fichas/` | Uma ficha por documento: data, unidade, função, ação, instalação fiscalizada, não conformidades, prazos e normas em trecho literal | Conteúdo e esforço (fase 1) |
| `scripts/` | `fatos_fis.py` (linha do tempo e intervalos), `casos_fis.py` (um caso por relatório), `conformidade_fis.py`, `verificar_trechos_fis.py`, `validar_avaliacao_fis.py`, `simular_tobe_fis.py`, `priorizacao_fis.py` | Etapas determinísticas |
| `mapeamento/` | `fatos_FIS.json`, `linha_do_tempo_FIS.json`, `casos_FIS.*`, `evidencias_FIS.md`, `modelo_FIS.json` e `bpmn/` (AS-IS), `vinculos_FIS.json`, `avaliacao_FIS.json`, `normas_FIS.json`, `conformidade_FIS.*`, `benchmark_FIS.json` e `BENCHMARKING_FIS.md`, `melhorias_FIS.json`, `controles_FIS.json`, `modelo_tobe_FIS.json` e `bpmn_tobe/` (TO-BE), `priorizacao_FIS.md`, **`TOBE_FIS.md`** (relatório legível) | Fases 1 a 4 do mapeamento |

## Como refazer (a partir desta pasta)

```bash
python scripts/fatos_fis.py
```

```bash
python scripts/casos_fis.py
```

```bash
python scripts/conformidade_fis.py
```

```bash
python scripts/verificar_trechos_fis.py
```

```bash
python scripts/validar_avaliacao_fis.py
```

```bash
python scripts/simular_tobe_fis.py
```

```bash
python scripts/priorizacao_fis.py
```

Geradores executados uma vez (registro do que foi feito): `montar_normas_fis.py` (normas_FIS.json) e `benchmark_*_fis.py` (benchmarking). O BPMN AS-IS e o TO-BE saem de `gerar_bpmn.py --modelos <pasta> --visualizador <pasta>` do repositório, rodado de `mapeamento-processos-sei/scripts`.

## Limites que valem para tudo

- **Recorte do processo.** O PDF traz 23 relatórios com texto, mas o Parecer CASAN 250/2025 lista 42; as respostas
  e planos de ação da concessionária e a reiteração do parecer não estão no PDF. Os números descrevem o que está nos
  autos exportados.
- **Vários casos dentro de um processo.** Cada relatório é um caso do subprocesso vistoria → relatório → aprovação →
  ofício, o que permite medianas; a etapa de análise das respostas tem um único caso (o parecer anual).
- **Sem trilha de andamentos do SEI.** Posse por unidade e horas de trabalho não foram medidas; datas vêm das
  assinaturas eletrônicas e dos documentos.
- **Dias úteis** pelo calendário do RJ em `scripts/fatos_fis.py`: hipótese (pontos facultativos não conferidos).
- **Normas:** trechos literais só do que está transcrito nos autos (conferidos por script); textos fora dos autos
  estão marcados para obter.
- **Pendências de validação:** BPMN e gargalos com a CASAN; matriz de requisitos legais com a Procuradoria.
