"""
How to use the program, what options are available.
"""

def show_help():
    text = """
melt - visual cat-like file viewer with syntax highlighting supporting 2-file views

Usage: melt FILE1 FILE2 [options]

Options:

-h, --help                show this help
--light                   theme for light background

melt requires bat (https://github.com/sharkdp/bat) for the syntax highlighting
""".strip()
    print(text)
