#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from datetime import date
from os import path, makedirs
from time import sleep
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

    parser.add_argument(
        "file",
        help="The markdown file to render",
    )

    parser.add_argument(
        "-b",
        "-o",
        "--build-dir",
        default="build",
        help="The directory to write output to",
    )

    parser.add_argument(
        "-s",
        "--style",
        "--css",
        help="Optional CSS stylesheet",
    )

    return parser.parse_args()


def file_changed(filename):
    # Ensure key exists
    if filename not in file_changed.times:
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
    if not filename:
        return None
    with open(filename, "r") as file:
        return file.read()


def write_pdf(html, css):
    filename = f"build/resume-{date.today()}.pdf"
    stylesheets = [CSS(string=css, font_config=FontConfiguration())] if css else []
    HTML(string=html).write_pdf(filename, stylesheets=stylesheets)


def write_html(html, css):
    filename = f"build/resume-{date.today()}.html"
    styleTag = f"<style>\n{css}\n</style>" if css else ""
    src = dedent(
        f"""
          <!DOCTYPE html>
          <html>
          <head>
          {styleTag}
          </head>
          <body>
          {html}
          </body>
          </html>
        """
    ).strip()

    with open(filename, "w") as out:
        out.write(src)


def main(args):
    md_file = args.file
    css_file = args.style
    build_dir = args.build_dir

    print("Building resume in pdf and html format under build/")
    if args.watch:
        optional = f" and {css_file}" if css_file else ""
        print(f"Watching for changes to {md_file}{optional}. Use Ctrl+C to cancel.")

    # Ensure output directory exists:
    makedirs(build_dir, exist_ok=True)

    html = ""
    css = ""
    first_iteration = True
    while True:
        try:
            # Check for changed files
            modified = [
                file for file in [md_file, css_file] if file and file_changed(file)
            ]

            # Print changes on subsequent iterations
            if not first_iteration:
                for file in modified:
                    print(f"File modified: {file}")

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
