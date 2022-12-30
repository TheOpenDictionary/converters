freedict language="all":
	poetry run python generators/freedict.py {{language}}

cedict:
	poetry run python generators/cedict.py

ecdict:
	poetry run python generators/ecdict.py

jmdict language="eng":
  poetry run python generators/jmdict.py {{language}}