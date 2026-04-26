"""
Database and data persistence tools
"""

import json
import sqlite3
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager
from smolagents import tool


@contextmanager
def get_db_connection(db_path: str):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@tool
def create_database(db_path: str) -> str:
    """Create a new SQLite database.

    Args:
        db_path: Path where the SQLite database file should be created.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with get_db_connection(db_path) as conn:
        conn.execute("VACUUM")

    return f"Database created at {db_path}"


@tool
def create_table(db_path: str, table_name: str, columns: Dict[str, str],
                 primary_key: str = None) -> str:
    """Create a table in the database.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to create.
        columns: Dictionary mapping column names to SQLite data types.
        primary_key: Optional name of the auto-increment primary key column.
    """
    column_defs = [f"{name} {dtype}" for name, dtype in columns.items()]

    if primary_key:
        column_defs.insert(0, f"{primary_key} INTEGER PRIMARY KEY AUTOINCREMENT")

    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"

    with get_db_connection(db_path) as conn:
        conn.execute(create_sql)
        conn.commit()

    return f"Table '{table_name}' created"


@tool
def insert_record(db_path: str, table_name: str, data: Dict[str, Any]) -> str:
    """Insert a record into a table.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to insert into.
        data: Dictionary of column names to values for the new record.
    """
    columns = list(data.keys())
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)

    insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    with get_db_connection(db_path) as conn:
        conn.execute(insert_sql, list(data.values()))
        conn.commit()
        last_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    return f"Record inserted with ID {last_id}"


@tool
def insert_many(db_path: str, table_name: str, records: List[Dict[str, Any]]) -> str:
    """Insert multiple records into a table.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to insert into.
        records: List of dictionaries, each representing a record to insert.
    """
    if not records:
        return "No records to insert"

    columns = list(records[0].keys())
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)

    insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    with get_db_connection(db_path) as conn:
        values = [[record.get(col) for col in columns] for record in records]
        conn.executemany(insert_sql, values)
        conn.commit()
        count = conn.execute("SELECT changes()").fetchone()[0]

    return f"Inserted {count} records"


@tool
def select_records(db_path: str, table_name: str, where: str = None,
                   params: Tuple = None, order_by: str = None,
                   limit: int = None) -> List[Dict[str, Any]]:
    """Select records from a table.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to query.
        where: Optional SQL WHERE clause (without the WHERE keyword).
        params: Optional tuple of parameters for the WHERE clause.
        order_by: Optional SQL ORDER BY expression.
        limit: Optional maximum number of rows to return.
    """
    query = f"SELECT * FROM {table_name}"

    if where:
        query += f" WHERE {where}"

    if order_by:
        query += f" ORDER BY {order_by}"

    if limit:
        query += f" LIMIT {limit}"

    with get_db_connection(db_path) as conn:
        if params:
            cursor = conn.execute(query, params)
        else:
            cursor = conn.execute(query)

        return [dict(row) for row in cursor.fetchall()]


@tool
def update_records(db_path: str, table_name: str, data: Dict[str, Any],
                   where: str, params: Tuple = None) -> str:
    """Update records in a table.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to update.
        data: Dictionary of column names to new values.
        where: SQL WHERE clause (without the WHERE keyword).
        params: Optional tuple of parameters for the WHERE clause.
    """
    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {where}"

    all_params = list(data.values()) + list(params) if params else list(data.values())

    with get_db_connection(db_path) as conn:
        cursor = conn.execute(update_sql, all_params)
        conn.commit()
        count = cursor.rowcount

    return f"Updated {count} records"


@tool
def delete_records(db_path: str, table_name: str, where: str,
                   params: Tuple = None) -> str:
    """Delete records from a table.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to delete from.
        where: SQL WHERE clause (without the WHERE keyword).
        params: Optional tuple of parameters for the WHERE clause.
    """
    delete_sql = f"DELETE FROM {table_name} WHERE {where}"

    with get_db_connection(db_path) as conn:
        cursor = conn.execute(delete_sql, params)
        conn.commit()
        count = cursor.rowcount

    return f"Deleted {count} records"


@tool
def get_table_schema(db_path: str, table_name: str) -> List[Dict[str, Any]]:
    """Get the schema of a table.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to inspect.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        return [{
            'cid': col[0],
            'name': col[1],
            'type': col[2],
            'notnull': bool(col[3]),
            'default': col[4],
            'pk': bool(col[5])
        } for col in columns]


@tool
def list_tables(db_path: str) -> List[str]:
    """List all tables in the database.

    Args:
        db_path: Path to the SQLite database file.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND NOT name LIKE 'sqlite_%'"
        )
        return [row[0] for row in cursor.fetchall()]


@tool
def drop_table(db_path: str, table_name: str) -> str:
    """Drop a table from the database.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to drop.
    """
    with get_db_connection(db_path) as conn:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()

    return f"Table '{table_name}' dropped"


@tool
def execute_query(db_path: str, query: str, params: Tuple = None) -> Any:
    """Execute a raw SQL query.

    Args:
        db_path: Path to the SQLite database file.
        query: The SQL query string to execute.
        params: Optional tuple of parameters to bind to the query.
    """
    with get_db_connection(db_path) as conn:
        if params:
            cursor = conn.execute(query, params)
        else:
            cursor = conn.execute(query)

        conn.commit()

        if query.strip().upper().startswith('SELECT'):
            return [dict(row) for row in cursor.fetchall()]

        return {'rows_affected': cursor.rowcount}


@tool
def export_to_csv(db_path: str, table_name: str, output_path: str) -> str:
    """Export a table to CSV.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to export.
        output_path: File path where the CSV should be written.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            return "Table is empty"

        columns = [description[0] for description in cursor.description]

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))

    return f"Exported {len(rows)} rows to {output_path}"


@tool
def import_from_csv(db_path: str, table_name: str, csv_path: str) -> str:
    """Import data from CSV into a table.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to import data into.
        csv_path: Path to the CSV file to import.
    """
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return "CSV file is empty"

    columns = list(rows[0].keys())
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)

    insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    with get_db_connection(db_path) as conn:
        values = [[row.get(col) for col in columns] for row in rows]
        conn.executemany(insert_sql, values)
        conn.commit()

    return f"Imported {len(rows)} rows from {csv_path}"


@tool
def backup_database(db_path: str, backup_path: str) -> str:
    """Create a backup of the database.

    Args:
        db_path: Path to the source SQLite database file.
        backup_path: Destination path for the backup file.
    """
    import shutil

    Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(db_path, backup_path)

    return f"Database backed up to {backup_path}"


@tool
def get_database_stats(db_path: str) -> Dict[str, Any]:
    """Get statistics about the database.

    Args:
        db_path: Path to the SQLite database file.
    """
    with get_db_connection(db_path) as conn:
        tables = list_tables(db_path)
        stats = {
            'tables': {},
            'total_size': os.path.getsize(db_path),
            'last_modified': datetime.fromtimestamp(
                os.path.getmtime(db_path)
            ).isoformat()
        }

        for table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            stats['tables'][table] = {'row_count': count}

        return stats


@tool
def add_column(db_path: str, table_name: str, column_name: str,
               column_type: str, default: Any = None) -> str:
    """Add a column to an existing table.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to alter.
        column_name: Name of the new column.
        column_type: SQLite data type for the new column.
        default: Optional default value for the new column.
    """
    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"

    if default is not None:
        if isinstance(default, str):
            alter_sql += f" DEFAULT '{default}'"
        else:
            alter_sql += f" DEFAULT {default}"

    with get_db_connection(db_path) as conn:
        conn.execute(alter_sql)
        conn.commit()

    return f"Column '{column_name}' added to table '{table_name}'"


@tool
def create_index(db_path: str, table_name: str, column_name: str,
                 index_name: str = None, unique: bool = False) -> str:
    """Create an index on a column.

    Args:
        db_path: Path to the SQLite database file.
        table_name: Name of the table to index.
        column_name: Name of the column to index.
        index_name: Optional custom name for the index.
        unique: If True, create a UNIQUE index.
    """
    if index_name is None:
        index_name = f"idx_{table_name}_{column_name}"

    unique_str = "UNIQUE" if unique else ""
    create_sql = f"CREATE {unique_str} INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"

    with get_db_connection(db_path) as conn:
        conn.execute(create_sql)
        conn.commit()

    return f"Index '{index_name}' created on {table_name}.{column_name}"
