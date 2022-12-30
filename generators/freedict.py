import sys
import requests
import asyncio
import tarfile

from os import path
from pathlib import Path
from theopendictionary import Dictionary as ODictionary
from ctypes import *
from os import path
from tempfile import TemporaryDirectory
from lxml import etree
from bs4 import BeautifulSoup
from alive_progress import alive_bar

from utils import Definition, Dictionary, Entry, Etymology, Usage

target_dictionary = sys.argv[1] if len(sys.argv) > 1 else "all"


def tei_to_odxml(tei_doc):
    document = BeautifulSoup(tei_doc, features="xml")
    root = Dictionary(name="FreeDict")
    entries = {}

    with alive_bar(title="> Processing entries...") as bar:
        for entry in document.body.findAll("entry"):
            term = entry.orth.getText()
            pron = entry.pron.getText() if entry.pron is not None else ""
            usages: list[Usage] = []

            for sense in entry.findAll("sense"):
                defs: list[Definition] = []

                for cit in sense.findAll("cit"):
                    defs.append(Definition(cit.getText().strip()))

                if len(defs) > 0:
                    usages.append(Usage(definitions=defs))

            if len(usages) > 0:
                entries[term] = Entry(
                    term, pronunciation=pron, etymologies=set([Etymology(usages)])
                )
                bar()

    for entry in entries.values():
        root.entries.append(entry)

    return etree.tostring(root.xml()).decode("utf-8")


def read_tei_archive(path):
    with tarfile.open(path) as tar:
        for member in tar.getmembers():
            f = tar.extractfile(member)

            if ".tei" in member.name:
                return f.read()
    return None


async def process_dict(language_pair, url):
    with TemporaryDirectory() as dirpath:
        print("> Processing language pair %s..." % language_pair)
        file_name = url.split("/")[-1]
        output_path = path.join(dirpath, file_name)

        if not path.exists(output_path):
            print("> Downloading dictionary from %s..." % url)
            blob = requests.get(url).content
            new_file = open(output_path, "w+b")
            new_file.write(blob)
            new_file.close()
            print("> Download complete!")

        content = read_tei_archive(output_path)
        dictionary = tei_to_odxml(content)
        dict_base = "dictionaries/freedict"
        dict_path = "%s/%s.odict" % (dict_base, language_pair)

        print('> Writing to "%s"...' % dict_path)

        with open("%s/%s.xml" % (dict_base, language_pair), "w") as f:
            f.write(dictionary)

        ODictionary.write(dictionary, dict_path)


async def process():

    Path("dictionaries").mkdir(parents=True, exist_ok=True)

    json = requests.get("https://freedict.org/freedict-database.json").json()

    tasks = []

    for j in json:
        if "name" in j:
            language_pair = j["name"]
            if language_pair == target_dictionary or target_dictionary == "all":
                for release in j["releases"]:
                    if release["platform"] == "src":
                        url = release["URL"]
                        tasks.append(
                            asyncio.ensure_future(process_dict(language_pair, url))
                        )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(process())
