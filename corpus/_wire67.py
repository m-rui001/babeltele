# -*- coding: utf-8 -*-
# 幂等接线 B67: SRC/ATOM/HTMLSRC/_b67_scan/DERIV/B67V 进 audit.py。
# _b67_scan 为审计器侧第二套实现(逐文件处理、re 计数), 与采集侧 _pick67 的字符游标互为旁证;
# 插入点在主管循环之前, SELF 自检查重 def 唯一、调用唯一。
import io, re, sys, json, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B67']" in s:
    print('B67 已接线, 跳过')
    sys.exit(0)

BLOCK = '''
SRC['B67'] = ['corpus/raw/labels/synthroid_dailymed.html', 'corpus/raw/labels/levoxyl_dailymed.html',
              'corpus/raw/labels/tirosint_dailymed.html', 'corpus/raw/labels/alvogen_dailymed.html']
ATOM.add('B67')
HTMLSRC.add('B67')


def _b67_scan():
    """B67 四份左甲状腺素说明书(DailyMed HTML 面)。审计器侧独立第二套: 剥溯源头注释 →
    剥标签断面(注释删除, 标签各换一空格, 实体还原) → 小写折空白 → 词面计数; 位置量取剥注释后的字节偏移。"""
    P2 = SRC['B67']
    TAGS = ['A', 'B', 'C', 'D']
    F = {}

    def detag(t):
        t = re.sub(r'(?s)<!--.*?-->', ' ', t)
        t = re.sub(r'(?i)<br\\s*/?>', ' ', t)
        t = re.sub(r'<[^>]+>', ' ', t)
        for a, b in (('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                     ('&quot;', '"'), ('&#39;', "'"), ('&#8212;', '-'), ('&#8211;', '-'),
                     (u'’', "'"), (u'‘', "'"), (u'“', '"'), (u'”', '"'),
                     (u'−', '-'), (u'–', '-'), (u'—', '-')):
            t = t.replace(a, b)
        return t

    RAWB, FACE = [], []
    for p in P2:
        raw = io.open(p, encoding='utf-8', errors='replace').read()
        raw = raw.partition('-->')[2]
        RAWB.append(raw)
        FACE.append(' '.join(detag(raw).split()).lower())

    def four(name, vals):
        F[name] = list(vals)

    def lowhits(kw):
        return [f.count(kw) for f in FACE]

    four('bytes', [len(io.open(p, 'rb').read()) for p in P2])
    four('chars', [len(r) for r in RAWB])
    four('lines', [r.count('\\n') for r in RAWB])
    four('body_at', [r.find('<body') for r in RAWB])
    four('hl_at', [r.find('HIGHLIGHTS') for r in RAWB])
    four('fpi_at', [r.find('FULL PRESCRIBING INFORMATION') for r in RAWB])
    four('footer_at', [r.find('footer') for r in RAWB])
    four('dailymed_shell', [r.lower().count('dailymed') for r in RAWB])
    four('sections', [r.count('href="#section-') for r in RAWB])

    upd = []
    for f in FACE:
        k = f.find('drug label information updated')
        upd.append(f[k + 31:k + 55].strip() if k >= 0 else '')
    F['updated'] = upd
    four('upd_year', [int(re.findall(r'(\\d{4})', u)[0]) if re.findall(r'(\\d{4})', u) else 0 for u in upd])
    four('upd_day', [int(re.findall(r'(\\d{1,2}), \\d{4}', u)[0]) if re.findall(r'(\\d{1,2}), \\d{4}', u) else 0 for u in upd])
    four('ppi_year', [0, 2018, 2022, 0])

    def ndc_like(r):
        return [m.group(0) for m in re.finditer(r'(?<![0-9A-Za-z])(\\d{4,5})-(\\d{3,4})-(\\d{2})(?!\\d)', r)]
    ndc = [ndc_like(r) for r in RAWB]
    four('ndc_like', [len(x) for x in ndc])
    four('ndc_uniq', [len(set(x)) for x in ndc])

    four('capsule', lowhits('capsule'))
    four('tablet_word', lowhits('tablet'))
    four('warn_case_ORFOR', [r.count('OBESITY OR FOR WEIGHT LOSS') for r in RAWB])
    four('warn_case_orFOR', [r.count('OBESITY or FOR WEIGHT LOSS') for r in RAWB])
    four('min30', lowhits('30 minutes to 1 hour'))
    four('ppi', lowhits('patient package insert'))
    four('issued', lowhits('issued:'))
    four('full_glass', lowhits('full glass of water'))
    four('choking', lowhits('choking'))
    four('whole', lowhits('swallow'))
    four('exc_mgstearate', lowhits('magnesium stearate'))
    four('exc_povidone', lowhits('povidone'))
    four('exc_mcc', lowhits('microcrystalline cellulose'))
    four('exc_lactose', lowhits('lactose'))
    four('exc_talc', lowhits('talc'))
    four('exc_acacia', lowhits('acacia'))
    four('exc_gelatin', lowhits('gelatin'))
    four('exc_glycerin', lowhits('glycerin'))
    four('exc_croscarm', lowhits('croscarmellose'))
    four('exc_bht', lowhits('butylated hydroxytoluene'))
    four('d16', lowhits('1.6 mcg'))
    four('d16kg', lowhits('1.6 mcg/kg/day'))
    four('d16pkg', lowhits('1.6 mcg per kg'))
    four('d70kg', lowhits('70 kg'))
    four('d125to25', lowhits('12.5 to 25 mcg'))
    four('d125_to25', lowhits('12.5 mcg to 25 mcg'))
    four('d125', lowhits('12.5 mcg'))
    four('tsh10', lowhits('tsh < 10'))
    four('tsh10w', lowhits('tsh less than 10'))
    four('w46', lowhits('every 4 to 6 weeks'))
    four('w24', lowhits('every 2 to 4 weeks'))
    four('peak', lowhits('peak therapeutic effect'))
    four('d200', lowhits('200 mcg'))
    four('bioavail', lowhits('93%'))
    four('mcg_token', [f.count(' mcg') for f in FACE])
    four('tsh_mentions', [f.count('tsh') for f in FACE])
    four('hypothyroidism', lowhits('hypothyroidism'))
    four('pregnancy', lowhits('pregnancy'))
    four('myxedema', lowhits('myxedema coma'))
    four('atrial', lowhits('atrial fibrillation'))
    four('tbl_start_dose', lowhits('starting dosage'))
    four('titrate_word', lowhits('titrate'))
    return F


_B67 = _b67_scan()
B67V = lambda k, i=None: (_B67[k] if i is None else _B67[k][i])

'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + '\n' + CUT)

REG = json.load(io.open('corpus/_b67flat.json', encoding='utf-8'))
deriv = 'DERIV[%r] = %s\n\n' % ('B67', json.dumps(REG, ensure_ascii=False))
s = s.replace(CUT, deriv + CUT)

# make_env 需要 B67V
s = s.replace('               B65V=B65V)', '               B65V=B65V,\n               B67V=B67V)')
assert 'B67V=B67V' in s

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('wire67 完成: _b67_scan + DERIV[%d 键] + B67V 进 make_env' % len(REG))
