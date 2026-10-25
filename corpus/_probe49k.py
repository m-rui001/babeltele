# -*- coding: utf-8 -*-
"""B49 工具侧实测: 同一份程序, 逐条破坏数据(表/码表/数据)与逐条改坏比较符, 记录 exit 与两条流。
数字写进 corpus/_b49battery.json, 由 _fill49.py 读取生成 ⛓解读注(不手填)。"""
import io, os, re, json, subprocess, tempfile

TZ = 'corpus/raw/tz'
DATA = ['africa', 'antarctica', 'asia', 'australasia', 'europe', 'northamerica',
        'southamerica', 'etcetera', 'factory', 'backward']
EXTRA = ['iso3166.tab', 'zone1970.tab', 'zone.tab', 'checktab.awk']
BASE = {f: open(os.path.join(TZ, f), 'rb').read() for f in DATA + EXTRA}
PROG = BASE['checktab.awk']


def run(prog, zt, warn=0, files=None):
    d = tempfile.mkdtemp()
    io.open(os.path.join(d, 'checktab.awk'), 'wb').write(prog)
    for f in DATA + [x for x in EXTRA if x != 'checktab.awk']:
        io.open(os.path.join(d, f), 'wb').write(BASE[f])
    p = subprocess.run(['gawk', '-f', 'checktab.awk', '-v', 'iso_table=iso3166.tab',
                        '-v', 'zone_table=%s' % zt, '-v', 'want_warnings=%d' % warn] + DATA,
                       cwd=d, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    er = p.stderr.decode('utf-8', 'replace').split('\n')
    ou = p.stdout.decode('utf-8', 'replace').split('\n')
    return {'exit': p.returncode, 'err': er[:-1] if er[-1:] == [''] else er,
            'out': ou[:-1] if ou[-1:] == [''] else ou}


def rec(k, res, zt=None):
    v = {'exit': res['exit'], 'nerr': len(res['err']), 'nout': len(res['out']),
         'bytes_err': sum(len(x) + 1 for x in res['err']), 'bytes_out': sum(len(x) + 1 for x in res['out']),
         'first_err': res['err'][0] if res['err'] else '',
         'first_out': res['out'][0] if res['out'] else ''}
    if res['err']:
        cc = {}
        for l in res['err']:
            m = re.search(r"country code '([A-Z]{2})'", l)
            if m:
                cc[m.group(1)] = cc.get(m.group(1), 0) + 1
        if cc:
            v['top_cc'] = sorted(cc.items(), key=lambda x: (-x[1], x[0]))[:6]
        pre = {}
        for l in res['err'] + res['out']:
            m = re.search(r"'([A-Za-z]+)/", l)
            if m:
                pre[m.group(1)] = pre.get(m.group(1), 0) + 1
        if pre:
            v['top_prefix'] = sorted(pre.items(), key=lambda x: (-x[1], x[0]))[:6]
        v['kinds'] = sorted({re.sub(r"^.*?: ", '', re.sub(r"[\dA-Za-z']+", 'N', l)) for l in res['err']})
    R[k] = v


R = {}
for zt in ['zone1970.tab', 'zone.tab']:
    rec('base_' + zt, run(PROG, zt))


def t(name):
    return BASE[name].decode('utf-8').replace('\r\n', '\n')


def dlines(s):
    ls = s.split('\n')
    return ls, [i for i, l in enumerate(ls) if l[:1] != '#' and l.strip()]


def mutate(name, fn):
    keep = BASE[name]
    try:
        BASE[name] = fn(keep.decode('utf-8')).encode('utf-8')
        rec_m(name, fn)
    finally:
        BASE[name] = keep


CUR = {}


def rec_m(name, fn):
    zt = 'iso3166.tab' if name == 'iso3166.tab' else ('europe' if name == 'europe' else name)
    pass


# ---------- 数据侧 ----------
def d_coord(s):
    ls, idx = dlines(s)
    r = ls[idx[0]].split('\t')
    ls[idx[0]] = '\t'.join([r[0], r[1][:-1], r[2]] + r[3:])
    return '\n'.join(ls)


def d_order(s):
    ls, idx = dlines(s)
    for k in range(1, len(idx)):
        a = ls[idx[k - 1]].split('\t')[0].split(',')[0]
        b = ls[idx[k]].split('\t')[0].split(',')[0]
        if a < b:
            ls[idx[k - 1]], ls[idx[k]] = ls[idx[k]], ls[idx[k - 1]]
            return '\n'.join(ls)
    raise AssertionError


def codes_of(s):
    ls, idx = dlines(s)
    c = {}
    for i in idx:
        for x in ls[i].split('\t')[0].split(','):
            c[x] = c.get(x, 0) + 1
    return c


def d_misscomment(s):
    ls, idx = dlines(s)
    c = codes_of(s)
    for i in idx:
        r = ls[i].split('\t')
        if len(r) == 4 and max(c[x] for x in r[0].split(',')) > 1:
            ls[i] = '\t'.join(r[:3])
            return '\n'.join(ls)
    raise AssertionError


def d_extrashort(s):
    ls, idx = dlines(s)
    c = codes_of(s)
    for i in idx:
        r = ls[i].split('\t')
        if len(r) == 3 and max(c[x] for x in r[0].split(',')) <= 1:
            ls[i] = '\t'.join(r) + '\tprobe note'
            return '\n'.join(ls)
    raise AssertionError


def d_unknowncc(s):
    ls, idx = dlines(s)
    r = ls[idx[3]].split('\t')
    ls[idx[3]] = '\t'.join(['QQ'] + r[1:])
    return '\n'.join(ls)


def d_fivecol(s):
    ls, idx = dlines(s)
    ls[idx[2]] = ls[idx[2]] + '\tx\ty'
    return '\n'.join(ls)


def d_duprow(s):
    ls, idx = dlines(s)
    ls.insert(idx[5] + 1, ls[idx[5]])
    return '\n'.join(ls)


def i_extracol(s):
    ls, idx = dlines(s)
    ls[idx[4]] = ls[idx[4]] + '\textra'
    return '\n'.join(ls)


def i_lower(s):
    ls, idx = dlines(s)
    r = ls[idx[6]].split('\t')
    ls[idx[6]] = '\t'.join([r[0].lower(), r[1]])
    return '\n'.join(ls)


def i_dupcode(s):
    ls, idx = dlines(s)
    ls.insert(idx[8] + 1, ls[idx[8]])
    return '\n'.join(ls)


def i_samename(s):
    ls, idx = dlines(s)
    nm = ls[idx[2]].split('\t')[1]
    r = ls[idx[10]].split('\t')
    ls[idx[10]] = '\t'.join([r[0], nm])
    return '\n'.join(ls)


def i_swap(s):
    ls, idx = dlines(s)
    ls[idx[1]], ls[idx[2]] = ls[idx[2]], ls[idx[1]]
    return '\n'.join(ls)


def set_field(line, n, val):
    parts = re.split(r'(\s+)', line)
    cnt = 0
    for k, p in enumerate(parts):
        if p.strip():
            cnt += 1
            if cnt == n:
                parts[k] = val
                return ''.join(parts)
    raise AssertionError


def first_field(s, want, n):
    for l in s.split('\n'):
        p = l.split()
        if p[:1] == [want] and len(p) > n:
            yield l
        elif p[:1] == [want] and l[:1] != '#':
            yield l


def z_line(s, head, pred=None):
    for l in s.split('\n'):
        p = l.split()
        if p[:1] == [head] and (pred is None or pred(p)):
            return l
    raise AssertionError(head)


def z_rename(s):
    l = z_line(s, 'Zone')
    return s.replace(l, set_field(l, 2, 'Europe/LondonX'), 1)


def z_stdoff(s):
    l = z_line(s, 'Zone')
    return s.replace(l, set_field(l, 3, '44:00'), 1)


def z_month(s):
    l = z_line(s, 'Rule', lambda p: len(p) > 5 and p[5] == 'Mar')
    return s.replace(l, set_field(l, 6, 'Foo'), 1)


def z_ruleunused(s):
    l = z_line(s, 'Rule', lambda p: len(p) > 1 and p[1] == 'Albania')
    return s.replace(l, set_field(l, 2, 'AlbaniaX'), 1)


def z_ruleletters(s):
    l = z_line(s, 'Rule', lambda p: len(p) > 1 and p[1] == 'Eire')
    return s.replace(l, set_field(l, 2, 'EireX'), 1)


JOB = [('zone1970.tab', 'coord', d_coord), ('zone1970.tab', 'order', d_order),
       ('zone1970.tab', 'misscomment', d_misscomment), ('zone1970.tab', 'extracomment', d_extrashort),
       ('zone1970.tab', 'unknowncc', d_unknowncc), ('zone1970.tab', 'fivecol', d_fivecol),
       ('zone1970.tab', 'duprow', d_duprow), ('iso3166.tab', 'extracol', i_extracol),
       ('iso3166.tab', 'lower', i_lower), ('iso3166.tab', 'dupcode', i_dupcode),
       ('iso3166.tab', 'samename', i_samename), ('iso3166.tab', 'swap', i_swap),
       ('europe', 'rename', z_rename), ('europe', 'stdoff', z_stdoff),
       ('europe', 'month', z_month), ('europe', 'ruleunused', z_ruleunused),
       ('europe', 'ruleletters', z_ruleletters)]
for name, key, fn in JOB:
    keep = BASE[name]
    zt = 'zone1970.tab'
    BASE[name] = fn(keep.decode('utf-8')).encode('utf-8')
    rec('d_' + key, run(PROG, zt))
    BASE[name] = keep

rec('restore', run(PROG, 'zone1970.tab'))

# ---------- 码侧 ----------
C = t('checktab.awk')
NICE = [('cc_lt', ('if (cc < cc0 \\\n\t\t    && !(zone_table == "zone.tab"',
                   'if (cc <= cc0 \\\n\t\t    && !(zone_table == "zone.tab"'), 'zone1970.tab', 0),
          ('cc_lt_zonetab', ('if (cc < cc0 \\\n\t\t    && !(zone_table == "zone.tab"',
                             'if (cc <= cc0 \\\n\t\t    && !(zone_table == "zone.tab"'), 'zone.tab', 0),
          ('exempt_dead', ('&& !(zone_table == "zone.tab" \\\n\t\t\t && tz0 == "Europe/Simferopol")',
                           '&& !(zone_table == "zone.tabX" \\\n\t\t\t && tz0 == "Europe/Simferopol")',
                           ), 'zone.tab', 0),
          ('backward', ('FILENAME != "backward"', 'FILENAME != "backwardZ"'), 'zone1970.tab', 0),
          ('iso_lt', ('if (cc <= cc0) {', 'if (cc < cc0) {'), 'zone1970.tab', 0),
          ('usedmax', ('used_max <= 1', 'used_max < 1'), 'zone1970.tab', 0),
          ('nf3', ('if (NF != 2) {', 'if (NF != 3) {'), 'zone1970.tab', 0),
          ('main_etc', ('tz && tz ~ /\\// && tz !~ /^Etc\\//', 'tz && tz ~ /\\// && tz !~ /^EtcZ\\//'),
           'zone1970.tab', 0),
          ('end_etc', ('!zoneSeen[tz] && tz !~ /^Etc\\//', '!zoneSeen[tz] && tz !~ /^EtcZ\\//'),
           'zone1970.tab', 0),
          ('seen_off', ('if (tz && tz ~ /\// && tz !~ /^Etc\//) {',
                        'if (0 && tz && tz ~ /\// && tz !~ /^Etc\//) {'), 'zone1970.tab', 0),
          ('warn_on', ('if (0 < want_warnings)', 'if (0 < want_warnings)'), 'zone1970.tab', 1)]
for key, (old, new), zt, warn in [(j[0], j[1], j[2], j[3]) for j in NICE]:
    assert C.count(old) == 1, (key, C.count(old))
    rec('c_' + key, run(C.replace(old, new).encode('utf-8'), zt, warn))

# 换比较符 + 改死豁免串: 两枚改动合起来才看得见豁免的重量
P2 = C.replace(NICE[0][1][0], NICE[0][1][1]).replace(
    '&& !(zone_table == "zone.tab" \\\n\t\t\t && tz0 == "Europe/Simferopol")',
    '&& !(zone_table == "zone.tabZ" \\\n\t\t\t && tz0 == "Europe/Simferopol")')
assert C.count('&& !(zone_table == "zone.tab" \\\n\t\t\t && tz0 == "Europe/Simferopol")') == 1
rec('c_cc_lt_noexempt', run(P2.encode('utf-8'), 'zone.tab'))
rec('warn_off_flag', run(PROG, 'zone1970.tab', warn=1))

# ---------- CRLF 非不变 ----------
for nm in ['zone1970.tab', 'iso3166.tab', 'europe', 'ALL3', 'checktab.awk']:
    keep = {k: BASE[k] for k in BASE}
    try:
        if nm == 'ALL3':
            tgt = ['zone1970.tab', 'iso3166.tab', 'europe']
        elif nm == 'checktab.awk':
            tgt = []
        else:
            tgt = [nm]
        for f in tgt:
            BASE[f] = BASE[f].replace(b'\n', b'\r\n')
        prog = C.replace('\n', '\r\n').encode('utf-8') if nm == 'checktab.awk' else PROG
        rec('crlf_' + nm, run(prog, 'zone1970.tab'))
    finally:
        BASE.clear()
        BASE.update(keep)

json.dump(R, io.open('corpus/_b49battery.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k in sorted(R):
    v = R[k]
    print('%-18s exit=%-2s err=%-4s out=%-4s %-58s %s' %
          (k, v['exit'], v['nerr'], v['nout'], (v['first_err'] or v['first_out'])[:58],
           str(v.get('top_cc', v.get('top_prefix', '')))[:60]))
