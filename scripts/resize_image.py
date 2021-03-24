import argparse
import os
from PIL import Image

size = 720, 480

BASE_PATH = "./data"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--book-title", dest="book_title", required=True)
    parser.add_argument("-l", "--language", dest="language", required=True)
    return parser.parse_args()


def main():
    args = get_args()
    base_path = os.path.abspath(os.path.join(BASE_PATH, args.book_title, args.language))
    image_path = os.path.join(base_path, "wallpaper.raw.png")
    out_path = os.path.join(base_path, "wallpaper.png")
    image = Image.open(image_path)
    resized_image = image.resize(size, Image.ANTIALIAS)
    resized_image.save(out_path, "PNG")


if __name__ == '__main__':
    main()
