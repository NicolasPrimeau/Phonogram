import json
import os


def get_lines(fpath):
    with open(fpath) as mf:
        return mf.read().split("\n")


def map_title(title):
    title = "".join(letter for letter in title if letter.isalnum() or letter == " ")
    return title.lower().replace(" ", "_")


def save_info(base_path, data):
    with open(os.path.join(base_path, "info.json"), "w") as mf:
        json.dump(data, mf)
