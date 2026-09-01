from urllib.parse import urlparse

def prettify_domain(url):
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    hostname = hostname.replace("www.", "")
    
    # Convert "haveibeenpwned.com" → "have i been pwned"
    name = hostname.split('.')[0]
    name = name.replace('-', ' ').replace('_', ' ')
    return name.strip().lower().capitalize()

def format_url(url):
    text = prettify_domain(url)
    return f'{{ href: "{url}", text: "{text}" }},'

def main():
    print("Enter one or more URLs (comma or newline separated). Press Ctrl+D (Linux/macOS) or Ctrl+Z (Windows) to finish:")

    try:
        raw_input = ""
        while True:
            raw_input += input() + "\n"
    except EOFError:
        pass

    # Split input into clean URLs
    urls = [u.strip() for u in raw_input.replace(',', '\n').splitlines() if u.strip()]
    
    print("\nFormatted Output:\n")
    for url in urls:
        try:
            print(format_url(url))
        except Exception as e:
            print(f"# Skipped invalid URL: {url} ({e})")

if __name__ == "__main__":
    main()
