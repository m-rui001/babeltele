# -*- coding: utf-8 -*-
"""B51 探测: 同一模型、同一道题的两次采样, 哪些是逐字复现的文本、哪些必须重推。
用法: python -X utf8 corpus/_probe51.py <slugA> <slugB>
自检两档: 自己对自己应当处处满值; 换一道题应当断崖式下跌(否则“复现”这个量没有区分力)。
所有数现测; 区段找法用严格分节正则(不吃首尾换行), 头部自报长度与题面 sha 逐份验过才继续。"""
import difflib, hashlib, io, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
SECRX = (u'## \\[\\[PROMPT\\]\\]\\n(.*?)\\n\\n## \\[\\[REASONING\\]\\]\\n(.*?)'
         u'\\n\\n## \\[\\[ANSWER\\]\\]\\n?(.*)$')
HEADRX = u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$'


def load(slug):
    p = u'corpus/raw/cot/%s.md' % slug
    t = io.open(p, encoding='utf-8').read()
    g = re.search(SECRX, t, re.S)
    assert g, slug
    h = dict(re.findall(HEADRX, t, re.M))
    assert len(g.group(2)) == int(h['reasoning_chars']), (slug, len(g.group(2)), h['reasoning_chars'])
    assert len(g.group(3).strip()) == int(h['answer_chars']), slug
    assert hashlib.sha256(g.group(1).encode('utf-8')).hexdigest()[:16] == h['prompt_sha256'], slug
    return dict(slug=slug, raw=t, prompt=g.group(1), rf=g.group(2), ans=g.group(3).strip(),
                model=h['model'], retr=h['retrieved'], bytes=os.path.getsize(p))


def lines(x):
    return [l.strip() for l in x.split(NL) if l.strip()]


def sents(x):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', x) if s.strip()]


def shingles(x, n=5):
    w = re.findall(u'[a-z0-9]+', x.lower())
    return set(tuple(w[i:i + n]) for i in range(len(w) - n + 1))


def blocks(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    bs = sm.get_matching_blocks()
    tot = sum(x.size for x in bs)
    top = max(bs, key=lambda x: x.size)
    return tot, top.size, a[top.a:top.a + top.size], sm.ratio()


PATS = {
    u'wait': u'(?i)\\bWait\\b', u'actually': u'(?i)\\bactually\\b',
    u'maybe': u'(?i)\\bmaybe\\b|\\bperhaps\\b', u'prob': u'(?i)\\bprobably\\b|\\blikely\\b',
    u'assume': u'(?i)\\bassume[ds]?\\b|\\bassuming\\b',
    u'unsure': u'(?i)\\bnot sure\\b|\\bunclear\\b|\\bi (?:think|believe)\\b',
    u'verif': u'(?i)\\bcheck\\b|\\bverify\\b|\\bsanity\\b|\\bdouble[- ]check\\b|\\bconfirm\\b',
    u'redo': u'(?i)\\bredo\\b|\\bstart over\\b|\\blet me (?:recompute|recheck)\\b',
    u'wrong': u'(?i)\\bwrong\\b|\\bmistake\\b|\\berror\\b|\\boops\\b',
    u'therefore': u'(?i)\\btherefore\\b|\\bthus\\b|\\bhence\\b|\\bso\\b',
    u'however': u'(?i)\\bhowever\\b|\\bbut\\b|\\balthough\\b|\\bwhereas\\b',
    u'must': u'(?i)\\bmust\\b', u'caveat': u'(?i)\\bcaveat\\b|\\bcaution\\b|\\bcareful\\b|\\bbeware\\b',
    u'final': u'(?i)\\bfinal\\b|\\bconclusion\\b|\\banswer:|\\brecommend',
    u'equality': u'=', u'arrow': u'->', u'letme': u'(?i)\\blet me\\b',
    u'lets': u"(?i)\\blet's\\b", u'hmm': u'(?i)\\bHmm\\b', u'need': u'(?i)\\bneed\\b',
    u'q': u'\\?', u'bold': u'\\*\\*[^*]{2,60}\\*\\*',
}


def firstdiff(a, b):
    la, lb = lines(a), lines(b)
    for i in range(min(len(la), len(lb))):
        if la[i] != lb[i]:
            return i
    return None


def split_echo(ra, rb, prompt, minlen=8):
    """把逐字复现拆成两档: 题面回声(给定文本, 本来就该一样) ⇎ 推理复用(自己写出来的句子又撞上了)。
    逐字符匹配块可能短到空格, 所以只统计 >=minlen 的块, 且按“是否能在题面里原样找到”分类。
    判题面回声先剥掉块首尾的引号/标点/空白: 模型引用题面时会在原文两端贴上引号,
    整块直接 in prompt 会差一个字符而误判。"""
    bs = [x for x in difflib.SequenceMatcher(None, ra, rb, autojunk=False).get_matching_blocks()
          if x.size >= minlen]
    tot = sum(x.size for x in bs)
    ev = [x for x in bs if ra[x.a:x.a + x.size].strip(u'"“’\' \n\t.,;:!?') in prompt]
    e = sum(x.size for x in ev)
    return tot, e, tot - e, len(bs), bs, ev


def in_prompt(items, prompt):
    """共有句子/共有五词串里, 有多少其实来自题面。"""
    pg = re.findall(u'[a-z0-9]+', prompt.lower())
    psh = set(tuple(pg[i:i + 5]) for i in range(len(pg) - 4))
    hit = [x for x in items if (x in prompt if isinstance(x, type(u'')) else x in psh)]
    return len(hit)


def report(a, b):
    ra, rb = a['rf'], b['rf']
    la, lb = lines(ra), lines(rb)
    sa, sb = sents(ra), sents(rb)
    ha, hb = shingles(ra), shingles(rb)
    J = lambda x, y, z: 100.0 * x / max(1, y + z - x)
    ov_l = len(set(la) & set(lb))
    ov_s = len(set(sa) & set(sb))
    ov_g = len(ha & hb)
    tot, topn, topstr, ratio = blocks(ra, rb)
    o = [u'== %s ⇎ %s ==' % (a['slug'], b['slug'])]
    o.append(u'同题=%s (sha %s ⇎ %s) 模型 %s ⇎ %s 时刻 %s ⇎ %s' % (
        a['prompt'] == b['prompt'], hashlib.sha256(a['prompt'].encode('utf-8')).hexdigest()[:8],
        hashlib.sha256(b['prompt'].encode('utf-8')).hexdigest()[:8],
        a['model'].split('/')[-1], b['model'].split('/')[-1], a['retr'], b['retr']))
    o.append(u'推理字符 %d ⇎ %d (比值 %.2f) ⇎ 磁盘 %d ⇎ %d ⇎ 行 %d ⇎ %d ⇎ 句 %d ⇎ %d' % (
        len(ra), len(rb), 1.0 * max(len(ra), len(rb)) / max(1, min(len(ra), len(rb))),
        a['bytes'], b['bytes'], len(la), len(lb), len(sa), len(sb)))
    o.append(u'逐行复现 交 %d 行 (占A %.1f%% ⇎ Jaccard %.1f%%)' % (
        ov_l, 100.0 * ov_l / max(1, len(set(la))), J(ov_l, len(set(la)), len(set(lb)))))
    o.append(u'逐句复现 交 %d 句 (占A %.1f%% ⇎ Jaccard %.1f%%)' % (
        ov_s, 100.0 * ov_s / max(1, len(set(sa))), J(ov_s, len(set(sa)), len(set(sb)))))
    o.append(u'五词串复现 交 %d (Jaccard %.2f%%)' % (ov_g, J(ov_g, len(ha), len(hb))))
    o.append(u'字符层: 逐字命中共 %d 字符 (占A %.1f%% ⇎ SequenceMatcher ratio %.3f), 最长连续 %d 字符' % (
        tot, 100.0 * tot / max(1, len(ra)), ratio, topn))
    o.append(u'  最长块: %.70s' % topstr.replace(NL, u' ⏎ '))
    fd = firstdiff(ra, rb)
    o.append(u'首个不同行 %s ⇎ 前缀同 %d 行' % (fd, (fd if fd is not None else min(len(la), len(lb)))))
    o.append(u'末字符 %r ⇎ %r' % (ra[-1], rb[-1]))
    o.append(u'回答区 %d ⇎ %d 字符')
    o[-1] = o[-1] % (len(a['ans']), len(b['ans']))
    long_ = sorted(set(la) & set(lb), key=len, reverse=True)[:5]
    o.append(u'共有长行 top5: ' + u' ‖ '.join(u'%d 字 %.36s' % (len(x), x) for x in long_))
    ct, ce, co, cb, bs, ev = split_echo(ra, rb, a['prompt'])
    assert sum(x.size for x in bs) == ct and ce + co == ct
    o.append(u'复现拆解(块>=8 字, 共 %d 块 %d 字符): 题面回声 %d (%.1f%%) ⇎ 推理复用 %d (%.1f%%)' % (
        cb, ct, ce, 100.0 * ce / max(1, ct), co, 100.0 * co / max(1, ct)))
    rest = sorted([x for x in bs if x not in ev], key=lambda x: -x.size)
    evo = sorted(ev, key=lambda x: -x.size)
    o.append(u'  题面回声最长块 %d 字: %s' % (evo[0].size, ra[evo[0].a:evo[0].a + evo[0].size][:78].replace(NL, u' ⏎ ')))
    o.append(u'  推理复用里最长 3 块: ' + u' ‖ '.join(
        u'%d 字 %s' % (x.size, ra[x.a:x.a + x.size].replace(NL, u' ⏎ ')[:60]) for x in rest[:3]))
    o.append(u'  推理复用 >=8 字段落数 %d ⇎ 最长连续 %d 字' % (len(rest), rest[0].size if rest else 0))
    ps = in_prompt(sorted(set(sa) & set(sb)), a['prompt'])
    psg = in_prompt(ha & hb, a['prompt'])
    o.append(u'共有 %d 句里题面来 %d 句 ⇎ 共有 %d 个五词串里题面来 %d 个' % (
        ov_s, ps, ov_g, psg))
    d = []
    for k in sorted(PATS):
        ca, cb = len(re.findall(PATS[k], ra)), len(re.findall(PATS[k], rb))
        d.append(u'%s %d⇎%d(%+d)' % (k, ca, cb, cb - ca))
    o.append(u'词法计数 ' + u' '.join(d))
    o.append(u'回答区摘录 A: %s' % (a['ans'][:80].replace(NL, u' ⏎ ') or u'(空)'))
    o.append(u'回答区摘录 B: %s' % (b['ans'][:80].replace(NL, u' ⏎ ') or u'(空)'))
    print(NL.join(o))
    return dict(ov_line=ov_l, ov_sent=ov_s, ov_sh=ov_g, lcs=topn, char_match=tot,
                ratio=ratio, first=firstdiff(ra, rb), lena=len(ra), lenb=len(rb),
                echo=ce, orig=co, blocks=cb, sent_from_prompt=ps, sh_from_prompt=psg)


if __name__ == '__main__':
    slugs = sys.argv[1:] or [u'math_subsets', u'math_subsets']
    if len(slugs) == 2:
        report(load(slugs[0]), load(slugs[1]))
    else:
        A = load(slugs[0])
        for s in slugs[1:]:
            report(A, load(s))
