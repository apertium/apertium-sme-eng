#!/usr/bin/env -O python3
"""Run WMT26 tests on apertium-sme-eng."""

import json
import subprocess
import sys
from argparse import ArgumentParser, FileType, Namespace


def main():
    """Run CLI"""
    argp = ArgumentParser()
    argp.add_argument("-i", "--input", type=open, required=True,
                      help="read json input from file")
    argp.add_argument("-o", "--output", type=FileType("w"), required=True,
                      help="write json output to file")
    options = argp.parse_args()
    dostuff(options)


def dostuff(options: Namespace):
    """Do the main thang."""
    testset = json.load(options.input)
    lines = 0
    for test in testset:
        lines = lines + 1
        if test["tgt_lang"] == "sme_Latn":
            print("*", end="")
            dotest(options, test)
        else:
            print(lines, "...", end="\r")


def dotest(options: Namespace, test):
    """process single jsonl lien with relevant test."""
    if "<p>" in test["source_doc"]:
        translate_xml(options, test)
    elif "\n" in test["source_doc"]:
        translate_lines(options, test)
    else:
        translate_lines(options, test)


def translate_lines(options: Namespace, test):
    """Translate test set made of \\n separated lines."""
    doc = test["source_doc"]
    hypothesis = {}
    hypothesis["doc_id"] = test["doc_id"]
    hypothesis["tgt_lang"] = test["tgt_lang"]
    hypothesis["source_doc"] = test["source_doc"]
    results = subprocess.run(["apertium", "-u", "-d", ".", "-f", "line",
                              "eng-sme"],
                             input=doc.encode("utf-8"),
                             stdout=subprocess.PIPE,
                             check=True)
    translations = results.stdout.decode("utf-8")
    hypothesis["hypothesis"] = translations
    print_jsonl(hypothesis, options)


def translate_xml(options, test):
    """Translate teset set of xml-y stuff."""
    doc = test["source_doc"]
    hypothesis = {}
    hypothesis["doc_id"] = test["doc_id"]
    hypothesis["tgt_lang"] = test["tgt_lang"]
    hypothesis["source_doc"] = test["source_doc"]
    results = subprocess.run(["apertium", "-u", "-d", ".", "-f", "html",
                              "eng-sme"],
                             input=doc.encode("utf-8"),
                             stdout=subprocess.PIPE,
                             check=True)
    translations = results.stdout.decode("utf-8")
    hypothesis["hypothesis"] = translations
    print_jsonl(hypothesis, options)


def print_jsonl(hyp: dict[str, str], options: Namespace):
    """Print properly formatted jsonl for test scripts.

    printing python repr of the dict will make WMT26 test scripts freak out :-(
    """
    translations = hyp["hypothesis"]
    source_doc = hyp["source_doc"]
    # just replace ASCII junk with unicode goats for smoother jsoning
    translations = translations.replace("\"", "”").replace("'", "’")
    translations = translations.replace("\n", "\\n")
    source_doc = source_doc.replace("\"", "”").replace("'", "’")
    source_doc = source_doc.replace("\n", "\\n")
    print("{" +
          f"\"doc_id\": \"{hyp["doc_id"]}\", " +
          f"\"source_doc\": \"{source_doc}\", " +
          f"\"tgt_lang\": \"{hyp["tgt_lang"]}\", " +
          f"\"hypothesis\": \"{translations}\"" +
          "}", file=options.output)


if __name__ == "__main__":
    main()
