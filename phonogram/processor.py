import os
import shutil
import datetime

import boto3
import re

import pydub

BASE_DIR = "./data"

ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
NUMBERS = [str(i) for i in range(0, 100)]


def get_text(book_fpath):
    print(f"Fetching text from {book_fpath}")
    with open(os.path.join(book_fpath, "text.ham")) as mf:
        return mf.read()


def merge_parts(book_fpath, log_interval=datetime.timedelta(seconds=10)):
    print("Merging audio")
    audio_fpath = os.path.join(book_fpath, "audio")
    parts = [
        os.path.join(audio_fpath, f)
        for f in os.listdir(audio_fpath)
        if os.path.isfile(os.path.join(audio_fpath, f))
    ]
    if not parts:
        print("No parts detected!")
        return
    print(f"{len(parts)} parts detected")
    sorted_parts = list(
        sorted(parts, key=lambda fname: int(os.path.split(fname)[-1].replace("part-", "").replace(".mp3", ""))))
    full_segment = linear_merge(sorted_parts, log_interval=log_interval)
    full_segment.export(os.path.join(book_fpath, "audio.mp3"), format="mp3")

    print("Done merging audio")


def linear_merge(sorted_parts, log_interval=datetime.timedelta(seconds=15)):
    full_segment = pydub.AudioSegment.from_mp3(sorted_parts.pop(0))
    last_log = datetime.datetime.now()
    while sorted_parts:
        full_segment = full_segment + pydub.AudioSegment.from_mp3(sorted_parts.pop(0))
        if (datetime.datetime.now() - last_log) > log_interval:
            print(f"{len(sorted_parts)} parts remaining")
            last_log = datetime.datetime.now()
    return full_segment


def heap_merge(sorted_parts, log_interval=datetime.timedelta(seconds=15)):
    last_log = datetime.datetime.now()

    def _heap_merge(parts):
        next_parts = list()
        for i in range(len(parts)):
            if i % 2 == 0 and i + 1 < len(parts):
                next_parts.append(parts[i] + parts[i + 1])
            elif i % 2 == 0:
                next_parts.append(parts[i])
        return next_parts
    cur_parts = list(sorted_parts)
    while len(cur_parts) > 1:
        cur_parts = _heap_merge(cur_parts)
        if (datetime.datetime.now() - last_log) > log_interval:
            print(f"{len(cur_parts)} parts remaining")
            last_log = datetime.datetime.now()
    return cur_parts[0]


class Line:

    def __init__(self, text, end_drift=500):
        self.text = text.rstrip().lstrip()
        self.end_drift = end_drift


class Pause:
    def __init__(self, length):
        self.length = length


class PartNamer:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.idx = 0

    def get(self):
        name = os.path.join(self.base_dir, f"part-{self.idx}.mp3")
        self.idx += 1
        return name


class Converter:

    def __init__(self, default_voice_id="Salli"):
        self.voice_id = default_voice_id

    def process_book(self, title, language, ask=True):
        book_fpath = os.path.abspath(os.path.join(BASE_DIR, title, language))
        text = get_text(book_fpath)
        num_chars = self.validate(text)
        cost = f"{num_chars} characters, ~${4*num_chars/1000000:.2f} USD"
        if ask:
            entry = input(f"{cost}, continue? (y/n): ")
            if entry.lower() != "y":
                print("Exiting")
                return
        else:
            print(f"{cost}")
        self.convert_to_audio_parts(book_fpath, text)
        merge_parts(book_fpath)
        print("Ding!")

    def validate(self, text):
        print("Validating")
        total_characters = 0
        for line_idx, audiopart in enumerate(self.get_next_line(text)):
            if isinstance(audiopart, Line):
                total_characters += len(audiopart.text)
        print("Done validation")
        return total_characters

    def convert_to_audio_parts(self, book_fpath, text):
        print("Converting to audio parts")
        output_dir = os.path.join(book_fpath, "audio")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=False)
        client = boto3.client("polly")

        part_namer = PartNamer(output_dir)

        for line_idx, audiopart in enumerate(self.get_next_line(text)):
            if isinstance(audiopart, Line):
                print(f"Processing line {line_idx} with voice id {self.voice_id}: {audiopart.text}")
                response = client.synthesize_speech(
                    VoiceId=self.voice_id,
                    Text=audiopart.text,
                    OutputFormat="mp3"
                )
                with open(part_namer.get(), "wb") as mf:
                    mf.write(response["AudioStream"].read())

                if audiopart.end_drift:
                    pydub.AudioSegment.silent(duration=audiopart.end_drift).export(part_namer.get(), format="mp3")
            elif isinstance(audiopart, Pause):
                pydub.AudioSegment.silent(duration=audiopart.length).export(part_namer.get(), format="mp3")
            else:
                print(f"Skipping part {line_idx}, unrecognized block type!")

        print("Done audio conversion")

    def get_next_line(self, text):
        lines = text.split("\n")
        block_parser = None
        for line in lines:
            if not line:
                pass
            elif re.match("<pause.*/>", line):
                yield Pause(int(re.search('length="(.*)"', line).groups()[0]))

            elif block_parser:
                if "</text>" in line:
                    block_parser.add_line(line.replace("</text>", ""))
                    for block_line in block_parser.parse():
                        yield Line(block_line)
                    block_parser = None
                else:
                    block_parser.add_line(line)
            elif re.match("<config.*/>", line):
                self.voice_id = re.search('voice_id="(.*)"', line).groups()[0]
            elif "<text>" in line:
                if "</text>" in line:
                    yield Line(line.replace("<text>", "").replace("</text>", ""), end_drift=0)
                else:
                    block_parser = BlockParser()
                    block_parser.add_line(line.replace("<text>", ""))
            else:
                raise RuntimeError(f"Unknown line: {line}")


class BlockParser:

    def __init__(self, max_length=2950):
        self._lines = list()
        self.punctuation = [".", "?", "!"]
        self.exceptions = ["mr", "mrs", "etc", "prof", "mme"]
        self.exceptions.extend([f" {letter}" for letter in ALPHABET])
        self.exceptions.extend([f" {number}" for number in NUMBERS])
        self.max_length = max_length

    def add_line(self, line):
        if line:
            self._lines.append(line)

    def is_punctuation(self, char, segment):
        return char in self.punctuation and not self.is_an_exception(segment)

    def is_too_long(self, start_idx, idx):
        return (idx - start_idx) > self.max_length

    def parse(self):
        text = " ".join(self._lines)
        start_idx = 0
        for idx, char in enumerate(text):
            if self.is_punctuation(char, text[start_idx:idx + 1]) or self.is_too_long(start_idx, idx):
                segment = text[start_idx:idx + 1]
                start_idx = idx + 1
                yield segment

        if text[start_idx:]:
            yield text[start_idx:]

    def is_an_exception(self, segment):
        for exception in self.exceptions:
            if len(segment) < len(exception) or segment[-len(exception)-1:-1].lower() == exception:
                return True
        return False
