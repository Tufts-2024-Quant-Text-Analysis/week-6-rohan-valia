CHARACTER_OF_INTEREST = "chorus"

import os
import pandas as pd
from lxml import etree

DIR = "tei"
NAMESPACES = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}


def to_urn(s: str):
    return f"urn:cts:greekLit:{s.replace('.xml', '')}"


FILES = [
    (os.path.join(DIR, f), to_urn(f))
    for f in os.listdir(DIR)
    if os.path.isfile(os.path.join(DIR, f))
]

speakers = set()

def get_dramatist(urn: str):
    if "tlg0006" in urn: return "Euripides"

    if "tlg0011" in urn: return "Sophocles"

    if "tlg0085" in urn: return "Aeschylus"


def iter_lines(title, urn, tree):
    rows = []

    for l in tree.iterfind(".//tei:l", namespaces=NAMESPACES):
        if l.text is not None:
            n = l.xpath("./@n")
            speaker = l.xpath("../tei:speaker//text()", namespaces=NAMESPACES)

            if len(speaker) > 0:
                speaker = speaker[0].strip().replace(".", "")

                if speaker != "":
                    speakers.add(speaker)
                    row = {
                        "n": n[0],
                        "urn": urn,
                        "dramatist": get_dramatist(urn),
                        "title": title,
                        "speaker": speaker,
                        "text": l.text.strip(),
                    }

                    rows.append(row)

    return rows

data = []

for f, urn in FILES:
    tree = etree.parse(f)
    title = tree.xpath("//tei:titleStmt/tei:title/text()", namespaces=NAMESPACES)[0]
    lines = iter_lines(title, urn, tree)
    data += lines

df = pd.DataFrame(data)

df.to_pickle('./greek-tragedy-by-line.pickle')