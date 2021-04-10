import argparse

from phonogram import refine, utils

REFINERS = [refine.SubstituteCodes(), refine.ChapterMarkup()]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--book-title", dest="book_title", required=True)
    parser.add_argument("-l", "--language", dest="language", required=True)
    return parser.parse_args()


def main():
    args = get_args()
    lines = list(utils.iterate_lines(utils.make_ham_path(args.book_title, args.language)))
    lines = list(refine.refine_lines_it(lines, refine.SubstituteCodes()))
    lines = list(refine.refine_lines_it(lines, refine.ChapterMarkup()))
    utils.write_lines(
        utils.make_ham_path(args.book_title, args.language)+".refined",
        lines
    )


if __name__ == '__main__':
    main()
