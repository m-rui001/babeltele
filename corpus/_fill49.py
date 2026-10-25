# -*- coding: utf-8 -*-
"""B49 ⛓解读注: 工具侧数字全部取自 corpus/_b49battery.json(_probe49k.py 实测落盘), 不手填。"""
import io, re, json

ENTRY = u'corpus/babeltele/B49_table_checker_and_checked_data.md'
BAT = json.load(io.open(u'corpus/_b49battery.json', encoding='utf-8'))
DATA = [u'africa', u'antarctica', u'asia', u'australasia', u'europe', u'northamerica',
        u'southamerica', u'etcetera', u'factory', u'backward']
g = lambda k: BAT[k]
kinds = lambda k: u'；'.join(sorted({re.sub(r'^[^:]*: \d+: ', '', re.sub(r'^[^:]*: ', '', x))
                                    for x in [g(k)['first_err']]}) or [u'—'])
TOP = lambda k, n=4: u' '.join(u'%s×%d' % (a, b) for a, b in g(k).get('top_cc', g(k).get('top_prefix', []))[:n])

TAB = [u'd_coord', u'd_order', u'd_misscomment', u'd_extracomment', u'd_unknowncc', u'd_fivecol',
       u'd_duprow']
ISO = [u'd_extracol', u'd_lower', u'd_dupcode', u'd_samename', u'd_swap']
DAT = [u'd_rename', u'd_stdoff', u'd_month', u'd_ruleunused', u'd_ruleletters']
CODE = [u'c_cc_lt', u'c_cc_lt_zonetab', u'c_cc_lt_noexempt', u'c_exempt_dead', u'c_backward',
        u'c_iso_lt', u'c_usedmax', u'c_nf3', u'c_main_etc', u'c_end_etc', u'c_seen_off', u'c_warn_on']
CRLF = [u'crlf_zone1970.tab', u'crlf_iso3166.tab', u'crlf_europe', u'crlf_ALL3', u'crlf_checktab.awk']


def row(k):
    v = g(k)
    return (u'| %s | %d | %d | %d | %s |' % (k.lstrip(u'dic_').replace(u'_', u' '), v['exit'],
                                            v['nerr'], v['nout'],
                                            (v['first_err'] or v['first_out'] or u'—')))


L = []
A = L.append
A(u'**怎么跑**: 本机 gawk 5.3.2(API 4.0) 按程序 BEGIN 里的默认取名——'
  u'`gawk -f checktab.awk -v iso_table=iso3166.tab -v zone_table=<表名> -v want_warnings=0` 再跟十份数据文件 '
  u'(%s)。`iso_table ⇎ zone_table ⇎ want_warnings` 三个变量都有默认值, 命令行只决定"给哪张表定性"; '
  u'数据文件走 ARGV 由主规则逐行读, 两张表走 getline 在 BEGIN 里读。基线: zone1970.tab 与 zone.tab 都是 exit %d、'
  u'stderr %d 字节、stdout %d 字节——判决的正常形态是空, 所以后面每张表都得先把东西改坏才看得见。'
  % (u' '.join(DATA), g('base_zone1970.tab')['exit'], g('base_zone1970.tab')['bytes_err'],
     g('base_zone1970.tab')['bytes_out']))
A(u'')
A(u'**数据侧逐条破坏**(每次只改一处, 其余还原; 表侧改 zone1970.tab, 码表侧改 iso3166.tab, 数据侧改 europe):')
A(u'')
A(u'| 场景 | exit | stderr 行 | stdout 行 | 首条诊断 |')
A(u'|---|---|---|---|---|')
for k in TAB + ISO + DAT:
    A(row(k))
A(row(u'restore'))
A(u'')
A(u'共 %d 类(表侧 %d ⇎ 码表侧 %d ⇎ 数据侧 %d)再加还原一次(%s: exit %d、两条流 %d+%d 字节)。'
  u'多数场景只落 1 行诊断; 两处例外: 把首码换成码表里没有的 `QQ` 得 %d 行(%s), 多塞两列也得 %d 行——'
  u'一处破坏常同时踩中两条检查; 复制整行则得 %d 行, 且它走 stdout 而非 stderr: %s。'
  % (len(TAB) + len(ISO) + len(DAT), len(TAB), len(ISO), len(DAT), u'还原',
     g('restore')['exit'], g('restore')['bytes_err'], g('restore')['bytes_out'],
     g('d_unknowncc')['nerr'], g('d_unknowncc')['first_err'], g('d_fivecol')['nerr'],
     g('d_duprow')['nout'], g('d_duprow')['first_out']))
A(u'')
A(u'**码侧变异**(只动程序里的比较符与常量, 数据一律不动; 比较符就是数据被容忍的程度):')
A(u'')
A(u'| 改动 | exit | stderr 行 | stdout 行 | 首条诊断 |')
A(u'|---|---|---|---|---|')
for k in CODE:
    A(row(k))
A(u'')
lt, ltz, ltx, ex = g('c_cc_lt'), g('c_cc_lt_zonetab'), g('c_cc_lt_noexempt'), g('c_exempt_dead')
A(u'一枚 `<` 换成 `<=` 把相邻相等的首码全判成越序: %d 行(zone1970.tab, top %s)。同一条改动落在 zone.tab 上是 %d 行, '
  u'再把豁免串改成 `zone.tabZ` 就是 %d 行——那条 Crimea 豁免的重量正好 %d 行; 不动比较符、只改死豁免串仍得 %d 行(%s), '
  u'因为 zone.tab 本身严格递增, 豁免在此刻是空转的保险。'
  % (lt['nerr'], TOP('c_cc_lt'), ltz['nerr'], ltx['nerr'], ltx['nerr'] - ltz['nerr'],
     ex['nerr'], ex['first_err']))
A(u'三处"改坏守卫却一行都不要"的对照: `FILENAME != "backward"` 改死 ⇒ %d 行; 码表顺序检查 `cc <= cc0` 收回 `cc < cc0` ⇒ %d 行'
  u'(码表严格递增, 一枚比较符的余量为 0); `used_max <= 1` 收成 `< 1` ⇒ %d 行(注释的"多余"与"缺失"两检查一起哑火)。'
  % (g('c_backward')['nerr'], g('c_iso_lt')['nerr'], g('c_usedmax')['nerr']))
A(u'两枚 Etc 守卫分居两地, 效果完全不对称: 主循环放行 Etc ⇒ %d 行 `no data for`(top %s; 数据里有 Etc 名而表里没有); '
  u'END 放行 Etc ⇒ %d 行(表里没有 Etc 名, 白改); 把主循环整个记录块关掉(`if (0 && ...)`, 于是 `zoneSeen[tz] = 1` 永不执行) '
  u'⇒ %d 行 `no Zone table for`, 恰为表行数, 前缀分布 %s, 首条 %s——此时 `no data for` 一并消失, 因为它就写在同一个块里。'
  % (g('c_main_etc')['nerr'], TOP('c_main_etc', 1), g('c_end_etc')['nerr'], g('c_seen_off')['nerr'],
     TOP('c_seen_off'), g('c_seen_off')['first_err']))
w = g('c_warn_on')
A(u'`want_warnings` 不改代码、只拧命令行开关(0 ⇒ 1): exit %d、stderr %d 行、stdout %d 行, 首条 %s。'
  u'警告不参与 `exit status`, 所以"全绿"的运行里可以已经躺着 %d 行未命中的点位符——这一类是判决之外的旁白。'
  % (w['exit'], w['nerr'], w['nout'], w['first_out'], w['nout']))
A(u'')
cr = u' ⇎ '.join(u'%s: exit %d、%d+%d 行' % (k.split(u'_', 1)[1], g(k)['exit'], g(k)['nerr'], g(k)['nout'])
                 for k in CRLF)
A(u'**行尾不是不变量**: 把副本改成 CRLF(%s)——诊断全为 0。在 `FS="\\t"` 之下每行末尾多出的 `\\r` 会并进最后一列, '
  u'于是"顺序"比较变成带尾巴的比较, 所有检查一起哑火; 程序自身换成 CRLF 也一样哑(它照跑, 只是再也判不出坏)。'
  u'顺带一个 Windows 陷阱: 变异副本必须二进制读写, 用文本模式写就等于每一步都先替上面这组实验铺好 `\\r`。' % cr)
A(u'')
A(u'**为什么这些数字只写在注里**: 执行结果不属于任何一份 raw, 它属于"这台机器上的 gawk 与这份副本"; '
  u'正文与 src 行里的每个形状数(158 ⇎ 249 ⇎ 312 ⇎ 1020⇎1027 ⇎ 29⇎36 ⇎ 503⇎12 ⇎ 447=440+7 ⇎ 18⇎17⇎15⇎14)都由 '
  u'audit.py 里 B49V/B49_LINES/B49_DROP/B49_BYTES 从三份 raw 现算复验, 而上面两张表只由本注的 JSON 供数——'
  u'两边一旦互相冒充(把 158 行诊断当成表形状, 或把 312 当成执行结果), 门槛立刻断。')
NOTES = u'\n'.join(L)
t = io.open(ENTRY, encoding='utf-8').read()
assert u'<!--FILL-->' in t
io.open(ENTRY, 'w', encoding='utf-8').write(t.replace(u'<!--FILL-->', NOTES))
print(u'notes written: %d chars; 场景 数据侧 %d + 码侧 %d + CRLF %d + 基线 2 + 还原 1'
      % (len(NOTES), len(TAB) + len(ISO) + len(DAT), len(CODE), len(CRLF)))
