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
        safe_attrs=frozenset(['src', 'color', 'href', 'title', 'class', 'name', 'id']),
        remove_tags=('span', 'font', 'div', 'dt', 'dl', 'p')
    )
    return cleaner.clean_html(dirty_html)

if __name__ == '__main__':
    # Check if a file path argument is provided
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_html_file>")
        sys.exit(1)

    try:
        # Open the input file with encoding handling
        with open(sys.argv[1], 'r', encoding='utf-8', errors='replace') as fin:
            # Open the output file to write the sanitized HTML
            with open('index.html', 'w+', encoding='utf-8') as fp:
                fp.write(sanitize(fin.read()))
        print("Sanitization complete. Output saved to 'index.html'.")

    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
    except UnicodeDecodeError as e:
        print(f"Error decoding the file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
