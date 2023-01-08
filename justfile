install:
  poetry install

freedict language="all": install
	poetry run python src/freedict.py {{language}}

cedict: install
	poetry run python src/cedict.py

ecdict: install
	poetry run python src/ecdict.py

jmdict language="eng": install
  poetry run python src/jmdict.py {{language}}