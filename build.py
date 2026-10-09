"""Сборка сайта: index.tpl.html + site.json -> index.html
Только site.json, фото (optimize_images.py) и тексты меняются от клиента к клиенту.
demo: true -> заявки идут автору (phone_author), плашка-ватермарк, noindex.
Публикация: 1) запушить img/ и fonts/  2) python3 build.py  3) запушить index.html (CDN jsDelivr закрепляется за коммитом)."""
import re, glob, os, json, subprocess

C = json.load(open('site.json', encoding='utf-8'))
DEMO = C['demo']
phone = C['phone_author'] if DEMO else C['phone_owner']
src = open('index.tpl.html', encoding='utf-8').read()

icon = lambda n: f'<svg class="i"><use href="#{n}"/></svg>'
facts = '\n    '.join(f'<div class="fact rv"><b>{s["num"]}</b><span>{s["label"]}</span></div>' for s in C['facts'])
benefits = '\n'.join(f'      <li class="rv"><div class="ic">{icon(b["icon"])}</div><div><h3>{b["title"]}</h3><p>{b["text"]}</p></div></li>' for b in C['benefits'])
tariffs = '\n'.join(
  f'      <article class="tar{" feat" if t["featured"] else ""} rv"><h3>{t["name"]}</h3><div class="price"><span class="pre">от</span><b>{t["price"]}</b><span class="u">{t["unit"]}</span></div>'
  '<ul>' + ''.join(f'<li>{icon("check")}{x}</li>' for x in t['items']) + '</ul>'
  f'<a class="btn {"btn-dark" if t["featured"] else "btn-line"}" href="#order" data-tariff="{t["name"]}">Выбрать тариф</a></article>' for t in C['tariffs'])
P = lambda n: f'<button class="add" type="button" data-n="{n}" aria-pressed="false" aria-label="Добавить в заявку: {n}"><svg class="i pl"><use href="#plus"/></svg><svg class="i ck"><use href="#check"/></svg></button>'
card = lambda x: f'      <article class="set rv"><h3>{x["name"]}</h3><ul>' + ''.join(f'<li>{l}</li>' for l in x['lines']) + f'</ul><div class="foot2"><span class="pr">{x["price"]}<small>тг</small></span>{P(x["name"])}</div></article>'
TOP = 6
sets_top = '\n'.join(card(x) for x in C['sets'][:TOP]); sets_rest = '\n'.join(card(x) for x in C['sets'][TOP:])
small = '\n'.join(
  f'        <li class="row-set" data-n="{n}" data-u="{u}"><span class="nm">{n}</span><span class="pr">{p}<small>тг{"" if u == "сет" else " за " + u}</small></span>'
  f'<div class="qty"><button class="add q-add" type="button" aria-label="Добавить в заявку: {n}"><svg class="i"><use href="#plus"/></svg></button>'
  f'<div class="q-step" hidden><button class="q-m" type="button" aria-label="Меньше: {n}"><svg class="i"><use href="#minus"/></svg></button>'
  f'<input class="q-n" type="text" inputmode="numeric" value="1" aria-label="Количество: {n}">'
  f'<button class="q-p" type="button" aria-label="Больше: {n}"><svg class="i"><use href="#plus"/></svg></button></div></div></li>' for n, p, u in C['sets_small'])
ni = ''.join(f'<span class="ni">{icon(e["icon"])}{e["label"]}</span>' for e in C['not_included']['items'])
L, H = C['lunch'], C['chef']
days = ''.join(f'<div><dt>{d}</dt><dd>{t}</dd></div>' for d, t in L['days'])
tiers = ''.join(f'<li><div><span class="t1">{a}</span><span class="t2">{r}</span></div><span class="t3">{p}</span></li>' for a, r, p in H['tiers'])
steps = '\n'.join(f'      <li class="rv"><div class="ic">{icon(s["icon"])}</div><div><h3>{s["title"]}</h3><p>{s["text"]}</p></div></li>' for s in C['steps'])
tokens = {
 'TITLE': C['title'], 'DESCRIPTION': C['description'], 'OG_DESCRIPTION': C['og_description'], 'SITE_URL': C['site_url'],
 'AUTHOR': C['author'], 'BRAND': C['brand'], 'EYEBROW': C['eyebrow'], 'H1_HTML': C['h1_html'], 'HERO_SUB': C['hero_sub'],
 'FACTS': facts, 'BENEFITS_TITLE': C['benefits_title'], 'BENEFITS_LEAD': C['benefits_lead'], 'BENEFITS': benefits,
 'TARIFFS_TITLE': C['tariffs_title'], 'TARIFFS_LEAD': C['tariffs_lead'], 'TARIFFS': tariffs, 'TARIFFS_NOTE': C['tariffs_note'],
 'NI_TITLE': C['not_included']['title'], 'NI_ITEMS': ni, 'NI_TEXT': C['not_included']['text'],
 'MENU_TITLE': C['menu_title'], 'MENU_LEAD': C['menu_lead'],
 'SETS_TITLE': C['sets_title'], 'SETS_LEAD': C['sets_lead'], 'SETS_TOP': sets_top, 'SETS_REST': sets_rest, 'SETS_SMALL_TITLE': C['sets_small_title'], 'SETS_SMALL': small,
 'GALLERY_TITLE': C['gallery_title'], 'GALLERY_LEAD': C['gallery_lead'], 'GALLERY_NOTE': C['gallery_note'], 'ALT_HERO': C['alt_hero'],
 'SERVICES_TITLE': C['services_title'], 'SERVICES_LEAD': C['services_lead'],
 'LUNCH_TITLE': L['title'], 'LUNCH_PRICE': L['price'], 'LUNCH_UNIT': L['unit'], 'LUNCH_TEXT': L['text'], 'LUNCH_DAYS': days, 'LUNCH_FORMAT': L['format'], 'LUNCH_CTA': L['cta'],
 'CHEF_TITLE': H['title'], 'CHEF_TEXT': H['text'], 'CHEF_TIERS': tiers, 'CHEF_UNIT': H['unit'], 'CHEF_FORMAT': H['format'], 'CHEF_CTA': H['cta'],
 'STEPS': steps, 'ORDER_TITLE': C['order_title'], 'ORDER_LEAD': C['order_lead'],
 'FOOTER_TEXT': C['footer_text'], 'PHONE_OWNER': C['phone_owner'], 'PHONE_OWNER_PRETTY': C['phone_owner_pretty'],
 'INSTAGRAM_URL': C['instagram_url'], 'INSTAGRAM_HANDLE': C['instagram_handle'], 'AREA_LABEL': C['area_label'],
 'MIN_GUESTS': str(C['min_guests']),
 'MENU_JSON': json.dumps(C['menu'], ensure_ascii=False, indent=2), 'FORMATS_JSON': json.dumps(C['formats'], ensure_ascii=False),
 'TARIFFS_JSON': json.dumps([t['name'] for t in C['tariffs']], ensure_ascii=False),
}
for i, a in enumerate(C['alt_g']): tokens[f'ALT_G{i}'] = a
for k, v in tokens.items(): src = src.replace('{{' + k + '}}', v)
left = re.findall(r'\{\{[A-Z_0-9]+\}\}', src)
assert not left, f'не заполнены токены: {sorted(set(left))}'

used = set(re.findall(r'<use href="#([a-z-]+)"', src)) | {'plus', 'minus', 'check'}
sym = []
for f in sorted(glob.glob('icons/*.svg')):
    n = os.path.basename(f)[:-4]
    if n not in used: continue
    s = open(f).read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    inner = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', s.strip())
    sym.append(f'<symbol id="{n}" viewBox="{vb}">{inner}</symbol>')
missing = sorted(n for n in used if not os.path.exists(f'icons/{n}.svg'))
assert not missing, f'нет иконок: {missing}'
out = src.replace('<!--SPRITE-->', '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + ''.join(sym) + '</svg>')

lq = json.load(open('lqip.json'))
out = re.sub(r'<!--LQ:([a-z0-9-]+)-->', lambda m: 'style="background-image:url(' + lq[m.group(1)] + ')"', out)

def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout.strip()
sha = os.environ.get('CDN_SHA') or sh('git', 'log', '-1', '--format=%H', '--', 'img', 'fonts')
dirty = sh('git', 'status', '--porcelain', 'img', 'fonts')
CDN = f'https://cdn.jsdelivr.net/gh/{C["repo"]}@{sha}/' if sha and (os.environ.get('CDN_SHA') or not dirty) else ''
out = out.replace('__CDN__', CDN)
if CDN: out = re.sub(r'(?<![\w/.@-])img/(?=[a-z0-9-]+\.webp)', CDN + 'img/', out)

out = out.replace('__PHONE__', phone).replace('__SRC__', 'макета сайта' if DEMO else 'сайта')
if DEMO:
    out = out.replace('<!--ROBOTS-->', '<meta name="robots" content="noindex, nofollow">')
    out = out.replace('<!--DEMONOTE-->', '<p class="fine demo-note">Это макет сайта. Заявка из макета придёт его автору, а не повару. После запуска сайта заявки будут приходить повару.</p>')
    out = re.sub(r'<a href="tel:\+[0-9]+">(.*?)</a>', r'<span class="telx">\1</span>', out)
else:
    out = out.replace('<!--ROBOTS-->', '').replace('<!--DEMONOTE-->', '')
open('index.html', 'w', encoding='utf-8').write(out)
bad = [c for c in ('—', '–') if c in out]
print('cdn', CDN or 'LOCAL', '| mode', 'DEMO' if DEMO else 'LIVE', '| заявки на', phone, '| тире:', bad or 'нет', '| байт', len(out))
