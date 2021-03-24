import argparse

from phonogram import processor


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--book-title", dest="book_title", required=True)
    parser.add_argument("-l", "--language", dest="language", required=True)
    return parser.parse_args()


def main():
    args = get_args()
    processor.Converter().process_book(args.book_title, args.language)


if __name__ == '__main__':
    main()
