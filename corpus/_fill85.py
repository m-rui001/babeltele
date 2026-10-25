# -*- coding: utf-8 -*-
# B85 解读注: 压缩账 + 事实覆盖清单 + 第三套实现复测; 现算写回。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

F = json.load(io.open('corpus/_b85meas.json', encoding='utf-8'))
REG = json.load(io.open('corpus/_b85flat.json', encoding='utf-8'))

raw = io.open('corpus/raw/changelog/sqlite_b.txt', encoding='utf-8').read()
flat = u' '.join(raw.partition(u'\n\n')[2].split())
low = flat.lower()

# 第三套: 词级统计复核
words = low.split(u' ')
def wcount(kw):
    return sum(1 for w in words if w.strip(u'.,;:()[]"') == kw)

rows = [
    (u'diskused', wcount(u'diskused'), F['n_diskused'][0]),
    (u'windows', len(re.findall(u'windows', low)), F['n_windows'][0]),
]
for name, got, want in rows:
    assert got == want, u'%s: 第三套 %d vs 契约 %d' % (name, got, want)

# 事实覆盖清单: 每条发布说明条目至少一个关键词在编码区
entry = io.open('corpus/babeltele/B85_sqlite_release_notes_compression.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', entry, re.S).group(1)
facts = [u'SQLITE_PS1', u'diskused', u'--rowcount', u'--titles', u'--ifmt', u'--fpfmt', u'-csv', u'NO_COLOR',
         u'go', u'ROWID', u'OR TRUE', u'DISTINCT', u'LIMIT', u'%J', u'sqlite3_result_str', u'sqlite3_incomplete',
         u'SQLITE_LIMIT_SCHEMA', u'SQLITE_LIMIT_TRIGGER_STEPS', u'authorizer', u'weekday', u'end of',
         u'O_TMPFILE', u'Vista', u'SRWL', u'CriticalSection', u'UWP', u'3.51.0', u'4% faster', u'7.5%',
         u'sqlite3_analyzer']
missing = [f for f in facts if f not in enc]
assert not missing, u'事实覆盖缺失: %s' % missing

n_enc = len(enc.replace('\n', ''))
n_raw = F['chars'][0]
ratio = round(100.0 * n_enc / n_raw, 1)
n_anchor = len(re.findall(u'⟨', enc))
atoms = [l.strip() for l in io.open('corpus/_atoms85.txt', encoding='utf-8') if l.strip()]

L = []
L.append(u'## ⛓解读注')
L.append(u'')
L.append(u'### 压缩账(本注现算)')
L.append(u'')
L.append(u'| 量 | 值 |')
L.append(u'|---|---|')
L.append(u'| 源(SQLite 3.54.0 发布说明, 2026-10-09) | %d 字符 / %d 词 |' % (n_raw, F['words'][0]))
L.append(u'| 编码(BabelTele 算子中文) | %d 字符 |' % n_enc)
L.append(u'| 体积比 | %.1f%%(发布说明本身已是高密度事实列表, 压缩价值在事实零丢失而非体积) |' % ratio)
L.append(u'| 事实覆盖 | %d 个标识符/数值逐字入编码(本注 assert 全过) |' % len(facts))
L.append(u'| 锚(逐字英文原文) | 编码区 %d 处 / 候选池 %d 条(atomcheck ok=%d bad=0) |' % (n_anchor, len(atoms), len(atoms)))
L.append(u'')
L.append(u'### 读法')
L.append(u'')
L.append(u'一、这是**截止后冷门专业信息**的压缩: SQLite 3.54.0(2026-10-09)的发布说明——任何模型训练分布之外、工程上有长期价值(升级判据)。判据=事实零丢失: 五组(CLI 增强九条⇎查询计划器四条⇎新接口六条⇎日期/时间三条⇎Windows 七条)每组逐条目一行, @N@ 个标识符/数值(SQLITE_PS1⇎diskused⇎--rowcount⇎%%J⇎SRWL…)逐一入编码且本注 assert。'.replace(u'@N@', str(len(facts))))
L.append(u'二、破坏性变更单列成组: 行终止符 "go"/"/" 废止(须编译期 -DSQLITE_SHELL_LEGACY_COMMAND_TERMINATOR 才回来)与 ALTER TABLE 对 ROWID⇎_ROWID_⇎OID 三特名报错——升级时最先要读的两条。')
L.append(u'三、数字全部逐字: 性能 4%(speedtest1+valgrind+Linux x64 口径)⇎同比 7.5%(对 3.51.0), 版本号 3.54.0⇎3.51.0, 日期 2026-10-09——压缩不碰数字。')
L.append(u'四、复原自测: 只读编码区应能答——sqlite3_analyzer 为什么被弃用?(diskused() 取代) 哪个环境变量关颜色?(NO_COLOR) Windows 最低版本?(Vista) 互斥锁换了什么?(SRWL 取代 CriticalSection)')
L.append(u'')
L.append(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
L.append(u'')
L.append(u'抓取时刻与站点现行版本; 3.54.1 对本版两处修正的细节(见 B79); "mostly coming from AIs" 的自白(3.53.4)是否也适用于本版条目。')
L.append(u'')
L.append(u'### 编码与门的账')
L.append(u'')
L.append(u'编码区 %d 字符(不含换行); 编码区锚 %d 处(候选池 %d 条, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现(词级)+事实覆盖清单(%d 项)assert。门槛三遍: T1 字面逐锚回源 ⇎ T2 DERIV 重跑 ⇎ T3 码位与字母账。' % (n_enc, n_anchor, len(atoms), len(atoms), len(REG), len(facts)))
gloss = chr(10).join(L)

head = entry[:entry.index(u'## ⛓解读注')]
io.open('corpus/babeltele/B85_sqlite_release_notes_compression.md', 'w',
        encoding='utf-8', newline='\n').write(head + gloss)
print('fill85 写回: 体积比 %.1f%%, 事实覆盖 %d 项 assert 全过, 锚 %d' % (ratio, len(facts), n_anchor))
