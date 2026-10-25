# -*- coding: utf-8 -*-
# B85 建条目: 单文本压缩(SQLite 3.54.0 发布说明 → BabelTele)。数字逐字保真, 覆盖全部条目。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

F = json.load(io.open('corpus/_b85meas.json', encoding='utf-8'))
REG = {}


def V(name):
    v = F[name][0]
    REG.setdefault(str(v), u"B85V('%s')" % name)
    return v


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


raw = io.open('corpus/raw/changelog/sqlite_b.txt', encoding='utf-8', errors='replace').read()
FACE = pnorm(u' '.join(raw.partition(u'\n\n')[2].split()))

ATOMS = [l.strip() for l in io.open('corpus/_atoms85.txt', encoding='utf-8').read().splitlines() if l.strip()]
for a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中: %s' % a[:60]

E = []
E.append(u'🧭 源账: SQLite 3.54.0 发布说明(2026-10-09, %d 字符⇎%d 词), 五组: CLI 增强⇎查询计划器⇎新接口⇎日期/时间⇎Windows 平台; 收尾哈希双锚(SQLITE_SOURCE_ID⇎SHA3-256 各 %d 处)。'
         % (V('chars'), V('words'), V('n_sqlite_source_id')))

E.append(u'🖥 CLI 组(9 条): ①提示串可含转义序列显示状态, 初值取 SQLITE_PS1⇎SQLITE_PS2 环境变量; ②默认提示用上新转义; ③列输出模式⇒无行也显示列头(默认); ④新 diskused() 扩展实现 .diskused 点命令 ⟦A⟧⟨Use the new diskused() extension to implement the ".diskused" dot-command.⟩——取代 sqlite3_analyzer(已弃用); ⑤unix 上 BLOB 原样输出保留零字节; ⑥.mode 新选项 --rowcount on⇎--titles always(后者已成默认, 旧观感用 -titles on 还原); ⑦--ifmt⇎--fpfmt: 整数⇎浮点渲染可用 printf 风格格式串精控; ⑧-csv 命令行选项自动关显示上限(兼容旧); ⑨提示尊重 NO_COLOR。')

E.append(u'⚠️ 破坏性变更: 行仅 "go" 或 "/" 结束 SQL 命令的兼容(分别为 SQL Server⇎Oracle)被终止 ⟦B⟧⟨The ability to end an SQL command using the line that contains just "go" or "/"⟩——除非编译期 -DSQLITE_SHELL_LEGACY_COMMAND_TERMINATOR; ALTER TABLE 对列名 ROWID⇎_ROWID_⇎OID 三特名增删改均报错 ⟦C⟧⟨The ALTER TABLE command raises an error on any attempt to add, drop, or rename columns with the special names⟩。')

E.append(u'🧮 查询计划器四条: 表有表达式索引时 UPDATE 不改值则不动索引; "expr OR TRUE"⇎"expr OR FALSE" 优化加强; IN 右侧 SELECT 的 DISTINCT 被忽略; UNION+LIMIT 恰 1 更快更省内存。')

E.append(u'🔌 新接口组: diskused() 升为 SQL 函数(可选扩展); printf()⇎format() 增 %J⇎%j 转换渲染 JSON 串字面 ⟦D⟧⟨Added the %J and %j conversions used to render JSON string literals⟩; 新 sqlite3_result_str()(内部简化代码); 新 sqlite3_incomplete()(用于提示串管理); sqlite3_limit() 增 SQLITE_LIMIT_SCHEMA⇎SQLITE_LIMIT_TRIGGER_STEPS 两上限; authorizer 回调现在也对 CREATE TABLE 的 DEFAULT 子句里的 SQL 函数触发(建表时⇎默认值实际使用时, 开库读模式时不)。')

E.append(u'📅 日期/时间: weekday 修饰符新增 "weekday -N" 形式 ⟦E⟧⟨Added the "weekday -N" form of the weekday modifier⟩; 新增 end of 修饰符; 临时文件改用 O_TMPFILE(支持的系统)。')

E.append(u'🪟 Windows 平台七条: 弃 XP 及更早(含 WindowsCE)⇒须 Vista(约 2007)起 ⟦F⟧⟨Drop support for WindowsXP and earlier Windows versions⟩; 非递归互斥改用 SRWL(Slim Reader/Writer Locks)取代 CriticalSection(全支持平台皆有); UWP⇎WebUI 应用用 -DSQLITE_UWP=1; 明示: 以上仅 Windows——Linux⇎Mac⇎BSD⇎其他 unix 构建不受影响。')

E.append(u'⚡ 性能账: 约快 4%(Linux x64 上 valgrind 数 CPU 周期的 speedtest1 基准) ⟦G⟧⟨About 4% faster, as measured by counting CPU cycles in the speedtest1⟩⇎同比一年前(3.51.0)约快 7.5%——随负载⇎构建选项⇎CPU⇎编译器⇎系统而异。')

E.append(u'ℒ 方法 ⇒ 截止后冷门专业文本的压缩判据: 事实零丢失(每条目一行), 数值与标识符逐字保真(3.54.0⇎3.51.0⇎4%%⇎7.5%%⇎全部宏名), 谱系做成键(diskused %d 处贯穿点命令⇎SQL 函数两处身份, windows %d 处聚焦平台组, sqlite3_ %d 处标接口组)。'
         % (V('n_diskused'), V('n_windows'), V('n_sqlite3_')))

enc = u'\n'.join(E)

assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
SRC_ALL = FACE.replace(u' ', u'')
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok) in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))

orig = u'### ⟦A⟧ ⟸ corpus/raw/changelog/sqlite_b.txt\n\n' + u'\n\n'.join(ATOMS)

title = (u'# B85 单文本压缩: SQLite 3.54.0 发布说明(%d 词, 截止后冷门专业信息)→算子中文——'
         u'五组 40+ 条事实零丢失, 破坏性变更(行终止符 go// 废止⇎ROWID 三特名报错)单列\n' % F['words'][0])
srcline = (u'src: corpus/raw/changelog/sqlite_b.txt (%d 字符) '
           u'(单文本压缩: 源=sqlite.org changes 页 3.54.0 段, 2026-10 发布即本库抓取, 任何模型训练分布之外; '
           u'数字与标识符一律逐字保留)\n' % F['chars'][0])
tagsline = (u'tags: 单文本压缩 截止后专业信息 事实零丢失键(每条目一行) 破坏性变更单列 标识符逐字保真键 谱系键(diskused/windows/sqlite3_) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B85_sqlite_release_notes_compression.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b85flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B85 建条目: %s' % out)
print(u'编码区 %d 字符(不含换行), 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
