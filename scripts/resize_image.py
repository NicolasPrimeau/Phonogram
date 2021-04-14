import argparse
import os
from PIL import Image
from phonogram import utils


SIZES = {
    "thumbnail": (120, 120),
    "wallpaper": (720, 480)
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--book-title", dest="book_title", required=True)
    parser.add_argument("-l", "--language", dest="language", required=False, default="en-us")
    parser.add_argument("-s", "--size", dest="size", required=True, choices=list(SIZES.keys()))
    return parser.parse_args()


def main():
    args = get_args()
    base_path = utils.make_base_path(args.book_title, args.language)
    image_path = utils.make_image_path(args.book_title, args.language)
    out_path = os.path.join(base_path, f"image.{args.size}.png")
    image = Image.open(image_path)
    resized_image = image.resize(SIZES[args.size], Image.ANTIALIAS)
    resized_image.save(out_path, "PNG")


if __name__ == '__main__':
    main()
