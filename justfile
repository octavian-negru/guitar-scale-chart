install:
	uv sync

chart *args:
	CALLER_PWD="{{invocation_directory()}}" uv run main.py {{args}}
