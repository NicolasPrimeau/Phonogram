import argparse
import os
import re

from phonogram import utils

BASE_PATH = "./data/"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", dest="prefix", help="Prefix", required=False, type=str, default="")
    parser.add_argument("-f", "--file", dest="file", help="File", required=True, type=str)
    parser.add_argument("-l", "--language", dest="language", help="Language", required=True, type=str)
    return parser.parse_args()


def main():
    args = get_args()
    lines = utils.get_lines(args.file)

    block_name = None
    block = None
    for line in lines:
        if re.match("<split.*/>", line):
            if block:
                save_block(args.prefix, block_name, block, args.language)
            block_name = re.search('name="(.*)"', line).groups()[0]
            block = list()
        elif block_name:
            block.append(line)
        else:
            raise RuntimeError(f"Bad format: {line}")

    if block:
        save_block(args.prefix, block_name, block, args.language)


def save_block(prefix, block_name, block, language):
    title = block_name.lower().replace(" ", "_")
    folder = os.path.join(BASE_PATH, prefix, title, language)
    os.makedirs(folder, exist_ok=False)
    with open(os.path.join(folder, "text.ham"), "w") as mf:
        mf.write("\n".join(block))


if __name__ == '__main__':
    main()