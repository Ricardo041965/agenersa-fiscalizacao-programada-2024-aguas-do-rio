"""Reabre a fonte de cada caso novo e procura o trecho literal (comparação normalizada)."""
import json, sys, os, re, unicodedata, subprocess, tempfile, urllib.request

ARQ = sys.argv[1]
OUTDIR = sys.argv[2]
os.makedirs(OUTDIR, exist_ok=True)

def norm(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'[^a-z0-9]', '', s.lower())

def texto(url, nome):
    dest = os.path.join(OUTDIR, nome)
    r = subprocess.run(['curl', '-sL', '-A', 'Mozilla/5.0', '-o', dest, '-w', '%{http_code}', url],
                       capture_output=True, text=True, timeout=180)
    code = r.stdout.strip()
    raw = open(dest, 'rb').read()
    if raw[:4] == b'%PDF':
        subprocess.run(['pdftotext', '-enc', 'UTF-8', dest, dest + '.txt'])
        return code, open(dest + '.txt', encoding='utf-8', errors='ignore').read()
    t = raw.decode('utf-8', errors='ignore')
    if 'api.openalex.org' in url:
        w = json.loads(t)
        ab = w.get('abstract_inverted_index') or {}
        pos = {p: k for k, v in ab.items() for p in v}
        return code, w.get('title', '') + ' ' + ' '.join(pos[i] for i in sorted(pos))
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S)
    import html
    return code, html.unescape(re.sub(r'<[^>]+>', ' ', t))

def crossref(doi):
    try:
        m = json.load(urllib.request.urlopen('https://api.crossref.org/works/' + doi, timeout=60))['message']
        return 'crossref', m['title'][0], (m.get('published') or m.get('issued'))['date-parts'][0][0]
    except Exception:
        try:
            a = json.load(urllib.request.urlopen('https://api.datacite.org/dois/' + doi, timeout=60))['data']['attributes']
            return 'datacite', a['titles'][0]['title'], a['publicationYear']
        except Exception as e:
            return 'nao_encontrado', None, None

d = json.load(open(ARQ, encoding='utf-8'))
res = {}
for i, c in enumerate(d['casos']):
    if not c['id'].startswith('B-FIS-'):
        continue
    f = c['fonte']
    code, t = texto(f['verificado_em'], 'src%02d' % i)
    achou = norm(f['trecho']) in norm(t)
    pal = len(f['trecho'].split())
    r = {'url_verificacao': f['verificado_em'], 'http': code, 'chars_lidos': len(t),
         'trecho_ok': achou, 'palavras_trecho': pal}
    if f['doi']:
        reg, tit, ano = crossref(f['doi'])
        r['doi_registro'] = reg
        r['doi_ok'] = reg != 'nao_encontrado'
        r['metadados_ok'] = bool(tit) and norm(tit)[:40] == norm(f['titulo'])[:40] and int(ano) == int(f['ano'])
        r['titulo_registro'] = tit; r['ano_registro'] = ano
    else:
        r['doi_ok'] = None
    # URL principal também abre?
    if f['url'] != f['verificado_em']:
        c2, t2 = texto(f['url'], 'url%02d' % i)
        r['url_principal_http'] = c2
        r['url_principal_contem_trecho'] = norm(f['trecho']) in norm(t2)
    res[c['id']] = r
json.dump(res, open(os.path.join(OUTDIR, 'mecanica.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(json.dumps(res, ensure_ascii=False, indent=1))
