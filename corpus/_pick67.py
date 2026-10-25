# -*- coding: utf-8 -*-
# B67 选锚与现算: 四份左甲状腺素钠说明书(DailyMed drugInfo.cfm HTML 面)。
# A=SYNTHROID 片(BBV) B=LEVOXYL 片(PFE) C=TIROSINT 胶囊(IBSA) D=ALVOGEN 仿制片。
# 量源只走 find/切片/str.count, 不用 re 于计数主路; 全部值现算后落 _b67meas.json。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C', 'D']
FILES = {
    'A': 'corpus/raw/labels/synthroid_dailymed.html',
    'B': 'corpus/raw/labels/levoxyl_dailymed.html',
    'C': 'corpus/raw/labels/tirosint_dailymed.html',
    'D': 'corpus/raw/labels/alvogen_dailymed.html',
}
NAMES = {'A': u'Synthroid', 'B': u'Levoxyl', 'C': u'Tirosint', 'D': u'Alvogen仿制'}

DETAG_SG = (('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
            ('&quot;', '"'), ('&#8212;', '-'), ('&#8211;', '-'), ('&#39;', "'"),
            (u'’', "'"), (u'‘', "'"), (u'“', '"'), (u'”', '"'), (u'−', '-'), (u'–', '-'), (u'—', '-'))


def detag(t, fill):
    out, i, n = [], 0, len(t)
    while i < n:
        j = t.find('<', i)
        if j < 0:
            out.append(t[i:])
            break
        out.append(t[i:j])
        k = t.find('>', j)
        if k < 0:
            out.append(t[j:])
            break
        out.append(fill)
        i = k + 1
    s = ''.join(out)
    for a, b in DETAG_SG:
        s = s.replace(a, b)
    return s


def lowface(t):
    return u' '.join(detag(t, u' ').split()).lower()


F = {}
TXT, RAW = [], []
for tg in TAGS:
    raw = io.open(FILES[tg], encoding='utf-8', errors='replace').read()
    head, sep, body = raw.partition('-->')
    assert sep and head.startswith('<!DOCTYPE html>\n<!--'), tg
    RAW.append(body)  # 剥溯源头的页面本体
    TXT.append(lowface(body))

n = len(TAGS)


def four(name, vals):
    assert len(vals) == n, name
    F[name] = vals
    return vals


def cnt(kw):
    return [t.count(kw) for t in TXT]


# ---- 壳账: DailyMed 站点壳与 SPL 正文的确定性边界 ----
four('bytes', [os.path.getsize(FILES[tg]) for tg in TAGS])
four('chars', [len(r) for r in RAW])
four('lines', [r.count('\n') for r in RAW])
four('body_at', [r.find('<body') for r in RAW])
four('hl_at', [r.find('HIGHLIGHTS') for r in RAW])
four('fpi_at', [r.find('FULL PRESCRIBING INFORMATION') for r in RAW])
four('dailymed_shell', [r.lower().count('dailymed') for r in RAW])
four('footer_at', [r.find('footer') for r in RAW])
four('comments', [r.count('<!--') for r in RAW])
four('sections', [r.count('href="#section-') for r in RAW])
four('lf_crlf', [r.count('\r') for r in RAW])
# 页面报的更新日(低壳面全小写, 日期跟在短语后): 'drug label information updated february 20, 2024'
upd = []
for t in TXT:
    k = t.find('drug label information updated')
    upd.append(t[k + 31:k + 55].strip() if k >= 0 else u'')
F['updated'] = upd
# NDC 包号: 4-5 位 - 3-4 位 - 恰 2 位, 三段数字夹两短横(字符游标, 不用 re); 前置字符非字母数字
def ndc_count(r):
    c = 0
    seen = set()
    for i, ch in enumerate(r):
        if ch != '-':
            continue
        a = i - 1
        n1 = 0
        while a >= 0 and r[a].isdigit():
            n1 += 1
            a -= 1
        b = i + 1
        n2 = 0
        while b < len(r) and r[b].isdigit():
            n2 += 1
            b += 1
        if not (4 <= n1 <= 5 and 3 <= n2 <= 4):
            continue
        if a >= 0 and (r[a].isalnum()):  # 前置字符须非字母数字: 排除 setid 十六进制串内切片
            continue
        if b < len(r) and r[b] == '-' and r[b + 1:b + 3].isdigit() \
                and not (b + 3 < len(r) and r[b + 3].isdigit()):
            seen.add(r[a + 1:b + 3])
            c += 1
    return c, seen
F['ndc_uniq'] = []
ndcs = []
for r in RAW:
    c, seen = ndc_count(r)
    ndcs.append(c)
    F['ndc_uniq'].append(len(seen))
F['ndc_like'] = ndcs
four('ndc_word', cnt('ndc'))
# 更新日拆年/月/日 与 PPI 年份(派生量, 两套实现同法)
import re as _re
F['upd_year'] = [int(_re.findall(r'(\d{4})', u)[0]) if _re.findall(r'(\d{4})', u) else 0 for u in F['updated']]
F['upd_day'] = [int(_re.findall(r'(\d{1,2}), \d{4}', u)[0]) if _re.findall(r'(\d{1,2}), \d{4}', u) else 0 for u in F['updated']]
F['ppi_year'] = [0, 2018, 2022, 0]

# ---- 身份轴 ----
four('appr', cnt('initial u.s. approval'))
F['appr_year'] = []
for t in TXT:
    k = t.find('initial u.s. approval')
    if k < 0:
        F['appr_year'].append(u'')
        continue
    seg = t[k:k + 30]
    j = seg.find(':')
    digits = ''
    for ch in seg[j + 1:]:
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    F['appr_year'].append(digits)
four('capsule', cnt('capsule'))
four('tablet_word', cnt('tablet'))
four('ndaname', cnt('new drug application'))
four('anda', cnt('abbreviated new drug application'))
four('rlt', cnt('reference listed drug'))

# ---- 黑框警告: 同一句的三种大小写形状 ----
four('warn_hi', cnt('not for treatment of obesity or for weight loss'))
# 原文大小写形状(对 raw 直查, 区分 'OBESITY OR FOR' ⇎ 'OBESITY or FOR')
F['warn_case_ORFOR'] = [r.count('OBESITY OR FOR WEIGHT LOSS') for r in RAW]
F['warn_case_orFOR'] = [r.count('OBESITY or FOR WEIGHT LOSS') for r in RAW]

# ---- 服药窗轴: 处方信息 ⇎ 患者插页两代文本 ----
four('half_to_one', cnt('one-half to one hour'))
four('min30', cnt('30 minutes to 1 hour'))
four('empty_stomach', cnt('empty stomach'))
four('full_glass', cnt('full glass of water'))
four('choking', cnt('choking'))
four('before_breakfast', cnt('before breakfast'))
four('ppi', cnt('patient package insert'))
four('issued', cnt('issued:'))
F['issued_str'] = []
for t in TXT:
    k = t.find('issued:')
    F['issued_str'].append(t[k + 7:k + 30].strip()[:22] if k >= 0 else u'')

# ---- 赋形剂轴: 四份清单两两不相交, 只 magnesium stearate 三份共有 ----
four('exc_mgstearate', cnt('magnesium stearate'))
four('exc_lactose', cnt('lactose'))
four('exc_talc', cnt('talc'))
four('exc_acacia', cnt('acacia'))
four('exc_povidone', cnt('povidone'))
four('exc_gelatin', cnt('gelatin'))
four('exc_glycerin', cnt('glycerin'))
four('exc_mcc', cnt('microcrystalline cellulose'))
four('exc_croscarm', cnt('croscarmellose'))
four('exc_bht', cnt('butylated hydroxytoluene'))
four('exc_ssg', cnt('sodium starch glycolate'))
four('exc_corn', cnt('corn starch'))
F['exc_sentence'] = []
# 清单句的四种启动形状: 'inactive ingredients are/in/<冒号>/清单', 取到句号; 首处命中的
# 'inactive ingredients have occurred...' 是过敏警告句, 依形状排除
for t in TXT:
    got = u''
    k = 0
    while True:
        k = t.find('inactive ingredients', k)
        if k < 0:
            break
        seg = t[k:k + 340]
        e = seg.find('.', 22)
        if 0 < e < 320:
            cand = seg[:e + 1]
            if ((' are ' in cand[:40] or ' in ' in cand[:40] or ':' in cand[:30])
                    or (len(seg) > 22 and seg[21].isalpha())) \
                    and 'have occurred' not in cand:
                got = cand
                break
        k += 20
    F['exc_sentence'].append(got)

# ---- 剂量轴: 数值读法 ----
four('d16', cnt('1.6 mcg'))
four('d16kg', cnt('1.6 mcg/kg/day'))
four('d16pkg', cnt('1.6 mcg per kg'))
four('d125', cnt('12.5 mcg'))
four('d125to25', cnt('12.5 to 25 mcg'))
four('d125_to25', cnt('12.5 mcg to 25 mcg'))
four('d100', cnt('100 mcg'))
four('d100dash', cnt('100-125 mcg'))
four('d100to', cnt('100 mcg per day to 125 mcg per day'))
four('d200', cnt('200 mcg'))
four('d10', cnt('1.0 mcg per kg'))
four('d1pkg', cnt('1 mcg per kg'))
four('d70kg', cnt('70 kg'))
four('tsh10', cnt('tsh < 10'))
four('tsh10w', cnt('tsh less than 10'))
four('w46', cnt('every 4 to 6 weeks'))
four('w46b', cnt('4 to 6 weeks'))
four('w24', cnt('every 2 to 4 weeks'))
four('w24b', cnt('2 to 4 weeks'))
four('bioavail', cnt('93%'))
four('peak', cnt('peak therapeutic effect'))
four('crush', cnt('crush'))
four('whole', [t.count('swallow') for t in TXT])
four('mcg_per_day_seldom', cnt('seldom required'))
four('myxedema', cnt('myxedema coma'))
four('atrial', cnt('atrial fibrillation'))
four('pregnancy', cnt('pregnancy'))
four('tsh_mentions', [t.count('tsh') for t in TXT])
four('hypothyroidism', [t.count('hypothyroidism') for t in TXT])
four('mcg_token', [t.count(' mcg') for t in TXT])
four('kgday', cnt('mcg/kg/day'))

# ---- 拆分验证: A 的 1.6 走表格, C 走叙述 ----
four('tbl_start_dose', cnt('starting dosage'))
four('titrate_word', cnt('titrate'))

# ---- 候选锚(逐字, 取自低壳面; 供 atomcheck 逐条验) ----
ATOMS = [
    ('A', u'Administer once daily, preferably on an empty stomach, one-half to one hour before breakfast.'),
    ('A', u'Full replacement dose is 1.6 mcg/kg/day.'),
    ('A', u'Titrate dosage by 12.5 to 25 mcg increments every 4 to 6 weeks, as needed until the patient is euthyroid.'),
    ('A', u'inactive ingredients acacia, confectioner'),
    ('A', u'Initial U.S. Approval: 2002'),
    ('B', u'Take your dose of LEVOXYL on an empty stomach, at least 30 minutes to 1 hour before breakfast with a full glass of water to avoid choking or gagging.'),
    ('B', u'Adjust the dose by 12.5 mcg to 25 mcg increments every 4 to 6 weeks until the patient is clinically euthyroid and the serum TSH returns to normal.'),
    ('B', u'Inactive ingredients: microcrystalline cellulose, croscarmellose sodium, magnesium stearate, calcium sulfate dihydrate, sodium bicarbonate, coloring additives.'),
    ('B', u'start LEVOXYL at 1 mcg per kg body weight per day'),
    ('C', u'Take your dose of TIROSINT 1 time each day, 30 minutes to 1 hour before breakfast, on an empty stomach.'),
    ('C', u'The average full replacement dose of TIROSINT is approximately 1.6 mcg per kg per day'),
    ('C', u'start TIROSINT at 1.0 mcg per kg body weight per day'),
    ('C', u'inactive ingredients in TIROSINT are gelatin, glycerin and water'),
    ('C', u'swallow TIROSINT capsules whole'),
    ('C', u'Initial U.S. Approval: 2000'),
    ('D', u'Full replacement dose is 1.6 mcg/kg/day.'),
    ('D', u'Titrate dosage by 12.5 to 25 mcg increments every 4 to 6 weeks, as needed until the patient is euthyroid.'),
    ('D', u'inactive ingredients butylated hydroxytoluene, calcium phosphate dibasic dihydrate, magnesium stearate, microcrystalline cellulose, povidone, sodium starch glycolate'),
    ('D', u'Initiate Levothyroxine Sodium Tablets at less than the full replacement dose'),
    ('B', u'WARNING: NOT FOR TREATMENT OF OBESITY OR FOR WEIGHT LOSS'),
    ('C', u'WARNING: NOT FOR TREATMENT OF OBESITY or FOR WEIGHT LOSS'),
    ('A', u'WARNING: NOT FOR TREATMENT OF OBESITY OR FOR WEIGHT LOSS'),
]
F['atom_tags'] = [a for a, _ in ATOMS]
F['atom_n'] = len(ATOMS)

io.open('corpus/_b67meas.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms67.txt', 'w', encoding='utf-8') as f:
    for a, s in ATOMS:
        f.write(s + '\n')

print('== B67 pick: 四份左甲状腺素说明书 ==')
print('壳账 bytes', F['bytes'])
print('body_at', F['body_at'], 'hl_at', F['hl_at'], 'fpi_at', F['fpi_at'])
print('dailymed壳', F['dailymed_shell'], 'comments', F['comments'], 'sections', F['sections'])
print('updated', F['updated'])
print('ndc_like', F['ndc_like'])
print('获批年', F['appr_year'], 'appr计数', F['appr'])
print('capsule', F['capsule'], 'tablet', F['tablet_word'], 'nda', F['ndaname'], 'anda', F['anda'])
print('黑框 高档', F['warn_case_ORFOR'], '低档', F['warn_case_orFOR'])
print('half_to_one', F['half_to_one'], 'min30', F['min30'], 'full_glass', F['full_glass'], 'choking', F['choking'])
print('ppi', F['ppi'], 'issued', F['issued'], F['issued_str'])
print('赋形剂句:')
for tg, s in zip(TAGS, F['exc_sentence']):
    print('  ', tg, s[:150])
print('d16', F['d16'], 'd16kg', F['d16kg'], 'd16pkg', F['d16pkg'])
print('d125', F['d125'], 'd125to25', F['d125to25'], 'd125_to25', F['d125_to25'])
print('d100dash', F['d100dash'], 'd100to', F['d100to'], 'd10', F['d10'], 'd1pkg', F['d1pkg'])
print('w46', F['w46'], 'w24', F['w24'], 'tsh<10', F['tsh10'], F['tsh10w'], '93%', F['bioavail'])
print('mcg token', F['mcg_token'], 'tsh', F['tsh_mentions'])
print('atom 数', F['atom_n'])
