# datakwaliteit-tool
Grafische tool om de knowledge graph te analyseren en verbeteren van de Wikibase instantie op kg.kunsten.be, met als doel de datakwaliteit te verhogen.

# How to run

The project uses [pipenv](https://pipenv.pypa.io/en/latest/) to manage it's python environment. Install it for your platform, then run the following to install the necessary modules:

```pipenv install```

To then run the application, use the following:

```pipenv run python app.py```

If you want to generate a release binary, use `pyside6-deploy` which is part of the used [PySide6](https://wiki.qt.io/Qt_for_Python) Qt UI toolkit library.

```pipenv run pyside6-deploy -c pysidedeploy.spec```
