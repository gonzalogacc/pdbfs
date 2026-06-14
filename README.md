# DBFS: PostgreSQL as a Filesystem

DBFS mounts your PostgreSQL database as a local filesystem, turning SQL tables, columns, and rows into a browsable directory tree. Use standard CLI tools like `ls`, `grep`, and `cat` to explore your data.

## Features

- **Hierarchical Navigation**: Browse from tables down to individual row values.
- **Dynamic Queries**: Reading a "file" dynamically executes the SQL required to fetch the data.
- **ISO Date Handling**: Automatic conversion of date/timestamp columns to ISO 8601 filenames.
- **Everything is a File**: Pipe database rows directly into other CLI utilities.
- **Multi-Mount Support**: Mount multiple databases simultaneously via a single configuration.

## Directory Structure

- `/`: Lists all tables as `<name>.table/`
- `/<table.table>/`: Lists all columns as `<name>.column/`
- `/<table.table>/<column.column>/`: Lists unique values as `<value>.dbf`
- `/<table.table>/<column.column>/<value>.dbf`: A text file containing the full row data.

## Prerequisites

- **Python 3.12+**
- **System Dependencies**: You must have FUSE and its development headers installed (e.g., `libfuse-dev` and `fuse` on Ubuntu/Debian).
- **PostgreSQL**: A running instance (a `docker-compose.yaml` is provided).

## Setup

1. **Database**:
   ```bash
   docker-compose up -d
   ```

2. **Dependencies**:
   Using `uv` (recommended):
   ```bash
   uv sync
   ```
   *Note: This will install SQLAlchemy, Psycopg2, and fuse-python.*

3. **Configuration**:
   Edit `config.toml` to define your database connections and mount points:
   ```toml
   [[databases]]
   name = "local_test"
   user = "user"
   password = "pass"
   host = "localhost"
   port = 5432
   db_name = "testdb"
   mount_point = "mnt1"
   ```

## Usage

### Mounting via Makefile (Recommended)
The launcher tests every connection before spawning background mount processes using `uv run`.
```bash
make run
```

### Manual Mounting
You can also mount a single database directly:
```bash
uv run main.py mnt1 --db-user user --db-pass pass --db-host localhost --db-name testdb
```

### Unmounting
To unmount everything defined in `config.toml`:
```bash
make unmount
```

To unmount a specific directory manually:
```bash
fusermount -u mnt1
```

## Examples

**Browse tables:**
```bash
ls /mnt1
```

**View a specific row by a column value:**
```bash
cat /mnt1/users.table/email.column/admin@example.com.dbf
```

**Search across a column with grep:**
```bash
grep "important_info" /mnt1/logs.table/message.column/*.dbf
```

## Maintenance

To remove logs and clear cache:
```bash
make clean
```
