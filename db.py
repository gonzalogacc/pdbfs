import sqlalchemy as sa
from sqlalchemy import create_engine
import datetime

engine = create_engine("postgresql+psycopg2://user:pass@localhost:5432/testdb")


def list_tables() -> list[str]:
    with engine.connect() as conn:
        result = conn.execute(sa.text("select table_name from information_schema.tables where table_schema = 'public' ;"))
        return [f"{table[0]}.table" for table in result]

def list_table_columns(tablename: str) -> list[str]:
    with engine.connect() as conn:
        result = conn.execute(
            sa.text(
                "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' and table_name = :tablename;"
            ),
            {"tablename": tablename}
        )
        return [f"{col[0]}.column" for col in result]

def list_column_rows(table_name, column_name):
    with engine.connect() as conn:
        # Note: Table and column names cannot be parameterized in the same way as values.
        # However, for a PoC, using sa.text safely or validating inputs is preferred.
        # Here we use f-strings but could benefit from quoting if needed.
        query = sa.text(f"SELECT {column_name} from {table_name};")
        result = conn.execute(query)
        rows = []
        for row in result:
            val = row[0]
            if isinstance(val, (datetime.date, datetime.datetime)):
                val = val.isoformat()
            rows.append(f"{val}.dbf")
        return rows

def read_table_data(tablename: str, columname: str, columnvalue: str):
    with engine.connect() as conn:
        query = sa.text(f"SELECT * from {tablename} where {columname} = :columnvalue;")
        result = conn.execute(query, {"columnvalue": columnvalue})
        return [row for row in result]

if __name__ == "__main__":
    tables  = list_tables()
    print(['.', '..', *tables])
    columns = list_table_columns(tables[0])
    print(f"{tables[0]=}: {columns=}")
    print(read_table_data(tables[0], "title", "Fargo"))