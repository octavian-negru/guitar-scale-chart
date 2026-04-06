#!/usr/bin/env python3
import re
import sys

STRINGS = ["E", "A", "D", "G", "B", "E"]
SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLATS = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
MAJOR_STEPS = [2, 2, 1, 2, 2, 2, 1]
MINOR_STEPS = [2, 1, 2, 2, 1, 2, 2]
MAJOR_PENTATONIC_STEPS = [2, 2, 3, 2, 3]
MINOR_PENTATONIC_STEPS = [3, 2, 2, 3, 2]
NUM_FRETS = 16

FLAT_KEYS_MINOR = ["D", "G", "C", "F", "Bb", "Eb"]
FLAT_KEYS_MAJOR = ["F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"]
SHARP_KEYS_MINOR = ["A", "E", "B", "F#", "C#", "G#", "D#"]
SHARP_KEYS_MAJOR = ["C", "G", "D", "A", "E", "B", "F#", "C#"]

FRET_MARKER_LOCATIONS = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]

# one of "fret markers" or "fret numbers"
FRET_DISPLAY_STYLE = "fret markers"

# Wider rendering settings for a larger, easier-to-read chart.
SEGMENT_PAD = 2
NOTE_BLOCK_WIDTH = 4
FRET_STRIDE = SEGMENT_PAD + NOTE_BLOCK_WIDTH + SEGMENT_PAD + 1
BOLD_NOTES = True

COLOR_CONFIG = ["white", "red", "green", "yellow", "blue", "magenta", "cyan"]

ANSI_COLORS = {
    "white": "\033[37m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
}
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"


def first_index(seq, value):
    try:
        return seq.index(value)
    except ValueError:
        return -1


def colored(text, color_name):
    style = ANSI_BOLD if BOLD_NOTES else ""
    return f"{style}{ANSI_COLORS[color_name]}{text}{ANSI_RESET}"


def normalize_mode(mode_text):
    mode = re.sub(r"[^a-z]", "", mode_text.lower())
    mode_aliases = {
        "major": "major",
        "minor": "minor",
        "majorpentatonic": "major_pentatonic",
        "majorpenta": "major_pentatonic",
        "majpentatonic": "major_pentatonic",
        "majpenta": "major_pentatonic",
        "minorpentatonic": "minor_pentatonic",
        "minorpenta": "minor_pentatonic",
        "minpentatonic": "minor_pentatonic",
        "minpenta": "minor_pentatonic",
    }
    return mode_aliases.get(mode, mode)


def build_scale(key, mode):
    if mode in ("major", "major_pentatonic"):
        if key in FLAT_KEYS_MAJOR:
            chromatic = FLATS
            pos = first_index(FLATS, key)
            steps = MAJOR_STEPS if mode == "major" else MAJOR_PENTATONIC_STEPS
        elif key in SHARP_KEYS_MAJOR:
            chromatic = SHARPS
            pos = first_index(SHARPS, key)
            steps = MAJOR_STEPS if mode == "major" else MAJOR_PENTATONIC_STEPS
        else:
            raise ValueError("not found")
    elif mode in ("minor", "minor_pentatonic"):
        if key in FLAT_KEYS_MINOR:
            chromatic = FLATS
            pos = first_index(FLATS, key)
            steps = MINOR_STEPS if mode == "minor" else MINOR_PENTATONIC_STEPS
        elif key in SHARP_KEYS_MINOR:
            chromatic = SHARPS
            pos = first_index(SHARPS, key)
            steps = MINOR_STEPS if mode == "minor" else MINOR_PENTATONIC_STEPS
        else:
            raise ValueError("not found")
    else:
        raise ValueError("not found")

    scale = []
    for step in steps:
        scale.append(chromatic[pos])
        pos = (pos + step) % len(chromatic)

    return chromatic, scale


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <key> <major|minor|major pentatonic|minor pentatonic>")
        sys.exit(1)

    key = sys.argv[1]
    mode = normalize_mode(" ".join(sys.argv[2:]))

    try:
        chromatic, scale = build_scale(key, mode)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    strings_display_order = list(reversed(STRINGS))

    if FRET_DISPLAY_STYLE == "fret numbers":
        print(" ", end="")
        for n in range(NUM_FRETS + 1):
            print(f"{n:^{FRET_STRIDE}}", end="")
        print()

    for string_index, string_note in enumerate(strings_display_order):
        pos = first_index(chromatic, string_note)
        for fret in range(NUM_FRETS + 1):
            note = chromatic[(pos + fret) % len(chromatic)]
            degree = first_index(scale, note)

            if fret == 0:
                print(" " * SEGMENT_PAD, end="")
            else:
                print("─" * SEGMENT_PAD, end="")

            if degree != -1:
                print(colored(note.center(NOTE_BLOCK_WIDTH), COLOR_CONFIG[degree]), end="")
            else:
                if fret == 0:
                    print(" " * NOTE_BLOCK_WIDTH, end="")
                else:
                    print("─" * NOTE_BLOCK_WIDTH, end="")

            if fret == 0:
                print(" " * SEGMENT_PAD, end="")
            else:
                print("─" * SEGMENT_PAD, end="")

            if fret == 0:
                if string_index == 0:
                    print("┌", end="")
                elif string_index == 5:
                    print("└", end="")
                else:
                    print("├", end="")
            else:
                if string_index == 0:
                    print("┬", end="")
                elif string_index == 5:
                    print("┴", end="")
                else:
                    print("┼", end="")
        print()

    if FRET_DISPLAY_STYLE == "fret markers":
        print(" ", end="")
        for fret_num in range(NUM_FRETS + 1):
            if fret_num in (12, 24):
                print(f"{'⬤ ⬤':^{FRET_STRIDE}}", end="")
            elif fret_num in FRET_MARKER_LOCATIONS:
                print(f"{'⬤':^{FRET_STRIDE}}", end="")
            else:
                print(f"{'':^{FRET_STRIDE}}", end="")
        print()


if __name__ == "__main__":
    main()
