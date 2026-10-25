# B85 单文本压缩: SQLite 3.54.0 发布说明(605 词, 截止后冷门专业信息)→算子中文——五组 40+ 条事实零丢失, 破坏性变更(行终止符 go// 废止⇎ROWID 三特名报错)单列
src: corpus/raw/changelog/sqlite_b.txt (4047 字符) (单文本压缩: 源=sqlite.org changes 页 3.54.0 段, 2026-10 发布即本库抓取, 任何模型训练分布之外; 数字与标识符一律逐字保留)
; tags: 单文本压缩 截止后专业信息 事实零丢失键(每条目一行) 破坏性变更单列 标识符逐字保真键 谱系键(diskused/windows/sqlite3_) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/changelog/sqlite_b.txt

Use the new diskused() extension to implement the ".diskused" dot-command.

The ability to end an SQL command using the line that contains just "go" or "/"

The ALTER TABLE command raises an error on any attempt to add, drop, or rename columns with the special names

Added the %J and %j conversions used to render JSON string literals

Drop support for WindowsXP and earlier Windows versions

About 4% faster, as measured by counting CPU cycles in the speedtest1

Added SQLITE_LIMIT_SCHEMA and SQLITE_LIMIT_TRIGGER_STEPS

Added the "weekday -N" form of the weekday modifier

## ⟪BabelTele⟫
🧭 源账: SQLite 3.54.0 发布说明(2026-10-09, 4047 字符⇎605 词), 五组: CLI 增强⇎查询计划器⇎新接口⇎日期/时间⇎Windows 平台; 收尾哈希双锚(SQLITE_SOURCE_ID⇎SHA3-256 各 1 处)。
🖥 CLI 组(9 条): ①提示串可含转义序列显示状态, 初值取 SQLITE_PS1⇎SQLITE_PS2 环境变量; ②默认提示用上新转义; ③列输出模式⇒无行也显示列头(默认); ④新 diskused() 扩展实现 .diskused 点命令 ⟦A⟧⟨Use the new diskused() extension to implement the ".diskused" dot-command.⟩——取代 sqlite3_analyzer(已弃用); ⑤unix 上 BLOB 原样输出保留零字节; ⑥.mode 新选项 --rowcount on⇎--titles always(后者已成默认, 旧观感用 -titles on 还原); ⑦--ifmt⇎--fpfmt: 整数⇎浮点渲染可用 printf 风格格式串精控; ⑧-csv 命令行选项自动关显示上限(兼容旧); ⑨提示尊重 NO_COLOR。
⚠️ 破坏性变更: 行仅 "go" 或 "/" 结束 SQL 命令的兼容(分别为 SQL Server⇎Oracle)被终止 ⟦B⟧⟨The ability to end an SQL command using the line that contains just "go" or "/"⟩——除非编译期 -DSQLITE_SHELL_LEGACY_COMMAND_TERMINATOR; ALTER TABLE 对列名 ROWID⇎_ROWID_⇎OID 三特名增删改均报错 ⟦C⟧⟨The ALTER TABLE command raises an error on any attempt to add, drop, or rename columns with the special names⟩。
🧮 查询计划器四条: 表有表达式索引时 UPDATE 不改值则不动索引; "expr OR TRUE"⇎"expr OR FALSE" 优化加强; IN 右侧 SELECT 的 DISTINCT 被忽略; UNION+LIMIT 恰 1 更快更省内存。
🔌 新接口组: diskused() 升为 SQL 函数(可选扩展); printf()⇎format() 增 %J⇎%j 转换渲染 JSON 串字面 ⟦D⟧⟨Added the %J and %j conversions used to render JSON string literals⟩; 新 sqlite3_result_str()(内部简化代码); 新 sqlite3_incomplete()(用于提示串管理); sqlite3_limit() 增 SQLITE_LIMIT_SCHEMA⇎SQLITE_LIMIT_TRIGGER_STEPS 两上限; authorizer 回调现在也对 CREATE TABLE 的 DEFAULT 子句里的 SQL 函数触发(建表时⇎默认值实际使用时, 开库读模式时不)。
📅 日期/时间: weekday 修饰符新增 "weekday -N" 形式 ⟦E⟧⟨Added the "weekday -N" form of the weekday modifier⟩; 新增 end of 修饰符; 临时文件改用 O_TMPFILE(支持的系统)。
🪟 Windows 平台七条: 弃 XP 及更早(含 WindowsCE)⇒须 Vista(约 2007)起 ⟦F⟧⟨Drop support for WindowsXP and earlier Windows versions⟩; 非递归互斥改用 SRWL(Slim Reader/Writer Locks)取代 CriticalSection(全支持平台皆有); UWP⇎WebUI 应用用 -DSQLITE_UWP=1; 明示: 以上仅 Windows——Linux⇎Mac⇎BSD⇎其他 unix 构建不受影响。
⚡ 性能账: 约快 4%(Linux x64 上 valgrind 数 CPU 周期的 speedtest1 基准) ⟦G⟧⟨About 4% faster, as measured by counting CPU cycles in the speedtest1⟩⇎同比一年前(3.51.0)约快 7.5%——随负载⇎构建选项⇎CPU⇎编译器⇎系统而异。
ℒ 方法 ⇒ 截止后冷门专业文本的压缩判据: 事实零丢失(每条目一行), 数值与标识符逐字保真(3.54.0⇎3.51.0⇎4%⇎7.5%⇎全部宏名), 谱系做成键(diskused 3 处贯穿点命令⇎SQL 函数两处身份, windows 7 处聚焦平台组, sqlite3_ 4 处标接口组)。

## ⛓解读注

### 压缩账(本注现算)

| 量 | 值 |
|---|---|
| 源(SQLite 3.54.0 发布说明, 2026-10-09) | 4047 字符 / 605 词 |
| 编码(BabelTele 算子中文) | 2111 字符 |
| 体积比 | 52.2%(发布说明本身已是高密度事实列表, 压缩价值在事实零丢失而非体积) |
| 事实覆盖 | 30 个标识符/数值逐字入编码(本注 assert 全过) |
| 锚(逐字英文原文) | 编码区 7 处 / 候选池 8 条(atomcheck ok=8 bad=0) |

### 读法

一、这是**截止后冷门专业信息**的压缩: SQLite 3.54.0(2026-10-09)的发布说明——任何模型训练分布之外、工程上有长期价值(升级判据)。判据=事实零丢失: 五组(CLI 增强九条⇎查询计划器四条⇎新接口六条⇎日期/时间三条⇎Windows 七条)每组逐条目一行, 30 个标识符/数值(SQLITE_PS1⇎diskused⇎--rowcount⇎%%J⇎SRWL…)逐一入编码且本注 assert。
二、破坏性变更单列成组: 行终止符 "go"/"/" 废止(须编译期 -DSQLITE_SHELL_LEGACY_COMMAND_TERMINATOR 才回来)与 ALTER TABLE 对 ROWID⇎_ROWID_⇎OID 三特名报错——升级时最先要读的两条。
三、数字全部逐字: 性能 4%(speedtest1+valgrind+Linux x64 口径)⇎同比 7.5%(对 3.51.0), 版本号 3.54.0⇎3.51.0, 日期 2026-10-09——压缩不碰数字。
四、复原自测: 只读编码区应能答——sqlite3_analyzer 为什么被弃用?(diskused() 取代) 哪个环境变量关颜色?(NO_COLOR) Windows 最低版本?(Vista) 互斥锁换了什么?(SRWL 取代 CriticalSection)

### 本条不能由在库文件判定的(只登记, 不进门槛)

抓取时刻与站点现行版本; 3.54.1 对本版两处修正的细节(见 B79); "mostly coming from AIs" 的自白(3.53.4)是否也适用于本版条目。

### 编码与门的账

编码区 2111 字符(不含换行); 编码区锚 7 处(候选池 8 条, 工具侧逐字校验 ok=8 bad=0); 扁平契约 6 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现(词级)+事实覆盖清单(30 项)assert。门槛三遍: T1 字面逐锚回源 ⇎ T2 DERIV 重跑 ⇎ T3 码位与字母账。