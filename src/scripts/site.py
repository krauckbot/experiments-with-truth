import os, shutil, json, math
from PIL import Image, ImageDraw

OUT = '/home/claude/site'
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT + '/img')
for f in os.listdir('/home/claude/build/img'):
    if f.endswith('.jpg'):
        shutil.copy('/home/claude/build/img/' + f, OUT + '/img/' + f)

# ---- app icon: gold spinning wheel on indigo ----
def icon(size, pad=0.0):
    S = size * 4
    im = Image.new('RGB', (S, S), (20, 23, 41))
    d = ImageDraw.Draw(im)
    c = S / 2; R = S * (0.34 - pad)
    gold, gold2 = (217, 150, 26), (244, 195, 91)
    w = int(S * 0.035)
    d.ellipse([c - R, c - R, c + R, c + R], outline=gold2, width=w)
    for i in range(12):
        a = math.pi * 2 * i / 12
        d.line([c, c, c + R * math.cos(a), c + R * math.sin(a)], fill=gold, width=int(w * 0.6))
    r = S * 0.07
    d.ellipse([c - r, c - r, c + r, c + r], fill=gold2)
    return im.resize((size, size), Image.LANCZOS)
icon(512).save(OUT + '/icon-512.png')
icon(192).save(OUT + '/icon-192.png')
icon(180).save(OUT + '/apple-touch-icon.png')
icon(512, 0.06).save(OUT + '/icon-maskable.png')

json.dump({
    'name': 'Experiments with Truth', 'short_name': 'Experiments',
    'description': "Read Gandhi's autobiography, collect the people you meet, and level up.",
    'start_url': './', 'scope': './', 'display': 'standalone', 'orientation': 'portrait',
    'background_color': '#141729', 'theme_color': '#141729',
    'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
              {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
              {'src': 'icon-maskable.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]
}, open(OUT + '/manifest.webmanifest', 'w'), indent=1)

imgs = sorted('img/' + f for f in os.listdir(OUT + '/img'))
open(OUT + '/sw.js', 'w').write("""const C = 'ewt-v2';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png'];
const IMGS = %s;
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(C).then(c => c.addAll(CORE).then(() => c.addAll(IMGS).catch(() => {})))); });
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request).then(r => {
    if (r.ok && (r.type === 'basic' || r.type === 'cors')) { const cp = r.clone(); caches.open(C).then(c => c.put(e.request, cp)); }
    return r;
  }).catch(() => hit)));
});
""" % json.dumps(imgs))

body = open('/home/claude/build/gandhi-reader.html', encoding='utf-8').read()
body = body.replace('<title>Experiments with Truth</title>\n', '', 1)
body = body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1)
# split: everything up to the first <svg is head material (links + style)
i = body.index('<svg width="0"')
head, rest = body[:i], body[i:]
html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Experiments with Truth</title>
<meta name="description" content="Read Gandhi's autobiography, collect the people you meet, and level up.">
<meta name="theme-color" content="#141729">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Experiments">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:title" content="Experiments with Truth">
<meta property="og:description" content="Gandhi's autobiography as a reading game: collect cards, earn XP, unlock badges.">
<meta property="og:image" content="img/s_student.jpg">
{head}</head>
<body>
{rest}
<script>if ('serviceWorker' in navigator && location.protocol === 'https:') addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {{}}));</script>
</body>
</html>
"""
open(OUT + '/index.html', 'w', encoding='utf-8').write(html)
open(OUT + '/README.txt', 'w').write("""Experiments with Truth - standalone web app

Put this whole folder on any static web host (Netlify Drop, Cloudflare Pages, GitHub Pages, Vercel).
Keep the folder structure as is: index.html next to the img/ folder.
On a phone, open the link and choose "Add to Home Screen" to get a full-screen app that also works offline.

Text: Mahadev Desai's translation of M. K. Gandhi's autobiography (public domain; Standard Ebooks edition).
Photos: Wikimedia Commons, all public domain; sources are listed under "Photo credits" in the app.
""")
print('ok', sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs) // 1024, 'KB')
