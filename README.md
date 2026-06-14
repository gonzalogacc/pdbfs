# DBFS: PostgreSQL as a Filesystem

DBFS mounts your PostgreSQL database as a local filesystem, turning SQL tables, columns, and rows into a browsable directory tree. Use standard CLI tools like `ls`, `grep`, and `cat` to explore your data.

## Features

- **Hierarchical Navigation**: Browse from tables down to individual row values.
- **Dynamic Queries**: Reading a "file" dynamically executes the SQL required to fetch the data.
- **ISO Date Handling**: Automatic conversion of date/timestamp columns to ISO 8601 filenames.
- **Everything is a File**: Pipe database rows directly into other CLI utilities.

## Directory Structure

- `/`: Lists all tables as `<name>.table/`
- `/<table.table>/`: Lists all columns as `<name>.column/`
- `/<table.table>/<column.column>/`: Lists unique values as `<value>.dbf`
- `/<table.table>/<column.column>/<value>.dbf`: A text file containing the full row data.

## Setup

1. **Database**:
   ```bash
   docker-compose up -d
   ```

2. **Dependencies**:
   ```bash
   pip install sqlalchemy psycopg2-binary fuse-python
   ```

3. **Mount**:
   ```bash
   mkdir mnt1
   python main.py mnt1
   ```

## Usage Examples

**List all tables:**
```bash
ls /mnt1
```

**Find a specific record by ID:**
```bash
cat /mnt1/users.table/id.column/42.dbf
```

**Search for a string across all rows in a column:**
```bash
grep "search_term" /mnt1/posts.table/content.column/*.dbf
```

## Unmounting

```bash
fusermount -u mnt1
```
# pdbfs
