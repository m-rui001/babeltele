# -*- coding: utf-8 -*-
"""把 B54 条目派给本机免费模型做独立文字质检: 只读文本, 不看原始文件, 输出落在 corpus/_rev54_*.txt。"""
import io, json, os, subprocess, sys

CFG = r'E:\tools\OpenCode2API-main\config.json'
ASK = r'E:\tools\oc2a_ask.py'
TASK = u'corpus/_rev54.txt'


def walk(o, acc):
    if isinstance(o, dict):
        for v in o.values():
            walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)
    elif isinstance(o, str) and o.endswith('-free') and '/' in o:
        acc.append(o)
    return acc


cfg = json.load(io.open(CFG, encoding='utf-8'))
models = []
for m in walk(cfg, []):
    if m not in models:
        models.append(m)
if not models:
    models = [u'opencode/glm-5.3-flash-free']
print(u'模型: %s' % models[:4])
for i, m in enumerate(models[:3]):
    out = u'corpus/_rev54_%d.txt' % i
    with io.open(out, 'w', encoding='utf-8') as fh:
        p = subprocess.run([sys.executable, '-X', 'utf8', ASK, '--model', m,
                            '--session', u'b54rev%d' % i, TASK],
                           stdout=fh, stderr=subprocess.PIPE)
    txt = io.open(out, encoding='utf-8').read()
    print(u'%s -> %s (%d 字符) err=%s %s' % (
        m, out, len(txt), p.returncode, (p.stderr or b'').decode('utf-8', 'replace')[-160:].replace('\n', ' ')))
