# B92 重定向跳次上限: 五份实现侧一手文书各答一遍 20⇎50⇎30⇎10⇎30, 同宗 curl 两面互斥 50⇎30——Go 面上写 10 而判据实拦 9 跳, requests 的 30 只活在注释面
src: corpus/raw/redirHops/b92/fetch.html(网页 1854393 B, 剥壳面 294288 字符) ⇎ corpus/raw/redirHops/b92/max-redirs.md(558 B) ⇎ corpus/raw/redirHops/b92/CURLOPT_MAXREDIRS.md(1657 B) ⇎ corpus/raw/redirHops/b92/client.go(35914 B) ⇎ corpus/raw/redirHops/b92/sessions.py(34072 B) (五份均为实现侧一手文本: WHATWG Fetch Standard 当前快照 ⇎ curl --max-redirs 手册页 ⇎ libcurl CURLOPT_MAXREDIRS(3) ⇎ Go net/http client.go ⇎ python-requests sessions.py; 数字一律从面内现读, 一个都不手填; "该跟几跳"在 IETF 侧只留 legacy 注记, 本条不取 RFC 文书, 与 B72/B80 的规范面不成同题对照; 上游改版后的现值只在本机或站外成立, 不进门槛)
; tags: 答案键(20⇎50⇎30⇎10⇎30 五值) 尺键(请求尺⇎跳尺, 差一枚) 档键(五档读面阶梯) 层键(码面⇎注释面⇎DEFAULT 段) 哨兵键(0⇎-1 只 curl 有) 谱系键(RFC 引用零对四) 锚归属由正文现推 闭合账 标量 2⇎清单 11 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/redirHops/b92/fetch.html

If request’s redirect count is 20, then return a network error

Increase request’s redirect count by 1

A request has an associated redirect count

Unless stated otherwise, it is zero

A redirect status is a status that is 301, 302, 303, 307, or 308

### ⟦B⟧ ⟸ corpus/raw/redirHops/b92/max-redirs.md

Set the maximum number of redirections to follow.

By default the limit is set to 50 redirects.

Set this option to -1 to make it unlimited.

this option prevents curl from following too many redirects

Added: 7.5

### ⟦C⟧ ⟸ corpus/raw/redirHops/b92/CURLOPT_MAXREDIRS.md

The set number is the redirection limit *amount*.

the next redirect triggers the error

Setting the limit to 0 makes libcurl refuse any redirect.

Set it to -1 for an infinite number of redirects.

This allows your application to get stuck in never-ending redirect loops.

30 (since 8.3.0), it was previously unlimited.

Added-in: 7.5

### ⟦D⟧ ⟸ corpus/raw/redirHops/b92/client.go

which is to stop after 10 consecutive requests

Get follows the redirect, up to a maximum of 10 redirects

if len(via) >= 10 {

stopped after 10 redirects

the requests made already, oldest first

RFC 2616 allowed automatic redirection only with GET and

See Issue 18570.

### ⟦E⟧ ⟸ corpus/raw/redirHops/b92/sessions.py

Maximum number of redirects allowed.

This defaults to requests.models.DEFAULT_REDIRECT_LIMIT, which is 30.

if len(resp.history) >= self.max_redirects:

Exceeded {self.max_redirects} redirects.

Handle redirection without scheme (see: RFC 1808 Section 4)

raise TooManyRedirects(

## ⟪BabelTele⟫
🧭 同一条 30x 链最多跟几跳, 五份一手文书各答一遍且互不同值: WHATWG Fetch(网页面 1854393 B, 剥壳后 294288 字符 7763 行)⟦A⟧⟨If request’s redirect count is 20, then return a network error⟩ 第 3673 行 20 跳 ⇎ curl 命令行手册(558 B)⟦B⟧⟨By default the limit is set to 50 redirects.⟩ 第 20 行 50 ⇎ libcurl 3 号页(1657 B)⟦C⟧⟨30 (since 8.3.0), it was previously unlimited.⟩ 第 30 行 30 ⇎ Go net/http client.go(35914 B 1065 行)⟦D⟧⟨which is to stop after 10 consecutive requests⟩ 第 65 行 10 ⇎ requests sessions.py(34072 B 921 行)⟦E⟧⟨This defaults to requests.models.DEFAULT_REDIRECT_LIMIT, which is 30.⟩ 第 484 行 30——最大 50 ⇎ 最小 10 差 5 倍, 同宗 curl 两面互斥 50⇎30。🪜 读面阶梯五档(原面逐行 ⇎ 全篇折平 ⇎ 剥壳折平 ⇎ 带壳网页 ⇎ 抹标记折平), 36 枚判词针逐档过闸: 折平比逐行多读得 2+2=4 枚(硬折行把句子劈成两段: fetch 2 枚 ⇎ cli 2 枚 ⇎ 其余三面 0 枚); 网页带壳面丢针 4 枚(标签插在词间 ⟦A⟧⟨Increase request’s redirect count by 1⟩), 反有 1 枚只在带壳面读得(剥壳把 script/style 整块抹平 ⟦A⟧⟨If request’s redirect count is 20, then return a network error⟩), 两面都读得却计数不等 2 枚(network error 81⇎91 枚 ⇎ redirect count 5⇎8 枚); 行首标记把句子拦腰截断——抹去 // 与 #: 才读得 ⟦D⟧⟨before following an HTTP redirect⟩ 一类 3 枚, frontmatter 壳独占 2 枚 ⟦C⟧⟨Added-in: 7.5⟩, 注释壳独占 4 枚 ⟦E⟧⟨Maximum number of redirects allowed.⟩; 反向对照: 别家的判词句在本家五档全零 3 枚。⚖ 计数对象不统一, 单位词即口径: hop 一枚不写; 整词面 redirect 121⇎0⇎6⇎37⇎17 枚 ⇎ redirects 24⇎3⇎4⇎17⇎30 ⇎ redirection 0⇎0⇎1⇎1⇎1 ⇎ redirections 0⇎1⇎1⇎0⇎0 ⇎ count 5⇎0⇎1⇎0⇎0 ⇎ consecutive 0⇎0⇎0⇎1⇎0——标准面(Fetch)说 count 不说 times, 命令行说 redirections(复数), 3 号页两种都写, Go 只说 consecutive requests, requests 只说 redirects; 子串减整词的差 46⇎4⇎6⇎63⇎41 枚即被更长词吃掉的 redirect。🧮 判据形三式与尺差: Fetch 用等号 ⟦A⟧⟨Increase request’s redirect count by 1⟩(全库 1 枚 "count is 20", 他家 0 枚)⇎ Go 用 >=(1 枚)与 requests 用 >=(1 枚)同形 ⇎ libcurl 用散文⟦C⟧⟨the next redirect triggers the error⟩ ⇎ 命令行只报默认值(Go 1 枚 ⇎ requests 1 枚 ⇎ fetch 1 枚 ⇎ curl 两面 0 枚)。尺差在 Go: 判据数的是"已发出的请求"⟦D⟧⟨the requests made already, oldest first⟩, 首发占一格 ⇒ 实跟 9 跳, 而同一文件的错误串⟦D⟧⟨stopped after 10 redirects⟩ 与 Get/Head 文档⟦D⟧⟨Get follows the redirect, up to a maximum of 10 redirects⟩ 都写 10 ⇒ 面上 10 ⇎ 码面 10 差一枚; requests 更彻底: 30 只活在注释里, 剥壳正文面 30 出现 0 次(数不落码)。🚦 哨兵与版本层只 curl 有: libcurl 两面同页写 0 与 -1 ⟦C⟧⟨Setting the limit to 0 makes libcurl refuse any redirect.⟩⟦C⟧⟨Set it to -1 for an infinite number of redirects.⟩, 命令行只写 -1 ⟦B⟧⟨Set this option to -1 to make it unlimited.⟩; 默认值带版本 ⟦C⟧⟨30 (since 8.3.0), it was previously unlimited.⟩(8.3.0 前无上限), 两面同引 Added 1 ⟦B⟧⟨Added: 7.5⟩⇎⟦C⟧⟨Added-in: 7.5⟩; Fetch/Go/requests 三面 0/-1 不是配置位。数字家族在折平面(数字邻界): 20 = 9⇎0⇎0⇎0⇎0 ⇎ 50 = 0⇎1⇎0⇎0⇎0 ⇎ 30 = 4⇎0⇎1⇎0⇎1 ⇎ 10 = 6⇎0⇎0⇎6⇎0——20 与 50 各只一家, 30 与 10 在他家面上另有 4 枚与 6 枚, 故独占必须连语境词一起核 ⟦C⟧⟨The set number is the redirection limit *amount*.⟩。🧬 谱系与语气: Fetch 面引 24 枚 RFC 号(含 9110/8470 那批拒绝给数的文书)与 rfc 词 73 枚 ⇎ Go 4 枚(2616/2617/7230/7231) ⇎ requests 4 枚(1808/3986/7231/7235) ⇎ curl 两面各 0 枚(它只引 curl 自己的页)⟦D⟧⟨RFC 2616 allowed automatic redirection only with GET and⟩⟦E⟧⟨Handle redirection without scheme (see: RFC 1808 Section 4)⟩; issue 词 8⇎0⇎0⇎8⇎1 枚 ⟦D⟧⟨See Issue 18570.⟩; 年份面 17⇎0⇎0⇎1⇎0 枚。可跳转码集只两家列全 2⇎0⇎0⇎8⇎1 枚(301)⇎ 5⇎0⇎0⇎8⇎1(302)⇎ 5⇎0⇎0⇎8⇎0(303)⇎ 1⇎0⇎0⇎8⇎0(307)⇎ 1⇎0⇎0⇎8⇎0(308), 另有一枚已废的代理重定向码在五面全 0 枚(面里查无此码)——Fetch⟦A⟧⟨A redirect status is a status that is 301, 302, 303, 307, or 308⟩与 Go 同列五个码, requests 只在源码写符号名 ⟦E⟧⟨raise TooManyRedirects(⟩。语气: 大写 MUST/SHOULD/MAY 逐行档全库仅 1 枚(在 Go 引用的那句 "Clients SHOULD NOT include a Referer header field" ⟦D⟧⟨which is to stop after 10 consecutive requests⟩ 同族), 而保大小写折平档同样读到 1 枚、先小写化的折平档读到 0 枚——尺子自陷; 小写 must 28⇎0⇎0⇎8⇎4 ⇎ should 45⇎0⇎0⇎16⇎6 ⇎ may 19⇎0⇎0⇎9⇎8 ⇎ can 99⇎0⇎0⇎8⇎3 枚: 规范动词只在标准面成规模, 实现面用描述语气。🧱 共现池: 五面两两共现 7 对(共 16 行, 上限 4 行)——最大一对是 curl 手册页 ⇎ 3 号页共 4 行(copyright/SPDX/See-also 那几行 frontmatter 逐字同, 同宗仓库), 原面逐字档 4 行与折平档 8 行同数; 其余共现全是代码 braces 一类(⟦D⟧⟨if len(via) >= 10 {⟩ ⇎ ⟦E⟧⟨if len(resp.history) >= self.max_redirects:⟩ 同形而不同值)。窗口密度: redirect 词 ±60 字符内出现的不同数字 26⇎2⇎6⇎17⇎3 枚——命令行最少。ℒ 方法 ⇒ 跳次上限的隐性知识分四键: ①答案键 20⇎50⇎30⇎10⇎30 五值并置, 最大最小差 25 倍且同宗互斥; ②尺键 请求尺(Go 10 ⇎ requests 30)与跳尺(Fetch 20 ⇎ libcurl 30)不可混 ⟦A⟧⟨Unless stated otherwise, it is zero⟩⟦D⟧⟨if len(via) >= 10 {⟩; ③档键 同一句在带壳面/剥壳面/折平面/逐行面/抹标记面五档上的可读性各不同(4 枚丢/7 枚得/2 枚计数不同); ④层键 数值落在哪一层(码面 3 次 ⇎ 注释面 35 枚 ⇎ 文档 DEFAULT 段)。每键都是 count 可机检量, 零项照占键位。

## ⛓解读注

### 压缩账(本注现算, 第三把尺)

| 量 | ⟦A⟧fet | ⟦B⟧cli | ⟦C⟧lib | ⟦D⟧go | ⟦E⟧req |
|---|---|---|---|---|---|
| 源字符 | 1839728 | 558 | 1657 | 35910 | 34072 |
| 源字节(UTF-8) | 1854393 | 558 | 1657 | 35914 | 34072 |
| 源词 | 86667 | 84 | 208 | 5377 | 3467 |
| 源行(非空) | 18915(16160) | 23(21) | 76(55) | 1064(985) | 920(758) |
| 源唯一码位 | 176 | 58 | 75 | 93 | 87 |
| 本遍剥壳后字符 | 855551 | 524 | 1451 | 30443 | 24947 |

编码区 4051 字符(不含换行, 唯一码位 346 枚), 对五源合账(1911925 字符)为 0.2%; 逐字符状态机数出的词 95803 枚 ⇎ 编码区 4051 字符: 一格中文压着整句规范。

### 锚的归属(本遍独立核验)
编码区 32 枚 ⟨锚⟩, 本遍穿到 32 枚 ⇎ 穿不到 0 枚; 归属 ⟦A⟧6 ⇎ ⟦B⟧3 ⇎ ⟦C⟧8 ⇎ ⟦D⟧10 ⇎ ⟦E⟧5。比对面是**剥壳后的网页面**(fetch.html 的 ⟨If request’s redirect count is 20, then return a network error⟩ 跨三枚标签, 原面逐字符扫读不到——本遍游标剥壳 ⇎ 建条目遍 finditer 拼块, 两把尺都得过)。标签 32 枚 ⇎ 锚 32 枚: 一句里可挂两面, 逐标签配对由门槛 T1 现验。

### 读法: 同一问题的五个答案与四把尺
答案 20(fet) ⇎ 50(cli) ⇎ 30(lib) ⇎ 10(go) ⇎ 30(req)。三件事各自独立:
① **答案键**——五个数互不相同, 且 curl 一家两面互斥(手册页 50 ⇎ 3 号页 30); 本遍在各自剥壳面上重扫这五个数, 命中 13⇎1⇎1⇎6⇎0 枚(数在别家面上偶然重现属正常, 判据是句不是数字符)。
② **尺键**——Go 的 `len(via)` 数的是**已跟过的跳**, `resp.history` 数的是**请求链**, 两把尺在 10 与 9 之间分岔; requests 的 30 只活在注释面, 代码面写符号名。
③ **档键**——同一句在原面逐行 ⇎ 全篇折平 ⇎ 剥壳 ⇎ 带壳 ⇎ 抹标记五档上可读性不同, 硬换行与行首 //、#: 各自切断一批针。
④ **层键**——数字落在码面、消息面还是文档面: Go 面上写的数与实拦的数不同层。

### 本条不能由在库文件判定的(只登记, 不进门槛)
已废的 305(代理重定向)在五份面的出现 0⇎0⇎0⇎0⇎0 枚——建条目遍因此不在编码区印这个字面, 只在🧬段的针表键位上留零; IETF 侧(RFC 2616 的 5 跳 legacy 注记)不在本条五源里, 故本条不引任何 RFC 文书的数; 各实现的实际默认值随版本漂移, 本条只认盘上这五份文本自身。

### 编码与门的账
T1 逐锚回源(本遍 32/32, 面按扩展名分档) ⇎ T2 DERIV 复算(corpus/_b92flat.json 的 44 枚面值逐枚现算) ⇎ T3 码位与字母账(源面唯一码位 176 ⇎ 编码面 346)。A⇎B 对账 114 键, 两套实现换机制不换定义; 小整数待核只进本注, 不进 FAIL。

