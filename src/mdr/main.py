#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from datetime import date
from importlib import resources
from os import path, makedirs
from pathlib import Path
from time import sleep
from textwrap import dedent

from markdown import markdown as md
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


def parse_args():
    parser = ArgumentParser(
        prog="mdr",
        description="Render a html and/or pdf page from a markdown and css file",
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
    with open(filename, "r") as file:
        return file.read()


def write_pdf(html, css, out):
    path = out / f"{date.today()}.pdf"
    stylesheets = [CSS(string=css, font_config=FontConfiguration())]
    HTML(string=html).write_pdf(target=path, stylesheets=stylesheets)


def write_html(html, css, out):
    path = out / f"{date.today()}.html"
    path.write_text(
        dedent(
            f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                {css}
                </style>
                </head>
                <body>
                {html}
                </body>
                </html>
             """
        ).strip()
    )


def main():
    args = parse_args()
    md_file = args.file
    css_file = args.style
    build_dir = Path(args.build_dir)

    print(f"Rendering pdf and html in {build_dir}")
    if args.watch:
        optional = f" and {css_file}" if css_file else ""
        print(f"Watching for changes to {md_file}{optional}. Use Ctrl+C to cancel.")

    # Ensure output directory exists:
    makedirs(build_dir, exist_ok=True)

    html = ""
    css = ""
    first_iteration = True

    # Read the default CSS file
    if not css_file:
        css = resources.files("mdr").joinpath("main.css").read_text()

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

            if css_file and first_iteration or css_file in modified:
                css = read(css_file)

            if first_iteration or modified:
                write_pdf(html, css, build_dir)
                write_html(html, css, build_dir)

            first_iteration = False

            # if not watching, break after the first run (i.e. don't loop)
            if not args.watch:
                break

            sleep(1)
        except KeyboardInterrupt:
            print("\nDone")
            break
