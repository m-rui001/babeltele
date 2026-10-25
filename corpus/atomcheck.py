"""临时工具: 校验候选 ⟨原子⟩ 是否逐字命中 raw 源(与 audit.py prose_norm 同规则)。
用法: python corpus/atomcheck.py <tag> <候选文件(每行一个原子)>
"""
import re, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SRC = {
 'B37': ['corpus/raw/prose/pmc_ards_chang_phases.txt', 'corpus/raw/prose/pmc_ards_dad.txt', 'corpus/raw/cot/b37_dad_review_deepseek.md', 'corpus/raw/cot/b37_dad_review_glm.md'],
 'B12': ['corpus/raw/prose/pmc_pap_vape.txt'],
 'B16': ['corpus/raw/prose/biorxiv_bacterial_organelles.txt'],
 'B17': ['corpus/raw/prose/pmc_mechaware_ai_drug.txt'],
 'B18': ['corpus/raw/cot/med_gitalb.md'],
 'B19': ['corpus/raw/cot/math_subsets.md'],
 'B20': ['corpus/raw/cot/law_ewca_method.md'],
 'B21': ['corpus/raw/cot/fin_credit_cmte.md'],
 'B22': ['corpus/raw/prose/csb_marathon_martinez.txt'],
 'B23': ['corpus/raw/cot/ind_creep_rupture.md'],
 'B24': ['corpus/raw/cot/str_quake_slab.md'],
 'B25': ['corpus/raw/prose/csb_givaudan.txt'],
 'B26': ['corpus/raw/cot/bio_stat_interim.md'],
 'B27': ['corpus/raw/cot/bio_stat_interim.md', 'corpus/raw/cot/bio_stat_interim_glm.md',
         'corpus/raw/cot/bio_stat_interim_nemotron.md'],
 'B28': ['corpus/raw/prose/cn_fire_abduction.txt'],
 'B29': ['corpus/raw/prose/cn_fire_uncertainty_court_doctrine.txt',
         'corpus/raw/prose/cn_fire_uncertainty_practice_qa.txt',
         'corpus/raw/prose/cn_fire_shantou_report.txt'],
 'B30': ['corpus/raw/prose/cn_report_guide_technical.txt',
         'corpus/raw/prose/cn_report_guide_management.txt'],
 'B31': ['corpus/raw/prose/cn_edata_review_theory.txt',
         'corpus/raw/prose/cn_edata_review_practice.txt'],
 'B32': ['corpus/raw/prose/cn_csrc_manipulation_fourmen.txt',
         'corpus/raw/prose/cn_csrc_manipulation_tenmen.txt',
         'corpus/raw/prose/cn_csrc_fake_info_lurunkai.txt'],
 'B33': ['corpus/raw/prose/csb_clairton_update.txt',
         'corpus/raw/prose/csb_clairton_interim.txt',
         'corpus/raw/prose/csb_clairton_final.txt'],
 'B34': ['corpus/raw/prose/cn_fire_report_spread.txt',
         'corpus/raw/prose/cn_fire_report_liability.txt'],
 'B35': ['corpus/raw/prose/cftc_swap_exclusion_ifr.txt',
         'corpus/raw/prose/cftc_swap_inclusions_nprm.txt'],
 'B36': ['corpus/raw/cot/b36_tdi_deepseek.md',
         'corpus/raw/cot/b36_tdi_glm.md',
         'corpus/raw/cot/b36_tdi_nemotron.md'],

}
SRC['B64'] = ['corpus/raw/dhcp/rfc2131.txt', 'corpus/raw/dhcp/rfc3315.txt',
              'corpus/raw/dhcp/rfc7083.txt', 'corpus/raw/dhcp/rfc8415.txt']
SRC['B63'] = ['corpus/raw/tcpRTO/rfc1122.txt', 'corpus/raw/tcpRTO/rfc2988.txt',
              'corpus/raw/tcpRTO/rfc6298.txt', 'corpus/raw/tcpiw/rfc9002.txt']
SRC['B62'] = ['corpus/raw/tcpiw/rfc2581.txt', 'corpus/raw/tcpiw/rfc3390.txt',
            'corpus/raw/tcpiw/rfc5681.txt', 'corpus/raw/tcpiw/rfc6928.txt',
            'corpus/raw/tcpiw/rfc9002.txt']
SRC['B61'] = ['corpus/raw/ipv6/rfc1883.txt', 'corpus/raw/ipv6/rfc2460.txt',
              'corpus/raw/ipv6/rfc8200.txt', 'corpus/raw/ipv6/rfc2675.txt',
              'corpus/raw/ipv6/rfc8201.txt']
SRC['B60'] = ['corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt',
              'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.layout.txt',
              'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt',
              'corpus/raw/cert/le_lifetimes.html', 'corpus/raw/cert/rfc5280.txt']
SRC['B59'] = ['corpus/raw/pwd/nist_63b_rev3.html', 'corpus/raw/pwd/asvs_40_v2.md',
              'corpus/raw/pwd/nist_63b_rev4.html', 'corpus/raw/pwd/owasp_auth_cs.html']
SRC['B58'] = ['corpus/raw/cvss/cvss_v30_spec.html', 'corpus/raw/cvss/cvss_v31_spec.html',
              'corpus/raw/cvss/cvss_v40_spec.html', 'corpus/raw/cvss/cvss_examples.html']
SRC['B57'] = ['corpus/raw/ietf/rfc5246.txt', 'corpus/raw/ietf/rfc7525.txt',
              'corpus/raw/ietf/rfc8446.txt', 'corpus/raw/ietf/rfc9325.txt']
SRC['B56'] = ['corpus/raw/tz/iso3166.tab', 'corpus/raw/tz/zone1970.tab', 'corpus/raw/langsubtag.txt']
SRC['B55'] = ['corpus/raw/langsubtag.txt', 'corpus/raw/tz/zone1970.tab']
SRC['B54'] = ['corpus/raw/codata_table.html', 'corpus/raw/codata_all.html']
SRC['B53'] = ['corpus/raw/fips202.txt', 'corpus/raw/fips202_pdflayout.txt',
              'corpus/raw/fips202_plain.txt', 'corpus/raw/fips202.html']
SRC['B52'] = ['corpus/raw/tz/zonenow.tab', 'corpus/raw/tz/zone1970.tab',
              'corpus/raw/tz/checknow.awk', 'corpus/raw/tz/Makefile']
SRC['B50'] = ['corpus/raw/cot/math_subsets.md', 'corpus/raw/cot/med_gitalb.md',
            'corpus/raw/cot/law_ewca_method.md', 'corpus/raw/cot/fin_credit_cmte.md',
            'corpus/raw/cot/ind_creep_rupture.md', 'corpus/raw/cot/str_quake_slab.md']
SRC['B51'] = ['corpus/raw/cot/math_subsets.md', 'corpus/raw/cot/math_subsets_s2.md',
              'corpus/raw/cot/med_gitalb.md', 'corpus/raw/cot/med_gitalb_s2.md']
SRC['B49'] = ['corpus/raw/tz/zone1970.tab', 'corpus/raw/tz/checktab.awk', 'corpus/raw/tz/europe']
SRC['B48'] = ['corpus/raw/tz/leap-seconds.list', 'corpus/raw/tz/leapseconds.awk', 'corpus/raw/tz/leapseconds']
SRC['B47'] = ['corpus/raw/UnicodeData.txt', 'corpus/raw/scripts.txt']
SRC['B46'] = ['corpus/raw/api/bio_recent_2026w01.json', 'corpus/raw/prose/biorxiv_bacterial_organelles.txt']
SRC['B45'] = ['corpus/raw/tz/zone1970.tab', 'corpus/raw/zone1970_latest.tab', 'corpus/raw/tz/zone.tab', 'corpus/raw/zone1970.tab']
SRC['B44'] = ['corpus/raw/prose/pmc_ards.xml', 'corpus/raw/prose/pmc_ards_dad.txt']
SRC['B43'] = ['corpus/raw/prose/law_aviator_spribe.txt', 'corpus/raw/prose/law_ewca_aviator.txt']
SRC['B42'] = ['corpus/raw/prose/csb_marathon_martinez.txt']
SRC['B41'] = ['corpus/raw/prose/fr_fda_ish_proposed_order.txt',
             'corpus/raw/prose/fr_fda_ish_final_order.txt']
SRC['B40'] = ['corpus/raw/prose/fr_fda_cardio_ml_notification.txt',
             'corpus/raw/prose/fr_fda_radiology_ml_pccp.txt',
             'corpus/raw/prose/fr_fda_opioid_impairment_monitor.txt']
SRC['B39'] = ['corpus/raw/prose/pmc_mobilization_dose_study.txt',
             'corpus/raw/prose/pmc_mobilization_targettrial_letter.txt']
SRC['B38'] = ['corpus/raw/prose/pmc_sepsis_lpa_comment.txt',
             'corpus/raw/prose/pmc_sepsis_lpa_response.txt']
def prose_norm(s):
    s = s.lower().replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = re.sub(u'[’\'"\u2018\u2019`´]+', '', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', '-', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff\-\. ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

SRC['B67'] = ['corpus/raw/labels/synthroid_dailymed.html', 'corpus/raw/labels/levoxyl_dailymed.html',
              'corpus/raw/labels/tirosint_dailymed.html', 'corpus/raw/labels/alvogen_dailymed.html']
SRC['B73'] = ['corpus/raw/filings/aapl25_10k_1a.txt', 'corpus/raw/filings/aapl24_10k_1a.txt',
              'corpus/raw/filings/msft25_10k_1a.txt', 'corpus/raw/filings/goog25_10k_1a.txt']
SRC['B75'] = ['corpus/raw/opinions/loper_a.txt', 'corpus/raw/opinions/loper_b.txt',
              'corpus/raw/opinions/loper_c.txt', 'corpus/raw/opinions/loper_d.txt']
SRC['B76'] = ['corpus/raw/fomc/fomc25sep_a.txt', 'corpus/raw/fomc/fomc25sep_b.txt',
              'corpus/raw/fomc/fomc25sep_c.txt']
SRC['B77'] = ['corpus/raw/arxiv/llama3_a.txt', 'corpus/raw/arxiv/llama3_b.txt', 'corpus/raw/arxiv/llama3_c.txt']
SRC['B78'] = ['corpus/raw/faa/ad_a.txt', 'corpus/raw/faa/ad_b.txt']
SRC['B79'] = ['corpus/raw/changelog/sqlite_a.txt', 'corpus/raw/changelog/sqlite_b.txt', 'corpus/raw/changelog/sqlite_c.txt']
SRC['B83'] = ['corpus/raw/nws/afd_a.txt', 'corpus/raw/nws/afd_b.txt', 'corpus/raw/nws/afd_c.txt']
SRC['B84'] = ['corpus/raw/constitution/us_constitution_full.txt']
SRC['B85'] = ['corpus/raw/changelog/sqlite_b.txt']
SRC['B87'] = ['corpus/raw/faa/ad_2026ge.txt']
SRC['B88'] = ['corpus/raw/fintech/part15_subparta.txt']
SRC['B89'] = ['corpus/raw/fips204/fips204_full.txt']
HTML = {'B58', 'B59', 'B60', 'B67'}
NAMED = {'nbsp': ' ', 'amp': '&', 'lt': '<', 'gt': '>', 'quot': '"', 'apos': "'",
         'times': 'x', 'minus': '-', 'rarr': '->', 'larr': '<-', 'mdash': '-',
         'ndash': '-', 'deg': 'deg', 'infin': 'inf', 'ldquo': '"', 'rdquo': '"',
         'lsquo': u'‘', 'rsquo': u'’', 'hellip': '...', 'ge': '>=', 'le': '<='}


def detag(s, fill=''):
    """HTML 剥壳的工具侧写法: 按 '<' 手工分段扫描, 数字实体按码位解, 命名实体查表。
    标签替成什么由 fill 定: '' 是粘面(标签两侧直接相接), ' ' 是断面(标签替空格)。
    两面都送去比对, 因为建条目侧的转义层本就分两代: B58/B59 用 '<' 游标粘面, B60 用三条正则一次替换的断面,
    同一句 "</a>." 在前者得 "2028."、在后者得 "2028 ."——锚文本换不出剥壳口径, 于是口径两档并记。"""
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    out, k = [], 0
    while True:
        j = s.find('<', k)
        if j < 0:
            out.append(s[k:]); break
        out.append(s[k:j])
        e = s.find('>', j)
        if e < 0:
            out.append(s[j:]); break
        nm = re.match(r'(?is)/?([a-zA-Z][a-zA-Z0-9]*)', s[j + 1:e])
        out.append(' ' if (nm and nm.group(1).lower() == u'br') else fill)
        k = e + 1
    s = u''.join(out)
    for a, b in UNIMAP:
        s = s.replace(a, b)
    s = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), s)
    s = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), s)
    return re.sub(r'&([a-zA-Z]+);', lambda m: NAMED.get(m.group(1).lower(), m.group(0)), s)

UNIMAP = [(u' ', ' '), (u'−', '-'), (u'–', '-'), (u'—', '-'), (u'×', 'x'),
          (u'‘', "'"), (u'’', "'"), (u'“', '"'), (u'”', '"'), (u'→', '->')]

files = SRC[sys.argv[1]]
RAW0 = [open(f, encoding='utf-8', errors='replace').read() for f in files]
# 剥壳只施于 HTML 那份: Markdown 与纯文本源没有壳可剥, 它们的原子按原文面逐字回验。
HTMLF = [f.lower().endswith(('.html', u'.htm')) for f in files]


def face(fill):
    return prose_norm(u'\n'.join([detag(r, fill) if h else r for h, r in zip(HTMLF, RAW0)]))


PS = [face(u''), face(u' ')] if (sys.argv[1] in HTML and any(HTMLF)) else [face(u'')]
ok = bad = 0
for line in open(sys.argv[2], encoding='utf-8'):
    a = line.strip()
    if not a:
        continue
    n = prose_norm(a)
    if len(n) < 3 or any(n in p for p in PS):
        ok += 1
    else:
        bad += 1
        print('MISS |' + a + '|')
print('ok=%d bad=%d' % (ok, bad))
