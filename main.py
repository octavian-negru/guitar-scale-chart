#!/usr/bin/env python3
import argparse
import os
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
TERMINAL_SCALE = max(1.0, float(os.environ.get("TERMINAL_SCALE", "1.3")))
SEGMENT_PAD = max(1, int(round(2 * TERMINAL_SCALE)))
NOTE_BLOCK_WIDTH = max(2, int(round(4 * TERMINAL_SCALE)))
STRING_SPACER_ROWS = max(0, int(round(TERMINAL_SCALE)) - 1)
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

ENHARMONIC_EQUIVALENTS = {
    "B#": "C",
    "E#": "F",
    "Cb": "B",
    "Fb": "E",
}

PDF_NOTE_COLORS = [
    "#D1D5DB",
    "#C96B5C",
    "#5E9D76",
    "#B89A4A",
    "#5F89C9",
    "#9A70B5",
    "#4E98A0",
]


def first_index(seq, value):
    try:
        return seq.index(value)
    except ValueError:
        return -1


def colored(text, color_name):
    style = ANSI_BOLD if BOLD_NOTES else ""
    return f"{style}{ANSI_COLORS[color_name]}{text}{ANSI_RESET}"


def key_filename_fragment(key):
    fragment = key.strip().lower()
    fragment = fragment.replace("#", "-sharp")

    if len(fragment) > 1 and fragment.endswith("b"):
        fragment = f"{fragment[:-1]}-flat"

    return fragment


def output_filename_for_request(key, mode):
    mode_fragment = mode.replace("_", "-")
    return f"{key_filename_fragment(key)}-{mode_fragment}-fretboard.pdf"


def caller_working_directory():
    for var_name in ("CALLER_PWD", "JUST_WORKING_DIRECTORY", "INIT_CWD", "PWD"):
        value = os.environ.get(var_name)
        if value and os.path.isdir(value):
            return value

    return os.getcwd()


def mode_title(mode):
    return mode.replace("_", " ").title()


def parse_key_input(key_text):
    key = key_text.strip()
    match = re.fullmatch(r"([A-Ga-g])([#b]?)", key)

    if not match:
        raise ValueError("invalid key")

    letter, accidental = match.groups()
    is_minor_hint = letter.islower()
    return f"{letter.upper()}{accidental}", is_minor_hint


def normalize_mode(mode_text):
    mode = re.sub(r"[^a-z]", "", mode_text.lower())
    mode_aliases = {
        "major": "major",
        "minor": "minor",
        "pentatonic": "pentatonic",
        "penta": "pentatonic",
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
    preferred_chromatic = None

    if "#" in key:
        preferred_chromatic = SHARPS
    elif "b" in key:
        preferred_chromatic = FLATS

    key_for_lookup = ENHARMONIC_EQUIVALENTS.get(key, key)

    if preferred_chromatic is None:
        if mode in ("major", "major_pentatonic"):
            if key_for_lookup in FLAT_KEYS_MAJOR:
                preferred_chromatic = FLATS
            else:
                preferred_chromatic = SHARPS
        else:
            if key_for_lookup in FLAT_KEYS_MINOR:
                preferred_chromatic = FLATS
            else:
                preferred_chromatic = SHARPS

    fallback_chromatic = FLATS if preferred_chromatic == SHARPS else SHARPS

    if mode in ("major", "major_pentatonic"):
        steps = MAJOR_STEPS if mode == "major" else MAJOR_PENTATONIC_STEPS
    elif mode in ("minor", "minor_pentatonic"):
        steps = MINOR_STEPS if mode == "minor" else MINOR_PENTATONIC_STEPS
    else:
        raise ValueError("not found")

    pos = first_index(preferred_chromatic, key_for_lookup)
    if pos != -1:
        chromatic = preferred_chromatic
    else:
        pos = first_index(fallback_chromatic, key_for_lookup)
        if pos == -1:
            raise ValueError("not found")
        chromatic = fallback_chromatic

    scale = []
    for step in steps:
        scale.append(chromatic[pos])
        pos = (pos + step) % len(chromatic)

    return chromatic, scale


def build_fretboard(chromatic, scale):
    fretboard = []
    strings_display_order = list(reversed(STRINGS))

    for string_note in strings_display_order:
        pos = first_index(chromatic, string_note)
        frets = []

        for fret in range(NUM_FRETS + 1):
            note = chromatic[(pos + fret) % len(chromatic)]
            frets.append(
                {
                    "fret": fret,
                    "note": note,
                    "degree": first_index(scale, note),
                }
            )

        fretboard.append({"string_note": string_note, "frets": frets})

    return fretboard


def render_terminal_lines(fretboard):
    lines = []

    if FRET_DISPLAY_STYLE == "fret numbers":
        parts = [" "]
        for fret in range(NUM_FRETS + 1):
            parts.append(f"{fret:^{FRET_STRIDE}}")
        lines.append("".join(parts))

    for string_index, row in enumerate(fretboard):
        parts = []
        for cell in row["frets"]:
            fret = cell["fret"]
            degree = cell["degree"]
            note = cell["note"]

            parts.append(" " * SEGMENT_PAD if fret == 0 else "─" * SEGMENT_PAD)

            if degree != -1:
                parts.append(colored(note.center(NOTE_BLOCK_WIDTH), COLOR_CONFIG[degree]))
            elif fret == 0:
                parts.append(" " * NOTE_BLOCK_WIDTH)
            else:
                parts.append("─" * NOTE_BLOCK_WIDTH)

            parts.append(" " * SEGMENT_PAD if fret == 0 else "─" * SEGMENT_PAD)

            if fret == 0:
                if string_index == 0:
                    parts.append("┌")
                elif string_index == len(fretboard) - 1:
                    parts.append("└")
                else:
                    parts.append("├")
            else:
                if string_index == 0:
                    parts.append("┬")
                elif string_index == len(fretboard) - 1:
                    parts.append("┴")
                else:
                    parts.append("┼")

        lines.append("".join(parts))

        for _ in range(STRING_SPACER_ROWS):
            spacer_parts = []
            for cell in row["frets"]:
                fret = cell["fret"]
                spacer_parts.append(" " * SEGMENT_PAD)
                spacer_parts.append(" " * NOTE_BLOCK_WIDTH)
                spacer_parts.append(" " * SEGMENT_PAD)
                spacer_parts.append("│" if fret == 0 else "┆")
            lines.append("".join(spacer_parts))

    if FRET_DISPLAY_STYLE == "fret markers":
        parts = [" "]
        for fret_num in range(NUM_FRETS + 1):
            if fret_num in (12, 24):
                marker = "⬤ ⬤"
            elif fret_num in FRET_MARKER_LOCATIONS:
                marker = "⬤"
            else:
                marker = ""
            parts.append(f"{marker:^{FRET_STRIDE}}")
        lines.append("".join(parts))

    return lines


def write_pdf(output_path, key, mode, fretboard):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import legal, landscape
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError("PDF export requires reportlab. Install dependencies with: uv sync") from exc

    page_width, _ = landscape(legal)

    cell_height = 40
    top_reserved = 86
    bottom_reserved = 24
    marker_reserved = 26 if FRET_DISPLAY_STYLE == "fret markers" else 0
    page_height = top_reserved + (cell_height * len(fretboard)) + marker_reserved + bottom_reserved

    pdf = canvas.Canvas(output_path, pagesize=(page_width, page_height))

    margin_x = 36
    title_y = page_height - 34
    grid_top = page_height - 86
    label_width = 44
    cell_width = (page_width - (2 * margin_x) - label_width) / (NUM_FRETS + 1)
    grid_left = margin_x + label_width
    grid_bottom = grid_top - (cell_height * len(fretboard))

    pdf.setTitle(f"{key} {mode_title(mode)} Fretboard")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(margin_x, title_y, f"{key} {mode_title(mode)} Fretboard")

    pdf.setFont("Helvetica", 10)
    for fret in range(NUM_FRETS + 1):
        x = grid_left + (fret * cell_width)
        pdf.drawCentredString(x + (cell_width / 2), grid_top + 12, str(fret))

    for row_index, row in enumerate(fretboard):
        y = grid_top - ((row_index + 1) * cell_height)
        mid_y = y + (cell_height / 2)

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawRightString(grid_left - 10, mid_y - 4, row["string_note"])

        pdf.setStrokeColor(colors.HexColor("#111827"))
        pdf.line(grid_left, mid_y, grid_left + ((NUM_FRETS + 1) * cell_width), mid_y)

        for cell in row["frets"]:
            x = grid_left + (cell["fret"] * cell_width)

            pdf.setLineWidth(2 if cell["fret"] == 0 else 1)
            pdf.line(x, y, x, y + cell_height)

            if cell["fret"] == NUM_FRETS:
                pdf.line(x + cell_width, y, x + cell_width, y + cell_height)

            if cell["degree"] == -1:
                continue

            note_color = colors.HexColor(PDF_NOTE_COLORS[cell["degree"]])
            center_x = x + (cell_width / 2)
            radius = min(cell_width, cell_height) * 0.38

            pdf.setLineWidth(1.4)
            pdf.setStrokeColor(note_color)
            pdf.setFillColor(colors.HexColor("#FCFCFB"))
            pdf.circle(center_x, mid_y, radius, stroke=1, fill=1)
            pdf.setFillColor(colors.HexColor("#111827"))
            pdf.setFont("Helvetica-Bold", 12 if len(cell["note"]) == 1 else 11)
            pdf.drawCentredString(center_x, mid_y - 4, cell["note"])

    if FRET_DISPLAY_STYLE == "fret markers":
        marker_y = grid_bottom - 18
        pdf.setFillColor(colors.HexColor("#4B5563"))

        for fret_num in range(NUM_FRETS + 1):
            center_x = grid_left + (fret_num * cell_width) + (cell_width / 2)

            if fret_num in (12, 24):
                offset = min(cell_width * 0.12, 6)
                pdf.circle(center_x - offset, marker_y + 5, 3.2, stroke=0, fill=1)
                pdf.circle(center_x + offset, marker_y + 5, 3.2, stroke=0, fill=1)
            elif fret_num in FRET_MARKER_LOCATIONS:
                pdf.circle(center_x, marker_y + 5, 3.2, stroke=0, fill=1)

    pdf.save()


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Render a guitar fretboard chart for a key and mode."
    )
    parser.add_argument(
        "key",
        help=(
            "Root note, for example C, E, F#, or Bb. "
            "If mode is omitted, uppercase defaults to major and lowercase defaults to minor."
        ),
    )
    parser.add_argument("mode", nargs="*", help="Scale mode, for example minor or major pentatonic")
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Write the fretboard chart to a PDF file instead of stdout.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Path for the generated PDF file. Relative paths are resolved from the caller's "
            "working directory."
        ),
    )
    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])

    try:
        key, is_minor_hint = parse_key_input(args.key)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    if args.mode:
        mode = normalize_mode(" ".join(args.mode))
    else:
        mode = "minor" if is_minor_hint else "major"

    if mode == "pentatonic":
        mode = "minor_pentatonic" if is_minor_hint else "major_pentatonic"

    try:
        chromatic, scale = build_scale(key, mode)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    fretboard = build_fretboard(chromatic, scale)

    if args.output and not args.pdf:
        args.pdf = True

    if args.pdf:
        output_path = args.output or output_filename_for_request(key, mode)

        if not output_path.lower().endswith(".pdf"):
            output_path = f"{output_path}.pdf"

        if not os.path.isabs(output_path):
            output_path = os.path.join(caller_working_directory(), output_path)

        try:
            write_pdf(output_path, key, mode, fretboard)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

        print(output_path)
        return

    for line in render_terminal_lines(fretboard):
        print(line)


if __name__ == "__main__":
    main()
