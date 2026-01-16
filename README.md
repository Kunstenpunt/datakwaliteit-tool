# datakwaliteit-tool
Grafische tool om de knowledge graph te analyseren en verbeteren van de Wikibase instantie op kg.kunsten.be, met als doel de datakwaliteit te verhogen.

## How to run

The project uses [pipenv](https://pipenv.pypa.io/en/latest/) to manage it's python environment. Install it for your platform, then run the following to install the necessary modules:

```pipenv install```

To then run the application, use the following:

```pipenv run python app.py```

If you want to generate a release binary, use `pyside6-deploy` which is part of the used [PySide6](https://wiki.qt.io/Qt_for_Python) Qt UI toolkit library.

```pipenv run pyside6-deploy -c pysidedeploy.spec```
## Configurations
### Configuration for kg.kunsten.be instance
- default language: "nl"
- wikibase url: "https://kg.kunsten.be"
- mediawiki api url: "https://kg.kunsten.be/w/api.php"
- mediawiki index url: "https://kg.kunsten.be/w/index.php"
- mediawiki rest url: "https://kg.kunsten.be/w/rest.php"
- sparql endpoint url: "https://kg.kunsten.be/query/proxy/wdqs/bigdata/namespace/wdq/sparql"
- property constraint pid: "P85"

### Configuration for www.wikidata.org instance
- default language: "en"
- wikibase url: "http://www.wikidata.org"
- mediawiki api url: "https://www.wikidata.org/w/api.php"
- mediawiki index url: "https://www.wikidata.org/w/index.php"
- mediawiki rest url: "https://www.wikidata.org/w/rest.php"
- sparql endpoint url: "https://query.wikidata.org/sparql"
- property constraint pid: "P2302"