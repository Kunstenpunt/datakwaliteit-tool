from PySide6.QtCore import Signal, QObject, QThread

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config
from wikibaseintegrator.wbi_helpers import execute_sparql_query
from wikibaseintegrator.wbi_login import Login

from .utils import query_result_to_list
from .secrets import password, user

BASE_URL = "https://kg.kunsten.be"


class QueryWorker(QObject):
    finished = Signal()

    def __init__(self, query, prefixes):
        super().__init__()
        self.query = query
        self.prefixes = prefixes
        self.result_list = None

    def run(self):
        result = None
        try:
            result = execute_sparql_query(self.query, self.prefixes, max_retries=1)
        except Exception as e:
            print(e)
        self.result_list = query_result_to_list(result)
        self.finished.emit()


class WikibaseHelper(QObject):
    query_started = Signal()  # For loading indicator
    query_done = Signal()  # For loading indicator
    _ready_for_new_query = Signal()

    def __init__(self):
        super().__init__()

        # The necessary configuration for the wikibase instance of Kunstenpunt
        config["DEFAULT_LANGUAGE"] = "nl"
        config["WIKIBASE_URL"] = "https://kg.kunsten.be"
        config["MEDIAWIKI_API_URL"] = "https://kg.kunsten.be/w/api.php"
        config["MEDIAWIKI_INDEX_URL"] = "https://kg.kunsten.be/w/index.php"
        config["MEDIAWIKI_REST_URL"] = "https://kg.kunsten.be/w/rest.php"
        config["SPARQL_ENDPOINT_URL"] = (
            "https://kg.kunsten.be/query/proxy/wdqs/bigdata/namespace/wdq/sparql"
        )
        # All used prefixes to keep queries in other code more lean looking
        self.query_prefixes = """
            PREFIX kp:<https://kg.kunsten.be/entity/>
            PREFIX kpt:<https://kg.kunsten.be/prop/direct/>
            PREFIX kpp:<https://kg.kunsten.be/prop/>
            PREFIX kpps:<https://kg.kunsten.be/prop/statement/>
            PREFIX kppq:<https://kg.kunsten.be/prop/qualifier/>
        """

        self.executing_query = False
        self.query_result = None
        self.most_recent_query = None

    def login(self, user=user, password=password):
        # Login using the bot account username and password
        login = Login(user=user, password=password)
        wbi = WikibaseIntegrator(login=login)

    def execute_query(self, query_string, callback):
        try:
            self._ready_for_new_query.disconnect()
        except TypeError:
            pass

        self._ready_for_new_query.connect(callback)

        if self.executing_query:
            return
        else:
            self.executing_query = True

        self.query_thread = QThread()
        self.query_worker = QueryWorker(query_string, self.query_prefixes)
        self.query_worker.moveToThread(self.query_thread)
        self.query_thread.started.connect(self.query_worker.run)
        self.query_worker.finished.connect(self.query_worker_finished)
        self.query_worker.finished.connect(self.query_thread.quit)
        self.query_worker.finished.connect(self.query_worker.deleteLater)
        self.query_thread.finished.connect(self.query_thread.deleteLater)
        self.query_thread.destroyed.connect(self.query_thread_destroyed)

        self.most_recent_query = query_string
        self.query_started.emit()
        self.query_thread.start()

    def query_worker_finished(self):
        self.query_result = self.query_worker.result_list
        self.query_done.emit()

    def query_thread_destroyed(self):
        self.executing_query = False
        self._ready_for_new_query.emit()
