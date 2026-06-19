#!/usr/bin/env -O python3
"""Utility to cross two apertium dix files to make third dix file."""

import sys
import xml.etree.ElementTree
from argparse import ArgumentParser, FileType
from typing import TextIO


def parseilr(ilr) -> dict[str, str]:
    """parse an i or l or r structure into a lexeme."""
    lexeme = {}
    lexeme["lemma"] = ilr.text
    for child in ilr:
        if child.tag == "s":
            if "tags" in lexeme:
                lexeme["tags"].append(child.attrib["n"])
            else:
                lexeme["tags"] = [child.attrib["n"]]
        elif child.tag == "par":
            if "paradigms" in lexeme:
                lexeme["paradigms"].append(child.attrib["s"])
            else:
                lexeme["paradigms"] = [child.attrib["s"]]
    return lexeme


def parsee(e) -> dict[dict[str, str], dict[str, str]]:
    """parse an e structure into a lexeme pair."""
    lexpair = {}
    for child in e:
        if child.tag == "p":
            for pchild in child:
                if pchild.tag == "l":
                    lexpair["sl"] = parseilr(pchild)
                elif pchild.tag == "r":
                    lexpair["tl"] = parseilr(pchild)
        elif child.tag == "i":
            lexpair["sl"] = parseilr(child)
            lexpair["tl"] = parseilr(child)
    return lexpair


def parsesection(section) -> list[dict[dict[str, str], dict[str, str]]]:
    """parse an actual dictionary section into lexeme pairs."""
    lexpairs = []
    for child in section:
        if child.tag == "e":
            lexpair = parsee(child)
            lexpairs.append(lexpair)
    return lexpairs


def parsedix(dixfile: TextIO) -> list[dict[dict[str,str], dict[str, str]]]:
    """read apertium bi dix file, create a data structure of lexeme pairs."""
    dixtree = xml.etree.ElementTree.parse(dixfile)
    root = dixtree.getroot()
    lexpairs = []
    for child in root:
        if child.tag == "section":
            newlexpairs = parsesection(child)
            lexpairs += newlexpairs
    return lexpairs


def main():
    """CLI interface for crossing dix."""
    argp = ArgumentParser()
    argp.add_argument("-1", "--first-dix", type=open, required=True,
                      help="first dix file")
    argp.add_argument("-2", "--second-dix", type=open, required=True,
                      help="second dix file")
    argp.add_argument("-o", "--output", type=FileType("w"), required=True,
                      help="output dix file")
    argp.add_argument("-y", "--no-interactive", default=False,
                      action="store_true",
                      help="answer yes to all questions DANGER TERROR HORROR")
    options = argp.parse_args()
    dix1 = parsedix(options.first_dix)
    dix2 = parsedix(options.second_dix)
    print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>", file=options.output)
    print("<dictionary>", file=options.output)
    print("  <alphabet/>", file=options.output)
    print("  <section id=\"crossdix\" type=\"standard\">", file=options.output)
    for lexpair in dix1:
        sourcel = lexpair["sl"]
        middel = lexpair["tl"]
        if not sourcel["lemma"]:
            continue
        if not middel["lemma"]:
            continue
        print(f"** new word: {sourcel["lemma"]}**")
        for lexpair2 in dix2:
            if lexpair2["sl"]["lemma"] == middel["lemma"]:
                targetl = lexpair2["tl"]
                if not targetl["lemma"]:
                    continue
                print(sourcel["lemma"] + "." + ".".join(sourcel["tags"]),
                      middel["lemma"] + "." + ".".join(middel["tags"]),
                      targetl["lemma"] + "." + ".".join(targetl["tags"]),
                      sep=" <=> ")
                answer = input("yes / no / maybe = 1-100 / quit ? ")
                if answer in ["y", "yes"]:
                    print("adding")
                    print(f"    <e><p><l>{sourcel["lemma"]}"
                          f"<s n=\"{sourcel["tags"][0]}\"/></l>"
                          f"<r>{targetl["lemma"]}"
                          f"<s n=\"{targetl["tags"][0]}\"/></r></p></e>",
                          file=options.output)
                elif answer.isdigit():
                    print("weighting")
                    print(f"    <e w=\"{answer}\">><p><l>{sourcel["lemma"]}"
                          f"<s n=\"{sourcel["tags"][0]}\"/></l>"
                          f"<r>{targetl["lemma"]}"
                          f"<s n=\"{targetl["tags"][0]}\"/></r></p></e>",
                          file=options.output)
                elif answer in ["q", "quit"]:
                    print("ok quitting")
                    sys.exit(0)
                elif answer in ["n", "no"]:
                    print("skipping")
                else:
                    print(f"Assuming {answer} means no, skipping")
    print("  </section>", file=options.output)
    print("</dictionary>", file=options.output)


if __name__ == "__main__":
    main()
