# -*- coding: utf-8 -*-
import re, io, json

R = {}
for tag, f in (('N', u'corpus/raw/prose/cn_csrc_manipulation_fourmen.txt'),
               ('O', u'corpus/raw/prose/cn_csrc_manipulation_tenmen.txt'),
               ('K', u'corpus/raw/prose/cn_csrc_fake_info_lurunkai.txt')):
    t = io.open(f, encoding='utf-8').read()
    R[tag] = t.split(u'# note:', 1)[1].split(u'\n', 1)[1]

def glue(s):
    return re.sub(u'(?<=\\d) (?=\\d)', u'', s.replace(u',', u' '))

ALL = glue(u'\n'.join(R.values()))

def L(x):
    k = glue(x)
    assert k in ALL, u'常量缺失: ' + x
    return float(x.replace(u',', u''))

def CNT(pat, i):
    return len(re.findall(pat, R[('N', 'O', 'K')[i]]))

def C(x):
    return u'L("%s")' % x

# --- 逐股盈亏(源 O) ---
stocks = re.findall(u'盈利([0-9][0-9,\\.]*[0-9])元', R['O'])
loss = re.findall(u'亏损([0-9][0-9,\\.]*[0-9])元', R['O'])
print('profit_stocks=%d loss_stocks=%d' % (len(stocks), len(loss)))
conf = re.findall(u'承担([0-9,\\.]+)元', R['O'].split(u'一、对于盈利')[1].split(u'并处以')[0])
fine = re.findall(u'承担([0-9,\\.]+)元', R['O'].split(u'并处以')[1].split(u'二、对于亏损')[0])
flat = re.findall(u'承担([0-9,\\.]+)元', R['O'].split(u'二、对于亏损')[1])
print('conf=%d fine=%d flat=%d' % (len(conf), len(fine), len(flat)))

def s(exprs):
    return u'+'.join(exprs)

E = {}
E['91439472.81'] = u'round(%s,2)' % s([C(v) for v in stocks])
E['91439472.79'] = u'round(%s,2)' % s([C(v) for v in conf])
E['91439472.79f'] = u'round(%s,2)' % s([C(v) for v in fine])
E['90767781.33'] = u'round((%s)-(%s),2)' % (s([C(v) for v in stocks]), s([C(v) for v in loss]))
E['0.02'] = u'round((%s)-(%s),2)' % (s([C(v) for v in stocks]), s([C(v) for v in conf]))
E['8'] = u'CNT("承担37,500元", 1)'
E['30'] = u'L("37,500")*CNT("承担37,500元", 1)/10000'
E['11'] = u'CNT("盈利[0-9]", 1)+CNT("亏损[0-9]", 1)'
E['4'] = u'round(L("62,711,748.37")/L("15,677,937.09"))'
E['80'] = u'round(L("62,711,748.37")*2/L("156,779,370.92")*100)'
E['20'] = u'round(L("15,677,937.09")*2/L("156,779,370.92")*100)'
E['3'] = u'round(L("470,338,112.76")/L("156,779,370.92"))'
E['627117483.68'] = u'round(L("156,779,370.92")+L("470,338,112.76"),2)'
E['6.27'] = u'round((L("156,779,370.92")+L("470,338,112.76"))/100000000,2)'
E['3f'] = u'round(L("188,135,245.10")/L("62,711,748.37"),4)'
E['0.01'] = u'round(3*L("62,711,748.37")-L("188,135,245.10"),2)'
E['470338112.76'] = u'round(L("188,135,245.10")*2+L("47,033,811.28")*2,2)'
E['182878945.6'] = u'round(L("91,439,472.8")*2,2)'

want = {'91439472.81': 91439472.81, '91439472.79': 91439472.79, '91439472.79f': 91439472.79,
        '90767781.33': 90767781.33, '0.02': 0.02, '8': 8, '30': 30, '11': 11, '4': 4,
        '80': 80, '20': 20, '3': 3, '627117483.68': 627117483.68, '6.27': 6.27,
        '3f': 3.0, '0.01': 0.01, '470338112.76': 470338112.76, '182878945.6': 182878945.6}
for k, e in sorted(E.items()):
    try:
        v = eval(e, {}, {'L': L, 'CNT': CNT, 'round': round})
    except Exception as ex:
        print('%-14s ERR %s' % (k, ex)); continue
    flag = u'' if k not in want or abs(float(v) - want[k]) < 1e-9 else u'  <<< want %s' % want[k]
    print('%-14s = %s%s   [%s]' % (k, v, flag, e[:150]))

SKIP={'91439472.79f','3f'}
print('=== paste-ready ===')
for k in sorted(E):
    if k in SKIP: continue
    print(" '%s': %r," % (k, E[k]))

import json as _j
_j.dump({k: E[k] for k in sorted(E) if k not in SKIP}, io.open(u'corpus/raw/probe/b32_deriv.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('dumped')
