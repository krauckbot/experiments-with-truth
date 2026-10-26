import json, glob, re, sys, collections

chapters = json.load(open('/root/book/chapters.json', encoding='utf-8'))
ents, ann = {}, {}
for f in sorted(glob.glob('/home/claude/ann/b*.json')):
    d = json.load(open(f, encoding='utf-8'))
    for e in d['entities']:
        if not e.get('intro'):
            continue
        if e['id'] in ents:
            # merge aliases, keep first intro
            ents[e['id']]['aliases'] += [a for a in e['aliases'] if a not in ents[e['id']]['aliases']]
        else:
            ents[e['id']] = e
    for c in d['chapters']:
        assert c['id'] not in ann, ('dup chapter', c['id'])
        ann[c['id']] = c

# ---- alias fixes (ambiguity / ranges) ----
FIX = {
 'nic': ['Natal Indian Congress', ['the Congress', 45, 67], ['The Congress', 45, 67]],
 'incongress': ['Indian National Congress', ['Congress', 68, 169]],
 'sis': ['Servants of India Society', ['the Society', 127, 131]],
 'raychand': ['Raychand', 'Raychandbhai', 'Rajchandra', ['the poet', 27, 30]],
 'tagore': ['Tagore', 'Gurudev', ['the Poet', 126, 169], ['The Poet', 126, 169]],
 'godfrey': [['Godfrey', 34, 43], 'Subhan Godfrey'],
 'georgegodfrey': ['George Godfrey', ['Mr. Godfrey', 81, 81]],
 'williamgodfrey': ['Dr. Godfrey', 'William Godfrey'],
 'khan': ['Mr. Khan'],
 'west': [['West', 94, 169], ['Mr. West', 94, 169]],
 'baker': [['Mr. Baker', 36, 41], ['Baker', 36, 41]],
 'motilal': [['Motilal', 128, 128]],
 'motilalnehru': ['Motilalji', 'Motilal Nehru'],
 'ww1': [['the War', 115, 153], ['the war', 115, 153], ['War', 115, 153], 'Netley', 'great War'],
 'zulu': ['Zulu', 'Zulus', ['rebellion', 102, 103]],
 'location': [['location', 92, 95], 'coolie location'],
 'ashram': [['Ashram', 134, 169], ['ashram', 134, 169], 'Kochrab'],
 'captain': [['the Captain', 32, 32], ['The Captain', 32, 32]],
 'sheth': [['the Sheth', 13, 13], ['The Sheth', 13, 13]],
 'politicalagent': ['Political Agent', ['the sahib', 30, 31], ['The sahib', 30, 31]],
 'durbandoctor': [['the doctor', 106, 106], ['The doctor', 106, 106]],
 'anand': ['Swami Anand', ['the Swami', 1, 1], ['The Swami', 1, 1]],
 'brightonlady': [['old lady', 20, 20], ['the good lady', 20, 20]],
 'desai': ['M. D.', 'Mahadev Desai', ['Mahadev', 140, 169]],
 'anasuyabai': ['Anasuyabai', 'Anasuyabehn'],
 'brajkishore': ['Brajkishore', 'Brajkishorebabu'],
 'rajendra': ['Rajendra', 'Rajendrababu'],
 'sarojini': ['Sarojini', 'Mrs. Naidu'],
 'shyness': ['shy', 'shyness', 'tongue-tied'],
 'law': ['barrister', 'the bar', 'Inns of Court', 'vakil', 'vakils', 'barristers'],
 'pjmehta': ['Dr. Mehta', 'Pranjivan Mehta', 'Pranjivandas Mehta', 'P. J. Mehta'],
 'mehtab': [['this friend', 7, 13], ['This friend', 7, 13], ['my friend', 7, 12], ['the friend', 7, 12]],
 'richmondfriend': [['the friend', 15, 16], ['The friend', 15, 16], ['my friend', 15, 16]],
 'companion': [['companion', 49, 49]],
 'kalitemple': ['Kali temple', ['Kali', 73, 74]],
 'christianity': ['Christian', 'Christians', 'Christianity', 'Bible', 'Sermon on the Mount', 'missionaries', 'Jesus'],
 'religion': ['religion', 'religious', 'Vaishnava', 'Haveli', 'Ramanama'],
 'truth': ['truth', 'Truth'],
 'harishchandra': ['Harishchandra', 'Shravana'],
 'phoenix': [['Phoenix', 97, 169]],
 'tolstoyfarm': ['Tolstoy Farm', ['the Farm', 108, 114], ['The Farm', 108, 114]],
 'shastri': [['Shastri', 131, 155], ['Shastriji', 131, 155], 'Srinivasa Shastri'],
 'hardvar': ['Hardvar', 'Kumbha', 'Lakshman Jhula', 'Rishikesh', 'Hrishikesh'],
 'jail': ['jail', 'jails', 'prison', 'imprisonment'],
 'vegsociety': ['Vegetarian Society', 'vegetarian club'],
 'indianopinion': ['Indian Opinion'],
 'kallenbach': ['Kallenbach'],
 'dress': ['Parsi sari', 'European style', 'costume', ['dress', 56, 56], ['dress', 126, 128], ['dress', 71, 71]],
 'shukla': [['Shukla', 14, 15], 'Dalpatram Shukla'],
 'education': ['education', ['school', 60, 60], ['school', 101, 101], ['school', 110, 113], ['schools', 142, 143], ['school', 142, 143]],
}
for k, v in FIX.items():
    if k in ents:
        ents[k]['aliases'] = v

# ---- validation ----
problems = []
for i in range(len(chapters)):
    if i not in ann:
        problems.append(f'missing chapter {i}')
for cid, c in ann.items():
    for k in list(c.get('updates', {})) + list(c.get('status', {})) + c.get('where', []):
        if k not in ents:
            problems.append(f'ch{cid}: unknown entity {k}')
print('\n'.join(problems) or 'no problems')

# ---- detection ----
SUF = r'(?:ji|bhai|babu|behn|bai|saheb)?'
def compile_alias(a):
    s, lo, hi = (a, 0, 999) if isinstance(a, str) else (a[0], a[1], a[2])
    flags = 0 if re.search(r'[A-Z]', s) else re.I
    pat = r'(?<![\w\-’])' + re.escape(s) + SUF + r'(?![\w\-])'
    return re.compile(pat, flags), lo, hi

matchers = {eid: [compile_alias(a) for a in e['aliases']] for eid, e in ents.items()}
strip = lambda h: re.sub(r'<[^>]+>', ' ', h)

out_ch = []
first_seen = {}
mentions = collections.defaultdict(lambda: collections.defaultdict(list))  # eid -> chapter -> [para idx]
for c in chapters:
    cid = c['id']
    paras = []
    for pi, p in enumerate(c['paras']):
        text = strip(p['h'])
        found = []
        for eid, ms in matchers.items():
            for rx, lo, hi in ms:
                if lo <= cid <= hi and rx.search(text):
                    found.append(eid); break
        for eid in found:
            mentions[eid][cid].append(pi)
        paras.append({'t': p['t'], 'h': p['h'], 'e': found})
    a = ann[cid]
    for eid in list(a.get('updates', {})) + a.get('where', []):
        first_seen[eid] = min(first_seen.get(eid, 999), cid)
    for eid in mentions:
        if cid in mentions[eid]:
            first_seen[eid] = min(first_seen.get(eid, 999), cid)
    out_ch.append({'id': cid, 'part': c['part'], 'roman': c['roman'], 'title': c['title'], 'paras': paras})

# entity mentioned in a chapter but with update there -> fine. Also attach "last mention para" per chapter for spoiler gating
for eid, e in ents.items():
    e['first'] = first_seen.get(eid, None)
    e['mentions'] = {str(k): v for k, v in mentions[eid].items()}

unused = [eid for eid, e in ents.items() if e['first'] is None]
print('never seen:', unused)
cnt = collections.Counter(eid for c in out_ch for p in c['paras'] for eid in p['e'])
print('top detections:', cnt.most_common(25))
print('entities:', len(ents), 'chapters:', len(out_ch))

data = {'chapters': out_ch, 'ann': [ann[i] for i in range(len(chapters))], 'ents': ents}
json.dump(data, open('/home/claude/build/data.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
