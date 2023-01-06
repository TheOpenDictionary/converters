from lxml import etree


class Definition:
    def __init__(self, text: str) -> None:
        self.text = text

    def xml(self):
        node = etree.Element("definition", attrib={"value": self.text})
        return node


class Group:
    def __init__(self, definitions: list[Definition], description: str = "") -> None:
        self.definitions = definitions
        self.description = description

    def xml(self) -> str:
        node = etree.Element("group", attrib={"description": self.description})

        for definition in self.definitions:
            node.append(definition.xml())

        return node


class Usage:
    def __init__(
        self,
        partOfSpeech: str = "",
        description: str = "",
        groups: list[Group] = [],
        definitions: list[Definition] = [],
    ) -> None:
        self.pos = partOfSpeech
        self.groups = groups
        self.description = description
        self.definitions = definitions

    def xml(self):
        attrib = {}

        if self.pos != "":
            attrib["pos"] = self.pos

        if self.description != "":
            attrib["description"] = self.description

        node = etree.Element("usage", attrib=attrib)

        for group in self.groups:
            node.append(group.xml())

        for definition in self.definitions:
            node.append(definition.xml())

        return node


class Etymology:
    def __init__(self, usages: list[Usage] = [], description: str = "") -> None:
        self.usages = usages
        self.description = description

    def xml(self):
        node = etree.Element("ety", attrib={"description": self.description})

        for usage in self.usages:
            node.append(usage.xml())

        return node


class Entry:
    def __init__(
        self,
        term: str,
        see: str = "",
        pronunciation: str = "",
        etymologies: list[Etymology] = [],
    ) -> None:
        self.etymologies = etymologies
        self.see = see
        self.term = term
        self.pronunciation = pronunciation

    def xml(self):
        node = etree.Element("entry", attrib={"see": self.see, "term": self.term})

        for ety in self.etymologies:
            node.append(ety.xml())

        return node


class Dictionary:
    def __init__(self, name: str, entries: list[Entry] = []) -> None:
        self.name = name
        self.entries = entries

    def xml(self):
        node = etree.Element("dictionary", attrib={"name": self.name})

        for entry in self.entries:
            node.append(entry.xml())

        return node
