from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config
from wikibaseintegrator.wbi_helpers import execute_sparql_query
from wikibaseintegrator.wbi_login import Login

from .utils import query_result_to_list
from .secrets import password, user

BASE_URL = "https://kg.kunsten.be"


class WikibaseHelper:
    def __init__(self):
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

    def login(self, user=user, password=password):
        # Login using the bot account username and password
        login = Login(user=user, password=password)
        wbi = WikibaseIntegrator(login=login)

    def execute_query(self, query_string):
        result = None

        try:
            result = execute_sparql_query(query_string, self.query_prefixes)
        except Exception as e:
            print(e)
        return query_result_to_list(result)
