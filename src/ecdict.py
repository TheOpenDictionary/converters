import csv
from os import path
from tempfile import TemporaryDirectory

from lxml import etree
import requests
from theopendictionary import Dictionary as ODictionary
from utils import Dictionary, Entry, Etymology, Usage, Definition
from alive_progress import alive_bar

url = "https://raw.githubusercontent.com/TheOpenDictionary/ecdict/master/ecdict.csv"

with TemporaryDirectory() as dirpath:
    try:
        file_name = path.basename(url)
        blob = requests.get(url).content
        output_path = path.join(dirpath, file_name)

        new_file = open(output_path, "w+b")
        new_file.write(blob)
        new_file.close()

        entries = []

        with open(output_path, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")

            with alive_bar(title="> Processing entries...") as bar:
                for row in reader:
                    m = dict(
                        zip(
                            [
                                "word",
                                "phonetic",
                                "definition",
                                "translation",
                                "pos",
                                "collins",
                                "oxford",
                                "tag",
                                "bnc",
                                "frq",
                                "exchange",
                                "detail",
                                "audio",
                            ],
                            row,
                        )
                    )

                    prn = m["phonetic"]
                    definitions = m["translation"].splitlines()
                    defs = []

                    for deff in definitions:
                        d = Definition(deff)
                        defs.append(d)

                    entries.append(
                        Entry(
                            term=m["word"],
                            pronunciation=prn,
                            etymologies=[Etymology(usages=[Usage(definitions=defs)])],
                        )
                    )

                    bar.text(m["word"])
                    bar()

            root = Dictionary(name="ECDICT", entries=entries).xml()
            xml = etree.tostring(root, pretty_print=True).decode("utf-8")

            print("> Writing ecdict.xml...")

            with open("dictionaries/ecdict.xml", "w") as f:
                f.write(xml)

            print("> Writing ecdict.odict...")

            ODictionary.write(xml, "dictionaries/ecdict.odict")
    except Exception as e:
        print(e)
