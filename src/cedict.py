import gzip
from alive_progress import alive_bar
import requests
import re

from os import path
from lxml import etree
from tempfile import TemporaryDirectory
from theopendictionary import Dictionary as ODictionary
from utils import Dictionary, Entry, Etymology, Usage, Definition

url = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz"


with TemporaryDirectory() as dirpath:

    file_name = url.split("/")[-1]
    blob = requests.get(url).content
    output_path = path.join(dirpath, file_name)

    new_file = open(output_path, "w+b")
    new_file.write(blob)
    new_file.close()

    g = gzip.open(output_path, "rb")
    entries = []

    with alive_bar(title="> Processing entries...") as bar:
        while True:
            line = g.readline().decode("utf-8")

            if not line:
                break

            m = re.match("(.*?)\s(.*?)\s\[(.*?)]\s/(.*)/", line)

            if m is not None:
                traditional = m.group(1)
                simplified = m.group(2)
                pronunciation = m.group(3)
                definitions = m.group(4).split("/")
                defs = []

                for deff in definitions:
                    d = Definition(deff)
                    defs.append(d)

                entries.append(
                    Entry(
                        term=simplified,
                        pronunciation=pronunciation,
                        etymologies=[Etymology(usages=[Usage(definitions=defs)])],
                    )
                )

                bar.text(simplified)
                bar()

    g.close()

    xml = etree.tostring(
        Dictionary(name="CC-CEDICT", entries=entries).xml(), pretty_print=True
    ).decode("utf-8")

    with open("dictionaries/cedict.xml", "w") as f:
        f.write(xml)

    print('> Writing to "cedict.odict"...')

    ODictionary.write(xml, "dictionaries/cedict.odict")
