import argparse

from phonogram import process


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--book-title", dest="book_title", required=True)
    parser.add_argument("-l", "--language", dest="language", required=False, default="en-us")
    parser.add_argument("-y", "--yes", dest="no_ask", action="store_false")
    parser.add_argument("-o", "--overwrite", dest="overwrite", action="store_true")
    return parser.parse_args()


def main():
    args = get_args()
    process.Converter().process_book(args.book_title, args.language, ask=args.no_ask, overwrite=args.overwrite)


if __name__ == '__main__':
    main()
