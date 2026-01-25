# datakwaliteit-tool

Graphical tool to help improve data quality (_datakwaliteit_ in Dutch) on a wikibase instance. Some features include:
- Generate a list of all defined constraints on properties
- Ability to validate constraints on properties (user can choose to limit input or output if the query takes to long)
- Generate QuickStatements based on a template for batch correction of data
- Any Q-number, P-number or statement ID can be double clicked to open the corresponding page in a default web browser.

This tool is initially solely developed for use on the kg.kunsten.be instance, and therefore currently only implements the constraints that are used in this database.

## How to run

The project uses python. Use your preferred method for installing specific python versions on your operating system.

The project makes use of [pipenv](https://pipenv.pypa.io/en/latest/) to manage its python environment. Install it for your platform, then run the following to install the necessary modules:

```pipenv install```

The project uses a fixed python version to have equal development environments. If your installation does not have the correct python version, the previous command will give a warning. Install the correct python version (as indicated by the warning) and try again.

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
