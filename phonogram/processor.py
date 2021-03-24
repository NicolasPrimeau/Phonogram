import os

import boto3
import re

import pydub

BASE_DIR = "./data"


def get_text(book_fpath):
    print(f"Fetching text from {book_fpath}")
    with open(os.path.join(book_fpath, "text.ham")) as mf:
        return mf.read()


def merge_parts(book_fpath):
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
    full_segment = sum([
        pydub.AudioSegment.from_mp3(fname) for fname in
        sorted(parts, key=lambda fname: int(os.path.split(fname)[-1].replace("part-", "").replace(".mp3", "")))
    ])
    full_segment.export(os.path.join(book_fpath, "audio.mp3"), format="mp3")
    print("Done merging audio")


class Line:

    def __init__(self, text, end_drift=500):
        self.text = text
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

    def process_book(self, title, language):
        book_fpath = os.path.abspath(os.path.join(BASE_DIR, title, language))
        text = get_text(book_fpath)
        entry = input(f"{len(text)} characters, ~${4*len(text)/1000000:.2f} USD, continue? (y/n): ")
        if entry.lower() != "y":
            print("Exiting")
            return
        self.convert_to_audio_parts(book_fpath, text)
        merge_parts(book_fpath)
        print("Ding!")

    def convert_to_audio_parts(self, book_fpath, text):
        print("Converting to audio parts")
        output_dir = os.path.join(book_fpath, "audio")
        os.makedirs(output_dir, exist_ok=True)
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


class BlockParser:

    def __init__(self):
        self._lines = list()

    def add_line(self, line):
        if line:
            self._lines.append(line)

    def parse(self):
        text = " ".join(self._lines)
        for line in text.split("."):
            yield line
