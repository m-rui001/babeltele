# -*- coding: utf-8 -*-
import io, re, sys
def render(fn):
    s = io.open('raw/pwd/'+fn, encoding='utf-8', errors='replace').read()
    o, i = [], 0
    while True:
        j = s.find(u'<', i)
        if j < 0:
            o.append(s[i:]); break
        o.append(s[i:j])
        if s[j:j+4] == u'<!--':
            k = s.find(u'-->', j)
            i = (k+3) if k > 0 else j+1
            continue
        k = s.find(u'>', j)
        if k < 0:
            o.append(s[j:]); break
        t = s[j:k+1].lower()
        if u'<br' in t or u'</p' in t or u'</div' in t or u'</li' in t or u'</h' in t or u'</tr' in t:
            o.append(u'\n')
        i = k+1
    s = u''.join(o)
    s = re.sub(u'&#(\d+);', lambda m: unichr(int(m.group(1))) if sys.version_info[0]==2 else chr(int(m.group(1))), s)
    for k, v in ((u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&quot;', u'"'), (u'&#8217;', u"'"),
                 (u'&rsquo;', u"'"), (u'&ldquo;', u'"'), (u'&rdquo;', u'"'), (u'&minus;', u'-'),
                 (u'&times;', u'x'), (u'&hellip;', u'...'), (u'&mdash;', u'-')):
        s = s.replace(k, v)
    s = re.sub(u'[ \t]+', u' ', s)
    return s
for fn in ('nist_63b_rev3.html', 'nist_63b_rev4.html', 'ncsc_passwords.html'):
    t = render(fn)
    io.open('_scout59_%s.txt' % fn.split('.')[0], 'w', encoding='utf-8').write(t)
    print(fn, len(t), 'chars', len(t.split('\n')), 'lines')
