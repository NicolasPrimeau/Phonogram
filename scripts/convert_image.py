import argparse
import glob
import os
from PIL import Image
from phonogram import utils

ACCEPTED = {
    "image.jpg"
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--book-title", dest="book_title", required=True)
    parser.add_argument("-l", "--language", dest="language", required=False, default="en-us")
    return parser.parse_args()


def main():
    args = get_args()
    out_image_path = utils.make_image_path(args.book_title, args.language)
    if os.path.exists(out_image_path):
        print("PNG already exists")
        return

    image_path = get_image_path(utils.make_base_path(args.book_title, args.language))
    if not image_path:
        raise RuntimeError("No image found!")

    Image.open(image_path).save(out_image_path, "PNG")


def get_image_path(base):
    for file in glob.glob(os.path.join(base, "*")):
        fname = os.path.split(file)[-1]
        if fname in ACCEPTED:
            return file
    return None


if __name__ == '__main__':
    main()
