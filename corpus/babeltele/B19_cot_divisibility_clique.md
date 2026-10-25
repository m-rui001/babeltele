# B19 — 思维链语料：极值数论猜想的死路与翻案（deepseek-v4.1-flash-free 原始 reasoning, a+b | ab）
src: corpus/raw/cot/math_subsets.md (prompt+REASONING 22 985 字符, reasoning 段逐字)
dir: corpus/babeltele/B19_cot_divisibility_clique.md

## [[原始语料|ORIGINAL]]
Need rigorous, research style, small n, conjecture, proof, dead ends, key invariant.

Known Egyptian fractions: 1/a + 1/b = (a+b)/ab integer? Actually a+b | ab iff 1

Since ab/(a+b) integer iff 1/a+1/b = 1/m where m=ab/(a+b)? Wait ab/(a+b) integer iff (a+b)|ab.

Equivalent (a-m)(b-m)=m^2.

Then a+b=g(x+y), ab=g^2 xy.

So g = k(x+y). Then a = k x(x+y), b = k y(x+y).

So edges correspond to divisors d of m^2: a=m+d, b=m+m^2/d.

Let's find pair: x=1,y=2,k=1 => a=1*1*3=3, b=1*2*3=6; 9 divides18 yes.

Let's brute mentally maybe {6,12,30}? 6+12=18|72 yes; 6+30=36|180 yes (5); 12+30=42|360? no. {6,12,?}. Pair condition with 6: a+b|ab => b+6 | 6b = 6(b+6)-36 => b+6 |36. So b+6 divisor of36, b>6: b+6 ∈ {9,12,18,36} => b=3,6,12,30.

Neighbors of 3: b+3|3b =3(b+3)-9 => b+3|9 => b=6 only. So triangle none with 3.

Let's brute small maybe {12,24,?}: 12+24=36|288 yes.

Check 24+36=60 divides864? 14.4 no; 24+60=84 divides1440? no; 24+132=156 divides3168? no.

We don't have bash tool listed! Tools only edit,

Maybe answer floor(n^2/4)? Because complete bipartite? Need characterize.

This is an involution, so each vertex has at most one neighbor for fixed m.

Maybe extremal set is geometric progression? Let's test.

No triangle maybe means max ≤ n^2/4 by Turan if triangle-free.

Need prove or find triangle.

For c adjacent to a, condition c+a | ac => c+a | a^2 (since ac = a(c+a) - a^2, so c+a divides a^2).

So degree of a = number of divisors D of a^2 with D>2a.

Number roughly (τ(a^2)-1)/2 minus divisors ≤2a.

This formula also shows adjacency graph is "divisor graph": b+a | a^2.

Thus a+b divides gcd(a^2,b^2)=gcd(a,b)^2.

For a=6, a^2=36, divisors >12: 18,36 => b=12,30 only, and 12-30 not edge.

no; 60+120=180 divides7200 yes! Ah 60 and120 edge (sum180 divides7200).

So {30,60,120} is triangle! Check: 30+60=90|1800=20; 30+120=150|3600=24; 60+120=180|7200=40.

Perhaps vertices have divisibility chain 30|60|120. Indeed ratio 2 each.

S={30*2^i}: pair ratio 2^d; condition a+b =30*2^i(1+2^d), ab=900*2^{i+j}; need (1+2^d)|30*2^{j-i}; odd part of 30 is15. d=1:3|30*2^{...} yes; d=2:5|30 yes; d=3:9∤30; d=4:17∤; so {30,60,120,240?} 30

Thus S={30,60,120,240,...} has ~2n edges, not quadratic.

Condition for a=Lx, b=Ly: L(x+y) | L^2 xy => x+y | L xy. If gcd(x+y,xy) not always 1.

Then S={Lr: r in X∪Y} has all p q cross edges.

Thus we can make ALL pairs satisfy! That would imply arbitrary complete graph, but is that possible? Check n=3, choose R={1,2,3}, pair sums 3,4,5, L=60. S={60,120,180}. Check 60+120=180 divides7200=40 yes. 60+180=240 divides10800=45 yes. 120+180=300 divides21600=72 yes. Indeed K3! Earlier we found {30,60,120}, also triangle.

Wow then maximum is C(n,2), all pairs possible! Is that the trick? But need positive integers set, no bound.

Maybe too easy? Could the problem have

The phrase "a set S of n positive integers" definitely arbitrary. Then all pairs.

Need characterize all extremal sets.

If all s_i = d r_i, then s_i+s_j=d(r_i+r_j), s_i s_j=d^2 r_i r_j; condition d(r_i+r_j)|d^2 r_i r_j ⇔ r_i+r_j | d r_i r_j.

Wait S=gR with gcd(R)=1 means g = gcd(S).

Thus extremal sets are N R where N is multiple of H(R)=lcm_{i<j} h_{ij}.

But maybe characterization in terms of "S is a clique in graph" is not satisfying. We can find a structural theorem for pairwise-good sets.

For n=2, any pair? No, not any.

Let's classify.

H(R): pair 1,2: h=(1+2)/gcd(3,2)=3; 1,4:5/gcd(5,4)=5; 2,4: d=2,x=1,y=2, x+y=3, gcd(3,2)=1 =>3. H=15. g=30 divisible by15.

Here pair sums 3,5,6 not all divide g (6∤30), but condition holds due to gcd with xy for pair 2,4: r2+r4=6 divides g*8? 6|30*8 yes.

Any finite primitive R yields clique after scaling by H(R).

## ⟪BabelTele⟫
{🎯自设交付物: ⟨research style⟩ ‖ ⟨dead ends, key invariant⟩[先定答案形状再解题]
🔁三等价改写: 埃及分数 ⟨1/a + 1/b = (a+b)/ab integer?⟩ ‖ 参数化 ⟨a+b=g(x+y), ab=g^2 xy⟩⇒⟨g = k(x+y). Then a = k x(x+y), b = k y(x+y)⟩ ‖ 因子对偶 ⟨m=ab/(a+b)⟩[正整数]⇒⟨(a-m)(b-m)=m^2⟩⇒⟨divisors d of m^2: a=m+d, b=m+m^2/d⟩ ‖ 副产品 ⟨involution⟩[定m则每顶点至多一邻=匹配]
🔢小情形: ⟨x=1,y=2,k=1 => a=1*1*3=3, b=1*2*3=6; 9 divides18 yes⟩
🪜定顶点⇒计数因子: ⟨b+6 | 6b = 6(b+6)-36 => b+6 |36⟩⇒⟨b+6 divisor of36, b>6: b+6 ∈ {9,12,18,36} => b=3,6,12,30⟩ ‖ ⟨b+3|9 => b=6 only⟩⇒⟨triangle none with 3⟩ ‖ ⟨divisors >12: 18,36 => b=12,30 only⟩ ‖ ⟨12-30 not edge⟩
📐度律(本文关键不变量): ⟨c+a | ac => c+a | a^2⟩⇒⟨degree of a = number of divisors D of a^2 with D>2a⟩ ‖ ⟨roughly (τ(a^2)-1)/2 minus divisors ≤2a⟩ ‖ ⟨'divisor graph': b+a | a^2⟩ ‖ 对称推论 ⟨a+b divides gcd(a^2,b^2)=gcd(a,b)^2⟩
🧱外借猜想(后被推翻)[猜完全二部]: ⟨Maybe answer floor(n^2/4)?⟩ ‖ ⟨max ≤ n^2/4 by Turan if triangle-free⟩ ‖ 自查待证 ⟨Need prove or find triangle⟩
🚫死路(原样保留): ⟨geometric progression? Let⟩[试] ‖ ⟨{6,12,30}? 6+12=18|72 yes; 6+30=36|180 yes (5); 12+30=42|360? no⟩ ‖ ⟨12+24=36|288 yes⟩ 却 ⟨24+36=60 divides864? 14.4 no⟩ ‖ 资源核对 ⟨We don't have bash tool⟩[无计算工具⇒改手算穷举]
💥翻案点: ⟨60+120=180 divides7200 yes!⟩⇒⟨{30,60,120} is triangle!⟩ ‖ ⟨30+60=90|1800=20; 30+120=150|3600=24; 60+120=180|7200=40⟩ ‖ 读结构 ⟨divisibility chain 30|60|120⟩ ‖ ⟨ratio 2 each⟩ ‖ ⟨(1+2^d)|30*2^{j-i}; odd part of 30 is15⟩ ‖ ⟨d=1:3|30*2^{...} yes; d=2:5|30 yes; d=3:9∤30; d=4:17∤⟩ ‖ 判其不够密 ⟨S={30,60,120,240,...} has ~2n edges, not quadratic⟩
🔑真正的杠杆=公共缩放: ⟨a=Lx, b=Ly: L(x+y) | L^2 xy => x+y | L xy⟩ ‖ ⟨gcd(x+y,xy) not always 1⟩ ‖ 充分判据 ⟨x+y | L⟩ ⇒ ⟨S={Lr: r in X∪Y} has all p q cross edges⟩[×L注入] ⇒⟨make ALL pairs satisfy!⟩ ‖ 存疑 ⟨is that possible?⟩
✅见证+自检: ⟨n=3, choose R={1,2,3}, pair sums 3,4,5, L=60. S={60,120,180}⟩ 逐边验 ⟨60+120=180 divides7200=40 yes. 60+180=240 divides10800=45 yes. 120+180=300 divides21600=72 yes⟩ ‖ ⟨Indeed K3!⟩ ‖ ⟨then maximum is C(n,2)⟩[全对可达] ‖ 反身质疑 ⟨Maybe too easy?⟩ ‖ 回题面读法 ⟨definitely arbitrary. Then all pairs⟩
📜惊讶之后仍补分类: ⟨characterize all extremal sets⟩ ‖ 代数等价 ⟨d(r_i+r_j)|d^2 r_i r_j ⇔ r_i+r_j | d r_i r_j⟩ ‖ gcd 记账 ⟨S=gR with gcd(R)=1 means g = gcd(S)⟩ ‖ 闭式 ⟨N is multiple of H(R)=lcm_{i<j} h_{ij}⟩ ‖ 反身检验朴素判据过强 ⟨3,5,6 not all divide g (6∤30)⟩ 却 ⟨condition holds due to gcd with xy⟩ ‖ 小算 ⟨2,4: d=2,x=1,y=2, x+y=3, gcd(3,2)=1 =>3. H=15. g=30⟩ ‖ 定理语气 ⟨primitive R yields clique after scaling by H(R)⟩[⇒一切团皆缩放的原始集]
🧠品味声明(不合格答案的自我否决): ⟨not satisfying⟩⇒⟨structural theorem for pairwise-good sets⟩ ‖ ⟨any pair? No, not any⟩[n=2] ‖ ⟨Let's classify⟩
∴骨架: ①先把条件压成多个等价形, 各暴露一种计数 ②固定单点把整除变因子枚举⇒度数可算 ③外借极值猜想(Turán)须标为待证 ④死路留痕: 几何级数仅 ~2n 条边 ⑤真杠杆在整体缩放这类自由度, 非单点结构 ⑥构造成功≠解答完成: 仍需分类+反身验朴素判据(6∤30 却成立) ⑦嫌过于简单⇒回题面语词复核

## ⛓解读注
⟨…⟩=该思维链文件内逐字锚点(v3: 只留判决片段/算式行, 长句已回剪为原锚的连续切片; audit.py prose_norm 逐字校验, ' 引号与大小写差异已忽略) ‖ ⇒推出 ‖ 并列 ※…=编者注
※本条目无派生算术: 36/180/7200/10800/21600/14.4/60/240 等均为 trace 原值; C(n,2)、floor(n^2/4)、H(R) 为 trace 自身写下的符号式。
※不可传达的是过程纪律(Turán 记为待证、死路留痕、缩放后仍补分类与反例、无 bash 即改手算), 非结论 C(n,2)。
