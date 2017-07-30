#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
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
        help='The css file to use (use - for stdin)')
    parser.add_argument('--html', type=outfile, default=False,
        help='Where to build the html output (use - for stdout)')
    parser.add_argument('-p', '--pdf', type=outfile, default=False,
        help='Where to build the pdf output (use - for stdout)')
    # parser.add_argument('-w', '--watch', action='store_true', default=False, help='Enable watching for changes')

    return parser.parse_args()

def sass(infile):
    return compile_scss(infile.read())

def markdown(infile):
    return md(infile.read(), output_format='xhtml5')

def pdf(outfile, html='', css=''):
    font_config = FontConfiguration()
    HTML(string=html).write_pdf(outfile.buffer, stylesheets=[CSS(string=css, font_config=font_config)])

def main():

    # Parse arguments
    args = parse_args()

    # Ensure we have at least one output
    if not args.pdf and not args.html:
        exit('You must specify at least one output (--html or --pdf)!')
    # Ensure we only use stdin for one input
    if args.input == stdin and args.style == stdin:
        exit('You can only use stdin for one thing (input or --style)!')
    # Ensure we only use stdout for one output
    if args.html == stdout and args.pdf == stdout:
        exit('You can only print stdout to one output (--html or --pdf)!')


    html = markdown(args.input)

    css = ''
    if args.style:
        css = sass(args.style)

    if args.html:
        print('building html') # TODO

    if args.pdf:
        pdf(args.pdf, html, css)

main()
