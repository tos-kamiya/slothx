import sys
import argparse
import re
from bs4 import BeautifulSoup
from markdown import markdown

def format_latex_math_blocks(text):
    """
    Align the format of LaTeX equations.
    Convert inline math `$...$` to `$$...$$`, keeping existing `$$...$$` as is.
    """

    # Temporarily replace $$...$$ with a placeholder
    placeholder = "PLACEHOLDER_FOR_DOUBLE_DOLLAR"
    text = text.replace('$$', placeholder)

    # Use replace $ with $$
    text = text.replace('$', '$$')

    # Restore the original $$...$$ from the placeholder
    text = text.replace(placeholder, '$$')

    return text

def main():
    parser = argparse.ArgumentParser(description="Convert markdown to Moodle-ish html")
    parser.add_argument(
        'inputmd', type=str,
        help='Markdown file to process. "-" for read from the standard input)',
    )
    args = parser.parse_args()

    if args.inputmd == "-":
        text = sys.stdin.read()
    else:
        with open(args.inputmd, "r", encoding="utf-8") as inp:
            text = inp.read()

    # Properly convert the format of LaTeX equations
    try:
        text = format_latex_math_blocks(text)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert Markdown to HTML
    html = markdown(text, extensions=['fenced_code', 'tables'])
    soup = BeautifulSoup(html, 'html.parser')

    # Add border attribute to tables
    tables = soup.find_all("table")
    for t in tables:
        t.attrs['border'] = '1'

    # Add style to <pre> tags
    pres = soup.find_all('pre')
    for t in pres:
        s = t.attrs.setdefault('style', '')
        s = s.rstrip()
        if s and not s.endswith(';'):
            s = s + ';'
        t.attrs['style'] = s + 'background-color: #e8e8e8; padding: 10px;'

    print(soup.prettify())

if __name__ == "__main__":
    main()
