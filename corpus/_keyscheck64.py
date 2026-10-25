# -*- coding: utf-8 -*-
"""_keyscheck64.py: 静态收集正文模板里的 V/JOIN/CLOS/CLOS4 键名, 与 SCAN 段产出的 F 键对表。
用法: python -X utf8 corpus/_keyscheck64.py"""
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
s = io.open(u'corpus/_mkB64.py', encoding='utf-8').read()
i = s.find(u'# ---------- \u6b63\u6587 ----------')
j = s.find(u'assert not MISSING')
body = s[i:j]
SCAN = s[:i]

keys = set()
for m in re.finditer(r"\b(?:V|JOIN|CLOS|CLOS4)\(\s*u?'([a-z0-9_]+)'", SCAN):
    keys.add(m.group(1))
for m in re.finditer(r"^F\[u?'([a-z0-9_]+)'\]", SCAN, re.M):
    keys.add(m.group(1))
for m in re.finditer(r"F\[u?'([a-z0-9_]+)'\] = ", SCAN):
    keys.add(m.group(1))
for m in re.finditer(r"put\(u?'([a-z0-9_]+)'", SCAN):
    keys.add(m.group(1))
for m in re.finditer(r"four\(u?'([a-z0-9_]+)'", SCAN):
    keys.add(m.group(1))
litk = set()
for m in re.finditer(r"u'([a-z0-9_]+)':\s*u'", SCAN):
    litk.add(u'lit_' + m.group(1))
keys |= litk
for pre in (u'lit_', u'pv_', u'cite_', u'v_', u'u_', u'l_', u'share_', u'only_', u'durms_',
            u'durlit_', u'secw_', u'outw_', u'y_secw_', u'y_outw_', u's_', u'n_', u'wrapgap_',
            u'wrap_', u'pool_', u'num_lines_', u'on_pair_', u'on_n_', u'sec_len_', u'sec_off_',
            u'lines_ge40', u'union_', u'hdr', u'foot'):
    pass
for m in re.finditer(r"for k in sorted\(LITK\):", SCAN):
    pass

used = []
for m in re.finditer(r"\b(?:V|JOIN|CLOS|CLOS4)\(\s*u?'([a-z0-9_]+)'", body):
    used.append(m.group(1))
bad = [x for x in used if x not in keys]
print(u'SCAN 产出键 %d ⇎ 正文引用 %d ⇎ 存疑 %d' % (len(keys), len(used), len(set(bad))))
for x in sorted(set(bad)):
    print(u'  ? %s' % x)
