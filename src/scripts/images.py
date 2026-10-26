import hashlib, urllib.parse, subprocess, os, json, io, time
from PIL import Image

# key -> (commons filename, date, credit, kind)  kind: p = portrait, s = scene
IMG = {
 # portraits (key = entity id)
 'gandhi': ("Portrait of a young Mahatma Gandhi.jpg", "1906", "Unknown", "p"),
 'kasturba': ("Kasturba Gandhi 1940.jpg", "1940", "Unknown", "p"),
 'karamchand': ("Karamchand Gandhi.jpg", "before 1885", "Unknown", "p"),
 'putlibai': ("Putlibai Gandhi.jpg", "1880s", "Unknown", "p"),
 'harilal': ("Harilal Mohandas Gandhi in 1910.jpg", "1910", "Unknown", "p"),
 'manilal': ("Manilal Gandhi, 1925 photo by Underwood & Underwood (cropped).jpg", "1925", "Underwood & Underwood", "p"),
 'dadabhai': ("Dadabhai Naoroji 1889.jpg", "1889", "Unknown", "p"),
 'gokhale': ("GKGokhale.jpg", "1909", "Unknown", "p"),
 'tilak': ("Bal Gangadhar Tilak (1856-1920).webp", "c. 1900", "Unknown", "p"),
 'tolstoy': ("Leo Tolstoy 1908 Portrait (3x4 cropped).jpg", "1908", "Sergei Prokudin-Gorskii", "p"),
 'ruskin': ("John Ruskin 1863.jpg", "1863", "W. & D. Downey", "p"),
 'raychand': ("Srimad Rajcandra.jpg", "before 1901", "Unknown", "p"),
 'besant': ("Annie Besant - portrait.jpg", "", "London Stereoscopic Company", "p"),
 'arnold': ("Picture of Edwin Arnold.jpg", "before 1897", "Stereoscopic Co.", "p"),
 'salt': ("Henry Stephens Salt.jpg", "", "Unknown", "p"),
 'polak': ("H S L Polak.jpg", "1914", "Unknown", "p"),
 'tagore': ("Rabindranath Tagore in 1909.jpg", "1909", "Generalstabens litografiska anstalt", "p"),
 'shraddhanand': ("Swami Shraddhanand.jpg", "c. 1900", "Unknown", "p"),
 'vivekanand': ("Swami Vivekananda-1893-09-signed.jpg", "1893", "Unknown", "p"),
 'malaviya': ("Mahamana Madan Mohan Malaviya ji Smiling.jpg", "", "Banaras Hindu University", "p"),
 'motilalnehru': ("MotilalNehru3.jpg", "c. 1910", "Unknown", "p"),
 'vallabhbhai': ("Sardar patel (cropped).jpg", "1949", "Government of India", "p"),
 'sarojini': ("Sarojini Naidu in 1928.jpg", "1928", "Bibliothèque nationale de France", "p"),
 'jinnah': ("Jinnah1945c.jpg", "1945", "Unknown", "p"),
 'lajpatrai': ("Mahatma Lala Lajpat Rai.jpg", "", "Punjab State Archives", "p"),
 'cr_das': ("Chittaranjan Das 2.jpg", "before 1925", "Unknown", "p"),
 'alibrothers': ("Molana-Muhammad-Ali.jpg", "before 1931", "Unknown", "p"),
 'curzon': ("George Curzon2.jpg", "", "Bain Collection, Library of Congress", "p"),
 'chelmsford': ("Chelmsford Governor.jpg", "1907", "Unknown", "p"),
 'hardinge': ("Charles Hardinge.jpg", "", "Unknown", "p"),
 'chamberlain': ("Joseph Chamberlain MP.png", "before 1914", "Elliott & Fry", "p"),
 'kruger': ("Paul Kruger Cropped.png", "1890", "Unknown", "p"),
 'escombe': ("Rt. Hon. Harry Escombe (1838-1899), Premier of Natal.jpg", "1897", "Lafayette, London", "p"),
 'maganlal': ("MGandhi (1917) 10 pg 41 (2) Mr Maganlal K Gandhi.png", "1917", "Unknown", "p"),
 'ranade': ("Mahadev Govind Ranade garu1911.jpg", "1911", "Andhra Patrika", "p"),
 'bhandarkar': ("Ramkrishna Gopal Bhandarkar.jpg", "", "Unknown", "p"),
 'nivedita': ("Sœur Nivedita.jpg", "before 1911", "Unknown", "p"),
 'odwyer': ("Sir Michael Francis O'Dwyer (died 1940).jpg", "", "Unknown", "p"),
 'murray': ("Andrew Murray.JPG", "", "Unknown", "p"),
 'manning': ("Henry Edward Manning, negative, 1883 (by Alexander Bassano; NPG x96182) (3x4 cropped).png", "1883", "Alexander Bassano", "p"),
 'bradlaugh': ("Charles Bradlaugh.jpg", "", "Unknown", "p"),
 'theosophy': ("Helena Petrovna Blavatsky.jpg", "1877", "Unknown", "p"),
 'willingdon': ("Freeman Freeman-Thomas by Henry Walter Barnett.jpg", "c. 1915", "Henry Walter Barnett", "p"),
 'ripon': ("Marquess of Ripon (cropped).jpg", "1890s", "London Stereoscopic & Photographic Co.", "p"),
 'elgin': ("Picture of Victor Bruce, 9th Earl of Elgin.jpg", "1897", "Bourne & Shepherd", "p"),
 'buller': ("VCRedversHenryBuller.jpg", "", "Unknown", "p"),
 'hills': ("Arnold Hills 1889-12-21.jpg", "1889", "Georg Meisenbach", "p"),
 'oldfield': ("Josiah Oldfield.png", "before 1898", "Unknown", "p"),
 'allinson': ("Allinson TR Vanity Fair 1911-10-04.jpg", "1911", "Vanity Fair", "p"),
 'hobhouse': ("Hobhouse2.jpg", "1902", "Henry Walter Barnett", "p"),
 'hemchandra': ("Narayan Hemchandra (cropped) 2.jpg", "1880–1900", "Unknown", "p"),
 'pjmehta': ("Pranjivan Mehta.jpg", "", "Unknown", "p"),
 'horniman': ("B G Horniman.jpg", "1918", "Unknown", "p"),
 'bhupendranath': ("Bhupendranath Bose.jpg", "1912", "Unknown", "p"),
 'shastri': ("VS Srinivasa Sastri 1921b.jpg", "1921", "National Photo Company", "p"),
 # scenes
 's_porbandar': ("Birth place of Mahatma Gandhi.jpg", "before 1948", "Unknown", "s"),
 's_student': ("Gandhi student.jpg", "c. 1890", "Unknown", "s"),
 's_paris': ("Eiffel tower at Exposition Universelle, Paris, 1889.jpg", "1889", "Neurdein", "s"),
 's_bombay': ("The Bombay Yacht Club in February 1891.jpg", "1891", "Unknown", "s"),
 's_bombay2': ("Tapiwalis in Bombay in the 1890s, photographed by Cambridge and Company.jpg", "1890s", "Cambridge and Company", "s"),
 's_durban': ("Durban 1890s H0061-L351324335.jpg", "c. 1894", "William J. Frazer", "s"),
 's_portnatal': ("AFR V4 D241 Port Natal and Durban - view taken from the bluff.png", "1893", "Élisée Reclus", "s"),
 's_pmb': ("PMB 1898 Railway Station.jpg", "1898", "Unknown", "s"),
 's_pmb2': ("Railway station Pietermaritzburg, South Africa - Winterton Collection of East African Photographs 6-13-1.jpg", "late 1890s", "Winterton Collection", "s"),
 's_pretoria': ("Kerkstraat, Pretoria 1890s.jpg", "1890s", "Unknown", "s"),
 's_jhb': ("Station Johannesburg, later Braamfontein, c. 1893.jpg", "c. 1893", "Unknown", "s"),
 's_nic': ("Natal Indian Congress.jpg", "1895", "Unknown", "s"),
 's_kast1902': ("Gandhi and Kasturbhai 1902.jpg", "1902", "Unknown", "s"),
 's_kastkids': ("Kasturba and children.jpg", "1902", "Unknown", "s"),
 's_boer': ("Gandhi Boer War.jpg", "1899–1900", "Unknown", "s"),
 's_spion': ("Boers at Spion Kop, 1900 - Project Gutenberg eText 16462.jpg", "1900", "Unknown", "s"),
 's_zulu': ("Gandhi Zulu war.jpg", "1906", "Unknown", "s"),
 's_bhambatha': ("Bhambatha and warriors.png", "c. 1906", "Unknown", "s"),
 's_law': ("Gandhi Law Office.jpg", "1905", "Unknown", "s"),
 's_jhb1905': ("Gandhi Johannesburg 1905.jpg", "1905", "Unknown", "s"),
 's_io': ("Indian Opinion.jpg", "1913", "Indian Opinion", "s"),
 's_ioad': ("Indian opinion advertisement in 1910.jpg", "1910", "Indian Opinion", "s"),
 's_phoenix': ("Phoenix settlement.jpg", "", "Unknown", "s"),
 's_tfarm': ("Tolstoy farm.jpg", "1913", "Unknown", "s"),
 's_tf1910': ("Gandhi Tolstoy Farm.jpg", "1910", "Unknown", "s"),
 's_tf1912': ("Gandhi Tolstoy farm 1912.jpg", "1912", "Unknown", "s"),
 's_sa1906': ("Mohandas K. Gandhi in South Africa, 1906.jpg", "1906", "Unknown", "s"),
 's_lon1906': ("Gandhi London 1906.jpg", "1906", "Unknown", "s"),
 's_costume': ("Gandhi costume.jpg", "1906", "Unknown", "s"),
 's_1909': ("CWMG, vol.9 (1908-1909), Frontispiece, Gandhi-ji in London, 1909 - Code Swaraj.jpg", "1909", "Unknown", "s"),
 's_satya': ("Gandhi satyagrahi.jpg", "1913", "Unknown", "s"),
 's_march': ("Transvaal Protest March 1913.jpg", "1913", "Unknown", "s"),
 's_march2': ("During Transvaal march 1913.jpg", "1913", "Unknown", "s"),
 's_champ': ("Gandhiji and Sub-Inspector Qurban Ali in Champaran (1917).jpg", "1917", "Unknown", "s"),
 's_kheda': ("Gandhi Kheda 1918.jpg", "1918", "Unknown", "s"),
 's_kheda2': ("Gandhi during the Kheda satyagraha.jpg", "1918", "Unknown", "s"),
 's_benares': ("Benares Ghats in the 1890s.jpg", "1890s", "Unknown", "s"),
 's_benares2': ("Benares 1890.jpg", "1890", "Edward Molyneux", "s"),
 's_durbar': ("Delhi Durbar, 1911.jpg", "1911", "Unknown", "s"),
 's_gita': ("BhagavadGita-19th-century-Illustrated-Sanskrit-Chapter 1.20.21.jpg", "19th century", "Unknown", "s"),
 's_charkha': ("A Charkha or Spinning Wheel, Jammu, ca.1875-ca.1940 (imp-cswc-GB-237-CSWC47-LS10-024).jpg", "c. 1875–1940", "Unknown", "s"),
 's_desai': ("Gandhi with Mahadev Desai.jpg", "1931", "James A. Mills", "s"),
 's_1931': ("Mahatma-Gandhi, studio, 1931.jpg", "1931", "Elliott & Fry", "s"),
}

UA = "EWTReaderBuild/1.0 (personal e-reader companion)"
def urls(name):
    n = name.replace(' ', '_'); h = hashlib.md5(n.encode()).hexdigest(); q = urllib.parse.quote(n)
    base = f"https://upload.wikimedia.org/wikipedia/commons"
    return [f"{base}/thumb/{h[0]}/{h[:2]}/{q}/960px-{q}" + ('.jpg' if n.lower().endswith(('.webp','.tif','.tiff')) else ('.png' if n.lower().endswith('.png') else '')),
            f"{base}/thumb/{h[0]}/{h[:2]}/{q}/960px-{q}", f"{base}/{h[0]}/{h[:2]}/{q}"]

os.makedirs('/home/claude/build/img', exist_ok=True)
meta = json.load(open('/home/claude/build/img/meta.json')) if os.path.exists('/home/claude/build/img/meta.json') else {}
for k, (name, date, credit, kind) in IMG.items():
    if k in meta: continue
    out = f'/home/claude/build/img/{k}.jpg'
    if os.path.exists(out):
        im = Image.open(out)
        meta[k] = {'file': name, 'date': date, 'credit': credit, 'w': im.width, 'h': im.height, 'kind': kind,
                   'src': 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(name.replace(' ', '_'))}
        continue
    data = None
    for u in urls(name):
        r = subprocess.run(["curl", "-s", "-L", "-m", "40", "-A", UA, "-w", "\n%{http_code}", u], capture_output=True)
        body, code = r.stdout.rsplit(b"\n", 1)
        tries = 0
        while code == b"429" and tries < 4:
            time.sleep(8 * (tries + 1)); tries += 1
            r = subprocess.run(["curl", "-s", "-L", "-m", "40", "-A", UA, "-w", "\n%{http_code}", u], capture_output=True)
            body, code = r.stdout.rsplit(b"\n", 1)
        time.sleep(2.5)
        if code == b"200" and len(body) > 2000:
            try:
                Image.open(io.BytesIO(body)); data = body; break
            except Exception:
                pass
    if not data:
        print('FAIL', k); continue
    im = Image.open(io.BytesIO(data))
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (236, 232, 222)); im = im.convert('RGBA'); bg.paste(im, mask=im.split()[-1]); im = bg
    im = im.convert('RGB')
    maxw = 440 if kind == 'p' else 1000
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    out = f'/home/claude/build/img/{k}.jpg'
    im.save(out, 'JPEG', quality=74 if kind == 's' else 78, optimize=True, progressive=True)
    meta[k] = {'file': name, 'date': date, 'credit': credit, 'w': im.width, 'h': im.height, 'kind': kind,
               'src': 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(name.replace(' ', '_'))}
    print('ok', k, im.size, os.path.getsize(out) // 1024, 'KB', flush=True)
    json.dump(meta, open('/home/claude/build/img/meta.json', 'w'), ensure_ascii=False, indent=1)
json.dump(meta, open('/home/claude/build/img/meta.json', 'w'), ensure_ascii=False, indent=1)
