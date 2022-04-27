import os
import pathlib
import datetime
import shutil

import backoff as backoff
import boto3
import re

import pydub

from phonogram import utils

BASE_DIR = "./data"

ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
NUMBERS = [str(i) for i in range(0, 100)]

POLLY_CLIENT = boto3.client("polly")


def get_text(book_fpath):
    utils.log(f"Fetching text from {book_fpath}")
    with open(os.path.join(book_fpath, "text.ham")) as mf:
        return mf.read()


def merge_parts(book_fpath, log_interval=datetime.timedelta(seconds=10)):
    utils.log("Merging audio")
    audio_fpath = os.path.join(book_fpath, "audio")
    parts = [
        os.path.join(audio_fpath, f)
        for f in os.listdir(audio_fpath)
        if os.path.isfile(os.path.join(audio_fpath, f))
    ]
    if not parts:
        utils.log("No parts detected!")
        return
    utils.log(f"{len(parts)} parts detected")

    utils.log("Converting to audio segments")
    audio_parts = convert_to_audio_segment(parts, log_interval=log_interval)
    utils.log("Done converting to audio segments")
    utils.log("Merging audio parts")
    full_segment = linear_merge(audio_parts, log_interval=log_interval)
    utils.log("Done merging audio parts")
    utils.log("Saving audio")
    full_segment.export(os.path.join(book_fpath, "audio.mp3"), format="mp3")
    utils.log("Done saving audio")


def convert_to_audio_segment(parts, log_interval=datetime.timedelta(seconds=15)):
    sorted_parts = list(
        sorted(parts, key=lambda fname: int(os.path.split(fname)[-1].replace("part-", "").replace(".mp3", ""))))
    last_log = datetime.datetime.now()
    audio_parts = list()
    for cnt, part in enumerate(sorted_parts):
        audio_parts.append(pydub.AudioSegment.from_mp3(part))
        if (datetime.datetime.now() - last_log) > log_interval:
            utils.log(f"Converted part {cnt} of {len(sorted_parts)} into audio segment")
            last_log = datetime.datetime.now()
    return audio_parts


def linear_merge(sorted_parts, log_interval=datetime.timedelta(seconds=15)):
    full_segment = sorted_parts.pop(0)
    last_log = datetime.datetime.now()
    while sorted_parts:
        full_segment = full_segment +sorted_parts.pop(0)
        if (datetime.datetime.now() - last_log) > log_interval:
            utils.log(f"{len(sorted_parts)} parts remaining")
            last_log = datetime.datetime.now()
    return full_segment


def heap_merge(sorted_parts, log_interval=datetime.timedelta(seconds=15)):
    last_log = datetime.datetime.now()

    def _heap_merge(parts):
        last_log = datetime.datetime.now()
        next_parts = list()
        for i in range(len(parts)):
            if (datetime.datetime.now() - last_log) > log_interval:
                utils.log(f"Merging {i} and {i + 1}")
                last_log = datetime.datetime.now()

            if i % 2 == 0 and i + 1 < len(parts):
                next_parts.append(parts[i] + parts[i + 1])
            elif i % 2 == 0:
                next_parts.append(parts[i])

        return next_parts

    cur_parts = list(sorted_parts)
    while len(cur_parts) > 1:
        cur_parts = _heap_merge(cur_parts)
        if (datetime.datetime.now() - last_log) > log_interval:
            utils.log(f"{len(cur_parts)} parts remaining")
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


@backoff.on_exception(backoff.expo, Exception, max_tries=10)
def synthesize(voice_id, text):
    return POLLY_CLIENT.synthesize_speech(
        VoiceId=voice_id,
        Text=text,
        OutputFormat="mp3"
    )["AudioStream"].read()


class Converter:

    def __init__(self, default_voice_id="Salli"):
        self.voice_id = default_voice_id

    def process_book(self, title, language, ask=True, overwrite=False):
        book_fpath = os.path.abspath(os.path.join(BASE_DIR, title, language))
        text = get_text(book_fpath)
        num_chars = self.validate(text)
        cost = f"{num_chars} characters, ~${4*num_chars/1000000:.2f} USD"
        if ask:
            entry = input(f"{cost}, continue? (y/n): ")
            if entry.lower() != "y":
                utils.log("Exiting")
                return
        else:
            utils.log(f"{cost}")
        self.convert_to_audio_parts(book_fpath, text, overwrite)
        merge_parts(book_fpath)
        utils.log("Ding!")

    def validate(self, text):
        utils.log("Validating")
        total_characters = 0
        for line_idx, audiopart in enumerate(self.get_next_line(text)):
            if isinstance(audiopart, Line):
                total_characters += len(audiopart.text)
        utils.log("Done validation")
        return total_characters

    def convert_to_audio_parts(self, book_fpath, text, overwrite=False):
        utils.log("Converting to audio parts")
        output_dir = os.path.join(book_fpath, "audio")

        if True and os.path.exists(output_dir):
           shutil.rmtree(output_dir)
        try:
            os.makedirs(output_dir, exist_ok=False)
        except:
            pass

        part_namer = PartNamer(output_dir)

        for line_idx, audiopart in enumerate(self.get_next_line(text)):
            part_fp = pathlib.Path(part_namer.get())
            if isinstance(audiopart, Line):
                utils.log(f"Processing line {line_idx} with voice id {self.voice_id}: {audiopart.text}")
                data = synthesize(self.voice_id, audiopart.text)
                with part_fp.open("wb") as mf:
                    mf.write(data)

                if audiopart.end_drift:
                    pydub.AudioSegment.silent(duration=audiopart.end_drift).export(part_namer.get(), format="mp3")
            elif isinstance(audiopart, Pause):
                pydub.AudioSegment.silent(duration=audiopart.length).export(part_namer.get(), format="mp3")
            else:
                raise RuntimeError("Unknown block type!")

        utils.log("Done audio conversion")

    def get_next_line(self, text):
        lines = text.split("\n")
        block_parser = None
        for number, line in enumerate(lines):
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
                self.voice_id = re.search('voice_id="([A-Za-z]+)"', line).groups()[0]
            elif "<text>" in line:
                if "</text>" in line:
                    yield Line(line.replace("<text>", "").replace("</text>", ""), end_drift=0)
                else:
                    block_parser = BlockParser()
                    block_parser.add_line(line.replace("<text>", ""))
            else:
                raise RuntimeError(f"Unknown line {number}: {line}")


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
