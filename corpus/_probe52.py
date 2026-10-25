# -*- coding: utf-8 -*-
"""B52 探测: 一张只谈“从现在起”的时效表(zonenow.tab) ⇎ 它的分组注释 ⇎ 检查它的 awk(其输入表在库里根本不存在)。
本脚本只测量与打印, 不写条目。要回答的问题:
  1) 表的组织原则(按标准时 UTC 偏移排序)住在哪一列? —— 若不住在列里, 断言就只能靠注释行;
  2) 头部声称“第一列无关且被忽略”, 检查器真的不读它吗;
  3) 检查器凭什么判“从现在起一致”——它读的那份 zdump 表在不在库内;
  4) 注释行声称的偏移分组与行序是否自洽(偏移序列是否单调、同一组内是否真的相邻);
  5) 每一行的第四列(注释)是否非空、第一列是否恒为 XX 或真国码;
  6) 与姊妹表 zone1970.tab ⇎ zone.tab 的行/区/国码关系(同一批时区被切成两种“一致”口径)。
"""
import io, os, re, sys, glob, collections

sys.stdout.reconfigure(encoding='utf-8')
NOW = u'corpus/raw/tz/zonenow.tab'
Z19 = u'corpus/raw/tz/zone1970.tab'
ZON = u'corpus/raw/tz/zone.tab'
CHK = u'corpus/raw/tz/checknow.awk'
OUT = u'corpus/_probe52.txt'
L = []
def P(s):
    L.append(s if isinstance(s, str) else str(s))
    print(s)

def load(p):
    return io.open(p, encoding='utf-8', errors='replace').read()

T = {k: load(v) for k, v in (('now', NOW), ('1970', Z19), ('zone', ZON), ('chk', CHK))}
for k, v in (('now', NOW), ('1970', Z19), ('zone', ZON)):
    ln = [x for x in T[k].split(u'\n') if x]
    com = [x for x in ln if x.startswith(u'#')]
    dat = [x for x in ln if not x.startswith(u'#')]
    tabn = [x for x in dat if u'\t' in x]
    P(u'%s: 非空行 %d = 注释 %d + 数据 %d; 数据里带制表符的 %d; 字节 %d'
      % (k, len(ln), len(com), len(dat), len(tabn), os.path.getsize(v)))
    flds = collections.Counter(len(x.split(u'\t')) for x in tabn)
    P(u'   每行字段数分布 %s' % dict(sorted(flds.items())))

dat = [x for x in T['now'].split(u'\n') if x and not x.startswith(u'#')]
rows = [x.split(u'\t') for x in dat]
c1 = collections.Counter(r[0] for r in rows)
P(u'\nzonenow 第一列取值分布: %s (种类 %d)' % (dict(c1.most_common(6)), len(c1)))
P(u'   头部原话: %s' % [x for x in T['now'].split(u'\n') if u'first column' in x])
z3 = [r[2] for r in rows]
P(u'第三列(TZ)行数 %d, 去重 %d, 含逗号的 %d, 含斜杠多段的 %d' % (len(z3), len(set(z3)), len([z for z in z3 if u',' in z]), len([z for z in z3 if z.count(u'/') > 1])))
P(u'   多时区行的例子: %s' % [r[2] for r in rows if u',' in r[2]][:3])
c4 = [r[3] if len(r) > 3 else u'' for r in rows]
P(u'第四列非空行数 %d/%d; 空注释行 %d; 含分号(合并多地)的 %d'
  % (len([x for x in c4 if x.strip()]), len(rows), len([x for x in c4 if not x.strip()]), len([x for x in c4 if u';' in x])))

# ---- 组织原则住在哪一层: 注释行的偏移标签 ⇎ 数据行序 ----
lines = T['now'].split(u'\n')
def parse_tag(body):
    m = re.match(u'^([-+]\\d{2}(?::\\d{2})?)(?:/([-+]\\d{2}(?::\\d{2})?))?(.*)$', body)
    if not m:
        return None
    rest = m.group(3)
    ab = u''
    if rest.startswith(u' - '):
        ab = rest[3:]
        ab = re.sub(u' \\([^)]*\\)$', u'', ab)
    return (m.group(1), m.group(2), ab, body)
grp = []
cur = None
tagall, tagmiss = 0, []
for x in lines:
    if x.startswith(u'#'):
        body = x[1:].strip()
        if re.match(u'^[-+]\\d{2}', body):
            tagall += 1
            p = parse_tag(body)
            if p is None:
                tagmiss.append(x)
                continue
            cur = [body, 0, [], p[1], p[2]]
            grp.append(cur)
    elif x and cur is not None:
        cur[1] += 1
        f = x.split(u'\t')
        cur[2].append((f[2], f[3] if len(f) > 3 else u''))
P(u'\n偏移标签注释行 %d 行, 其中可解析 %d, 解析失败 %d: %s' % (tagall, len(grp), len(tagmiss), tagmiss[:3]))
P(u'偏移分组注释行 %d 组; 组内行数合计 %d; 未归组的 %d'
  % (len(grp), sum(g[1] for g in grp), len(rows) - sum(g[1] for g in grp)))
P(u'   组内行数分布 %s (标签行数 ⇎ 数据行数 = %d ⇎ %d)'
  % (dict(sorted(collections.Counter(g[1] for g in grp).items())), tagall, len(rows)))
P(u'   带第二枚偏移(DST)的组 %d; 带缩写的组 %d; 两组之间夹的纯注释行(#) %d'
  % (len([g for g in grp if g[3]]), len([g for g in grp if g[4]]),
     len([x for x in lines if x == u'#'])))
P(u'   前 6 组标签: %s' % [g[0] for g in grp[:6]])
P(u'   双偏移组标签例子: %s' % [g[0] for g in grp if g[3]][:4])
P(u'   行数最多的 4 组: %s' % sorted([(g[0], g[1]) for g in grp], key=lambda q: -q[1])[:4])
P(u'   空组(有标签无行) %d 个: %s' % (len([g for g in grp if g[1] == 0]), [g[0] for g in grp if g[1] == 0][:8]))
# 声称的偏移序: 把标签里的十进制小时取出来看是否单调
def hh(tag):
    m = re.match(u'^([-+])(\\d{2})(?::(\\d{2}))?', tag)
    return (1 if m.group(1) == u'+' else -1) * (int(m.group(2)) + int(m.group(3) or 0) / 60.0)
try:
    seq = [hh(g[0]) for g in grp]
    P(u'   组标签偏移是否单调不减: %s; 首末 %s ⇎ %s; 逆序对数 %d'
      % (seq == sorted(seq), seq[0], seq[-1], len([(i, j) for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j]])))
    P(u'   偏移种类 %d 种; 同一偏移出现两次以上的 %s' % (len(set(seq)), sorted([k for k, c in collections.Counter(seq).items() if c > 1])))
except Exception as e:
    P(u'   组标签解析失败: %r' % (e,))
# 标签里的缩写 ⇎ 同一行第四列末尾括号里的缩写: 组织键与可读键是否闭合
ABP = []
for g in grp:
    if not g[4]:
        continue
    z, cm = (g[2][0] if g[2] else (u'', u''))
    m2 = re.search(u'\\(([^()]*)\\)\\s*$', cm)
    ABP.append((g[4], m2.group(1) if m2 else u'', z))
withpar = [(a, b, z) for a, b, z in ABP if b]
sameraw = [(a, b) for a, b, _ in withpar if a.split(u' ')[-1] == b]
sameflat = [(a, b) for a, b, _ in withpar if a.replace(u' ', u'').split(u' ')[-1] == b.replace(u' ', u'')
            or a.split(u' ')[-1].replace(u' ', u'') == b.replace(u' ', u'')]
P(u'   带缩写的标签 %d; 同行注释以括号缩写收尾的 %d; 逐字相等 %d; 去空格后相等 %d'
  % (len(ABP), len(withpar), len(sameraw), len(sameflat)))
P(u'   去空格仍不等的例子: %s' % [(a, b) for a, b, _ in withpar
                                 if a.split(u' ')[-1].replace(u' ', u'') != b.replace(u' ', u'')][:5])
ABTAG = set(g[2][0][0] for g in grp if g[4] and g[2])
P(u'   有括号缩写而标签无缩写的行数(反方向): %d'
  % len([r for r in rows if re.search(u'\\(([^()]*)\\)\\s*$', r[3]) and r[2] not in ABTAG]))
# 每一组恰一行时: 标签序 ⇎ 行序 是否同一序列(1:1 交错)
P(u'   标签与数据行是否严格 1:1 交错: %s' % (len([g for g in grp if g[1] == 1]) == len(grp) and len(grp) == len(rows)))
# 表里有没有“偏移”这一列
hdr = [x for x in lines if x.startswith(u'#XX') or x.startswith(u'#\tXX') or u'coordinates' in x and x.startswith(u'#')]
P(u'   列头注释行: %s' % hdr)
P(u'   任何数据列里出现 :00 之类偏移写法的行数: %d' % len([r for r in rows if re.search(u'^[+-]\\d{2}:?\\d{2}$', r[0])]))
# 坐标列的形状口径: 度分秒位数不齐
cw = collections.Counter(len(r[1]) for r in rows)
P(u'   坐标字符数分布 %s; 以 0 补位的 %d 行; 秒位缺失(只有分)的 %d 行'
  % (dict(sorted(cw.items())), len([r for r in rows if r[1][1:3] == u'01' or r[1].startswith(u'+0') or r[1].startswith(u'-0')]),
     len([r for r in rows if len(r[1]) in (9, 10)])))
latlon = [re.match(u'^([+-])(\\d{2,3})(\\d{2})?([+-])(\\d{2,3})(\\d{2})?$', r[1]) for r in rows]
P(u'   坐标可解析 %d/%d; 纬度位数种类 %s ⇎ 经度位数种类 %s'
  % (len([m for m in latlon if m]), len(rows),
     sorted(set(len(m.group(2)) for m in latlon if m)), sorted(set(len(m.group(5)) for m in latlon if m))))
P(u'   同一纬度位数在不同行混用: %s' % (len(set(len(m.group(2)) for m in latlon if m)) > 1))
# 注释列的“分号合并且多地”写法 ⇎ 括号缩写 ⇎ 时区名本身
P(u'   第四列含分号的 %d ⇎ 含括号的 %d ⇎ 含“; ”的 %d; 第四列里出现国名/地区词的例: %s'
  % (len([r for r in rows if u';' in r[3]]), len([r for r in rows if u'(' in r[3]]),
     len([r for r in rows if u'; ' in r[3]]), [r[3][:28] for r in rows[:3]]))
# 时效表里带“未来日期”的行: 表只谈 now, 却在标签里写下了会过期的日子
DATED = []
for x in lines:
    for m in re.finditer(u'(\\d{4}-\\d{2}-\\d{2})(?: (\\d{2}:\\d{2}))?', x):
        DATED.append((x.startswith(u'#'), m.group(1), m.group(2), x.strip()[:78]))
P(u'\n带 ISO 日期的行 %d(注释 %d ⇎ 数据 %d); 日期集合 %d 种: %s'
  % (len(DATED), len([d for d in DATED if d[0]]), len([d for d in DATED if not d[0]]),
     len(set(d[1] for d in DATED)), sorted(set(d[1] for d in DATED))))
for d in DATED[:12]:
    P(u'   [%s] %s %s | %s' % (u'注释' if d[0] else u'数据', d[1], d[2] or u'', d[3]))
# 头部“from now on”这句话本身
P(u'\n头部谓词句: %s' % [x for x in lines if u'now on' in x])
P(u'   出现 “now” 的行数 %d; 出现 “1970” 的行数 %d' % (len([x for x in lines if u'now' in x]), len([x for x in lines if u'1970' in x])))

# ---- 检查器读哪些字段 ⇎ 它要的外部输入 ----
A = T['chk']
P(u'\nchecknow.awk: 字节 %d 行数 %d' % (os.path.getsize(CHK), len([x for x in A.split(u'\n') if x])))
P(u'   出现的字段引用 $n: %s' % sorted(set(re.findall(u'\\$(\\d)', A))))
P(u'   FS 赋值: %s' % re.findall(u'FS = .*', A))
P(u'   外部变量: %s' % sorted(set(re.findall(u'\\b(zdump_table|now_out|now|zonenow_table|srcdir)\\b', A))))
P(u'   被引用但从未赋值的输入文件名在库内是否存在: zdump_table -> %s'
  % [os.path.basename(x) for x in glob.glob(u'corpus/raw/tz/*zdump*') + glob.glob(u'corpus/raw/tz/admin/*zdump*')])
P(u'   诊断语句(printf 首参): %s' % re.findall(u'printf "([^"]*)"', A))
P(u'   退出与状态: %s' % re.findall(u'(status = 1|exit status|if \\(now_out\\))', A))
P(u'   是否提到 -v zdump_table 或 Makefile 里的生成处: %s'
  % len([1 for f in (u'corpus/raw/tz/Makefile',) if os.path.exists(f) and u'zdump_table' in io.open(f, encoding='utf-8', errors='replace').read()]))
mk = io.open(u'corpus/raw/tz/Makefile', encoding='utf-8', errors='replace').read() if os.path.exists(u'corpus/raw/tz/Makefile') else u''
P(u'   Makefile 里含 zdump_table 的行 %d 条; 含 checknow 的行 %d 条'
  % (len([x for x in mk.split(u'\n') if u'zdump_table' in x]), len([x for x in mk.split(u'\n') if u'checknow' in x])))
for x in [x for x in mk.split(u'\n') if u'zdump_table' in x or u'checknow' in x][:8]:
    P(u'      %s' % x.strip()[:160])

# ---- 三种“一致”口径的姊妹表关系 ----
def zones(p):
    o = []
    for x in [y for y in load(p).split(u'\n') if y and not y.startswith(u'#')]:
        f = x.split(u'\t')
        if len(f) > 2:
            o.append((f[0], f[2]))
    return o
ZN, Z7, ZT = zones(NOW), zones(Z19), zones(ZON)
sn, s7, st = set(z for _, z in ZN), set(z for _, z in Z7), set(z for _, z in ZT)
P(u'\n时区名集合: zonenow %d 行 ⇎ zone1970 %d 行 ⇎ zone.tab %d 行' % (len(ZN), len(Z7), len(ZT)))
P(u'   去重后: now %d ⇎ 1970 %d ⇎ tab %d; now−1970 %s; 1970−now %d 个' % (len(sn), len(s7), len(st), sorted(sn - s7)[:5], len(s7 - sn)))
P(u'   1970−now 前 8: %s' % sorted(s7 - sn)[:8])
P(u'   tab−now %d 个 ⇎ now−tab %d 个' % (len(st - sn), len(sn - st)))
P(u'   zonenow 第一列全为 XX 的行 %d/%d; zone1970 第一列多码行(含逗号) %d'
  % (len([r for r in rows if r[0] == u'XX']), len(rows), len([z for z, _ in Z7 if u',' in z])))
CZN = {z: c for c, z in ZN}
CZ7 = {z: c for c, z in Z7}
P(u'   同一时区在两表里国码不同的行数: %d' % len([z for z in sn & s7 if CZN[z] != CZ7[z]]))
P(u'   例子: %s' % [(z, CZN[z], CZ7[z]) for z in sorted(sn & s7) if CZN[z] != CZ7[z]][:5])
# 坐标是否同值(表声称 zonenow 与 zone1970 描述同一批区, 坐标应一致)
cn = {r[2]: r[1] for r in rows}
c7 = {}
for x in [y for y in T['1970'].split(u'\n') if y and not y.startswith(u'#')]:
    f = x.split(u'\t')
    if len(f) > 2:
        c7[f[2]] = f[1]
same = len([z for z in cn if z in c7 and cn[z] == c7[z]])
P(u'   坐标一致的共有时区 %d/%d(共有 %d)' % (same, len(cn), len([z for z in cn if z in c7])))
P(u'   坐标不一致的例子: %s' % [(z, cn[z], c7[z]) for z in sorted(cn) if z in c7 and cn[z] != c7[z]][:4])

io.open(OUT, 'w', encoding='utf-8', newline=u'\012').write(u'\n'.join(L) + u'\n')
P(u'\n-> %s (%d 行)' % (OUT, len(L)))
