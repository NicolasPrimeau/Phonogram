import csv
from abc import ABC, abstractmethod


DATA_FILE = "./utils/substitutions.csv"


def refine_lines_it(lines, refiner):
    for line in lines:
        for replaced in refiner.replace(line):
            yield replaced


class Refiner(ABC):
    @abstractmethod
    def replace(self, line):
        pass


class SubstituteCodes(Refiner):

    def __init__(self):
        self._map = dict()
        self._load_codes()

    def _load_codes(self):
        with open(DATA_FILE) as csvfile:
            reader = csv.DictReader(csvfile)
            self._map = {
                entry["from"]: entry["to"] for entry in reader
            }

    def replace(self, line):
        for code, replacement in self._map.items():
            line = line.replace(code, replacement)
        yield line


class ChapterMarkup(Refiner):
    def replace(self, line):
        if line.lower().startswith("chapter") and len(line.split(" ")) == 2:
            line = line.replace(".", "").capitalize()
            yield f"<text>{line}</text>"
            yield f"<pause length=\"1000\"/>"
            yield "<text>"
        else:
            yield line