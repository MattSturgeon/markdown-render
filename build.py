#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from datetime import date
from os import path, makedirs
from time import sleep
from sys import stdin, stdout, stderr
from textwrap import dedent

from markdown import markdown as md
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


def parse_args():
    parser = ArgumentParser(
        prog="build",
        description="Build a html and/or pdf resume from a markdown and css file",
    )

    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        default=False,
        help="Enable watching for changes",
    )

    return parser.parse_args()


def file_changed(file_obj):
    name = file_obj.name

    # Ensure key exists
    if not name in file_changed.times:
        file_changed.times[name] = 0

    # Check if time is different and update the chached time
    time = path.getmtime(file_obj.name)
    changed = time != file_changed.times[name]
    file_changed.times[name] = time

    return changed


file_changed.times = {}  # Keep track of modtimes for files


def peek(f, length=None):
    pos = f.tell()
    data = f.read(length)
    f.seek(pos)
    return data


def markdown(infile):
    return md(
        peek(infile), output_format="xhtml5", extensions=["markdown.extensions.extra"]
    )


def write_pdf(html, css):
    filename = "build/resume-{}.pdf".format(date.today())
    font_config = FontConfiguration()

    HTML(string=html).write_pdf(
        filename, stylesheets=[CSS(string=css, font_config=font_config)]
    )


def write_html(html, css):
    filename = "build/resume-{}.html".format(date.today())
    src = (
        dedent(
            """
              <!DOCTYPE html>
              <html>
              <head>
              <style>
              {1}
              </style>
              </head>
              <body>
              {0}
              </body>
              </html>
            """
        )
        .strip()
        .format(html, css)
    )

    with open(filename, "w") as out:
        out.write(src)
    out.close()


def main(args):
    # Ensure output directory exists:
    makedirs("build", exist_ok=True)

    with open("src/resume.md", "r") as md_file, open("src/main.css", "r") as css_file:
        html = ""
        css = ""

        print("Building resume in pdf and html format under build/")
        if args.watch:
            print(
                "Watching for changes to {} and {}. Use Ctrl+C to cancel.".format(
                    md_file.name, css_file.name
                )
            )

        while True:
            try:
                # Check for changed files
                md_changed = file_changed(md_file)
                sass_changed = file_changed(css_file)

                if md_changed:
                    html = markdown(md_file)

                if sass_changed:
                    css = peek(css_file)

                if md_changed or sass_changed:
                    write_pdf(html, css)
                    write_html(html, css)

                # if not watching, break after the first run (i.e. don't loop)
                if not args.watch:
                    break

                sleep(1)
            except KeyboardInterrupt:
                print("\nDone")
                break

    md_file.close()
    css_file.close()


main(parse_args())
