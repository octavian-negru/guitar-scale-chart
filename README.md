Python translation of https://github.com/mizlan/guitar-scale-chart

## Usage

Run from this folder:

```bash
uv run main.py <key> <mode>
```

Install dependencies with `uv`:

```bash
uv sync
```

Or use the included `just` recipes:

```bash
just install
just chart E minor
just chart E minor --pdf
```

- `<key>`: root note (examples: `C`, `E`, `F#`, `Bb`)
- `<mode>` examples: `major`, `minor`, `major pentatonic`, `major penta`, `major-pentatonic`, `minor pentatonic`, `minor penta`, `minor-pentatonic`

### PDF export

Write a PDF instead of printing the ANSI chart:

```bash
uv run main.py E minor --pdf
just chart E minor --pdf
```

That creates an auto-formatted filename based on the request, for example `e-minor-fretboard.pdf` or `f-sharp-major-pentatonic-fretboard.pdf`.

You can also override the destination path:

```bash
uv run main.py Bb major --pdf --output charts/b-flat-major.pdf
```

## Examples

```bash
uv run main.py C major
uv run main.py E minor
uv run main.py E major pentatonic
uv run main.py A minor penta
uv run main.py E minor --pdf
```

Output of `uv run main.py E major pentatonic`:
```             
   E    ┌────────┬── F# ──┬────────┬── G# ──┬────────┬────────┬── B  ──┬────────┬── C# ──┬────────┬────────┬── E  ──┬────────┬── F# ──┬────────┬── G# ──┬
   B    ├────────┼── C# ──┼────────┼────────┼── E  ──┼────────┼── F# ──┼────────┼── G# ──┼────────┼────────┼── B  ──┼────────┼── C# ──┼────────┼────────┼
        ├── G# ──┼────────┼────────┼── B  ──┼────────┼── C# ──┼────────┼────────┼── E  ──┼────────┼── F# ──┼────────┼── G# ──┼────────┼────────┼── B  ──┼
        ├────────┼── E  ──┼────────┼── F# ──┼────────┼── G# ──┼────────┼────────┼── B  ──┼────────┼── C# ──┼────────┼────────┼── E  ──┼────────┼── F# ──┼
        ├────────┼── B  ──┼────────┼── C# ──┼────────┼────────┼── E  ──┼────────┼── F# ──┼────────┼── G# ──┼────────┼────────┼── B  ──┼────────┼── C# ──┼
   E    └────────┴── F# ──┴────────┴── G# ──┴────────┴────────┴── B  ──┴────────┴── C# ──┴────────┴────────┴── E  ──┴────────┴── F# ──┴────────┴── G# ──┴
                              ⬤                ⬤                ⬤                 ⬤                       ⬤ ⬤                       ⬤             
```
