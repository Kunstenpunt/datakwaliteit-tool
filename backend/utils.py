import re


def queryResultToList(queryResult):
    if not queryResult:
        return None
    # First row is the header
    header = queryResult["head"]["vars"]
    result = [header]
    # Next come the value rows
    for queryRow in queryResult["results"]["bindings"]:
        resultRow = []
        for variableName in header:
            resultRow.append(
                queryRow[variableName]["value"] if variableName in queryRow else None
            )
        result.append(resultRow)
    return result


def stripUrlPart(url):
    return url.rsplit("/", 1)[-1]


def urlFromId(possibleId, baseUrl):
    propertyRegex = re.compile(r"^P\d+$")
    entityRegex = re.compile(r"^Q\d+$")
    statementRegex = re.compile(r"^Q\d+-[A-Za-z0-9\-]+$")

    if propertyRegex.match(possibleId) or entityRegex.match(possibleId):
        return f"{baseUrl}/entity/{possibleId}"
    elif statementRegex.match(possibleId):
        return f"{baseUrl}/entity/statement/{possibleId}"
    else:
        return None
