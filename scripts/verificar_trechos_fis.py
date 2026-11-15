"""Portão de qualidade da conformidade FIS: confere os trechos literais de mapeamento/normas_FIS.json
contra o texto integral do processo (texto/processo_completo.txt).

Normalização (igual nos dois lados): Unicode NFKC (desfaz ligaduras), aspas e travessões unificados,
hifenização de fim de linha desfeita ("publica-\\nção" → "publicação"), espaços e quebras de linha
colapsados, caixa baixa. A marca de página do PDF e o rodapé de cada página do SEI são removidos antes da
comparação, para que um trecho que atravessa a quebra de página seja encontrado. O trecho é procurado no
texto com e sem a hifenização desfeita (um hífen real no fim da linha não se perde).

Confere 'trecho' e 'mencao_nos_autos'. Trecho vazio só é aceito com situacao_trecho = 'obter texto (fora dos
autos)'. Quando a norma traz 'texto_referencia' (texto de norma já conferido na base AGENERSA e copiado de
normas_P06.json), confere que a cópia é idêntica ao original — não é trecho dos autos.
Para cada trecho achado, informa a(s) página(s) e confere com a página declarada em documento_origem
(para 'mencao_nos_autos', com 'mencao_pagina' quando a menção está em outra peça).

Uso: python scripts/verificar_trechos_fis.py   (grava mapeamento/verificacao_trechos_FIS.txt;
sai com código 1 se houver trecho sem correspondência)
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TEXTO = BASE / "texto" / "processo_completo.txt"
NORMAS = BASE / "mapeamento" / "normas_FIS.json"
SAIDA = BASE / "mapeamento" / "verificacao_trechos_FIS.txt"
RAIZ = BASE.parent.parent
P06 = RAIZ / "mapeamento-processos-sei" / "saida" / "fase3" / "normas_P06.json"
FORA = "obter texto (fora dos autos)"

RODAPE = re.compile(r"^.*SEI SEI-480002/001314/2024 / pg\. \d+\s*$", re.M)
MARCA = re.compile(r"===== PÁGINA (\d+) =====")
HIFEN = re.compile(r"(\w)-[ \t]*\n\s*(\w)")


def normalizar(s: str, desfazer_hifen: bool = False) -> str:
    s = unicodedata.normalize("NFKC", s)
    for a, b in (("“", '"'), ("”", '"'), ("„", '"'), ("‘", "'"), ("’", "'"), ("–", "-"), ("—", "-"), ("‑", "-"), ("­", "")):
        s = s.replace(a, b)
    if desfazer_hifen:
        s = HIFEN.sub(r"\1\2", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def montar_texto(desfazer_hifen: bool) -> tuple[str, list[tuple[int, int]]]:
    """Texto normalizado e lista (posição inicial, página) para localizar a página de cada achado."""
    partes = MARCA.split(TEXTO.read_text(encoding="utf-8"))
    texto, mapa = "", []
    for i in range(1, len(partes), 2):
        corpo = RODAPE.sub(" ", partes[i + 1])
        mapa.append((len(texto), int(partes[i])))
        texto += normalizar(corpo, desfazer_hifen) + " "
    return texto, mapa


def paginas_de(pos: int, fim: int, mapa: list[tuple[int, int]]) -> list[int]:
    inicio = max((p for ini, p in mapa if ini <= pos), default=0)
    return [p for ini, p in mapa if ini <= fim and p >= inicio]


def procurar(alvo_bruto: str, versoes) -> tuple[str, list[int], int, list[int]] | None:
    alvo = normalizar(alvo_bruto, desfazer_hifen=True)
    for rotulo, (texto, mapa) in versoes:
        pos = texto.find(alvo)
        if pos < 0:
            continue
        todas, p = [], pos
        while p >= 0:
            todas.extend(paginas_de(p, p + len(alvo), mapa))
            p = texto.find(alvo, p + 1)
        return rotulo, paginas_de(pos, pos + len(alvo), mapa), texto.count(alvo), sorted(set(todas))
    return None


def main() -> int:
    versoes = [("literal", montar_texto(False)), ("hifenização desfeita", montar_texto(True))]
    normas = json.loads(NORMAS.read_text(encoding="utf-8"))["normas"]
    p06 = {n["id"]: n for n in json.loads(P06.read_text(encoding="utf-8"))["normas"]} if P06.exists() else {}
    linhas, falhas, vazios_ok, conferidos, avisos, refs_ok = [], 0, 0, 0, 0, 0
    for n in normas:
        nid = n["id"]
        for campo in ("trecho", "mencao_nos_autos"):
            if campo not in n:
                continue
            valor = n.get(campo) or ""
            if not valor.strip():
                if campo == "trecho" and n.get("situacao_trecho") == FORA:
                    vazios_ok += 1
                    linhas.append(f"[FORA DOS AUTOS] {nid} trecho vazio ({n['norma']}, {n['dispositivo']})")
                elif campo == "trecho":
                    falhas += 1
                    linhas.append(f"[FALHA] {nid} trecho vazio sem situacao_trecho '{FORA}'")
                continue
            conferidos += 1
            achado = procurar(valor, versoes)
            if not achado:
                falhas += 1
                linhas.append(f"[FALHA] {nid} {campo} sem correspondência: {valor[:90]}...")
                continue
            rotulo, pags, ocorr, todas = achado
            decl = n.get("mencao_pagina") if campo == "mencao_nos_autos" and n.get("mencao_pagina") else (n.get("documento_origem") or {}).get("pagina")
            ok_pag = decl in todas if decl else True
            if not ok_pag:
                avisos += 1
            linhas.append(f"[OK] {nid} {campo}: achado ({rotulo}) na(s) pág. {pags} ({ocorr} ocorrência(s)); "
                          f"página declarada {decl}{'' if ok_pag else ' — DIVERGE'}")
        ref = n.get("texto_referencia")
        if ref:
            pid = ref["origem"].split(",")[-1].strip()
            if pid in p06 and p06[pid]["trecho"] == ref["trecho"]:
                refs_ok += 1
                linhas.append(f"[REFERÊNCIA P06] {nid} = {pid}: cópia idêntica ao normas_P06.json (texto fora dos autos)")
            else:
                falhas += 1
                linhas.append(f"[FALHA] {nid} texto_referencia difere de {pid} em normas_P06.json")
    cab = [
        "Verificação dos trechos literais — normas_FIS.json × texto/processo_completo.txt",
        "Normalização: NFKC, aspas/travessões, hifenização de fim de linha, espaços e quebras de linha, caixa baixa; rodapés de página do SEI removidos.",
        f"Normas: {len(normas)} | trechos e menções conferidos: {conferidos} | sem correspondência: {falhas} | "
        f"trechos vazios fora dos autos: {vazios_ok} | textos de referência P06 idênticos: {refs_ok} | página declarada divergente: {avisos}",
        "Resultado: " + ("APROVADO (0 trecho sem correspondência)" if falhas == 0 else "REPROVADO"),
        "",
    ]
    SAIDA.write_text("\n".join(cab + linhas) + "\n", encoding="utf-8")
    print("\n".join(cab + linhas))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
