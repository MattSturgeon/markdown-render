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


def file_changed(filename):
    # Ensure key exists
    if not filename in file_changed.times:
        file_changed.times[filename] = 0

    # Check if time is different and update the chached time
    time = path.getmtime(filename)
    changed = time != file_changed.times[filename]
    file_changed.times[filename] = time

    return changed


file_changed.times = {}  # Keep track of modtimes for files


def markdown(filename):
    with open(filename, "r") as file:
        return md(
            file.read(),
            output_format="xhtml5",
            extensions=["markdown.extensions.extra"],
        )


def read(filename):
    with open(filename, "r") as file:
        return file.read()


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


def main(args):
    # TODO get files from args
    md_file = "src/resume.md"
    css_file = "src/main.css"
    out_dir = "build"

    print("Building resume in pdf and html format under build/")
    if args.watch:
        print(
            "Watching for changes to {} and {}. Use Ctrl+C to cancel.".format(
                md_file, css_file
            )
        )

    # Ensure output directory exists:
    makedirs(out_dir, exist_ok=True)

    html = ""
    css = ""
    first_iteration = True
    while True:
        try:
            # Check for changed files
            modified = [file for file in [md_file, css_file] if file_changed(file)]

            # Print changes on subsequent iterations
            if not first_iteration:
                for file in modified:
                    print("File modified: {}".format(file))

            if first_iteration or md_file in modified:
                html = markdown(md_file)

            if first_iteration or css_file in modified:
                css = read(css_file)

            if first_iteration or modified:
                write_pdf(html, css)
                write_html(html, css)

            first_iteration = False

            # if not watching, break after the first run (i.e. don't loop)
            if not args.watch:
                break

            sleep(1)
        except KeyboardInterrupt:
            print("\nDone")
            break


main(parse_args())
