# -*- coding: utf-8 -*-
# 取思维链: 把一道难题派给本机 opencode2api 代理, 把模型的 reasoning(思维链) 与 answer 原样落盘。
# reasoning 是模型的隐性推理文本, 与答案分离保存, 便于后续 BabelTele 压缩时逐字回溯。
# 用法: python -X utf8 corpus/fetch_cot.py <slug> <model> <prompt.txt>
#       python -X utf8 corpus/fetch_cot.py --list          # 列后端可用的免费 reasoning 模型
import io, json, sys, time, hashlib, urllib.request, os

CFG = os.environ.get('BABELTELE_CFG', os.path.expanduser('~/.config/babeltele/config.json'))
BASE = 'http://127.0.0.1:10000'          # opencode2api 代理
BACK = 'http://127.0.0.1:10001'          # opencode 后端(代理回合事件卡住时直连)

def list_free():
    """后端 /config/providers 里挑出 reasoning 能力且 cost 全零(免费)的模型。"""
    d = json.load(urllib.request.urlopen(BACK + '/config/providers', timeout=20))
    out = []
    for pv in d.get('providers', []):
        for mid, m in (pv.get('models') or {}).items():
            cap = m.get('capabilities') or {}
            cost = m.get('cost') or {}
            free = not any(v for v in cost.values() if isinstance(v, (int, float)))
            if cap.get('reasoning') and free:
                out.append('%s/%s  %s' % (pv['id'], mid, m.get('name') or ''))
    return out

def ask_back(model, prompt, session):
    """直连 opencode 后端: 一个 session 一条 message, 取回 reasoning 与 text 两类 part。"""
    def rq(path, data=None, method='GET'):
        r = urllib.request.Request(BACK + path, data=json.dumps(data).encode() if data else None,
                                   method=method, headers={'Content-Type': 'application/json'})
        return json.load(urllib.request.urlopen(r, timeout=600))
    sid = rq('/session', {'title': 'cot-' + session}, 'POST')['id']
    m, prov = model.split('/')[-1], 'opencode'
    t0 = time.time()
    d = rq('/session/%s/message' % sid,
           {'model': {'providerID': prov, 'modelID': m}, 'parts': [{'type': 'text', 'text': prompt}]}, 'POST')
    parts = d.get('parts') or []
    rs = ''.join(p.get('text', '') for p in parts if p.get('type') == 'reasoning')
    an = ''.join(p.get('text', '') for p in parts if p.get('type') == 'text')
    info = (d.get('info') or {}).get('tokens', {})
    sys.stderr.write('[%s] %.0fs model=%s tokens=%s\n' % (session, time.time() - t0, m, info))
    return rs, an

def ask(model, prompt, session):
    cfg = json.load(io.open(CFG, encoding='utf-8'))
    body = json.dumps({'model': model, 'max_tokens': 16000, 'user': session,
                       'messages': [{'role': 'user', 'content': prompt}]}).encode()
    req = urllib.request.Request(BASE + '/v1/chat/completions', data=body, headers={
        'Authorization': 'Bearer ' + cfg['API_KEY'], 'Content-Type': 'application/json'})
    t0 = time.time()
    d = json.load(urllib.request.urlopen(req, timeout=cfg.get('REQUEST_TIMEOUT_MS', 600000) / 1000.0))
    ch = d['choices'][0]
    sys.stderr.write('[%s] %.0fs finish=%s usage=%s\n' % (session, time.time() - t0,
                     ch.get('finish_reason'), d.get('usage')))
    m = ch['message']
    return (m.get('reasoning') or ''), (m.get('content') or '')

def main():
    if sys.argv[1] == '--list':
        for r in list_free():
            sys.stdout.write(r + '\n')
        return
    slug, model, pf = sys.argv[1], sys.argv[2], sys.argv[3]
    prompt = io.open(pf, encoding='utf-8').read()
    rs, an = ask_back(model, prompt, slug)
    os.makedirs('corpus/raw/cot', exist_ok=True)
    out = 'corpus/raw/cot/%s.md' % slug
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(u'# raw CoT\n')
        f.write(u'model: %s\nslug: %s\nprompt_sha256: %s\nreasoning_chars: %d\nanswer_chars: %d\nretrieved: %s\n'
                % (model, slug, hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16],
                   len(rs), len(an), time.strftime('%Y-%m-%dT%H:%M:%S')))
        f.write(u'\n## [[PROMPT]]\n' + prompt + u'\n')
        f.write(u'\n## [[REASONING]]\n' + rs + u'\n')
        f.write(u'\n## [[ANSWER]]\n' + an + u'\n')
    sys.stdout.write('wrote %s (%d B)\n' % (out, os.path.getsize(out)))

main()
