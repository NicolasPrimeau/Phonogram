import glob
import os
import subprocess
import sys

BASE_PATH = "./data/fables/"


def main():
    todo = list(glob.glob(os.path.join(BASE_PATH, "*")))
    while todo:
        book_title = "fables" + "/" + os.path.split(todo.pop(0))[-1]
        language = "fr-fr"
        print(f"Running for {book_title}")
        subprocess.run(
            ["bash", "./scripts/convert.sh", book_title, language, "-y"],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        print(f"{len(todo)} left")
        print()


if __name__ == '__main__':
    main()
