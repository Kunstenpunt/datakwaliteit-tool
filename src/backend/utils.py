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
    if not url:
        return None
    return url.rsplit("/", 1)[-1]


def stripUrlPartFromTable(url, table):
    return [
        [stripUrlPart(el) if el.startswith(url) else el for el in row] for row in table
    ]


def urlFromId(possibleId, baseUrl):
    propertyRegex = re.compile(r"^P\d+$")
    entityRegex = re.compile(r"^Q\d+$")
    statementRegex = re.compile(r"^[PQ]\d+-[A-Za-z0-9\-]+$")

    if propertyRegex.match(possibleId) or entityRegex.match(possibleId):
        return f"{baseUrl}/entity/{possibleId}"
    elif statementRegex.match(possibleId):
        return f"{baseUrl}/entity/statement/{possibleId}"
    else:
        return None


def alignTabColumns(text, tabWidth, nCols):
    """Modify tab separated text to create aligned columns

    This function will take an input text containing data in columns that are separated by single tabs, and add tabs
    where needed to make the columns visually align.

    :param text: The input data, containing one or more lines of single tab separated columns
    :param tabWidth: The width of the full tab character in number of characters
    :param nCols: The number of columns in the input text
    :return: The modified text with extra tabs for visually aligned columns
    """
    maxWidths = [0] * (nCols - 1)
    lines = text.split("\n")
    for line in lines:
        for i, w in enumerate(line.split("\t")):
            if i == nCols - 1:
                break
            maxWidths[i] = max(len(w), maxWidths[i])
    result = ""
    maxWidths = [((w // tabWidth) + 1) * tabWidth for w in maxWidths]
    print(maxWidths)
    for line in lines:
        for i, w in enumerate(line.split("\t")):
            result += w
            if i == nCols - 1:
                break
            spacesLeft = maxWidths[i] - len(w)
            nTabs = (max(spacesLeft - 1, 0) // tabWidth) + 1
            result += "\t" * nTabs
        result += "\n"
    return result
