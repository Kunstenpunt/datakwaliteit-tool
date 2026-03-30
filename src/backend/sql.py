from typing import Mapping, Sequence

from PySide6.QtCore import QObject, Signal
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from .types import Table
from .utils import stringOrDefault


class SqlDatabase(QObject):
    tableAdded = Signal(str)
    tableUpdated = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self._db = QSqlDatabase.addDatabase("QSQLITE")
        self._db.setDatabaseName(":memory:")
        if not self._db.open():
            raise RuntimeError("Unable to create SQLITE database in memory.")

    def addTable(self, name: str, table: Table[object]) -> None:
        if not table:
            raise ValueError(
                "An empty table is not a valid value for creating an SQL table. Need at least a header row."
            )

        self._dropTable(name)

        header = [stringOrDefault(columnName) for columnName in table[0]]
        self._createTable(name, header)

        query = QSqlQuery()
        query.prepare(
            f"INSERT INTO {name} ({", ".join(header)}) VALUES ({", ".join(["?"] * len(header))})"
        )

        for row in table[1:]:
            for value in row:
                query.addBindValue(value)
            if not query.exec():
                print(f"failed to insert row {row} into table {name}")
                print(query.lastError())
                print(query.executedQuery())

        self.tableAdded.emit(name)

    def _dropTable(self, name: str) -> None:
        query = QSqlQuery()
        queryStr = f"DROP TABLE IF EXISTS {name};"
        query.prepare(queryStr)
        if not query.exec():
            print(f"failed to drop table {name}")
            print(query.lastError())

    def _createTable(self, name: str, columns: Sequence[str]) -> None:
        if not columns:
            raise ValueError(
                "An table with no columns is an invalid value for creating an SQL table."
            )
        query = QSqlQuery()
        queryStr = (
            f"CREATE TABLE {name} ( {columns[0]} INTEGER PRIMARY KEY, "
            + ", ".join([f"{column} TEXT" for column in columns[1:]])
            + ");"
        )
        query.prepare(queryStr)
        if not query.exec():
            print(f"failed to create table {name}")
            print(query.lastError())

    def updateRow(
        self, table: str, rowId: tuple[str, int], keyValueMaping: Mapping[str, str]
    ) -> None:
        query = QSqlQuery()
        queryStr = (
            f"UPDATE {table} SET "
            + ", ".join(
                [f" {key} = '{value}'" for (key, value) in keyValueMaping.items()]
            )
            + f" WHERE {rowId[0]} = {rowId[1]};"
        )
        query.prepare(queryStr)
        if not query.exec():
            print(
                f"failed to update row {rowId} in table {table} with values {keyValueMaping.items()}"
            )
            print(query.lastError())
        self.tableUpdated.emit(table)
