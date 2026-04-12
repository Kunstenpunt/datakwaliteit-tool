import textwrap

from src.backend.constraint.base import (
    Constraint,
    Property,
)
from src.backend.constraint.queries import QueryBuilder

from test.backend.stubs import WikibaseConfigStub


def normalize_query(query):
    return textwrap.dedent(query).lstrip().rstrip()


def test_buildExceptionIdsQuery():
    wikibaseConfigStub = WikibaseConfigStub()
    queryBuilder = QueryBuilder(wikibaseConfigStub)

    constraint = Constraint("Q1", "constraint", Property("P1", "property"))

    exceptionIdsQuery = queryBuilder.buildExceptionIdsQuery(constraint)

    expectedResult = """
        SELECT ?exception
        WHERE
        {
            wd:P1 p:P2301 ?statement .
            ?statement ps:P2301 wd:Q1 .
            ?statement ?exceptionQualifier ?exception .

            BIND (IRI(replace(str(?exceptionQualifier), str(pq:), str(wd:)))  AS ?exceptionQualifierItem) .
            SERVICE wikibase:label
            {
                bd:serviceParam wikibase:language "en,nl,mul".
                ?exceptionQualifierItem rdfs:label ?exceptionQualifierLabel .
            }
            FILTER (str(?exceptionQualifierLabel) = "exception to constraint")

            SERVICE wikibase:label { bd:serviceParam wikibase:language "nl,mul" . }
        }
    """

    assert normalize_query(exceptionIdsQuery) == normalize_query(expectedResult)
