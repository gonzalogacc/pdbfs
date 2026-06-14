.PHONY: run unmount clean

# Default target to run the launcher
run:
	@uv run launcher.py

# Unmount all directories specified in config.toml
unmount:
	@uv run python -c "import tomllib; \
	with open('config.toml', 'rb') as f: config = tomllib.load(f); \
	for db in config.get('databases', []): \
		import subprocess; \
		mount = db.get('mount_point'); \
		if mount: \
			print(f'Unmounting {mount}...'); \
			subprocess.run(['fusermount', '-u', mount])"

# Clean up any log files or temporary cache
clean:
	rm -f /tmp/logs.log
	rm -rf __pycache__ .mypy_cache
