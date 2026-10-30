"""Builds the PropMaster PCG website into ../docs from guide.md, videos.json and the page templates below.
Run: python build.py   (no third-party packages; a small Markdown subset: headings, paragraphs, lists, tables, bold, code, links)."""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'docs')  # GitHub Pages serves /docs
SITE_NAME = 'PropMaster PCG'
FAB_URL = '#'  # set when the Fab listing is live


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def md_to_html(md):
    """Returns (html, toc) where toc = [(level, title, id)]."""
    out, toc = [], []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r'^(#{2,4}) (.+)$', line)
        if m:
            level, title = len(m.group(1)), m.group(2).strip()
            anchor = slug(title)
            toc.append((level, title, anchor))
            out.append('<h%d id="%s">%s</h%d>' % (level, anchor, inline(title), level))
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.match(r'^-+$', c) for c in r)]
            t = ['<div class="table"><table><thead><tr>' + ''.join('<th>%s</th>' % inline(c) for c in head) + '</tr></thead><tbody>']
            for r in body:
                t.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>')
            t.append('</tbody></table></div>')
            out.append(''.join(t))
            continue
        if re.match(r'^(\d+\.|-) ', line):
            ordered = bool(re.match(r'^\d+\.', line))
            items = []
            while i < len(lines) and re.match(r'^(\d+\.|-) ', lines[i]):
                items.append(re.sub(r'^(\d+\.|-) ', '', lines[i]))
                i += 1
            tag = 'ol' if ordered else 'ul'
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % inline(x) for x in items), tag))
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{2,4} |\||\d+\. |- )', lines[i]):
            para.append(lines[i])
            i += 1
        out.append('<p>%s</p>' % inline(' '.join(para)))
    return '\n'.join(out), toc


def page(title, body, active, description):
    nav = ''.join('<a href="%s"%s>%s</a>' % (href, ' class="active"' if name == active else '', name)
                  for name, href in [('Home', 'index.html'), ('Guide', 'guide.html'), ('Videos', 'videos.html')])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="top">
  <div class="wrap top-inner">
    <a class="brand" href="index.html"><span class="mark">PM</span>{SITE_NAME}</a>
    <nav>{nav}<a class="btn small" href="{FAB_URL}">Get it on Fab</a></nav>
  </div>
</header>
{body}
<footer class="foot"><div class="wrap">&copy; Caster. {SITE_NAME} for Unreal Engine 5.8. Unreal Engine is a trademark of Epic Games, Inc.</div></footer>
</body>
</html>
'''


def build():
    os.makedirs(OUT, exist_ok=True)
    md = open(os.path.join(HERE, 'guide.md'), encoding='utf-8').read()
    body, toc = md_to_html(md)
    side = ''.join('<a class="l%d" href="#%s">%s</a>' % (lvl, a, html.escape(t)) for lvl, t, a in toc if lvl <= 3)
    guide = f'''<main class="wrap guide">
  <aside class="toc"><div class="toc-inner"><div class="toc-title">On this page</div>{side}</div></aside>
  <article class="doc"><h1>User Guide</h1>{body}</article>
</main>'''
    open(os.path.join(OUT, 'guide.html'), 'w', encoding='utf-8').write(
        page(f'User Guide | {SITE_NAME}', guide, 'Guide', 'Every PropMaster PCG tool and setting, explained.'))

    videos = json.load(open(os.path.join(HERE, 'videos.json'), encoding='utf-8'))
    cards = []
    for v in videos:
        m = re.search(r'(?:v=|youtu\.be/|embed/)([\w-]{11})', v.get('url', ''))
        media = (f'<div class="embed"><iframe src="https://www.youtube-nocookie.com/embed/{m.group(1)}" title="{html.escape(v["title"])}" '
                 'loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
                 if m else '<div class="embed soon">Video coming soon</div>')
        cards.append(f'<div class="card video" id="{slug(v["title"])}">{media}<h3>{html.escape(v["title"])}</h3><p>{inline(v.get("about", ""))}</p></div>')
    vids = f'''<main class="wrap">
  <section class="page-head"><h1>Videos</h1><p>Short walkthroughs of each tool. The buttons in the tools' panels open these.</p></section>
  <section class="grid">{''.join(cards)}</section>
</main>'''
    open(os.path.join(OUT, 'videos.html'), 'w', encoding='utf-8').write(
        page(f'Videos | {SITE_NAME}', vids, 'Videos', 'PropMaster PCG video tutorials.'))

    home = f'''<section class="hero"><div class="wrap">
  <p class="eyebrow">PCG tools for Unreal Engine 5.8</p>
  <h1>Turn a blockout into a dressed scene in minutes.</h1>
  <p class="lead">Three procedural dressing tools for designers and environment artists. Draw a spline, drop a box or pick a mesh, and PropMaster fills it with your meshes, clusters, moss and decals. Every result is seeded and editable.</p>
  <div class="cta"><a class="btn" href="{FAB_URL}">Get it on Fab</a><a class="btn ghost" href="guide.html">Read the guide</a></div>
</div></section>
<main class="wrap">
  <section class="grid three">
    <div class="card tool"><h2>Spline</h2><p>Paths, walls, fences and pipes along a spline, or scatter filling a closed area. Stack meshes into walls, follow landscape layers, keep off tagged roads.</p><a href="guide.html#spline-tool">Spline guide &rarr;</a></div>
    <div class="card tool"><h2>Volume</h2><p>Dress a room's floors, walls and ceilings, or the outside of rocks and props. Pick faces by the way surfaces face, pile meshes out of any surface.</p><a href="guide.html#volume-tool">Volume guide &rarr;</a></div>
    <div class="card tool"><h2>Mesh Cover</h2><p>Grow moss, vines, debris and decals over meshes already in the level, by top, side and bottom, facing a direction or along tagged splines.</p><a href="guide.html#mesh-cover-tool">Mesh Cover guide &rarr;</a></div>
  </section>
  <section class="features">
    <h2>Built for fast iteration</h2>
    <div class="grid two">
      <div><h3>Layers that respect each other</h3><p>Later layers avoid earlier ones. Solo and Mute any layer while you tune.</p></div>
      <div><h3>Clusters and cover by intent</h3><p>Smaller meshes gather around each main mesh; moss and vines grow where you want them.</p></div>
      <div><h3>Stack Vertical</h3><p>Brick walls, sandbag walls, crate piles and rock towers from a single mesh list.</p></div>
      <div><h3>Footprint</h3><p>See instances, memory, streaming and GPU cost, and how much each optimize step saved.</p></div>
      <div><h3>Presets</h3><p>Save a look once and reuse it on any spline, volume or cover tool.</p></div>
      <div><h3>Convert to Mesh</h3><p>Bake the result into plain meshes when you're done.</p></div>
    </div>
  </section>
</main>'''
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(
        page(SITE_NAME, home, 'Home', 'PropMaster PCG: three procedural dressing tools for Unreal Engine 5.8.'))

    import shutil
    shutil.copy(os.path.join(HERE, 'style.css'), os.path.join(OUT, 'style.css'))
    open(os.path.join(OUT, 'CNAME'), 'w').write('propmasterpcg.com' + chr(10))  # GitHub Pages custom domain
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('built', sorted(os.listdir(OUT)))


if __name__ == '__main__':
    build()
