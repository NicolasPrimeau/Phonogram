import os
import random
import shutil

from phonogram import utils

PATH = "./data/fables/text.ham"
IMAGE_PATH = "./data/fables/image.png"

DATA_PATH = "./data/fables/"


VOICES = [
    "Celine",
    "Lea",
    "Mathieu",
    "Chantal"
]


def main():

    title = list()
    last_is_title = False
    text = list()
    for line in filter(None, map(lambda l: l.strip(), open(PATH))):
        if not title and is_title(line):
            title.append(line)
            last_is_title = True
        elif is_title(line) and last_is_title:
            title.append(line)
            last_is_title = True
        elif is_title(line):
            save_story(title, text)
            title = list()
            title.append(line)
            text = list()
            last_is_title = True
        elif should_keep(line):
            text.append(line)
            last_is_title = False

    if title:
        save_story(title, text)


def save_story(title, text):
    book_title = " ".join(title)
    base_path = os.path.join(DATA_PATH, utils.map_title(book_title), "fr-fr")

    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path, exist_ok=False)

    utils.save_info(base_path, {
        "title": title,
        "author": "Jean de la Fontaine",
        "link": "http://www.gutenberg.org/files/56327/56327-0.txt",
        "language": "French"
    })
    save_ham(base_path, generate_ham(book_title, text))
    copy_image(base_path, IMAGE_PATH)


def is_title(line):
    return all(a.isupper() for a in line if a.isalpha())


def should_keep(line):
    return line[0].isupper()


def generate_ham(title, text):
    content = list()
    content.append(f'<config voice_id="{random.choice(VOICES)}"/>')
    content.append('<pause length="2000"/>')
    content.append(f'<text>{title.lower().capitalize()}</text>')
    content.append('<pause length="2000"/>')
    content.append(f'<text>de Jean de la Fontaine</text>')
    content.append('<pause length="2000"/>')
    for line in text:
        content.append(f'<text>{line}</text>')
    return content


def copy_image(base_path, image_path):
    shutil.copy(image_path, os.path.join(base_path, "image.png"))


def save_ham(base_path, ham):
    with open(os.path.join(base_path, "text.ham"), "w") as mf:
        for line in ham:
            print(line, file=mf)


if __name__ == '__main__':
    main()
