Python translation of https://github.com/mizlan/guitar-scale-chart

## Usage

Run from this folder:

```bash
python3 main.py <key> <mode>
```

- `<key>`: root note (examples: `C`, `E`, `F#`, `Bb`)
- `<mode>` examples: `major`, `minor`, `major pentatonic`, `major penta`, `major-pentatonic`, `minor pentatonic`, `minor penta`, `minor-pentatonic`

## Examples

```bash
python3 main.py C major
python3 main.py E minor
python3 main.py E major pentatonic
python3 main.py A minor penta
```

Output of `python3 main.py E major pentatonic`:
```             
   E    ┌────────┬── F# ──┬────────┬── G# ──┬────────┬────────┬── B  ──┬────────┬── C# ──┬────────┬────────┬── E  ──┬────────┬── F# ──┬────────┬── G# ──┬
   B    ├────────┼── C# ──┼────────┼────────┼── E  ──┼────────┼── F# ──┼────────┼── G# ──┼────────┼────────┼── B  ──┼────────┼── C# ──┼────────┼────────┼
        ├── G# ──┼────────┼────────┼── B  ──┼────────┼── C# ──┼────────┼────────┼── E  ──┼────────┼── F# ──┼────────┼── G# ──┼────────┼────────┼── B  ──┼
        ├────────┼── E  ──┼────────┼── F# ──┼────────┼── G# ──┼────────┼────────┼── B  ──┼────────┼── C# ──┼────────┼────────┼── E  ──┼────────┼── F# ──┼
        ├────────┼── B  ──┼────────┼── C# ──┼────────┼────────┼── E  ──┼────────┼── F# ──┼────────┼── G# ──┼────────┼────────┼── B  ──┼────────┼── C# ──┼
   E    └────────┴── F# ──┴────────┴── G# ──┴────────┴────────┴── B  ──┴────────┴── C# ──┴────────┴────────┴── E  ──┴────────┴── F# ──┴────────┴── G# ──┴
                              ⬤                ⬤                ⬤                 ⬤                       ⬤ ⬤                       ⬤             
```
