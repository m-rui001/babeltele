# -*- coding: utf-8 -*-
# 探本机两个 OpenAI 兼容网关: 只打印模型 id, 绝不打印任何 key
import io
import json
import urllib.request

import sys

sys.stdout.reconfigure(encoding='utf-8')


def get(url, key):
    r = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + key})
    return json.load(urllib.request.urlopen(r, timeout=25))


cfg = json.load(io.open(r'E:\tools\OpenCode2API-main\config.json', encoding='utf-8'))
k1 = cfg['API_KEY']
try:
    d = get('http://127.0.0.1:10000/v1/models', k1)
    ids = [m.get('id') for m in d.get('data', [])]
    print('10000 total=%d' % len(ids))
    print('10000 reasoning-ish:', [i for i in ids if any(w in i for w in ('deepseek', 'glm', 'nemotron', 'minimax'))])
except Exception as e:
    print('10000 FAIL', type(e).__name__, e)

