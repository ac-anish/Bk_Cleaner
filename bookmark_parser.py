import os
import sys
import re
import html as html_mod
from lxml import etree


def clean_text(s):
    return re.sub(r'\s+', ' ', re.sub(r'[<>&]', '', s)).strip()


class SectionTree:
    def __init__(self, level):
        self.level = level
        self.title = None
        self.folders = []


# ---------------------------------------------------------------------------
# Page shell — identical to favorites.html / ungoogled.html (glass UI, search,
# dark mode). The body content is generated between PAGE_HEAD and PAGE_FOOTER.
# ---------------------------------------------------------------------------
PAGE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Searchable Bookmarks - Responsive</title>
  <style>
    :root {
      --bg: #eef2f7;
      --bg-gradient: linear-gradient(135deg, #e8edf4 0%, #d8dfe9 50%, #e6ecf3 100%);
      --text: #1a1c20;
      --text-muted: #5a5e6a;
      --glass-bg: rgba(255, 255, 255, 0.65);
      --glass-border: rgba(255, 255, 255, 0.7);
      --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
      --input-bg: rgba(255, 255, 255, 0.7);
      --input-border: rgba(0, 0, 0, 0.08);
      --pill-bg: rgba(255, 255, 255, 0.6);
      --pill-text: #1a1c20;
      --pill-hover-bg: rgba(255, 255, 255, 0.85);
      --pill-hover-text: #0066cc;
      --heading-color: #333;
      --heading-border: rgba(0, 0, 0, 0.06);
      --toggle-bg: #d1d5db;
      --toggle-active: #6366f1;
      --blob1: rgba(99, 102, 241, 0.12);
      --blob2: rgba(168, 85, 247, 0.09);
      --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    body.dark-mode {
      --bg: #0b0e14;
      --bg-gradient: linear-gradient(135deg, #0b0e14 0%, #131722 50%, #0f1219 100%);
      --text: #e4e6eb;
      --text-muted: #9ca3af;
      --glass-bg: rgba(30, 33, 45, 0.7);
      --glass-border: rgba(255, 255, 255, 0.1);
      --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      --input-bg: rgba(30, 33, 45, 0.75);
      --input-border: rgba(255, 255, 255, 0.08);
      --pill-bg: rgba(30, 33, 45, 0.65);
      --pill-text: #e4e6eb;
      --pill-hover-bg: rgba(40, 44, 58, 0.9);
      --pill-hover-text: #60a5fa;
      --heading-color: #e4e6eb;
      --heading-border: rgba(255, 255, 255, 0.08);
      --toggle-bg: #374151;
      --blob1: rgba(99, 102, 241, 0.08);
      --blob2: rgba(168, 85, 247, 0.06);
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font);
      background: var(--bg);
      background-image: var(--bg-gradient);
      color: var(--text);
      min-height: 100vh;
      padding: 0;
      margin: 0;
      overflow-x: hidden;
      transition: background 0.4s ease, color 0.35s ease;
    }
    body::before {
      content: "";
      position: fixed;
      width: 500px; height: 500px;
      top: -100px; left: -140px;
      background: var(--blob1);
      filter: blur(100px);
      border-radius: 50%;
      pointer-events: none;
    }
    body::after {
      content: "";
      position: fixed;
      width: 450px; height: 450px;
      bottom: -80px; right: -100px;
      background: var(--blob2);
      filter: blur(100px);
      border-radius: 50%;
      pointer-events: none;
    }
    #searchWrapper {
      position: relative;
      z-index: 10;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      align-items: center;
      gap: 12px;
      padding: 24px 20px 0;
      margin-bottom: 24px;
    }
    #homeIcon {
      height: 40px;
      width: 40px;
      cursor: pointer;
      fill: var(--text-muted);
      flex-shrink: 0;
      transition: fill 0.2s ease, transform 0.2s ease;
    }
    #homeIcon:hover {
      fill: var(--text);
      transform: scale(1.1);
    }
    #searchBox {
      flex: 1 1 300px;
      padding: 12px 18px;
      font-family: var(--font);
      font-size: 16px;
      color: var(--text);
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      border-radius: 50px;
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
      box-sizing: border-box;
      max-width: 500px;
      min-width: 200px;
      outline: none;
      transition: border-color 0.25s ease, box-shadow 0.25s ease, background 0.3s ease;
    }
    #searchBox::placeholder { color: var(--text-muted); opacity: 0.7; }
    #searchBox:focus {
      border-color: var(--toggle-active);
      box-shadow: 0 2px 16px rgba(99, 102, 241, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    #bookmarksContainer {
      position: relative;
      z-index: 1;
      width: 100%;
      padding: 0 14px 40px;
    }
    h3 {
      width: 100%;
      margin-top: 28px;
      margin-bottom: 10px;
      color: var(--heading-color);
      border-bottom: 2px solid var(--heading-border);
      padding-bottom: 8px;
      font-size: 1.15rem;
      font-weight: 600;
      letter-spacing: 0.02em;
      transition: color 0.3s ease;
    }
    .category {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 8px;
    }
    .category a {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: 5px;
      width: 100%;
      box-sizing: border-box;
      padding: 8px 12px;
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
      color: var(--pill-text);
      background: var(--pill-bg);
      border: 1px solid var(--glass-border);
      border-radius: 50px;
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      transition: background 0.25s ease, color 0.25s ease,
                  transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1),
                  box-shadow 0.25s ease;
    }
    .category a:hover {
      background: var(--pill-hover-bg);
      color: var(--pill-hover-text);
      transform: translateY(-1px) scale(1.02);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
    }
    @media (max-width: 480px) {
      #searchBox { width: 100%; }
      .category { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
<div id="searchWrapper">
  <a href="index.html" title="Home" aria-label="Home">
    <svg id="homeIcon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72">
      <path d="M 36 10 C 34.861 10 33.722922 10.386609 32.794922 11.162109 L 11.517578 28.941406 C 10.052578 30.165406 9.5519375 32.270219 10.460938 33.949219 C 11.711938 36.258219 14.661453 36.740437 16.564453 35.148438 L 35.359375 19.445312 C 35.730375 19.135313 36.269625 19.135313 36.640625 19.445312 L 55.435547 35.148438 C 56.183547 35.774437 57.093047 36.078125 57.998047 36.078125 C 59.171047 36.078125 60.333953 35.567219 61.126953 34.574219 C 62.503953 32.850219 62.112922 30.303672 60.419922 28.888672 L 58 26.867188 L 58 16.667969 C 58 15.194969 56.805984 14 55.333984 14 L 52.667969 14 C 51.194969 14 50 15.194969 50 16.667969 L 50 20.181641 L 39.205078 11.162109 C 38.277078 10.386609 37.139 10 36 10 z M 35.996094 22.925781 L 13.996094 41.302734 L 13.996094 50 C 13.996094 54.418 17.578094 58 21.996094 58 L 49.996094 58 C 54.414094 58 57.996094 54.418 57.996094 50 L 57.996094 41.302734 L 35.996094 22.925781 z M 32 38 L 40 38 C 41.105 38 42 38.895 42 40 L 42 50 L 30 50 L 30 40 C 30 38.895 30.895 38 32 38 z"></path>
    </svg>
  </a>
  <input type="text" id="searchBox" placeholder="Search bookmarks... Ctrl+K focus / Ctrl+H Home" />
</div>
<div id="bookmarksContainer">
"""

PAGE_FOOTER = """
</div>
<script>
const searchBox = document.getElementById('searchBox');
const container = document.getElementById('bookmarksContainer');

searchBox.addEventListener('input', () => {
  const filter = searchBox.value.trim().toLowerCase();
  const headings = container.querySelectorAll('h3');

  headings.forEach(h3 => {
    const category = h3.nextElementSibling;
    if (!category || !category.classList.contains('category')) return;
    const links = category.querySelectorAll('a');
    let anyVisible = !filter;   // when cleared, show everything

    if (filter) {
      links.forEach(link => {
        const match = link.textContent.toLowerCase().includes(filter);
        link.style.display = match ? '' : 'none';
        if (match) anyVisible = true;
      });
    } else {
      // Clearing the search resets to the stylesheet layout.
      links.forEach(link => { link.style.display = ''; });
    }

    h3.style.display = anyVisible ? '' : 'none';
    category.style.display = anyVisible ? '' : 'none';
  });
});

// Keyboard shortcuts: Ctrl/Cmd+K focuses search, Ctrl/Cmd+H goes home
document.addEventListener('keydown', (e) => {
  const key = e.key.toLowerCase();
  if (!(e.metaKey || e.ctrlKey)) return;
  if (key === 'k') {
    e.preventDefault();
    searchBox.focus();
    searchBox.select();
  } else if (key === 'h') {
    e.preventDefault();
    window.location.href = 'index.html';
  }
});
</script>
<script>
  if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
  }
</script>
</body>
</html>
"""


def build_fragment(raw):
    blobs = []

    tk = re.compile(
        r"<(?P<open>/?)\s*(?P<tag>[A-Za-z][\w-]*)"       # <, optional /, tag name
        r"(?P<attrs>[^>]*?)(?P<selfclose>/?)\s*>",       # attributes, optional />
        re.DOTALL,
    )

    open_dt = False  # whether we currently have an un-closed <dt>

    def close_dt():
        nonlocal open_dt
        if open_dt:
            blobs.append('</dt>')
            open_dt = False

    pos = 0
    for m in tk.finditer(raw):
        text = raw[pos:m.start()]
        blobs.append(html_mod.escape(text))
        pos = m.end()

        tag = m.group('tag').lower()
        closing = bool(m.group('open'))

        if tag not in ('dl', 'dt', 'h3', 'a'):
            continue

        if closing:
            if tag == 'dt':
                close_dt()
            elif tag == 'dl':
                close_dt()
                blobs.append('</dl>')
            elif tag == 'a':
                blobs.append('</a>')
            elif tag == 'h3':
                blobs.append('</h3>')
            continue

        if tag == 'dl':
            close_dt()
            blobs.append('<dl>')
        elif tag == 'dt':
            close_dt()
            blobs.append('<dt>')
            open_dt = True
        elif tag == 'h3':
            blobs.append('<h3>')
        elif tag == 'a':
            href_match = re.search(r'href\s*=\s*(["\'])(.*?)\1', m.group('attrs'), re.I | re.S)
            href_val = html_mod.escape(href_match.group(2)) if href_match else ''
            blobs.append('<a href="%s">' % href_val)

    blobs.append(html_mod.escape(raw[pos:]))

    fragment = ''.join(blobs)
    # Keep only the first complete <dl>...</dl> subtree (the bookmarks root).
    m = re.search(r'(<dl>.*</dl>)', fragment, re.DOTALL)
    if m:
        fragment = m.group(1)
    else:
        fragment = '<dl>%s</dl>' % fragment
    return fragment


def parse_entries(raw):
    fragment = build_fragment(raw)
    parser = etree.XMLParser(recover=True)
    doc = etree.fromstring(fragment.encode('utf-8'), parser)
    if doc is None:
        return []
    return _build(doc)


def _build(dl_elem):
    """Parse a <dl> element into a list of entries. Each entry is either a
    SectionTree (folder) or a (label, href) tuple (bookmark link)."""
    entries = []
    items = dl_elem.getchildren()
    i = 0
    while i < len(items):
        el = items[i]
        if el.tag == 'dt':
            h3 = None
            a = None
            for c in el.getchildren():
                if c.tag == 'h3':
                    h3 = c
                elif c.tag == 'a':
                    a = c
            if h3 is not None:
                # Folder header; the following sibling <dl> holds its contents.
                kid_dl = None
                j = i + 1
                while j < len(items) and items[j].tag != 'dl':
                    j += 1
                if j < len(items):
                    kid_dl = items[j]
                node = SectionTree(0)
                node.title = clean_text(h3.text or '')
                node.folders = _build(kid_dl) if kid_dl is not None else []
                entries.append(node)
            elif a is not None:
                href = (a.get('href') or '').strip()
                label = clean_text(a.text or '') or href
                if href:
                    entries.append((label, href))
        i += 1
    return entries


def emit_folders(entries, f):
    """Emit each folder as its own flat <h3> + <div class='category'> block
    (matching favorites.html / ungoogled.html). Sub-folders become their own
    independent sections; links shown under their immediate parent only."""
    for entry in entries:
        if isinstance(entry, tuple):
            # A bare link at the top level (no folder) — group them together
            # under a generic section is not desired; links only appear under
            # folders, so skip stray top-level links.
            continue
        _emit_folder(entry, f)


def _emit_folder(entry, f):
    safe_title = re.sub(r'[<>&]', '', entry.title).strip()
    if not safe_title:
        return
    f.write('\n<h3>%s</h3>\n<div class=\'category\'>\n' % safe_title)
    for child in entry.folders:
        if isinstance(child, tuple):
            label, href = child
            safe = re.sub(r'["<>\']', '', href)
            safe_label = re.sub(r'[<>&]', '', label)
            f.write('  <a href="%s" target="_blank">%s</a>\n' % (safe, safe_label))
    f.write('</div>\n')
    # Sub-folders become their own sections (flattened, in order).
    for child in entry.folders:
        if not isinstance(child, tuple):
            _emit_folder(child, f)


def build_output(entries, out_path):
    with open(out_path, 'w+', encoding='utf-8') as f:
        f.write(PAGE_HEAD)
        f.write('<div id="bookmarksContainer">\n')
        emit_folders(entries, f)
        f.write('\n</div>\n')
        f.write(PAGE_FOOTER)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python bookmark_parser.py <input_bookmarks_file> [output.html]  (defaults to <input>-converted.html)")
        sys.exit(1)

    in_path = sys.argv[1]
    base = os.path.splitext(in_path)[0]
    out_path = sys.argv[2] if len(sys.argv) > 2 else base + '-converted.html'

    # Never clobber the source export if no output name was given.
    if os.path.abspath(in_path) == os.path.abspath(out_path):
        out_path = base + '.gen.html'
        print("WARNING: refusing to overwrite input; writing to '%s'." % out_path)

    try:
        with open(in_path, 'r', encoding='utf-8', errors='replace') as fin:
            raw = fin.read()

        entries = parse_entries(raw)
        build_output(entries, out_path)
        print("Done. Output saved to '%s'." % out_path)
    except FileNotFoundError as e:
        print("File not found: %s" % e.filename)
    except Exception:
        import traceback
        traceback.print_exc()