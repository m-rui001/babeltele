import re, sys, io, unicodedata
import unicodedata as ud
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SECTIONS = [
    (0x0530,0x058F,'Armenian'),(0x10A0,0x10FF,'Georgian'),(0x1F100,0x1F1FF,'EnclosedSuppl'),(0x1F200,0x1F2FF,'EnclosedIdeo'),
    (0x1D400,0x1D7FF,'MathAlnum'),
    (0x2B00,0x2BFF,'ArrowsExt'),
    (0x0041,0x005A,0x0061,0x007A,'Latin'),
    (0x0370,0x03FF,'Greek'),(0x0400,0x04FF,'Cyrillic'),(0x0590,0x05FF,'Hebrew'),
    (0x0E00,0x0E7F,'Thai'),(0x3040,0x309F,'Hiragana'),(0x30A0,0x30FF,'Katakana'),
    (0x4E00,0x9FFF,'Han'),(0xAC00,0xD7AF,'Hangul'),(0x3000,0x303F,'CJK-Punct'),
    (0xFF00,0xFFEF,'Fullwidth'),(0x2190,0x21FF,'Arrows'),(0x2200,0x22FF,'Math'),
    (0x2500,0x257F,'Box'),(0x25A0,0x25FF,'Geometric'),(0x2600,0x26FF,'Misc-Symbols'),
    (0x2700,0x27BF,'Dingbats'),(0x1F300,0x1FAFF,'Emoji'),(0x2000,0x206F,'Gen-Punct'),
    (0x2C7C,0x2C7C,'Tone'),(0x0300,0x036F,'Comb-Diacritic'),
]
def script(cp):
    for s in SECTIONS:
        if len(s) == 5:
            if (s[0]<=cp<=s[1]) or (s[2]<=cp<=s[3]): return s[4]
        elif s[0]<=cp<=s[1]: return s[2]
    return None

def analyze(name, text):
    chars = text.replace('\n','')
    n = len(chars)
    uniq = set(chars)
    sc = Counter()
    scripts = set()
    for ch in chars:
        s = script(ord(ch))
        if s: scripts.add(s); sc[s]+=1
    words = len(re.findall(r'\w+', text)) or 1
    ent = n/words
    return dict(n=n, uniq=len(uniq), scripts=sorted(scripts), nscr=len(scripts), ent=ent, sc=sc)

out = []
out.append('| entry | original chars | babeltele chars | retention | unique symbols | scripts(种类) | 熵:chars/word |')
out.append('|---|---|---|---|---|---|---|')
tot_o=tot_b=0; all_enc=''
import glob, os
for p in sorted(glob.glob('corpus/babeltele/B*.md')):
    t = open(p,encoding='utf-8').read()
    mo = re.search(r'\[\[原始语料\|ORIGINAL\]\]\n(.*?)\n\n## ', t, re.S)
    mb = re.search(r'⟪BabelTele⟫\n(.*?)\n\n## ', t, re.S)
    orig, enc = mo.group(1), mb.group(1)
    all_enc += enc
    a, b = analyze(p, orig), analyze(p, enc)
    tot_o+=len(orig); tot_b+=len(enc)
    out.append(f'| {os.path.basename(p)[:21]} | {len(orig)} | {len(enc)} | {len(enc)/len(orig)*100:.1f}% | {b["uniq"]} | {b["nscr"]} | {b["ent"]:.2f} |')

a = analyze('ALL', all_enc)
out.append(f'| **TOTAL** | {tot_o} | {tot_b} | **{tot_b/tot_o*100:.1f}%** | {a["uniq"]} | **{a["nscr"]}** | {a["ent"]:.2f} |')
print('\n'.join(out))
print('\n=== 语料库 BabelTele 编码区 脚本分布 (字符数) ===')
for s,c in a['sc'].most_common(): print(f'  {s:14s} {c}')
print('\n脚本种类:', ', '.join(a['scripts']))
print('唯一码点:', a['uniq'], '/ 总字符:', a['n'])
