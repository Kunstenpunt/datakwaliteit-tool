from src.backend.utils import (
    idFromUrl,
    queryResultToTable,
    stringOrDefault,
    stripUrlPartFromTable,
    urlFromId,
)

BASE_URL = "some.url"
ENTITY_URL = "some.url/entity/Q1234"
ENTITY_ID = "Q1234"
PROPERTY_URL = "some.url/entity/P1234"
PROPERTY_ID = "P1234"
STATEMENT_URL = "some.url/entity/statement/Q158003-e7f2367a-469a-6620-a300-0ae2ebcbdc6e"
STATEMENT_ID = "Q158003-e7f2367a-469a-6620-a300-0ae2ebcbdc6e"


def test_idFromUrlEntity():
    url = ENTITY_URL
    id = idFromUrl(url)
    assert id == ENTITY_ID


def test_idFromUrlProperty():
    url = PROPERTY_URL
    id = idFromUrl(url)
    assert id == PROPERTY_ID


def test_idFromUrlStatement():
    url = STATEMENT_URL
    id = idFromUrl(url)
    assert id == STATEMENT_ID


def test_queryResultToTableCorrect():
    queryResult = {
        "head": {"vars": ["x", "y"]},
        "results": {
            "bindings": [
                {"x": {"value": "1"}},
                {
                    "y": {"value": "2"},
                    "x": {"value": "3"},
                    "z": {"value": "4"},
                },
                {},
            ]
        },
    }
    table = queryResultToTable(queryResult)
    correctTable = [["x", "y"], ["1", None], ["3", "2"], [None, None]]
    assert table == correctTable


def test_queryResultToTableIncorrect(subtests):
    invalidQueryResults = [
        {
            "head": {"?": ["x", "y"]},
            "results": {
                "bindings": [
                    {"x": {"value": "1"}},
                ]
            },
        },
        None,
        {
            "head": {"vars": ["x", "y"]},
            "results": {
                "wrong": [
                    {"x": {"value": "1"}},
                ]
            },
        },
        ["list", "of", "things"],
    ]

    for queryResult in invalidQueryResults:
        with subtests.test(queryResult=queryResult):
            table = queryResultToTable(queryResult)
            assert table is None


def test_stringOrDefaultString():
    result = stringOrDefault("hello", "default")
    assert result == "hello"


def test_stringOrDefaultNone():
    result = stringOrDefault(None, "default")
    assert result == "default"


def test_stringOrDefaultList():
    result = stringOrDefault([], "default")
    assert result == "default"


def test_stripUrlPartFromTable():
    table = [[ENTITY_URL, PROPERTY_URL], [STATEMENT_URL, "NOT A URL"]]
    strippedTable = stripUrlPartFromTable(BASE_URL, table)
    correctStrippedTable = [
        [ENTITY_ID, PROPERTY_ID],
        [STATEMENT_ID, "NOT A URL"],
    ]
    assert strippedTable == correctStrippedTable


def test_urlFromIdEntity():
    id = ENTITY_ID
    url = urlFromId(id, BASE_URL)
    assert url == ENTITY_URL


def test_urlFromIdProperty():
    id = PROPERTY_ID
    url = urlFromId(id, BASE_URL)
    assert url == PROPERTY_URL


def test_urlFromIdStatement():
    id = STATEMENT_ID
    url = urlFromId(id, BASE_URL)
    assert url == STATEMENT_URL


def test_urlFromIdInvalid(subtests):
    ids = ["Q1234N", "P1234-", "Q1234-dflkj-sdfj-ldfj k", ""]
    for id in ids:
        with subtests.test(id=id):
            url = urlFromId(id, BASE_URL)
            assert url is None


def test_urlFromIdBaseUrlWithSlash():
    id = ENTITY_ID
    url = urlFromId(id, BASE_URL + "/")
    assert url == ENTITY_URL
