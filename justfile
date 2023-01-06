freedict language="all":
	poetry run python src/freedict.py {{language}}

cedict:
	poetry run python src/cedict.py

ecdict:
	poetry run python src/ecdict.py

jmdict language="eng":
  poetry run python src/jmdict.py {{language}}