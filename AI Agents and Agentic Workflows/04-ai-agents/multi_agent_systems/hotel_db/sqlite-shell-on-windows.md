# SQLite Shell on Windows

## Finding

Running `sqlite3` in the VS Code Windows terminal used this executable:

```text
C:\msys64\ucrt64\bin\sqlite3.exe
```

This MSYS2 build accepted and executed commands, but its prompt and typed input
were invisible because its terminal handling was incompatible with the Windows
terminal host. The database itself was valid and was not the cause.

Check which executable is active with:

```cmd
where sqlite3
```

## Recommended for this project: Python's SQLite shell

The virtual environment's Python installation already provides a working
interactive SQLite shell:

```cmd
python -m sqlite3 azerbaijan_hotels.db
```

Example:

```sql
SELECT * FROM hotels;
SELECT * FROM hotel_room_offers;
```

Use `.help` for available commands and `.quit` to exit. If the continuation
prompt (`...>`) appears unexpectedly, press `Ctrl+C` and re-enter the complete
statement at the `sqlite>` prompt.

This option is simplest for learning, inspecting tables, and running ordinary
SQL because it requires no additional installation. Its output is Python-style,
and it does not provide every convenience of the full SQLite command-line tool.

## Alternative: install SQLite separately from MSYS2

Install the official Windows SQLite command-line tools when you need the full
native shell, including its complete set of dot commands, formatting modes,
schema import, and database export features. After installation, update `PATH`
so `where sqlite3` shows the standalone Windows executable before the MSYS2
copy.

In short:

- Use `python -m sqlite3` for this project and routine SQL exploration.
- Install the official Windows SQLite CLI for regular database administration
  or when the full shell feature set is required.
