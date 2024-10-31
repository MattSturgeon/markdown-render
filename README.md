# Markdown Renderer

A simple python script to render a markdown resume to both HTML and PDF.

> [!WARNING]
> **Do not use!**\
> While this was a fun experiment in writing a "real world" python utility, there are far better tools available.

> [!TIP]
> [pandoc](https://pandoc.org/) can be used to do everything this project does and more.
> ```
> pandoc --pdf-engine=weasyprint ./resume.md -o resume.pdf -c stlye.css
> ```

## Requirements

If building with nix, the requirements will be handled automatically.

Otherwise you will need:

- Python 3.9+
- [Python-Markdown](https://github.com/Python-Markdown/markdown)
- [WeasyPrint](https://github.com/Kozea/WeasyPrint)

## Usage

See `mdr --help`

