import sys

from lxml.html.clean import Cleaner


def sanitize(dirty_html):
    cleaner = Cleaner(page_structure=True,
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

    with open(sys.argv[1]) as fin:

        with open('index.html', 'w+') as fp:
            fp.write(sanitize(fin.read()))
