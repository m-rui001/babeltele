# -*- coding: utf-8 -*-
# 外派回收件试跑器: 从 corpus/_api9x_out/*.md 抽出 ```python 块(整件即以 # 开头的纯文本),
# 落成 corpus/_apick_<id>.py(独立命名, 不覆盖任何在用的遍脚本), 现跑现判, 逐件报退出码与尾迹。
# 用法: python -X utf8 corpus/_api_test.py [id 前缀...]
import io, os, re, subprocess, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.environ.get(u'API9X_OUT', u'corpus/_api9x_out')
SBX = os.environ.get(u'API9X_SANDBOX', u'1') == u'1'
PRE = sys.argv[1:] or [u'B93_mk', u'B94_mk', u'B97_mk']


def code_of(txt):
    m = re.search(u'```python\n(.*?)\n```', txt, re.S)
    if m:
        return m.group(1)
    if txt.lstrip().startswith((u'#', u'import', u'from')):
        return txt
    return None


for f in sorted(os.listdir(OUT)):
    if not f.endswith(u'.md'):
        continue
    cid = f[:-3]
    if not any(cid.startswith(p) for p in PRE):
        continue
    txt = io.open(os.path.join(OUT, f), encoding='utf-8', errors='replace').read()
    if txt.startswith(u'__FAILED__'):
        print(u'%-12s SKIP(外派失败件)' % cid)
        continue
    code = code_of(txt)
    if code is None:
        print(u'%-12s NOCODE 首 80: %s' % (cid, txt[:80].replace(u'\n', u' ')))
        continue
    tmp = u'corpus/_apick_%s.py' % cid
    io.open(tmp, 'w', encoding='utf-8', newline=u'\n').write(code)
    bad = [l.strip()[:90] for l in code.split(u'\n')
           if u'open(' in l and (u"'w'" in l or u'"w"' in l or u'\'w\'' in l)
           and any(x in l for x in (u'audit.py', u'README.md', u'_pick'))]
    if bad:
        print(u'%-12s REFUSE 写者在动共享件: %s' % (cid, bad[:3]))
        continue
    cmd = [sys.executable, u'-X', u'utf8'] + ([u'corpus/_sandbox.py', tmp] if SBX else [tmp])
    r = subprocess.run(cmd, capture_output=True,
                       text=True, encoding=u'utf-8', errors=u'replace', timeout=900)
    tail = (r.stdout or u'')[-300:] + u'||' + (r.stderr or u'')[-400:]
    print(u'%-12s exit=%d 行=%d\n    %s' % (cid, r.returncode, code.count(u'\n'),
                                            tail.replace(u'\n', u'\n    ')[-650:]))
