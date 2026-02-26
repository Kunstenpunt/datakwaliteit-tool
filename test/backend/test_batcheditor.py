from src.backend.batcheditor import BatchEditor

from .stubs import WikibaseConfigStub, WikibaseQueryRunnerStub

query = "some query"
queryResult = [
    ["y", "xy", "yz"],
    ["https://base.url/entity/Q1", "2", "https://base.url/entity/Q4"],
    ["https://base.url/entity/Q2", "4", "https://base.url/entity/Q5"],
]
recipe = """
    ?yz\t P1  \t|\t?y  
-?y | P2 | "?xy" || ?y\tP3\t"value"
"""

expectedStatements = """Q4\tP1\tQ1
-Q1\tP2\t"2"
Q1\tP3\t"value"
Q5\tP1\tQ2
-Q2\tP2\t"4"
Q2\tP3\t"value\""""


def test_BatchEditor(qtbot):
    wikibaseConfigStub = WikibaseConfigStub()
    wikibaseQueryRunnerStub = WikibaseQueryRunnerStub()
    wikibaseQueryRunnerStub.queryResult = queryResult
    batchEditor = BatchEditor(wikibaseConfigStub, wikibaseQueryRunnerStub)

    def check_statements():
        return batchEditor.generatedStatements == expectedStatements

    with qtbot.waitSignal(
        batchEditor.statementGenerationDone,
        raising=True,
        check_params_cb=check_statements,
    ):
        batchEditor.startPipeline(query, recipe)
