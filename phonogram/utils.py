import json
import os


DATA_PATH = "./data"


def make_base_path(book_title, language):
    return os.path.join(DATA_PATH, book_title, language)


def make_ham_path(book_title, language):
    return os.path.join(make_base_path(book_title, language), "text.ham")


def get_lines(fpath):
    with open(fpath) as mf:
        return mf.read().split("\n")


def write_lines(fpath, lines):
    with open(fpath, "w") as mf:
        mf.write("\n".join(lines))


def iterate_lines(fpath):
    for line in open(fpath):
        yield line.strip()


def map_title(title):
    title = "".join(letter for letter in title if letter.isalnum() or letter == " ")
    return title.lower().replace(" ", "_")


def save_info(base_path, data):
    with open(os.path.join(base_path, "info.json"), "w") as mf:
        json.dump(data, mf)
