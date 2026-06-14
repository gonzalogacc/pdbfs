.PHONY: run unmount clean

# Default target to run the launcher
run:
	@uv run launcher.py

# Unmount all directories specified in config.toml
unmount:
	@uv run unmount.py

# Clean up any log files or temporary cache
clean:
	rm -f /tmp/logs.log
	rm -rf __pycache__ .mypy_cache

ruff-fix:
	uv run ruff check --fix
