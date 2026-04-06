install:
	uv sync

chart *args:
	uv run main.py {{args}}
