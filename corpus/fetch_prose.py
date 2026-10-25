# -*- coding: utf-8 -*-
# 采集推理密集型正文: Europe PMC(JATS XML) / HTML / PDF -> 纯文本 + 溯源头。
# 用法: python -X utf8 corpus/fetch_prose.py <pmc|html|pdf> <url> <slug>
import io, os, re, sys, json, time, gzip, hashlib, urllib.request, urllib.parse

UA = {'User-Agent': 'Mozilla/5.0 (research corpus pull; contact: abuse@example.org)',
      'Accept-Encoding': 'gzip'}
OUT = 'corpus/raw/prose'

def get(url, extra=None):
    h = dict(UA)
    if extra:
        h.update(extra)
    r = urllib.request.Request(url, headers=h)
    b = urllib.request.urlopen(r, timeout=60).read()
    if b[:2] == b'\x1f\x8b':
        b = gzip.decompress(b)
    return b

def strip(html):
    html = re.sub(r'(?is)<(script|style|head)[^>]*>.*?</\1>', ' ', html)
    html = re.sub(r'(?is)<(br|/p|/div|/li|/h[1-6]|/tr)[^>]*>', '\n', html)
    txt = re.sub(r'(?s)<[^>]+>', ' ', html)
    txt = (txt.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
              .replace('&#39;', "'").replace('&quot;', '"').replace('&nbsp;', ' ')
              .replace('&mdash;', '-').replace('&#8212;', '-').replace('&#8211;', '-'))
    txt = re.sub(r'[ \t]+', ' ', txt)
    txt = re.sub(r'\n\s*\n+', '\n\n', txt)
    return txt.strip()

def pmc_text(slug, pmcid):
    x = get('https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML' % pmcid).decode('utf-8', 'replace')
    title = re.search(r'<article-title>(.*?)</article-title>', x, re.S)
    body = re.sub(r'(?is)<(front|back|ref-list|sec|disp-quote)[^>]*>', ' ', x)
    t = re.sub(r'(?s)<[^>]+>', ' ', body)
    t = re.sub(r'\s+', ' ', t).strip()
    return (title.group(1) if title else pmcid), t

def write(slug, src, url, title, text, note=''):
    os.makedirs(OUT, exist_ok=True)
    p = '%s/%s.txt' % (OUT, slug)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(u'# raw prose\nsrc: %s\nurl: %s\ntitle: %s\nchars: %d\ntext_sha256: %s\nretrieved: %s\n%s\n'
                % (src, url, title, len(text), hashlib.sha256(text.encode()).hexdigest()[:16],
                   time.strftime('%Y-%m-%dT%H:%M:%S'), (u'note: ' + note + u'\n') if note else u''))
        f.write(text)
    print('%s -> %s  (%d B, %d chars)' % (slug, p, os.path.getsize(p), len(text)))

def main():
    kind, url, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    if kind == 'pmc':
        title, text = pmc_text(slug, url)
        write(slug, 'Europe PMC', 'https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML' % url, title, text)
    elif kind == 'html':
        raw = get(url).decode('utf-8', 'replace')
        title = (re.search(r'(?i)<title[^>]*>(.*?)</title>', raw, re.S).group(1).strip()
                 if re.search(r'(?i)<title[^>]*>(.*?)</title>', raw, re.S) else url)
        write(slug, 'HTML', url, re.sub(r'\s+', ' ', title), strip(raw))
    elif kind == 'pdf':
        b = get(url)
        tmp = '%s/%s.pdf' % (OUT, slug)
        io.open(tmp, 'wb').write(b)
        import fitz
        d = fitz.open(tmp)
        text = '\n'.join(pg.get_text() for pg in d)
        write(slug, 'PDF', url, url.rsplit('/', 1)[-1], text, note='pages=%d bytes=%d' % (d.page_count, len(b)))

main()
