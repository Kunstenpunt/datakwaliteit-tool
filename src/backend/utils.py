import re
from typing import Any, Optional

from .types import Table


def queryResultToTable(queryResult: Any) -> Optional[Table[str]]:
    try:
        header = queryResult["head"]["vars"]
        result = [header]

        for queryRow in queryResult["results"]["bindings"]:
            resultRow = []
            for variableName in header:
                resultRow.append(
                    queryRow[variableName]["value"]
                    if variableName in queryRow
                    else None
                )
            result.append(resultRow)
    except:
        result = None
    return result


def stripUrlPartFromTable(baseUrl: str, table: Table[str]) -> Table[str]:
    return [
        [idFromUrl(el) if el.startswith(baseUrl) else el for el in row] for row in table
    ]


def idFromUrl(url: str) -> str:
    return url.rsplit("/", 1)[-1]


def urlFromId(possibleId: str, baseUrl: str) -> Optional[str]:
    entityRegex = re.compile(r"^[QPL]\d+$")
    statementRegex = re.compile(r"^[PQq]\d+-[A-Za-z0-9\-]+$")

    baseUrl = baseUrl.rstrip("/")

    if entityRegex.match(possibleId):
        return f"{baseUrl}/entity/{possibleId}"
    elif statementRegex.match(possibleId):
        return f"{baseUrl}/entity/statement/{possibleId}"
    else:
        return None


def stringOrDefault(value: Any, default: str = "") -> str:
    return value if type(value) == str else default
