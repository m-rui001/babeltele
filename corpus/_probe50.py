# -*- coding: utf-8 -*-
"""B50 探测: 同一模型 ⇎ 六个领域的六份思维链。所有计数现测, 落 corpus/_f50stats.txt。
六份 raw 的头部自报 reasoning_chars/answer_chars 必须等于实测区段长度, 否则抓取丢尾。"""
import io, os, re, sys, hashlib, json

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
SLUGS = [u'math_subsets', u'med_gitalb', u'law_ewca_method', u'fin_credit_cmte',
         u'ind_creep_rupture', u'str_quake_slab']
TAGS = [u'M', u'D', u'L', u'F', u'I', u'S']
R = {}
for slug in SLUGS:
    R[slug] = io.open(u'corpus/raw/cot/%s.md' % slug, encoding='utf-8').read()

# ---------- 头部自报 ⇎ 实测 ----------
META, REG = {}, {}
for slug in SLUGS:
    T = R[slug]
    m = dict(re.findall(u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', T, re.M))
    assert m[u'slug'] == slug, m
    pr = re.search(u'## \\[\\[PROMPT\\]\\]\\n(.*?)\\n\\n## \\[\\[REASONING\\]\\]\\n(.*?)\\n\\n## \\[\\[ANSWER\\]\\]\\n?(.*)$', T, re.S)
    assert pr, slug
    pf, rf, af = pr.group(1), pr.group(2), pr.group(3)
    rfs = rf.rstrip(u'\n')
    assert len(rf) - len(rfs) <= 2, slug
    assert len(rfs) == int(m[u'reasoning_chars']), (slug, len(rfs), len(rf), m[u'reasoning_chars'])
    assert len(af.strip()) == int(m[u'answer_chars']), (slug, len(af.strip()), m[u'answer_chars'])
    sha_pf = hashlib.sha256(pf.encode('utf-8')).hexdigest()[:16]
    assert sha_pf == m[u'prompt_sha256'], (slug, sha_pf, m[u'prompt_sha256'])
    m[u'trail'] = len(rf) - len(rfs)
    m[u'file_chars'] = len(T)
    m[u'prompt_chars'] = len(pf)
    m[u'sha_match'] = sha_pf == m[u'prompt_sha256']
    m[u'sha_recomputed'] = sha_pf
    m[u'reasoning'] = rfs
    META[slug] = m
    REG[slug] = (pf, rfs, af.strip())
MODELS = set(META[s][u'model'] for s in SLUGS)
print(u'模型串 %d 种: %s' % (len(MODELS), sorted(MODELS)))
print(u'题面哈希种类: %d (自校验命中 %d/6)' % (len(set(META[s][u'prompt_sha256'] for s in SLUGS)),
                                             len([1 for s in SLUGS if META[s][u'sha_match']])))
print(u'trail %s' % [META[s][u'trail'] for s in SLUGS])
print(u'题面字符 %s' % [META[s][u'prompt_chars'] for s in SLUGS])
print(u'推理字符 %s' % [len(REG[s][1]) for s in SLUGS])
print(u'回答字符 %s' % [len(REG[s][2]) for s in SLUGS])
print(u'文件字符 %s' % [META[s][u'file_chars'] for s in SLUGS])
print(u'抓取时刻 %s' % [META[s][u'retrieved'] for s in SLUGS])

# ---------- 语汇计数 ----------
PATS = {
    u'wait': r'(?i)\bWait\b',
    u'actually': r'(?i)\bactually\b',
    u'maybe': r'(?i)\bmaybe\b|\bperhaps\b',
    u'prob': r'(?i)\bprobably\b|\blikely\b',
    u'assume': r'(?i)\bassume[ds]?\b|\bassuming\b',
    u'unsure': r'(?i)\bnot sure\b|\bunclear\b|\bi (?:think|believe)\b',
    u'verif': r'(?i)\bcheck\b|\bverify\b|\bsanity\b|\bdouble[- ]check\b|\bconfirm\b',
    u'redo': r'(?i)\bredo\b|\bstart over\b|\blet me (?:recompute|recheck)\b',
    u'wrong': r'(?i)\bwrong\b|\bmistake\b|\berror\b|\boops\b',
    u'therefore': r'(?i)\btherefore\b|\bthus\b|\bhence\b|\bso\b',
    u'however': r'(?i)\bhowever\b|\bbut\b|\balthough\b|\bwhereas\b',
    u'must': r'(?i)\bmust\b',
    u'caveat': r'(?i)\bcaveat\b|\bcaution\b|\bcareful\b|\bbeware\b',
    u'final': r'(?i)\bfinal\b|\bconclusion\b|\banswer:|\brecommend',
    u'quote': r'"[^"]{10,60}"',
    u'equality': r'=',
    u'unit': r'(?i)\b(?:mm|MPa|kN|GPa|°C|kg|m|s|y|years|months|mm/yr|kW|Hz|Bq|Sv|Gy|%)\b',
    u'cfr': r'(?i)\b(?:article|section|§|clause|paragraph|paragraphs)\b',
    u'study': r'(?i)\bstudy\b|\bpaper\b|\bauthor',
}
STATS = {}
for slug in SLUGS:
    rf = REG[slug][1]
    STATS[slug] = dict((k, len(re.findall(v, rf))) for k, v in PATS.items())
    STATS[slug][u'sent'] = len(re.findall(r'[.!?](?:\s|$)', rf))
    STATS[slug][u'para'] = len([x for x in rf.split(NL) if x.strip()])
    STATS[slug][u'numsent'] = len([x for x in re.split(r'(?<=[.!?])\s+', rf) if re.search(r'\d', x)])
    STATS[slug][u'qmarks'] = rf.count(u'?')
    STATS[slug][u'try'] = len(re.findall(r'(?i)\blet me try\b|\btry\b', rf))
for k in PATS:
    print(u'%-10s %s' % (k, [STATS[s][k] for s in SLUGS]))
for k in (u'sent', u'para', u'numsent', u'qmarks', u'try'):
    print(u'%-10s %s' % (k, [STATS[s][k] for s in SLUGS]))

# ---------- 落统计文件(条目与 DERIV 都用这份) ----------
out = []
out.append(u'slugs\t%s' % u' '.join(SLUGS))
out.append(u'tags\t%s' % u' '.join(TAGS))
out.append(u'models\t%d' % len(MODELS))
out.append(u'rcot\t%s' % u' '.join(str(len(REG[s][1])) for s in SLUGS))
out.append(u'acot\t%s' % u' '.join(str(len(REG[s][2])) for s in SLUGS))
out.append(u'pcot\t%s' % u' '.join(str(len(REG[s][0])) for s in SLUGS))
out.append(u'fchars\t%s' % u' '.join(str(META[s][u'file_chars']) for s in SLUGS))
out.append(u'fbytes\t%s' % u' '.join(str(os.path.getsize(u'corpus/raw/cot/%s.md' % s)) for s in SLUGS))
out.append(u'sent\t%s' % u' '.join(str(STATS[s][u'sent']) for s in SLUGS))
out.append(u'para\t%s' % u' '.join(str(STATS[s][u'para']) for s in SLUGS))
out.append(u'numsent\t%s' % u' '.join(str(STATS[s][u'numsent']) for s in SLUGS))
for k in PATS:
    out.append(u'%s\t%s' % (k, u' '.join(str(STATS[s][k]) for s in SLUGS)))
print(u'每万字归一(maybe⇎equality⇎cfr⇎must⇎unsure⇎wrong):')
for s in SLUGS:
    print(u'  %-18s %s' % (s, [round(10000.0 * STATS[s][k] / len(REG[s][1]), 1)
                               for k in (u'maybe', u'actually', u'equality', u'cfr', u'must', u'unsure', u'wrong', u'wait')]))
io.open(u'corpus/_f50stats.txt', 'w', encoding='utf-8', newline='\n').write(u'\n'.join(out) + u'\n')
print(u'stats 落盘: %d 行' % len(out))
