#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from os import path
from sys import stdin, stdout, stderr

from markdown import markdown as md
from scss.compiler import compile_string as compile_scss
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

def parse_args():
    infile = FileType('r', encoding='UTF-8')
    outfile = FileType('w', encoding='UTF-8')

    parser = ArgumentParser(prog='build',
        description='Build a html and/or pdf resume from a markdown and css file')

    parser.add_argument('input', type=infile,
        help='The markdown file to use as input (use - for stdin)')
    parser.add_argument('-s', '--style', type=infile, default=False,
        help='The scss file to use (use - for stdin)')
    parser.add_argument('--html', type=outfile, default=False,
        help='Where to build the html output (use - for stdout)')
    parser.add_argument('-p', '--pdf', type=outfile, default=False,
        help='Where to build the pdf output (use - for stdout)')
    parser.add_argument('-c', '--css', type=outfile, default=False,
        help='Optional file to output CSS into')
    parser.add_argument('-i', '--inline', action='store_true', default=False,
        help='In HTML, include CSS within a <style> tag instead of linking to --css')
    parser.add_argument('--no-css', action='store_true', default=False,
        help='Prevent --css from adding CSS to --html')
    parser.add_argument('--no-sass', action='store_true', default=False,
        help='Don\'t parse --style as SCSS, instead assume it is raw CSS.')
    # parser.add_argument('-w', '--watch', action='store_true', default=False, help='Enable watching for changes')

    args = parser.parse_args()

    # Count how many args equal stdin or stdout
    stdin_count = 0
    stdout_count = 0
    for arg in vars(args):
        if arg == stdin: stdin_count += 1
        elif arg == stdout: stdout_count += 1

    # Ensure we have at least one output
    if not args.pdf and not args.html and not css:
        exit('You must specify at least one output (--html, --pdf or --css)!')
    # Ensure we only use stdin for one input
    if stdin_count > 1:
        exit('You can only use stdin for one thing (input or --style)!')
    # Ensure we only use stdout for one output
    if stdout_count > 1:
        exit('You can only print stdout to one output (--html or --pdf)!')

    return args


def sass(infile):
    return compile_scss(infile.read(), generate_source_map=False, output_style='expanded')

def markdown(infile):
    return md(infile.read(), output_format='xhtml5')

def pdf(outfile, html='', css=''):
    font_config = FontConfiguration()
    HTML(string=html).write_pdf(outfile.buffer, stylesheets=[CSS(string=css, font_config=font_config)])

def main(args):

    html = markdown(args.input)

    css = ''
    if args.style:
        css = args.style.read() if args.no_sass else sass(args.style)

    if args.css:
        args.css.write(css)

    if args.pdf:
        pdf(args.pdf, html, css)

    if args.html:
        # Work out how/if to inject CSS
        style=''
        if not args.no_css:
            if args.inline:
                style='<style>\n{0}\n</style>'.format(css)
            elif args.css:
                # Work out the relative path from html to css
                prefix=path.commonprefix([args.html.name, args.css.name])
                css_path=path.relpath(args.css.name, prefix)
                style='<link rel="stylesheet" type="text/css" href="{0}" />'.format(css_path)

        output='<!DOCTYPE html>\n<html><head>\n{css}\n</head><body>\n{html}\n</body></html>'.format(html=html, css=style)
        args.html.write(output)

main(parse_args())
