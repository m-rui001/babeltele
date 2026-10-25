# -*- coding: utf-8 -*-
# 外派件沙箱跑壳: 把 open/io.open 的写模式套上白名单, 再 exec 目标脚本。
# 白名单外的写(audit.py ⇎ README.md ⇎ 在用的 _pickNN/_mkNN ⇎ 任意他档)一律拒绝并计一次 SANDBOX 命中,
# 因为回收件的写目标不可信——它只该产自己的条目文件与自己的度量 json。
import builtins
import io
import os
import re
import sys

ALLOW = re.compile(u'(_apick_|_b\\d+(flat|meas|contract)\\.json|_tmp|babeltele/|emitbox)', re.I)
_real = io.open


def guarded(f, mode=u'r', *a, **k):
    if any(c in str(mode) for c in u'wxa') and not ALLOW.search(str(f)):
        raise IOError(u'SANDBOX-DENY write %r mode=%r' % (f, mode))
    return _real(f, mode, *a, **k)


io.open = guarded
builtins.open = guarded
target = sys.argv[1]
src = _real(target, encoding='utf-8', errors='replace').read()
g = {'__name__': '__main__', '__file__': target}
exec(compile(src, target, 'exec'), g)
