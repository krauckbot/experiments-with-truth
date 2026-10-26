import json, os, collections, re

d = json.load(open('/home/claude/build/data.json', encoding='utf-8'))
meta = json.load(open('/home/claude/build/img/meta.json', encoding='utf-8'))
have = set(k for k in meta if os.path.exists(f'/home/claude/build/img/{k}.jpg'))

CAP = {
 's_porbandar': "The house in Porbandar where Gandhi was born",
 's_student': "Gandhi as a law student in London, about 1890",
 's_paris': "The Eiffel Tower at the Paris Exhibition, 1889",
 's_bombay': "The Bombay Yacht Club, 1891",
 's_bombay2': "Street vendors in Bombay, 1890s",
 's_durban': "Durban in the mid-1890s",
 's_portnatal': "Port Natal and Durban, seen from the Bluff, 1893",
 's_pmb': "Pietermaritzburg railway station, 1898",
 's_pmb2': "Pietermaritzburg station, late 1890s",
 's_pretoria': "Kerkstraat, Pretoria, 1890s",
 's_jhb': "Johannesburg station, about 1893",
 's_nic': "Founders of the Natal Indian Congress, 1895",
 's_kast1902': "Gandhi and Kasturba, 1902",
 's_kastkids': "Kasturba with her sons, 1902",
 's_boer': "Gandhi with the Indian Ambulance Corps in the Boer War, 1899–1900",
 's_spion': "Boer fighters at Spion Kop, 1900",
 's_zulu': "Gandhi with the Indian stretcher-bearers, Natal, 1906",
 's_bhambatha': "Bhambatha and his followers, about 1906",
 's_law': "Gandhi outside his Johannesburg law office, 1905",
 's_jhb1905': "Gandhi with Sonja Schlesin and Hermann Kallenbach, Johannesburg",
 's_io': "A page of Indian Opinion, 1913",
 's_ioad': "An advertisement for Indian Opinion, 1910",
 's_phoenix': "Phoenix Settlement near Durban",
 's_tfarm': "Tolstoy Farm, 1913",
 's_tf1910': "Gandhi at Tolstoy Farm, 1910",
 's_tf1912': "Tolstoy Farm, 1912",
 's_sa1906': "Gandhi in South Africa, 1906",
 's_lon1906': "Gandhi in London, 1906",
 's_costume': "Gandhi in 1906",
 's_1909': "Gandhi in London, 1909",
 's_satya': "Gandhi as a satyagrahi, 1913",
 's_march': "The great march into the Transvaal, 1913",
 's_march2': "Marchers on the road to the Transvaal, 1913",
 's_champ': "Gandhi in Champaran, 1917",
 's_kheda': "Gandhi during the Kheda satyagraha, 1918",
 's_kheda2': "Gandhi in Kheda, 1918",
 's_benares': "The ghats of Benares on the Ganges, 1890s",
 's_benares2': "Benares, 1890",
 's_durbar': "A viceregal durbar in Delhi, 1911",
 's_gita': "An illustrated Bhagavad Gita manuscript, 19th century",
 's_charkha': "A charkha, the hand spinning wheel",
 's_desai': "Gandhi with Mahadev Desai, 1931",
 's_1931': "Gandhi in 1931, a few years after finishing this book",
}

# explicit hero choices per chapter range (first available wins)
R = [
 (0, 1, ['s_1931']), (2, 3, ['s_porbandar']), (4, 6, ['karamchand', 's_porbandar']), (7, 9, ['putlibai', 's_porbandar']),
 (10, 10, ['karamchand']), (11, 11, ['s_porbandar']), (12, 13, ['s_bombay2', 's_bombay']),
 (14, 20, ['s_student']), (21, 21, ['theosophy', 's_student']), (22, 22, ['s_student']), (23, 23, ['hemchandra', 's_student']),
 (24, 24, ['s_paris']), (25, 25, ['s_student']), (26, 26, ['dadabhai', 's_student']), (27, 27, ['raychand', 's_bombay']),
 (28, 29, ['s_bombay', 's_bombay2']), (30, 31, ['s_bombay2', 's_bombay']), (32, 32, ['s_portnatal', 's_durban']),
 (33, 33, ['s_durban']), (34, 34, ['s_pmb', 's_pmb2']), (35, 35, ['s_jhb']), (36, 41, ['s_pretoria']),
 (42, 44, ['s_durban', 's_portnatal']), (45, 47, ['s_nic']), (48, 49, ['s_portnatal', 's_durban']),
 (50, 53, ['s_bombay', 's_bombay2']), (54, 54, ['gokhale', 's_bombay']), (55, 55, ['s_bombay2']),
 (56, 57, ['s_portnatal', 's_durban']), (58, 59, ['s_durban']), (60, 61, ['s_kastkids', 's_kast1902']),
 (62, 63, ['s_zulu']), (64, 64, ['s_sa1906', 's_costume']), (65, 65, ['s_boer', 's_spion']), (66, 66, ['s_durban']),
 (67, 67, ['s_kast1902']), (68, 70, ['gokhale']), (71, 71, ['s_durbar']), (72, 74, ['gokhale']),
 (75, 75, ['s_benares', 's_benares2']), (76, 78, ['s_bombay', 's_bombay2']), (79, 81, ['s_jhb', 's_pretoria']),
 (82, 87, ['s_law', 's_jhb']), (88, 88, ['s_kast1902']), (89, 90, ['s_jhb1905', 's_law']), (91, 91, ['s_io', 's_ioad']),
 (92, 95, ['s_jhb']), (96, 96, ['ruskin']), (97, 99, ['s_phoenix', 's_io']), (100, 101, ['s_kastkids', 's_phoenix']),
 (102, 103, ['s_zulu', 's_bhambatha']), (104, 104, ['s_satya', 's_march']), (105, 105, ['s_jhb1905', 's_tf1910']),
 (106, 107, ['s_phoenix']), (108, 109, ['s_tf1910', 's_tfarm']), (110, 113, ['s_tfarm', 's_tf1912', 's_tf1910']),
 (114, 114, ['s_march', 's_march2']), (115, 120, ['s_lon1906', 's_1909']), (121, 121, ['gokhale']), (122, 125, ['s_costume', 's_sa1906']),
 (126, 126, ['s_bombay']), (127, 128, ['gokhale']), (129, 129, ['tagore']), (130, 131, ['gokhale']),
 (132, 133, ['s_benares', 's_benares2']), (134, 135, ['s_charkha']), (136, 136, ['s_bombay2']), (137, 144, ['s_champ']),
 (145, 147, ['s_charkha']), (148, 150, ['s_kheda', 's_kheda2']), (151, 153, ['s_kheda2', 's_kheda']),
 (154, 154, ['vallabhbhai', 's_kheda']), (155, 155, ['s_desai']), (156, 156, ['sarojini', 's_desai']), (157, 158, ['s_kheda', 's_kheda2']),
 (159, 159, ['s_ioad', 's_io']), (160, 160, ['malaviya', 'motilalnehru', 's_desai']), (161, 162, ['motilalnehru', 's_desai']),
 (163, 166, ['s_charkha']), (167, 167, ['tilak', 's_charkha']), (168, 169, ['s_1931']),
]
hero = [None] * len(d['chapters'])
for a, b, keys in R:
    for c in range(a, b + 1):
        hero[c] = next((k for k in keys if k in have), None)
print('chapters without hero:', [i for i, h in enumerate(hero) if not h])

PLACEIMG = {'porbandar': 's_porbandar', 'london': 's_student', 'paris': 's_paris', 'bombay': 's_bombay', 'natal': 's_durban',
  'pietermaritzburg': 's_pmb', 'transvaal': 's_pretoria', 'johannesburg': 's_jhb', 'nic': 's_nic', 'phoenix': 's_phoenix',
  'tolstoyfarm': 's_tfarm', 'indianopinion': 's_io', 'champaran': 's_champ', 'kheda': 's_kheda', 'benares': 's_benares',
  'delhi': 's_durbar', 'gita': 's_gita', 'khadi': 's_charkha', 'boerwar': 's_boer', 'zulu': 's_zulu', 'satyagraha': 's_satya',
  'location': 's_jhb', 'youngindia': 's_ioad', 'pretoria': 's_pretoria'}

# rarity
score = {}
for eid, e in d['ents'].items():
    nm = sum(len(v) for v in e['mentions'].values())
    nu = sum(1 for a in d['ann'] if eid in a.get('updates', {}))
    score[eid] = nu * 3 + nm
rank = sorted(score, key=lambda k: -score[k])
rar = {}
for i, k in enumerate(rank):
    rar[k] = 'legendary' if i < 12 else 'epic' if i < 40 else 'rare' if i < 110 else 'common'
rar['gandhi'] = 'legendary'

ents = {}
for k, e in d['ents'].items():
    img = k if k in have and meta[k]['kind'] == 'p' else PLACEIMG.get(k) if PLACEIMG.get(k) in have else None
    ents[k] = {'name': e['name'], 'kind': e['kind'], 'intro': e['intro'], 'first': e['first'], 'mentions': e['mentions'], 'r': rar[k], 'img': img}
imgs = {k: {'w': m['w'], 'h': m['h'], 'date': m['date'], 'credit': m['credit'], 'src': m['src'], 'cap': CAP.get(k, ''), 'file': m['file']} for k, m in meta.items() if k in have}
out = {'chapters': d['chapters'], 'ann': d['ann'], 'ents': ents, 'hero': hero, 'imgs': imgs}
s = json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
t = open('/home/claude/build/template2.html', encoding='utf-8').read().replace('__DATA__', s)
open('/home/claude/build/gandhi-reader.html', 'w', encoding='utf-8').write(t)
print('built', round(len(t.encode()) / 1e6, 2), 'MB; images', len(imgs), collections.Counter(rar.values()))
