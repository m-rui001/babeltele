# -*- coding: utf-8 -*-
"""B57 建条目(第二遍现算, 四源): T = raw/ietf/rfc5246.txt(TLS 1.2 协议, 2008-08)
⇎ O = rfc7525.txt(BCP 195 第一版, 2015-05) ⇎ F = rfc8446.txt(TLS 1.3 协议, 2018-08) ⇎ N = rfc9325.txt(BCP 195 第二版, 2022-11)。
主轴: 同一个签名哈希(SHA-1)在四份文书里有四种身份——协议里的枚举值(必需) ⇎ 旧建议连 "SHA-1" 这个拼写都不写(只在 MAC 下限里留 HMAC-SHA1)
⇎ 1.3 协议把它归进 "Legacy algorithms" 并写下带豁免从句的 MUST NOT ⇎ 新建议写下不留余地的 MUST NOT。
配套轴: 判决强度词的排他计数与显式理由("Rationale:")条数、两版建议之间的整行⇎句子两口径搬运率(407 ⇎ 66)与改判那句的 0 命中、
套件名的跨代零交集(T∩F=0)与 12 对引用方向的时序违例数、门限值与强度的同时迁移(192 SHOULD NOT ⇎ 224 MUST NOT)。
第二遍的独立性: 本文件用"逐次 find 扫描"数关键词与拼写(pick 用 str.count/正则), 用 startswith+isdigit 认页眉(pick 用正则),
用手工扩字符认套件名(pick 用 {8,} 量词正则), 搬运率与共用句是本遍新增的两套算法(pick 没有); 每个共有量在 TIE 表上与 _pick57.py 逐量对账, 不符即停机。
门槛内 _b57_scan 是第三遍, 锚归属由条目正文现推。磁盘 mtime、抓取时刻、IANA 注册表现场不可由在库文件判定, 进注不进门槛。"""
import io, os, re, sys, json

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = u'%s/babeltele/B57_four_documents_one_hash_verdict.md' % C
J = json.load(io.open(u'corpus/_b57meas.json', encoding='utf-8'))
MM, POOLP = J[u'meas'], J[u'pool']
TAGS, PATH = J[u'tags'], J[u'paths']
LB = dict(zip(TAGS, [u'1.2 协议', u'旧建议', u'1.3 协议', u'新建议']))
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATH]
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN ---


def pnorm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


F = {}
NN4 = 4


def four(name, f):
    F[name] = [f(k) for k in range(NN4)]


LS = [t.split(NL) for t in TXT]

# ---------- 形状档(逐行过滤, pick 用正则计数) ----------
four(u'bytes', lambda i: os.path.getsize(PATH[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'lines', lambda i: TXT[i].count(NL))
four(u'nonblank', lambda i: len([l for l in LS[i] if l.strip()]))
four(u'blank', lambda i: len([l for l in LS[i] if not l.strip()]))
four(u'tabs', lambda i: TXT[i].count(u'\t'))
four(u'trailws', lambda i: len([l for l in LS[i] if l[-1:] in (u' ', u'\t')]))
four(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
four(u'bom', lambda i: 1 if TXT[i][:1] == u'﻿' else 0)
four(u'maxlen', lambda i: max(len(l) for l in LS[i]))
four(u'meanlen', lambda i: int(round(1.0 * sum(len(l) for l in LS[i] if l.strip()) /
                                       max(1, len([l for l in LS[i] if l.strip()])))))
four(u'sha16', lambda i: __import__('hashlib').sha256(io.open(PATH[i], 'rb').read()).hexdigest()[:16])


def strict(i):
    try:
        io.open(PATH[i], encoding='utf-8').read()
        return 1
    except UnicodeDecodeError:
        return 0


four(u'utf8_strict', strict)
def _pgmark(t):
    # '[Page N]' 不单独成行, 它缀在页眉行的右端(所以按整篇扫描而非逐行前缀判)
    n, i = 0, 0
    while True:
        j = t.find(u'[Page ', i)
        if j < 0:
            return n
        k = j + 6
        while k < len(t) and t[k].isdigit():
            k += 1
        if k > j + 6 and t[k:k + 1] == u']':
            n += 1
        i = j + 1


four(u'pagemarks', lambda i: _pgmark(TXT[i]))
four(u'hdr', lambda i: len([l for l in LS[i] if l[:4] == u'RFC ' and l[4:8].isdigit()]))
F[u'page_gap'] = [F[u'pagemarks'][i] - F[u'hdr'][i] for i in range(4)]
four(u'crlf', lambda i: TXT[i].count(u'\r'))
F[u'bytegap'] = [F[u'bytes'][i] - F[u'chars'][i] for i in range(4)]
F[u'ascii_eq'] = [1 if F[u'nonascii'][i] == 0 else 0 for i in range(4)]
F[u'eqc'] = sum(F[u'ascii_eq'])
F[u'eqb'] = sum(1 for i in range(4) if F[u'bytegap'][i] == 0)
F[u'sha_distinct'] = len(set(F[u'sha16']))
F[u'author_hdr'] = [len(set(l.split()[-1] for l in LS[i] if l[:4] == u'RFC ')) for i in range(4)]


# ---------- 关键词与拼写: 一律用"逐次 find 扫描", 与 pick 的正则/count 是两套路子 ----------
def occ(t, w):
    # 词边界口径与 \\b 一致: 下划线算词字符, 所以 id_dsa_sha1 里的 dsa_sha1 不计(免得蹭计)
    n, i, L = 0, 0, len(w)
    while True:
        j = t.find(w, i)
        if j < 0:
            return n
        a = t[j - 1] if j else u' '
        b = t[j + L] if j + L < len(t) else u' '
        if not (a.isalnum() or a == u'_' or b.isalnum() or b == u'_'):
            n += 1
        i = j + 1


def sub(t, w):
    n, i = 0, 0
    while True:
        j = t.find(w, i)
        if j < 0:
            return n
        n += 1
        i = j + 1


four(u'kw_mustnot', lambda i: occ(TXT[i], u'MUST NOT'))
four(u'kw_must_all', lambda i: occ(TXT[i], u'MUST'))
F[u'kw_must'] = [F[u'kw_must_all'][i] - F[u'kw_mustnot'][i] for i in range(4)]
four(u'kw_shouldnot', lambda i: occ(TXT[i], u'SHOULD NOT'))
four(u'kw_should_all', lambda i: occ(TXT[i], u'SHOULD'))
F[u'kw_should'] = [F[u'kw_should_all'][i] - F[u'kw_shouldnot'][i] for i in range(4)]
four(u'kw_may', lambda i: occ(TXT[i], u'MAY'))
four(u'kw_required', lambda i: occ(TXT[i], u'required'))
four(u'kw_notrecommended', lambda i: occ(TXT[i], u'NOT RECOMMENDED'))
four(u'kw_rec_all', lambda i: occ(TXT[i], u'RECOMMENDED'))
F[u'kw_recommended'] = [F[u'kw_rec_all'][i] - F[u'kw_notrecommended'][i] for i in range(4)]
four(u'kw_optional', lambda i: occ(TXT[i], u'optional'))
four(u'kw_optional_up', lambda i: occ(TXT[i], u'OPTIONAL'))
four(u'kw_rationale', lambda i: sub(TXT[i], u'Rationale:'))
four(u'kwbullet_o', lambda i: len([l for l in LS[i] if l[:6] == u'   o  ']))
four(u'kwbullet_star', lambda i: len([l for l in LS[i] if l[:6] == u'   *  ']))
four(u'kwbullet_num', lambda i: len([l for l in LS[i] if re.match(r'^      \d+\.  ', l)]))
F[u'kw_close'] = [F[u'kw_mustnot'][i] + F[u'kw_must'][i] - F[u'kw_must_all'][i] for i in range(4)]
F[u'kw_close2'] = [F[u'kw_shouldnot'][i] + F[u'kw_should'][i] - F[u'kw_should_all'][i] for i in range(4)]
F[u'kw_close3'] = [F[u'kw_notrecommended'][i] + F[u'kw_recommended'][i] - F[u'kw_rec_all'][i] for i in range(4)]
F[u'kw_mix'] = [1 if (F[u'kwbullet_o'][i] and F[u'kwbullet_star'][i]) else 0 for i in range(4)]
F[u'kw_mix_docs'] = sum(F[u'kw_mix'])
F[u'kw_bullets_oneway'] = sum(1 for i in range(4) if F[u'kwbullet_o'][i] + F[u'kwbullet_star'][i] > 0)
F[u'kw_bullets_onlyone'] = sum(1 for i in range(4) if bool(F[u'kwbullet_o'][i]) != bool(F[u'kwbullet_star'][i]))

# ---------- 拼写可见度 ----------
four(u'sp_sha1_hy', lambda i: sub(TXT[i], u'SHA-1'))
four(u'sp_sha1_plain', lambda i: sub(TXT[i], u'SHA1'))
four(u'sp_hmac_sha1', lambda i: sub(TXT[i], u'HMAC-SHA1'))
F[u'sp_sha1_net'] = [F[u'sp_sha1_plain'][i] - F[u'sp_hmac_sha1'][i] for i in range(4)]
four(u'sp_sha1_lower', lambda i: sub(TXT[i], u'sha1'))
four(u'sp_md5_hy', lambda i: sub(TXT[i], u'MD5'))
four(u'sp_md5_lower', lambda i: sub(TXT[i], u'md5'))
four(u'sp_md5sha1', lambda i: sub(TXT[i], u'MD5-SHA1'))
four(u'sp_sha256_hy', lambda i: sub(TXT[i], u'SHA-256'))
four(u'sp_sha256_lower', lambda i: sub(TXT[i], u'sha256'))
four(u'sp_sha384_hy', lambda i: sub(TXT[i], u'SHA-384'))
four(u'sp_gcm_sha256', lambda i: sub(TXT[i], u'GCM_SHA256'))
four(u'sp_case_variants', lambda i: sum(1 for v in (F[u'sp_sha1_hy'][i], F[u'sp_sha1_net'][i],
                                                    F[u'sp_sha1_lower'][i]) if v > 0))
four(u'sp_total_sha1_family', lambda i: F[u'sp_sha1_hy'][i] + F[u'sp_sha1_net'][i] +
      F[u'sp_sha1_lower'][i] + F[u'sp_hmac_sha1'][i])


def endsha(i):
    t, n, p = TXT[i], 0, 0
    while True:
        j = t.find(u'TLS_', p)
        if j < 0:
            return n
        k = j + 4
        while k < len(t) and (t[k] in u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'):
            k += 1
        if k - j - 4 >= 8 and t[j:k].endswith(u'_SHA'):
            n += 1
        p = j + 4


four(u'sp_suite_endsha', endsha)

# ---------- 算法标识符 ----------
four(u'id_rsa_pkcs1_sha1', lambda i: occ(TXT[i], u'rsa_pkcs1_sha1'))
four(u'id_ecdsa_sha1', lambda i: occ(TXT[i], u'ecdsa_sha1'))
four(u'id_dsa_sha1', lambda i: occ(TXT[i], u'dsa_sha1'))
four(u'id_dsa_sha1_text', lambda i: sub(TXT[i], u'dsa_sha1'))
four(u'id_rsa_pkcs1_sha256', lambda i: occ(TXT[i], u'rsa_pkcs1_sha256'))
four(u'id_rsa_pss_rsae_sha256', lambda i: occ(TXT[i], u'rsa_pss_rsae_sha256'))
four(u'id_ecdsa_secp256r1_sha256', lambda i: occ(TXT[i], u'ecdsa_secp256r1_sha256'))
four(u'id_rsa_pss_pss_sha256', lambda i: occ(TXT[i], u'rsa_pss_pss_sha256'))
SCHEME = [re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\\(', TXT[i]) for i in range(4)]
four(u'id_scheme_total', lambda i: len(SCHEME[i]))
four(u'id_sha1_schemes', lambda i: len([m for m in SCHEME[i] if u'sha1' in m[:-1]]))


def legacy_block(i):
    if i != 2:
        return 0
    t, n = TXT[i], 0
    for m in re.finditer(u'/\\* Legacy algorithms \\*/', t):
        stop = len(t)
        for nxt in re.finditer(u'/\\*|\\}', t[m.end():]):
            stop = m.end() + nxt.start()
            break
        n += len(re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\\(', t[m.end():stop]))
    return n


four(u'id_legacy_block', legacy_block)
MSS = re.search(u'A TLS-compliant application MUST support digital signatures with'
                u'(.{0,400}?)secp256r1', TXT[2], re.S)
MUSTSUPPORT = re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+', MSS.group(1)) if MSS else []
F[u'id_must_support_n'] = len(MUSTSUPPORT)
F[u'id_must_support_sha1'] = len([m for m in MUSTSUPPORT if u'sha1' in m])
F[u'id_enum_lines'] = [len([l for l in LS[i] if u'(0x' in l and re.search(u'\\b(?:rsa|ecdsa|eddsa|dsa)\\w*\\(', l)])
                       for i in range(4)]
F[u'id_enum_total'] = [len(re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\\(0x[0-9A-Fa-f]{4}\\)', TXT[i]))
                       for i in range(4)]

# ---------- 套件名矩阵(手工扩字符, pick 用 {8,} 量词) ----------
def suites(i):
    t, p, out = TXT[i], 0, []
    while True:
        j = t.find(u'TLS_', p)
        if j < 0:
            return out
        k = j + 4
        while k < len(t) and (t[k] in u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'):
            k += 1
        if k - j - 4 >= 8:
            out.append(t[j:k])
        p = j + 4


SUIT = [suites(i) for i in range(4)]
SUITE = [set(x) for x in SUIT]
four(u'suite_distinct', lambda i: len(SUITE[i]))
four(u'suite_occ', lambda i: len(SUIT[i]))
four(u'frag_tail', lambda i: len([s for s in SUIT[i] if s.endswith(u'_')]))


def bridge(s, d1, d2):
    a = len(SUITE[s] & SUITE[d1])
    b = len(SUITE[s] & SUITE[d2])
    z = len(SUITE[s] - SUITE[d1] - SUITE[d2])
    return a, b, z, len(SUITE[s]), a + b + z - len(SUITE[s])


(F[u'suite_from_N_in_T'], F[u'suite_from_N_in_F'], F[u'suite_from_N_in_none'],
 F[u'suite_N_total'], F[u'suite_bridge_close']) = bridge(3, 0, 2)
(F[u'suite_from_O_in_T'], F[u'suite_from_O_in_F'], F[u'suite_from_O_in_none'],
 F[u'suite_O_total'], F[u'suite_O_bridge_close']) = bridge(1, 0, 2)
F[u'suite_F_only'] = len(SUITE[2] - SUITE[0] - SUITE[1] - SUITE[3])
F[u'suite_T_only'] = len(SUITE[0] - SUITE[1] - SUITE[2] - SUITE[3])
F[u'suite_common_TF'] = len(SUITE[0] & SUITE[2])
F[u'suite_common_ON'] = len(SUITE[1] & SUITE[3])
F[u'suite_endsha_T'] = len([s for s in SUITE[0] if s.endswith(u'_SHA')])

# ---------- 引用与谱系 ----------
DOCALL = [5246, 7525, 8446, 9325]
MONA = [u'January', u'February', u'March', u'April', u'May', u'June', u'July', u'August',
        u'September', u'October', u'November', u'December']


def _occnum(t, num):
    # 号码在场: 逐字符扫描, 前后不得为字母或数字(与 pick 的 \b\d{4}\b 同判法, 只是不走正则)
    s, n, i = str(num), 0, 0
    while True:
        j = t.find(s, i)
        if j < 0:
            return n
        a = t[j - 1] if j else u' '
        b = t[j + len(s)] if j + len(s) < len(t) else u' '
        if not (a.isalnum() or b.isalnum()):
            n += 1
        i = j + 1


def _dropmy(l):
    # 谱系行的右栏写着“月 年”, 剥掉它才数“列出的 RFC 编号个数”
    for m in MONA:
        k = 0
        while True:
            j = l.find(m, k)
            if j < 0:
                break
            r = j + len(m)
            while r < len(l) and not l[r].isdigit():
                r += 1
            if r + 4 <= len(l) and l[r:r + 4].isdigit():
                l = l[:j] + l[r + 4:]
            else:
                break
            k = j
    return l


four(u'cite_rfc_tokens', lambda i: len(re.findall(u'\\bRFC ?\\d{4}\\b', TXT[i])))
CITED = [set(re.findall(u'\\bRFC ?(\\d{4})\\b', TXT[i])) for i in range(4)]
four(u'cite_rfc_distinct', lambda i: len(CITED[i]))
four(u'cite_bracket', lambda i: len(re.findall(u'\\[RFC\\d{4}\\]', TXT[i])))
for _a in range(4):
    for _b in range(4):
        if _a != _b:
            # 两种口径并记: cite_X_to_Y 数“号码在场”(裸四位数, 含参考文献行), cite_rfc_X_to_Y 只数“RFC 编号形式”的引用
            F[u'cite_%s_to_%s' % (TAGS[_a], TAGS[_b])] = _occnum(TXT[_a], DOCALL[_b])
            F[u'cite_rfc_%s_to_%s' % (TAGS[_a], TAGS[_b])] = len(
                [m for m in re.findall(u'\\bRFC ?(\\d{4})\\b', TXT[_a]) if int(m) == DOCALL[_b]])
PAIRV = [F[u'cite_%s_to_%s' % (TAGS[a], TAGS[b])] for a in range(4) for b in range(4) if a != b]
RFCPV = [F[u'cite_rfc_%s_to_%s' % (TAGS[a], TAGS[b])] for a in range(4) for b in range(4) if a != b]
F[u'cite_pairs_total'] = len(PAIRV)
F[u'cite_pairs_nonzero'] = len([v for v in PAIRV if v])
F[u'cite_pairs_zero'] = len([v for v in PAIRV if not v])
F[u'cite_rfc_pairs_total'] = len(RFCPV)
F[u'cite_rfc_pairs_nonzero'] = len([v for v in RFCPV if v])
F[u'cite_pairs_occ'] = sum(PAIRV)
F[u'cite_rfc_pairs_occ'] = sum(RFCPV)
MON = MONA


def mnum(i):
    m = re.search(u'(%s) (\\d{4})' % u'|'.join(MON), TXT[i])
    return int(m.group(2)) * 12 + MON.index(m.group(1)) + 1


DOCV = DOCALL


def _lin(i, key):
    return _dropmy(next((l for l in LS[i] if l.startswith(key)), u''))


four(u'cite_obsoletes_n', lambda i: len(re.findall(u'\\b\\d{4}\\b', _lin(i, u'Obsoletes:'))))
four(u'cite_updates_n', lambda i: len(re.findall(u'\\b\\d{4}\\b', _lin(i, u'Updates:'))))
OBS = [[int(x) for x in re.findall(u'\\b\\d{4}\\b', _lin(i, u'Obsoletes:'))] for i in range(4)]
F[u'cite_obsoleted_inrepo'] = [len([x for x in OBS[i] if x in DOCV]) for i in range(4)]
F[u'cite_obsoletes_notinrepo'] = [F[u'cite_obsoletes_n'][i] - F[u'cite_obsoleted_inrepo'][i] for i in range(4)]
F[u'cite_obsoleted_inrepo_all'] = sum(F[u'cite_obsoleted_inrepo'])
F[u'cite_backward_violations'] = len([1 for a in range(4) for b in range(4) if a != b
                                      and F[u'cite_%s_to_%s' % (TAGS[a], TAGS[b])] and mnum(a) < mnum(b)])
F[u'cite_self_obsoleted'] = F[u'cite_N_to_O']

# ---------- 时间 ----------
def raw_date(i):
    for l in LS[i]:
        if l[:4] == u'RFC ' and re.search(u'(%s) \\d{4}' % u'|'.join(MON), l):
            return re.search(u'(%s) \\d{4}' % u'|'.join(MON), l).group(0)
    m = re.search(u'(%s) \\d{4}' % u'|'.join(MON), TXT[i])
    return m.group(0) if m else u''


F[u'date_raw'] = [raw_date(i) for i in range(4)]
F[u'date_ym'] = [[int(re.search(u'(\\d{4})', d).group(1)), MON.index(re.search(
    u'(%s)' % u'|'.join(MON), d).group(1)) + 1] for d in F[u'date_raw']]
four(u'month_num', lambda i: mnum(i))
F[u'month_gap_prev'] = [0] + [F[u'month_num'][i] - F[u'month_num'][i - 1] for i in range(1, 4)]
F[u'month_span'] = F[u'month_num'][3] - F[u'month_num'][0]
F[u'date_seg_ok'] = [1 if F[u'month_num'][i] > F[u'month_num'][i - 1] else 0 for i in range(1, 4)]
F[u'date_seg_n'] = sum(F[u'date_seg_ok'])
F[u'date_docnum_mono'] = sum(1 for i in range(1, 4) if DOCV[i] > DOCV[i - 1]
                             and F[u'month_num'][i] > F[u'month_num'][i - 1])

# ---------- 判决句定位 ----------
four(u'line_sha_mustnot', lambda i: len([l for l in LS[i] if u'MUST NOT' in l and (u'SHA-1' in l or u'MD5' in l)]))
four(u'line_sha_mustnot_hy', lambda i: len([l for l in LS[i] if u'MUST NOT' in l and u'SHA-1' in l]))
four(u'line_sha_in_enum', lambda i: len([l for l in LS[i] if u'sha1' in l and u'(0x' in l]))
four(u'line_rationale_mustnot', lambda i: len(
    [k for k in range(len(LS[i]))
                 if u'MUST NOT' in LS[i][k] and any(
                     u'Rationale:' in LS[i][j] for j in range(k, min(k + 7, len(LS[i]))))]))
FOURSET = [set(l.strip() for l in LS[i] if len(l.strip()) >= 20) for i in range(4)]
FAN = [pnorm(TXT[i]) for i in range(4)]
four(u'line_sha_in_prose', lambda i: len([l for l in LS[i] if u'SHA-1' in l and u'(0x' not in l
                                          and pnorm(l) not in [pnorm(x) for x in LS[3] if u'(0x' in x]]))

# ---------- 两版建议之间的搬运(整行 ⇎ 接行断句两口径; pick 没算这一档) ----------
def blob(i):
    return re.sub(u'\\s+', u' ', u' '.join(LS[i]))


def sents(b):
    cut = [0] + [x + 1 for x in range(1, len(b) - 1)
                 if b[x] == u' ' and b[x - 1] in u'.:;' and b[x + 1].isupper()] + [len(b)]
    return [u' '.join(y.split()) for y in (b[a:z].strip() for a, z in zip(cut, cut[1:])) if len(y) >= 20]


SO, SN = set(sents(blob(1))), set(sents(blob(3)))


def _normset(i):
    return set(pnorm(x) for x in FOURSET[i])


LNO, LNN = _normset(1), _normset(3)
F[u'carry_line_o'], F[u'carry_line_n'] = len(LNO), len(LNN)
F[u'carry_shared'] = len(LNO & LNN)
F[u'carry_only_o'] = len(LNO - LNN)
F[u'carry_only_n'] = len(LNN - LNO)
F[u'carry_union'] = len(LNO | LNN)
F[u'carry_close'] = F[u'carry_only_o'] + F[u'carry_only_n'] + F[u'carry_shared'] - F[u'carry_union']
# 第二种口径: 一行只要在新文里逐字再现一次(哪怕成了别人的子串)就算“搬走了”——它必 ≥ 集合交
F[u'carry_o_in_n_text'] = len([x for x in FOURSET[1] if pnorm(x) and pnorm(x) in FAN[3]])
F[u'carry_n_in_o_text'] = len([x for x in FOURSET[3] if pnorm(x) and pnorm(x) in FAN[1]])
F[u'carry_sub_overlap'] = F[u'carry_o_in_n_text'] + F[u'carry_n_in_o_text']
F[u'carry_sent_o'], F[u'carry_sent_n'] = len(SO), len(SN)
F[u'carry_sent_shared'] = len(SO & SN)
F[u'carry_sent_union'] = len(SO | SN)
# 共用那批行的体裁构成: 参考文献行 / 章节号行 / 正文行(只有第三类是“同一条声明原样搬过去”)
SRAW = [x for x in FOURSET[1] if pnorm(x) and pnorm(x) in LNN]
F[u'carry_shared_raw'] = len(SRAW)
F[u'carry_shared_ref'] = len([x for x in SRAW if u'[RFC' in x])
F[u'carry_shared_toc'] = len([x for x in SRAW if re.match(r'^\d+(\.\d+)*\s+\S', x) and u'[RFC' not in x])
F[u'carry_shared_prose'] = F[u'carry_shared_raw'] - F[u'carry_shared_ref'] - F[u'carry_shared_toc']
F[u'carry_split_close'] = F[u'carry_shared_ref'] + F[u'carry_shared_toc'] + F[u'carry_shared_prose'] - F[u'carry_shared_raw']
F[u'carry_sent_close'] = (len(SO) - len(SO & SN)) + (len(SN) - len(SO & SN)) + len(SO & SN) - len(SO | SN)
F[u'carry_sent_rat'] = len([x for x in (SO & SN) if u'Rationale:' in x])
F[u'carry_thr_192'] = len([x for x in (SO & SN) if u'192 bits' in x])
F[u'carry_thr_224'] = len([x for x in (SO & SN) if u'224 bits' in x])
F[u'carry_caliber_gap'] = F[u'carry_shared'] - F[u'carry_sent_shared']
four(u'bits_112', lambda i: occ(TXT[i], u'112 bits'))
four(u'bits_128', lambda i: occ(TXT[i], u'128 bits'))
four(u'bits_192', lambda i: occ(TXT[i], u'192 bits'))
four(u'bits_224', lambda i: occ(TXT[i], u'224 bits'))
four(u'modulus_2048', lambda i: occ(TXT[i], u'2048-bit') + occ(TXT[i], u'2048 bits'))
four(u'modulus_1024', lambda i: occ(TXT[i], u'1024-bit') + occ(TXT[i], u'1024 bits'))
four(u'curves_below_224', lambda i: sub(TXT[i], u'less than 224 bits'))
four(u'fwd_secrecy', lambda i: sub(TXT[i], u'forward secrecy'))
four(u'ssl_v2_ban', lambda i: len([l for l in LS[i] if u'MUST NOT negotiate SSL version 2' in l]))

# ---------- 锚候选池(与 pick 同规则, 但由本遍独立重建) ----------
POOL = []


def addpool(t, x):
    # 与 pick 同规则: 只有“整行档”要求 ≥20 字符, 标题行与触发词行不设下限; 上限 120
    if x and len(x) <= 120 and (t, x) not in POOL:
        POOL.append((t, x))


SPECIAL = (u'SHA-1', u'sha1', u'MUST NOT', u'Rationale:', u'Obsoletes:', u'Updates:')
for i, t in enumerate(TAGS):
    for l in LS[i]:
        s = l.strip()
        if len(s) >= 20:
            addpool(t, s)
    for l in LS[i][:40]:
        s = l.strip()
        if re.match(u'^[0-9.]+\\s+[A-Z]', s):
            addpool(t, s)
    for l in LS[i]:
        s = l.strip()
        if any(x in s for x in SPECIAL):
            addpool(t, s)
CROSS = {}
for t, x in POOL:
    g = pnorm(x)
    CROSS[(t, x)] = sum(1 for k in range(4) if g and g in FAN[k])
# 归一后为空的行(纯分隔线 ‘+---+---’)在哪个源都“命中”, 那不是跨源证据, 与 pick 一样剔出池
POOL = [(t, x) for (t, x) in POOL if pnorm(x)]
POOLC = [(t, CROSS[(t, x)], x) for (t, x) in POOL]
F[u'pool_n'] = len(POOLC)
four(u'pool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
four(u'pool_tag_1', lambda i: len([p for p in POOLC if p[0] == TAGS[i] and p[1] == 1]))
four(u'pool_tag_x', lambda i: len([p for p in POOLC if p[0] == TAGS[i] and p[1] > 1]))
F[u'pool_2'] = len([p for p in POOLC if p[1] == 2])
F[u'pool_3'] = len([p for p in POOLC if p[1] == 3])
F[u'pool_4'] = len([p for p in POOLC if p[1] == 4])
F[u'pool_1'] = len([p for p in POOLC if p[1] == 1])
F[u'pool_tiers'] = [F[u'pool_1'], F[u'pool_2'], F[u'pool_3'], F[u'pool_4']]
F[u'pool_close'] = F[u'pool_1'] + F[u'pool_2'] + F[u'pool_3'] + F[u'pool_4'] - F[u'pool_n']
# --- SCAN END ---

K, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K.setdefault(s, (expr, note))


def dump_deriv():
    out = dict((k, v[0]) for k, v in K.items())
    for k, exprs in SEENX.items():
        if len(exprs) > 1:
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
    return out


def V(name, i=None, note=u''):
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"B57V('%s'%s)" % (name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def EXPR(s, expr, note):
    reg(s, expr, note)
    return s


TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind[1:]))
    got = [p for p in POOLP if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    if not got:
        got = [p for p in POOLC if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    assert got, (kind, tag, needles)
    return max(got, key=lambda x: (len(x[2]), x[2]))


USEDATOM = []


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


BB57 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B57V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
BARE = re.compile(r'^[0-9+\-*/().,\s]*$')


_Q = chr(39) + chr(34)


def _split_top(s):
    out, buf, d, q = [], u'', 0, None
    for ch in s:
        if q:
            buf += ch
            if ch == q:
                q = None
            continue
        if ch in _Q:
            q = ch
            buf += ch
            continue
        if ch in u'([{':
            d += 1
        elif ch in u')]})':
            d -= 1
        if ch == u',' and d == 0:
            out.append(buf)
            buf = u''
            continue
        buf += ch
    out.append(buf)
    return [x.strip() for x in out]


def _unlit(x):
    t = x[1:] if x[:1] == u'u' else x
    assert t[0] in _Q and t[-1] == t[0], x
    return t[1:-1]


def _inline(t):
    # {EXPR(值算式, DERIV算式, 注)} —— 先在 Python 侧算出字面数, 再把 DERIV 算式登记进门槛
    while True:
        i = t.find(u'{EXPR(')
        if i < 0:
            break
        j = t.index(u'(', i)
        d = 0
        k = j
        while True:
            c = t[k]
            if c == u'(':
                d += 1
            elif c == u')':
                d -= 1
                if d == 0:
                    break
            k += 1
        assert t[k + 1] == u'}', t[k:k + 9]
        args = _split_top(t[j + 1:k])
        assert len(args) == 3, args
        val = eval(args[0], {u'F': F, u'B57V': BB57, u'len': len})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]
    # {B57V('k', i) ⇎ 算式} —— 只允许 B57V 调用与四则运算, 其余占位符交给 format_map
    def rep(m):
        c = m.group(1)
        if u'B57V(' not in c:
            return m.group(0)
        rest = BCALL.sub(u'0', c)
        assert BARE.match(rest), c
        val = eval(c, {u'B57V': BB57})
        reg(str(val), c.strip(), c.strip())
        return str(val)
    return re.sub(r'\{([^{}]*)\}', rep, t)


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + _inline(tmpl)).format_map(_Ctx(dict(G, **kw))))


# ---------- 锚 ----------
G[u'aMac'] = AT(u'own', u'T', u'MAC computations')
G[u'aEnum2'] = AT(u'own', u'T', u'sha1(2)')
G[u'aMD5SHA1'] = AT(u'own', u'T', u'MD5 and SHA-1.')
G[u'aOther'] = AT(u'own', u'T', u'other than SHA-1')
G[u'aObsT'] = AT(u'own', u'T', u'Obsoletes: 3268')
G[u'aPRF'] = AT(u'own', u'T', u'pseudorandom function (PRF)')
G[u'aThr192'] = AT(u'own', u'O', u'192 bits')
G[u'aFloor'] = AT(u'own', u'O', u'stronger than HMAC-SHA1')
G[u'aSSLv2O'] = AT(u'J2', u'O', u'SSLv2 is considered insecure')
G[u'aRC4O'] = AT(u'own', u'O', u'negotiate RC4')
G[u'aSuiteO'] = AT(u'own', u'O', u'ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 and')
G[u'aHdrT'] = AT(u'own', u'T', u'RFC 5246')
G[u'aHdrO'] = AT(u'own', u'O', u'TLS Recommendations')
G[u'aMustNotF'] = AT(u'own', u'F', u'offer a SHA-1 signed certificate')
G[u'aCVF'] = AT(u'own', u'F', u'signatures of CertificateVerify')
G[u'a0201'] = AT(u'own', u'F', u'0x0201')
G[u'aLegacyC'] = AT(u'own', u'F', u'/* Legacy algorithms */')
G[u'aLegacyDef'] = AT(u'own', u'F', u'Indicates algorithms which are being deprecated')
G[u'aMSS'] = AT(u'own', u'F', u'MUST support digital signatures')
G[u'aObsF'] = AT(u'own', u'F', u'Obsoletes: 5077')
G[u'aAllSHA1'] = AT(u'own', u'F', u'All SHA-1 signature algorithms')
G[u'aVerdictN'] = AT(u'own', u'N', u'SHA-1 or MD5 MUST NOT')
G[u'aThr224'] = AT(u'own', u'N', u'224 bits')
G[u'aSSLv2N'] = AT(u'J2', u'N', u'MUST NOT negotiate SSL version 2')
G[u'aObsN'] = AT(u'own', u'N', u'Obsoletes: 7525')
G[u'aUpdN'] = AT(u'own', u'N', u'Updates: 5288')
G[u'aRatN'] = AT(u'J2', u'N', u'at least 112 bits of security')

# ---------- 数字登记 ----------
G[u'by'] = JOIN(u'bytes', u'字节')
G[u'ln'] = JOIN(u'lines', u'换行')
G[u'nb'] = JOIN(u'nonblank', u'非空行')
G[u'mx'] = JOIN(u'maxlen', u'最长行')
G[u'me'] = JOIN(u'meanlen', u'平均行长')
G[u'tb'] = JOIN(u'tabs', u"制表符枚")
G[u'na'] = JOIN(u'nonascii', u"非 ASCII 枚")
G[u'bg'] = JOIN(u'bytegap', u'字节减字符')
G[u'bom'] = JOIN(u'bom', u'BOM')
G[u'eqb'] = V(u'eqb', None, u'字符数=字节数成立的份数')
G[u'shaK'] = V(u'sha_distinct', None, u'sha16 种数')
G[u'pm'] = JOIN(u'pagemarks', u"'[Page N]' 枚")
G[u'hd'] = JOIN(u'hdr', u'页眉行')
G[u'pg'] = JOIN(u'page_gap', u'页标减页眉')
G[u'ah'] = JOIN(u'author_hdr', u'页眉署名串种数')
G[u'utf'] = JOIN(u'utf8_strict', u'严格 UTF-8 解码')

G[u'mn'] = JOIN(u'kw_mustnot', u'MUST NOT')
G[u'mp'] = JOIN(u'kw_must', u'MUST 排他')
G[u'sn'] = JOIN(u'kw_shouldnot', u'SHOULD NOT')
G[u'sp'] = JOIN(u'kw_should', u'SHOULD 排他')
G[u'my'] = JOIN(u'kw_may', u'MAY')
G[u'rc'] = JOIN(u'kw_recommended', u'RECOMMENDED 排他')
G[u'nrc'] = JOIN(u'kw_notrecommended', u'NOT RECOMMENDED')
G[u'rat'] = JOIN(u'kw_rationale', u"'Rationale:' 枚")
G[u'kwc'] = JOIN(u'kw_close', u'MUST 排他闭合差')
G[u'kwc2'] = JOIN(u'kw_close2', u'SHOULD 排他闭合差')
G[u'kwc3'] = JOIN(u'kw_close3', u'RECOMMENDED 排他闭合差')
G[u'bo'] = JOIN(u'kwbullet_o', u"'o' 项目行")
G[u'bs'] = JOIN(u'kwbullet_star', u"'*' 项目行")
G[u'oway'] = V(u'kw_bullets_onlyone', None, u'只用一种项目符的份数')
G[u'prot'] = EXPR(str(4 - len([1 for i in range(4) if F[u'kw_rationale'][i]])),
                  u"(B57V('kw_rationale', 0) > 0) + (B57V('kw_rationale', 1) > 0)"
                  u" + (B57V('kw_rationale', 2) > 0) + (B57V('kw_rationale', 3) > 0)",
                  u"'Rationale:' 非零的份数")
G[u'bans'] = JOIN(u'ssl_v2_ban', u'SSLv2 禁令行')

G[u'h1'] = JOIN(u'sp_sha1_hy', u"'SHA-1'")
G[u'l1'] = JOIN(u'sp_sha1_lower', u"小写 'sha1'")
G[u'hm'] = JOIN(u'sp_hmac_sha1', u"'HMAC-SHA1'")
G[u'nt'] = JOIN(u'sp_sha1_net', u"'SHA1' 净")
G[u'va'] = JOIN(u'sp_case_variants', u'非零拼写种数')
G[u'fam'] = JOIN(u'sp_total_sha1_family', u'四档相加')
G[u'md5'] = JOIN(u'sp_md5_hy', u"'MD5'")
G[u'mdl'] = JOIN(u'sp_md5_lower', u"小写 'md5'")
G[u'h256'] = JOIN(u'sp_sha256_hy', u"'SHA-256'")
G[u'l256'] = JOIN(u'sp_sha256_lower', u"小写 'sha256'")
G[u'gcm'] = JOIN(u'sp_gcm_sha256', u"'GCM_SHA256'")
G[u'endsha'] = JOIN(u'sp_suite_endsha', u"'_SHA' 结尾套件")
G[u'endT'] = V(u'suite_endsha_T', None, u'1.2 协议里 _SHA 结尾的套件名种数')

G[u'sd'] = JOIN(u'suite_distinct', u'套件名种数')
G[u'so'] = JOIN(u'suite_occ', u'套件名出现处')
G[u'fr'] = JOIN(u'frag_tail', u'悬空下划线碎片')
G[u'ctf'] = V(u'suite_common_TF', None, u'1.2⇎1.3 套件名交集')
G[u'con'] = V(u'suite_common_ON', None, u'两版建议套件名交集')
G[u'nT'] = V(u'suite_from_N_in_T', None, u'新建议点名且在 1.2 协议')
G[u'nF'] = V(u'suite_from_N_in_F', None, u'新建议点名且在 1.3 协议')
G[u'nN'] = V(u'suite_from_N_in_none', None, u'新建议点名而两份协议都没有')
G[u'nTt'] = V(u'suite_N_total', None, u'新建议点名总数')
G[u'nB'] = V(u'suite_bridge_close', None, u'新建议桥闭合差')
G[u'oT'] = V(u'suite_from_O_in_T', None, u'旧建议点名且在 1.2 协议')
G[u'oF'] = V(u'suite_from_O_in_F', None, u'旧建议点名且在 1.3 协议')
G[u'oO'] = V(u'suite_from_O_in_none', None, u'旧建议点名而两份协议都没有')
G[u'oTt'] = V(u'suite_O_total', None, u'旧建议点名总数')
G[u'oB'] = V(u'suite_O_bridge_close', None, u'旧建议桥闭合差')
G[u'sF'] = V(u'suite_F_only', None, u'只在 1.3 协议出现')
G[u'sT'] = V(u'suite_T_only', None, u'只在 1.2 协议出现')

G[u'ct'] = JOIN(u'cite_rfc_tokens', u'RFC 号出现处')
G[u'cd'] = JOIN(u'cite_rfc_distinct', u'不同 RFC 号')
G[u'cb'] = JOIN(u'cite_bracket', u'方括号引用')
G[u'ob'] = JOIN(u'cite_obsoletes_n', u'Obsoletes 列出的号')
G[u'up'] = JOIN(u'cite_updates_n', u'Updates 列出的号')
G[u'obi'] = JOIN(u'cite_obsoleted_inrepo', u'废掉的号里在库的枚')
G[u'obn'] = JOIN(u'cite_obsoletes_notinrepo', u'废掉的号里不在库的枚')
G[u'oball'] = V(u'cite_obsoleted_inrepo_all', None, u'在库取代关系合计')
G[u'pnz'] = V(u'cite_pairs_nonzero', None, u'非零引用对')
G[u'pz'] = V(u'cite_pairs_zero', None, u'零引用对')
G[u'pt'] = V(u'cite_pairs_total', None, u'有序对总数')
G[u'bv'] = V(u'cite_backward_violations', None, u'引用早于自己的违例')
G[u'sel'] = V(u'cite_self_obsoleted', None, u'新建议引用它废掉的旧建议')
G[u'fTN'] = V(u'cite_F_to_N', None, u'1.3 协议引新建议')
G[u'oTN'] = V(u'cite_O_to_N', None, u'旧建议引新建议')

G[u'dt'] = u' ⇎ '.join(F[u'date_raw'])
G[u'mg'] = u' ⇎ '.join(str(x) for x in F[u'month_gap_prev'][1:])
G[u'span'] = V(u'month_span', None, u'首尾月差')
G[u'mgsum'] = EXPR(str(sum(F[u'month_gap_prev'])), u"B57V('month_gap_prev', 1)+B57V('month_gap_prev', 2)+B57V('month_gap_prev', 3)", u'三段月差相加')
G[u'dok'] = V(u'date_seg_n', None, u'日期单调段数')
G[u'ddoc'] = V(u'date_docnum_mono', None, u'文档号与日期同序段数')

G[u'lmn'] = JOIN(u'line_sha_mustnot', u'SHA/MD5 与 MUST NOT 同行')
G[u'lmh'] = JOIN(u'line_sha_mustnot_hy', u"'SHA-1' 与 MUST NOT 同行")
G[u'len'] = JOIN(u'line_sha_in_enum', u"小写 sha1 在枚举行")
G[u'lra'] = JOIN(u'line_rationale_mustnot', u'MUST NOT 后 6 行内有 Rationale')
G[u'b112'] = JOIN(u'bits_112', u"'112 bits'")
G[u'b128'] = JOIN(u'bits_128', u"'128 bits'")
G[u'b192'] = JOIN(u'bits_192', u"'192 bits'")
G[u'b224'] = JOIN(u'bits_224', u"'224 bits'")
G[u'm2048'] = JOIN(u'modulus_2048', u"'2048-bit'")
G[u'm1024'] = JOIN(u'modulus_1024', u"'1024'")
G[u'c224'] = JOIN(u'curves_below_224', u"'less than 224 bits'")
G[u'fwd'] = JOIN(u'fwd_secrecy', u"'forward secrecy'")

G[u'cl'] = V(u'carry_line_o', None, u'旧建议整行种数')
G[u'cn'] = V(u'carry_line_n', None, u'新建议整行种数')
G[u'cs'] = V(u'carry_shared', None, u'共用整行')
G[u'co1'] = V(u'carry_only_o', None, u'只在旧建议')
G[u'co2'] = V(u'carry_only_n', None, u'只在新建议')
G[u'cu'] = V(u'carry_union', None, u'并集')
G[u'cc'] = V(u'carry_close', None, u'整行三档闭合差')
G[u'so1'] = V(u'carry_sent_o', None, u'旧建议句数')
G[u'sn1'] = V(u'carry_sent_n', None, u'新建议句数')
G[u'ss'] = V(u'carry_sent_shared', None, u'共用句')
G[u'sc'] = V(u'carry_sent_close', None, u'句子三档闭合差')
G[u'sunion'] = V(u'carry_sent_union', None, u'句子并集')
G[u'coi'] = V(u'carry_o_in_n_text', None, u'旧建议行在新文里再现')
G[u'cni'] = V(u'carry_n_in_o_text', None, u'新建议行在旧文里再现')
G[u'csub'] = V(u'carry_sub_overlap', None, u'再现口径两向相加')
G[u'csubd'] = EXPR(str(F[u'carry_sub_overlap'] - F[u'carry_shared']),
                   u"B57V('carry_sub_overlap')-B57V('carry_shared')", u'再现口径比行集交多出的')
G[u'prot2'] = EXPR(str(F[u'kw_rationale'][1] + F[u'kw_rationale'][3]),
                   u"B57V('kw_rationale', 1)+B57V('kw_rationale', 3)", u'两版建议写理由的合计')
G[u'ratprot'] = EXPR(str(F[u'kw_rationale'][0] + F[u'kw_rationale'][2]),
                     u"B57V('kw_rationale', 0)+B57V('kw_rationale', 2)", u'两份协议写理由的合计')
G[u'bmixd'] = V(u'kw_mix_docs', None, u'两种项目符混用的文件份数')
G[u'craw'] = V(u'carry_shared_raw', None, u'共用行的原样条数')
G[u'cref'] = V(u'carry_shared_ref', None, u'共用行里的参考文献行')
G[u'ctoc'] = V(u'carry_shared_toc', None, u'共用行里的章节号行')
G[u'cprose'] = V(u'carry_shared_prose', None, u'共用行里的正文行')
G[u'csplit'] = V(u'carry_split_close', None, u'体裁三档闭合差')
G[u'sr'] = V(u'carry_sent_rat', None, u'共用句里带 Rationale 的')
G[u't192'] = V(u'carry_thr_192', None, u'共用句里的 192 门限句')
G[u't224'] = V(u'carry_thr_224', None, u'共用句里的 224 门限句')
G[u'cgap'] = V(u'carry_caliber_gap', None, u'两口径之差')

G[u'i101'] = V(u'id_rsa_pkcs1_sha1', 2, u'rsa_pkcs1_sha1 枚')
G[u'i03'] = V(u'id_ecdsa_sha1', 2, u'ecdsa_sha1 枚')
G[u'idt'] = V(u'id_scheme_total', 2, u'1.3 协议枚举行合计')
G[u'ish'] = V(u'id_sha1_schemes', 2, u'枚举项名含 sha1')
G[u'ileg'] = V(u'id_legacy_block', 2, u'遗留块内枚举项')
G[u'ims'] = V(u'id_must_support_n', None, u'明文必支持的签名枚')
G[u'imss'] = V(u'id_must_support_sha1', None, u'必支持清单里含 sha1 的枚')
G[u'iene'] = V(u'id_enum_lines', 2, u'1.3 协议枚举行')
G[u'it2'] = V(u'id_rsa_pkcs1_sha256', 2, u'rsa_pkcs1_sha256 枚')
G[u'it3'] = V(u'id_rsa_pss_rsae_sha256', 2, u'rsa_pss_rsae_sha256 枚')

G[u'pn'] = V(u'pool_n', None, u'锚候选池条数')
G[u'pb'] = JOIN(u'pool_tag_n', u'池内每源')
G[u'p1'] = JOIN(u'pool_tag_1', u'池内每源里只穿一源')
G[u'px'] = JOIN(u'pool_tag_x', u'池内每源里穿两源以上')
G[u'p2'] = V(u'pool_2', None, u'池内穿两源')
G[u'p3'] = V(u'pool_3', None, u'池内穿三源')
G[u'p4'] = V(u'pool_4', None, u'池内穿四源')
G[u'pcl'] = V(u'pool_close', None, u'池四档闭合差')
for n, note in ((u'anchor_total', u'锚处'), (u'anchor_distinct', u'锚去重串'),
                (u'anchor_err', u'锚错配'), (u'anchor_single', u'归一属一源'),
                (u'anchor_cross', u'归一属两或三源'), (u'anchor_all4', u'归一属四源'),
                (u'checks', u'逐源判成员次数')):
    G[u'tok_' + n] = TOK(n, note)

# ---------- 编码区 ----------
LINE(u'🧭', u"四源字节 {by}: 1.2 协议 {B57V('bytes', 0)} ⇎ 旧建议 {B57V('bytes', 1)} ⇎ 1.3 协议 {B57V('bytes', 2)} ⇎ 新建议 {B57V('bytes', 3)}。"
     u"换行 {ln}, 非空行 {nb}, 最长行 {mx}(四份同为 72 列), 平均行长 {me}, 制表符 {tb}(四份一个不用, 排版靠折行), 行尾空白 0⇎0⇎0⇎0。"
     u"非 ASCII {na}, 字节减字符 {bg}, BOM {bom}: 只有新建议带 BOM 与非 ASCII(共 14 枚), 它的字符数比字节数少 {B57V('bytegap', 3)}; 严格 UTF-8 解码 {utf} 四份全过; "
     u"字符数=字节数在 {eqb} 份上成立; 四份 sha16 是 {shaK} 个不同的串(串本身只进解读注)。")

LINE(u'📏', u"同一出版社的两种页式: '[Page N]' 页标 {pm} ⇎ 页眉行 {hd}, 两者之差 {pg}(前三份页标比页眉多 1, 即首页无顶栏), "
     u"页眉里作者姓列种数 {ah}。新建议两头都是 {B57V('pagemarks', 3)}——它整份不重复页眉页标, 是改版后的序列化; "
     u"页眉样例: 1.2 协议的顶栏 {aHdrT} ⇎ 新建议一份页眉也不写。四份的日期自写为 {dt}, 文档号 5246⇎7525⇎8446⇎9325 与日期同序 {ddoc}／3 段, "
     u"相邻月差 {mg}(三段相加校住 {mgsum}, 与首尾跨度 {span} 一致), 单调段数 {dok}／3。")

LINE(u'📐', u"判词用什么强度的词写成, 是可数的: 排他口径 MUST NOT {mn} ⇎ 纯 MUST {mp} ⇎ SHOULD NOT {sn} ⇎ 纯 SHOULD {sp} ⇎ MAY {my} ⇎ "
     u"RECOMMENDED {rc} ⇎ NOT RECOMMENDED {nrc}(排他闭合差 {kwc} ⇎ {kwc2} ⇎ {kwc3}, 六档全 0)。"
     u"体制差别: 两份协议共写 MUST {B57V('kw_must', 0)}＋{B57V('kw_must', 2)} 枚而两份建议只 {B57V('kw_must', 1)}＋{B57V('kw_must', 3)} 枚, "
     u"但显式理由 'Rationale:' 是 {rat}——两份协议一条不写({ratprot} 条), 两版建议合计 {prot2} 条({prot} 份文书在写), 理由是建议文体的本职。"
     u"项目符号: 'o' 行 {bo} ⇎ '*' 行 {bs}, 两种混用的文件 {bmixd} 份, 只用一种的 {oway}／4——同一份 BCP 的两版换了列表记号而各自不混用: "
     u"同一条禁令在旧建议写作 {aRC4O}, 在新建议把 'o' 换成 '*' 而整句其余逐字不变; "
     u"'SSLv2 禁令'那一行在两版建议里各 1 处({bans}), 新建议一侧是 {aSSLv2N}。")

LINE(u'🪢', u"本条主轴: 同一个哈希在四份文书里是四种东西。带连字符的 'SHA-1' {h1} ⇎ 标识符里的小写 'sha1' {l1} ⇎ "
     u"'HMAC-SHA1' {hm} ⇎ 'SHA1' 刨掉 HMAC 后净 {nt}; 三种拼写非零的种数 {va}——旧建议 {B57V('sp_case_variants', 1)} 种都不写, "
     u"它唯一一次提到 SHA-1 是给 MAC 定强度下限 {aFloor}, 不是签名判词。四档相加 {fam}。"
     u"判决句定位: 含 'SHA-1' 或 'MD5' 且含 'MUST NOT' 的同一行 {lmn}(合计 {EXPR(str(F['line_sha_mustnot'][2]+F['line_sha_mustnot'][3]), u'B57V(\"line_sha_mustnot\", 2)+B57V(\"line_sha_mustnot\", 3)', u'两份判禁行合计')} 处), "
     u"一处是 1.3 协议 {aMustNotF}(带豁免从句: 除非产不出有效证书链), 另一处是新建议 {aVerdictN}(不留从句); "
     u"1.3 协议另有 {aCVF}——握手消息里的签名一律不用, 而 {aAllSHA1} 只准用于遗留证书; 同一份文件对“证书里的签名”和“握手消息里的签名”给了两种强度。"
     u"小写 sha1 落在枚举行 {len}; 1.2 协议把它写成枚举值 {aEnum2} 与 MAC 清单 {aMac}, 那时的默认是 {aPRF} ⇎ {aMD5SHA1}; "
     u"它甚至留了一句 {aOther}——四种身份里只有这一份给 SHA-1 开了“可以换掉”的口子。")

LINE(u'🧱', u"门限同时改数值与强度: 旧建议 {aThr192} ⇎ 新建议 {aThr224}——同族判据从 192 升到 224, 从 SHOULD NOT 升到 MUST NOT。"
     u"字面计数 '192 bits' {b192} ⇎ '224 bits' {b224} ⇎ 'less than 224 bits' {c224}, 两值在四份里各只 1⇎1 处; "
     u"其余门限 '112 bits' {b112} ⇎ '128 bits' {b128} ⇎ '2048-bit' {m2048} ⇎ '1024' {m1024} ⇎ 'forward secrecy' {fwd}。"
     u"判据后面的理由跟得多快也可数: 'MUST NOT' 行之后 6 行内出现 'Rationale:' 的行数 {lra}(建议两份 {B57V('line_rationale_mustnot', 1)}＋{B57V('line_rationale_mustnot', 3)} ⇎ 协议两份 0＋0); "
     u"112/2048 那一档的理由两版建议共用同一行 {aRatN}, 而门限那一行不共用。")

LINE(u'🗣', u"套件名的跨代存活是零: 完整套件名(同一行内一次到位)种数 {sd}, 出现处 {so}, 而 1.2 协议与 1.3 协议的交集 {ctf} 枚——"
     u"整套换了名(T 独有 {sT} ⇎ F 独有 {sF})。两份建议点名的套件里能在库内协议文本找到的: 新建议 {nT}／{nTt} 枚在 1.2 协议 ⇎ {nF} 枚在 1.3 协议 ⇎ "
     u"{nN} 枚两份都不在(三档相加校住 {nTt}, 差 {nB}); 旧建议 {oT}⇎{oF}⇎{oO}, 校住 {oTt}, 差 {oB}。两份建议自己的交集 {con} 枚。"
     u"那 {nN} 枚的正式出处是库里没有的另外几份规范(AES-GCM 与 ECDHE 那一族, 本库只收这四份), 所以“建议点名的套件是否合法存在”不可由本条四份文件判定, 只进注; "
     u"旧建议点首选时写的一行是 {aSuiteO}——它在协议文本里逐字出现与否, 就是上面那两笔桥账。"
     u"以裸 '_SHA' 结尾=SHA-1 套件的套件名 {endsha} 处, 1.2 协议里这样的名有 {endT} 种; 72 列折行切出的悬空下划线碎片 {fr} 枚(旧建议 1 ⇎ 新建议 1)。")

LINE(u'🧵', u"引用方向与时间方向互不违反: 四份文件两两配成 {pt} 个有序对, 非零 {pnz} ⇎ 零 {pz}, 且非零者全部指向比自己早的文件(违例 {bv} 处)。"
     u"RFC 号出现处 {ct}, 不同号 {cd}, 方括号引用 {cb}。谱系行: Obsoletes 列 {ob} 枚 ⇎ Updates 列 {up} 枚; "
     u"其中在库的 {obi}(1.3 协议废 1.2 协议 {aObsF} ⇎ 新建议废旧建议 {aObsN}), 合计 {oball}／2 对取代关系全可在库内验(不在库的 {obn}); "
     u"1.2 协议自己废的三枚 {aObsT} 在库里 0 命中。新建议的谱系行是 {aObsN} ⇎ {aUpdN}(Updates 列它自己不废的那批); "
     u"新建议引用它废掉的旧建议 {sel} 处——废掉不等于不提; "
     u"反向为零: 1.3 协议提新建议 {fTN} 处 ⇎ 旧建议提新建议 {oTN} 处(时间不可能倒流)。")

LINE(u'🗂', u"两版建议之间的搬运, 按三种口径数: 归一后长度 ≥20 的整行种数 {cl} ⇎ {cn}, 按行集交得共用 {cs} 行(旧版一侧独有 {co1} ⇎ 新版一侧独有 {co2}, "
     u"三档相加校住并集 {cu}, 差 {cc}); 换成“只要在新文里逐字再现一次就算搬走”(允许成为别人更长行的一段)得 {coi} ⇎ {cni}, 相加 {csub}, 比行集交多 {csubd}; "
     u"接行归一再断句得句 {so1} ⇎ {sn1}, 共用 {ss} 句(三档校住并集 {sunion}, 差 {sc})。"
     u"两档相差 {cgap}: 句口径只认“接行后成文的声明”, 行口径还认目录行与参考文献行。把行口径那 {craw} 条按体裁拆开——"
     u"参考文献行 {cref} ⇎ 章节号行 {ctoc} ⇎ 正文行 {cprose}(三档校住 {craw}, 差 {csplit}): 只有 {cprose} 行是“同一条声明原样搬过去”的那批。"
     u"共用的 {ss} 条句里带 'Rationale:' 字样的 {sr} 条、含 '192 bits' 的 {t192} 条 ⇎ 含 '224 bits' 的 {t224} 条——"
     u"后两组为 0 就是这条的结论: 门限那句没被搬走而是被换掉({aThr192} ⇎ {aThr224} 互不逐字相等), "
     u"而同一句 SSLv2 判词 {aSSLv2O} 在两版里逐字相同; 'Rationale:' 字样为 0 则来自断句口径本身——冒号后的首字母大写, 标签被切进了上一句的尾部, "
     u"所以“理由是否成批搬走”只能按整行口径判, 那一档共用的是 {cs} 行。")

LINE(u'🧬', u"码位仍然定义着, 但不在强制清单里: 1.3 协议的 SignatureScheme 式枚举行 {iene} 处(含码位括号的枚举行, 正文与附录各一份清单, 合计 {idt} 枚), "
     u"其中名里含 sha1 的 {ish} 枚({a0201} ⇎ ecdsa_sha1(0x0203)), 全部落在 {aLegacyC} 注释块内(块内 {ileg} 枚); "
     u"明文“必须支持”的签名 {ims} 枚({aMSS}), 其中含 sha1 的 {imss} 枚——遗留集与必支持集的交是 0。"
     u"1.3 协议里 rsa_pkcs1_sha256 {it2} 枚 ⇎ rsa_pss_rsae_sha256 {it3} 枚; DSA 系一枚不中({B57V('id_dsa_sha1', 2)} 枚, 只作 RESERVED 注释)。"
     u"遗留身份的正式定义在 {aLegacyDef}——它写明“因已知弱算法而被废弃”, 且这些值“只指证书里的签名”, 握手消息里不定义。")

LINE(u'🧪', u"这条的可核事实分三档, 第一档全部由四份在库字节现推({aMac} ⇎ {aHdrO} ⇎ {aLegacyC} ⇎ {aVerdictN}) ⇒ B57V 可复算: "
     u"四源字节/换行/最长行/制表符/非 ASCII/BOM/sha 种数, 页标与页眉差 {pg}, 关键词六档排他闭合差 {kwc} ⇎ {kwc2} ⇎ {kwc3}, "
     u"项目符单用 {oway}／4, SHA-1 三种拼写的非零种数 {va} 与四档相加 {fam}, 判决行共现合计 {EXPR(str(F['line_sha_mustnot'][2]+F['line_sha_mustnot'][3]), u'B57V(\"line_sha_mustnot\", 2)+B57V(\"line_sha_mustnot\", 3)', u'两份判禁行合计')}, "
     u"门限 192⇎224 各 1 处, 套件名零交集 {ctf} 与两条桥差 {nB} ⇎ {oB}, 引用 12 对违例 {bv}, 在库取代关系 {oball}／2, "
     u"搬运两口径三档闭合 {cc} ⇎ {sc}, 共用句里改判句 {t192}＋{t224}, 遗留集与必支持集交 {imss}, 池四档闭合 {pcl}。"
     u"第二档只在本机成立: 四份字节的磁盘 mtime 与页眉自写的 {dt} 谁新谁旧、抓到的是否该号当前版本——进注不进门槛。"
     u"第三档不可由在库文件判定: 新建议点名的 {nN} 枚套件出自库里没有的规范, IANA 注册表里这些码位当前的弃用标记, "
     u"以及“为什么 1.3 要给证书里的 SHA-1 留豁免”的具体部署理由(正文只给 unless 从句, 不给数据)。"
     u"锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 ◘anchor_total◙ 处／◘anchor_distinct◙ 条去重串, 归属由正文现推, "
     u"每条对四源逐一判成员共 ◘checks◙ 次检查, 归一属一源 ◘anchor_single◙ ⇎ 两或三源 ◘anchor_cross◙ ⇎ 四源 ◘anchor_all4◙, 错配 ◘anchor_err◙ 处。")

LINE(u'∴', u"骨架 ⇒ ① 四源字节 {by}, 最长行 {mx}, 非 ASCII {na}, 页标 {pm} ⇎ 页眉 {hd}; "
     u"② 体制: MUST NOT {mn} ⇎ MUST {mp} ⇎ 'Rationale:' {rat} ⇎ 项目符 'o'{bo}／'*'{bs}; "
     u"③ 主轴: 'SHA-1' {h1} ⇎ 'sha1' {l1} ⇎ 'HMAC-SHA1' {hm} ⇎ 判禁同行 {lmn}; "
     u"④ 门限: 192 SHOULD NOT ⇎ 224 MUST NOT, 字面 {b192} ⇎ {b224}, 理由跟随 {lra}; "
     u"⑤ 套件: 种数 {sd}, T∩F={ctf}, 新建议桥 {nT}＋{nF}＋{nN}−{nTt}={nB}; "
     u"⑥ 引用: {pt} 对里非零 {pnz}, 时序违例 {bv}, 在库取代 {oball}; "
     u"⑦ 搬运: 整行 {cs}／并集 {cu} ⇎ 句子 {ss}／并集 {B57V('carry_sent_o') + B57V('carry_sent_n') - B57V('carry_sent_shared')}, 改判句共用 {t192}＋{t224}; "
     u"⑧ 枚举: sha1 枚举行 {len}, 遗留块 {ileg}, 必支持∩sha1 {imss}。"
     u"判词: “TLS 还能不能用 SHA-1 签名”没有单一答案——问 1.2 协议, 它是枚举值与默认 MAC; 问旧建议, 它连名字都没出现, 只作为 MAC 下限被越过; "
     u"问 1.3 协议, 它在证书里是“MUST NOT 除非别无选择”、在握手消息里是绝对 MUST NOT; 问新建议, 它与 MD5 并列为不留从句的 MUST NOT。"
     u"四种身份都能数出来: 拼写 {h1}, 同行共现 {lmn}, 强度词 {mn}／{mp}, 理由 {rat}, 门限一句改数值一句改强度。", **{})

LINE(u'ℒ', u"方法 ⇒ 遇到“同一个算法在多份规范性文本里被反复改判”的原料, 把“禁不禁”拆成三层可数码再判: "
     u"点名层(SHA-1 的三种拼写各自计数, 旧建议 {B57V('sp_case_variants', 1)} 种都不写)、"
     u"共现层('SHA-1' 与 'MUST NOT' 是否同一行: {lmn})、"
     u"从句层(禁令是否带豁免: 1.3 有 ⇎ 新建议无)。"
     u"两版建议的关系同时按整行({cs} 行)与接行断句({ss} 句)两种口径数, 并把它们的差 {cgap} 登记成键——"
     u"只报“搬运率”会把唯一要紧的改判句盖掉, 所以还要单独报“共用句里含 192⇎224 的枚数”({t192}＋{t224}); "
     u"跨文档命名关系写成零交集({ctf})与两条桥的闭合差({nB} ⇎ {oB}), 而不是断言“1.3 换了名”; "
     u"引用方向做成 {pt} 个有序对的违例计数({bv}), 让“不会引用未来的文件”成为算出来的性质。", **{})

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 四源各 {B57V('chars', 0)} ⇎ {B57V('chars', 1)} ⇎ {B57V('chars', 2)} ⇎ {B57V('chars', 3)} 字符, "
     u"窗口只能取锚点触到的行; 而本条的结论几乎全是跨文档量: T∩F={ctf} 的套件名零交集、{pt} 对引用方向、"
     u"两版建议 {cs} 行 ⇎ {ss} 句的两口径搬运、以及“改判那句在共用池里 0 命中”。"
     u"尤其“同一份文件对证书与握手消息给两种强度”这一条, 任何单源窗口都只看得见它问的那半。"
     u"读它请按“这个判词是哪一份文书、对哪一类签名位置、用哪个强度词说的”来读, 而不是按“少抄了多少原文”。", **{})

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(4) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCH if 1 < len(HITC[a]) < 4]),
       u'all4': len([a for a in ANCH if len(HITC[a]) == 4])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'], u'anchor_all4': CLS[u'all4'],
         u'checks': DIST * 4}
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all4'] == DIST
for n, v in sorted(AMETA.items()):
    reg(str(v), u"B57V('%s')" % n, TOKV.get(n, n))
for n in AMETA:
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv57.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b57flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms57.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[TONF]⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3), (u'four', 4))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV), u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': 4, u'flat': F}
json.dump(CH, io.open(u'corpus/_b57checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(u'%s (%d 字节／非空行 %d／\'[Page N]\' %d 枚／\'SHA-1\' %d 次／\'Rationale:\' %d 条)' % (
    PATH[i], F[u'bytes'][i], F[u'nonblank'][i], F[u'pagemarks'][i], F[u'sp_sha1_hy'][i], F[u'kw_rationale'][i])
    for i in range(4)) +
    u' (四份都来自 rfc-editor.org 的 .txt 序列化; 页眉自写日期 ' + u' ⇎ '.join(F[u'date_raw']) +
    u', 新建议无页眉故取其首部块的那一行; 抓取时刻与磁盘 mtime 只在本机成立, 不进门槛)\n')
联结 = (u'；联结不是“同一份数据的两种序列化”, 而是同一个签名哈希在四份文书里的四种身份: '
        u"1.2 协议把它写成枚举值与默认 MAC('SHA-1' %d 次 ⇎ 小写 %d 次), 旧建议连 'SHA-1' 这个拼写都不写(非零拼写种数 %d, "
        u"只留 'HMAC-SHA1' %d 处当 MAC 下限), 1.3 协议把它关进 Legacy 注释块(枚举行 %d 处含 %d 枚)并对证书⇎握手消息给两种 MUST NOT, "
        u"新建议写下不留从句的 'SHA-1 or MD5 MUST NOT'(判禁同行 %d 处); 两版建议之间整行共用 %d ⇎ 句子共用 %d, "
        u"而门限那句从 192 SHOULD NOT 改成 224 MUST NOT; 两份协议的套件名交集 %d 枚(整套换了名)\n") % (
    F[u'sp_sha1_hy'][0], F[u'sp_sha1_lower'][0], F[u'sp_case_variants'][1], F[u'sp_hmac_sha1'][1],
    F[u'id_enum_lines'][2], F[u'id_sha1_schemes'][2], F[u'line_sha_mustnot'][3],
    F[u'carry_shared'], F[u'carry_sent_shared'], F[u'suite_common_TF'])
text = (u'# B57 四份规范判同一个哈希：枚举值 ⇎ 连拼写都不提 ⇎ 关进遗留块还留豁免 ⇎ 与 MD5 并列禁死（共用 %d 行 ⇎ 改判句 %d 处）\n' % (
    F[u'carry_shared'], F[u'line_sha_mustnot'][2] + F[u'line_sha_mustnot'][3]))
text += (srcline + 联结 +
         u'tags: 排他口径闭合差 三档拼写可见度 判决行同现⇎豁免从句 门限同时改数值与强度 理由条数 Rationale '
         u'项目符两版换记号 套件名跨代零交集 桥闭合 引用⇎时间方向 在库取代关系 搬运率整行⇎句子两口径 '
         u'共用句里改判句 0 命中 遗留集与必支持集交 0 页式两代 BOM 锚归属由正文现推\n' +
         u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
         u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
         u'## ⛓解读注\n\n（此段由 corpus/_fill57.py 从 corpus/_b57checks.json 与 corpus/_b57meas.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d 串 ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两或三源 %d ⇎ 四源 %d ⇎ 错配 %d ｜ 池内取用 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], len(ERR), CH[u'pool_used']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组(复合式) ｜ 0 键折 %d 项' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO)))
for k, v in sorted(COLL.items(), key=lambda x: -len(x[1]))[:8]:
    print(u'  同数 %s ← %s' % (k, u' ⇎ '.join(v)))
print(u'残留未替换占位符 %d ｜ 未点名花括号 %d ｜ 扁平键 %d 个' % (
    len(re.findall(u'◘', body)), len(re.findall(u'[{][a-zA-Z_0-9]+[}]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))), len(F)))
print(u'锚内拉丁 %d ｜ 锚外拉丁 %d ｜ 标签 %d 枚' % (CH[u'letters_in'], CH[u'letters_out'], CH[u'tagn']))
for bk, mk in [(b, b) for b in sorted(F) if b in MM]:
    if F[bk] != MM[mk]:
        print(u'  与采集侧不符: %s 建条目=%s 采集=%s' % (bk, F[bk], MM[mk]))
print(u'对账: 共有键 %d 个, 其中不符 %d 个' % (
    len([b for b in F if b in MM]), len([b for b in F if b in MM and F[b] != MM[b]])))
