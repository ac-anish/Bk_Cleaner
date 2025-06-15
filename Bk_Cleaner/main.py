import sys
from lxml.html.clean import Cleaner

def sanitize(dirty_html):
    cleaner = Cleaner(
        page_structure=True,
        meta=True,
        embedded=True,
        links=True,
        style=True,
        processing_instructions=True,
        inline_style=True,
        scripts=True,
        javascript=True,
        comments=True,
        frames=True,
        forms=True,
        annoying_tags=True,
        remove_unknown_tags=True,
        safe_attrs_only=True,
        safe_attrs=frozenset(['src','color', 'href', 'title', 'class', 'name', 'id']),
        remove_tags=('span', 'font', 'div', 'dt', 'dl', 'p')
    )
    return cleaner.clean_html(dirty_html)

if __name__ == '__main__':
    # Open the input file with encoding handling
    try:
        with open(sys.argv[1], 'r', encoding='utf-8', errors='replace') as fin:
            with open('index.html', 'w+', encoding='utf-8') as fp:
                fp.write(sanitize(fin.read()))
    except UnicodeDecodeError as e:
        print(f"Error decoding the file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
