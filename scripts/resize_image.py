import argparse
import os
from PIL import Image

BASE_PATH = "./data"

SIZES = {
    "thumbnail": (120, 120),
    "wallpaper": (720, 480)
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--book-title", dest="book_title", required=True)
    parser.add_argument("-l", "--language", dest="language", required=True)
    parser.add_argument("-s", "--size", dest="size", required=True, choices=list(SIZES.keys()))
    return parser.parse_args()


def main():
    args = get_args()
    base_path = os.path.abspath(os.path.join(BASE_PATH, args.book_title, args.language))
    image_path = os.path.join(base_path, "image.png")
    out_path = os.path.join(base_path, f"image.{args.size}.png")
    image = Image.open(image_path)
    resized_image = image.resize(SIZES[args.size], Image.ANTIALIAS)
    resized_image.save(out_path, "PNG")


if __name__ == '__main__':
    main()
