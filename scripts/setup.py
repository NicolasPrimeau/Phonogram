import argparse
import json
import os
import re

import requests
from phonogram import utils


BASE_DIR = "./data"

LANGUAGE_MAP = {
    "English": "en-us",
    "French": "fr-fr"
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--link", dest="link", required=True)
    parser.add_argument("-f", "--force", dest="force", action="store_true")
    return parser.parse_args()


def main():
    args = get_args()
    data = requests.get(args.link)
    content = data.text
    lines = content.split("\n")

    print(f"Analyzing: {args.link}")

    language = find_field(lines, "Language")
    print(f"Language: {language}")

    title = find_field(lines, "Title")
    print(f"Title: {title}")

    author = find_field(lines, "Author")
    print(f"Author: {author}")

    translator = find_field(lines, "Translator")
    print(f"Translator: {translator}")

    base_path = os.path.join(BASE_DIR, utils.map_title(title), map_language(language))
    os.makedirs(base_path, exist_ok=args.force)

    print("Saving info")
    utils.save_info(base_path, {
        "title": title,
        "author": author,
        "translator": translator,
        "language": language,
        "link": args.link
    })

    print("Filtering lines")
    lines = filter_lines(lines)

    print("Saving text")
    print(save_text(base_path, lines))
    print("Done")


def find_field(lines, field):
    for line in lines:
        if re.match(f"^{field}", line):
            value = re.search(f'^{field}: (.*)', line).groups()[0]
            return value.lstrip().rstrip()


def map_language(language):
    if language not in LANGUAGE_MAP:
        raise RuntimeError(f"Unknown language: {language}")
    return LANGUAGE_MAP[language]


def filter_lines(lines):
    keep = False
    kept = list()
    for line in lines:
        if re.match("\*\*\* START", line):
            keep = True
        elif re.match("\*\*\* END", line):
            keep = False
        elif re.match("End of Project Gutenberg's", line):
            keep = False
        elif keep:
            kept.append(clean_line(line))
    return kept


def clean_line(line):
    for clean_fx in [
        remove_underline,
        lower_case
    ]:
        line = clean_fx(line)
    return line


def remove_underline(line):
    return line.replace("_", "")


def lower_case(line):
    return " ".join(
        token.lower()
        if token.isupper() and len(token) >= 2
        else token
        for token in line.split(" ")
    )


def save_text(base_path, lines):
    fpath = os.path.join(base_path, "text.ham")
    with open(fpath, "w") as mf:
        mf.write("\n".join(lines))
    return fpath


if __name__ == '__main__':
    main()
