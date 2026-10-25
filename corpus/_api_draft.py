# -*- coding: utf-8 -*-
"""并发外派写稿: 把建条目遍的缺件/坏件扔给 cssmapi 的多模型位, 几十路并发, 结果逐份落盘。
用法: python -X utf8 corpus/_api_draft.py <tasks.json> <outdir> [workers]
tasks.json: [{"id": "...", "system": "...", "prompt": "...",
              "temperature": 0.6, "max_tokens": 24000, "model": "..."}]
每路失败重 4 次(退避 3/6/9/12 秒), 全败落 __FAILED__ 标记, 不阻塞其它路。"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.environ.get(u'FREEAI_BASE', u'http://127.0.0.1:8317/v1')
KEYF = os.environ.get(u'FREEAI_KEYFILE', u'~/.freeai_key')
KEY = os.environ.get(u'FREEAI_KEY') or (io.open(os.path.expanduser(KEYF), encoding=u'utf-8').read().strip()
                                       if os.path.exists(os.path.expanduser(KEYF)) else u'free-local-8317')
# 网关心在活的别名(本机 8317 实测 38 枚, 跨 5 个 CN 直连上游)。池子轮转 = 并发摊到不同上游,
# 单一 key 打不动的量, 摊开就能打。POOL=逗号列表可覆盖。
ALL38 = (u'deepseek-v4.1-flash,glm-5.3-flash,minimax-m3.1-flash,nemotron-3-ultra,'
         u'nemotron-3.5-lightning,nemotron-3.5-super-vl,longcat-2.5-preview,mimo-v2.6-flash,'
         u'beam,big-pickle,sf-deepseek-v4.1-flash,sf-glm-5.3-flash,sf-kimi-k2.7-code,'
         u'sf-qwen3-coder,sf-deepseek-v4-pro,ms-deepseek-v4.1-flash,ms-glm-5.2,ms-mistral-large,'
         u'ms-nex-n2.5-mini,ms-qwen3.8-flash,or-gemma-4-31b,or-inkling,or-minimax-m3.1-flash,'
         u'or-nemotron-3-super,or-nemotron-3-ultra,or-north-mini-code,or-xing4.0-29b,cf-llama4-scout')
POOL = [x for x in os.environ.get(u'FREEAI_POOL', ALL38).split(u',') if x]
MODEL = os.environ.get(u'FREEAI_MODEL', POOL[0])


def call(prompt, system, temperature=0.6, max_tokens=24000, model=None, try_max=6):
    order = [model or MODEL] + [m for m in POOL if m != (model or MODEL)][:5]
    last = u''
    for n in range(try_max):
        mdl = order[min(n, len(order) - 1)]
        body = json.dumps({
            u'model': mdl,
            u'messages': [{u'role': u'system', u'content': system},
                          {u'role': u'user', 'content': prompt}],
            u'temperature': temperature,
            u'max_tokens': max_tokens,
            u'stream': False,
        }).encode(u'utf-8')
        req = urllib.request.Request(BASE + u'/chat/completions', data=body, headers={
            u'Content-Type': u'application/json',
            u'Authorization': u'Bearer ' + KEY,
            u'User-Agent': u'curl/8.6.0',
            u'Accept': u'application/json',
        })
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=900).read().decode(u'utf-8', u'replace'))
            txt = (r[u'choices'][0][u'message'][u'content'] or u'').strip()
            if txt:
                return u'<!--model:%s-->\n' % mdl + txt
            last = u'empty@' + mdl
        except Exception as e:
            last = repr(e)[:160] + u'@' + mdl
            if u'429' in last:
                time.sleep(8 + 6 * n)
                continue
        time.sleep(2 + 2 * n)
    return u'__FAILED__ ' + last


def main():
    tk = json.load(io.open(sys.argv[1], encoding=u'utf-8'))
    outdir = sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    done = [0]

    def run(z):
        # 车道轮转别名: 同一份提示词分给不同上游, 才把 5 个上游的并发都用上(失败另由 call() 内部再轮 5 枚)。
        mi = z.get(u'model') or POOL[z.get(u'_i', 0) % len(POOL)]
        op = os.path.join(outdir, z[u'id'] + u'.md')
        if os.path.exists(op):
            old = io.open(op, encoding=u'utf-8', errors=u'replace').read()
            if old.strip() and not old.startswith(u'__FAILED__'):
                return u'%s %d REUSE' % (z[u'id'], len(old))
        t = call(z[u'prompt'], z[u'system'], z.get(u'temperature', 0.6),
                 z.get(u'max_tokens', 24000), mi)
        io.open(op, 'w', encoding='utf-8', newline=u'\n').write(t)
        done[0] += 1
        return u'%s %d %s [%s]' % (z[u'id'], len(t), u'FAIL' if t.startswith(u'__FAILED__') else u'ok', mi)

    for i, z in enumerate(tk):
        z[u'_i'] = i

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for line in pool.map(run, tk):
            print(line)
    print(u'共 %d 路 → %s' % (len(tk), outdir))


main()
