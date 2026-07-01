#!/bin/bash
if ! test -d wmt-venv ; then
    python -m venv wmt-venv
fi
wmt-venv/bin/activate
pip install 'mtdata[hf,xlsx]==0.5.1'
wget https://www.statmt.org/wmt26/mtdata/mtdata.recipes.wmt26-constrained.yml
mtdata get-recipe -ri "wmt26-eng-sme" -o "wmt26-eng-sme" --compress --no-merge -j 12
wget https://data.statmt.org/wmt26/wmt26_genmt_blindset.jsonl
echo "[" > wmt26_genmt_blindset.json
sed -e 's/$/,/' wmt26_genmt_blindset.jsonl >> wmt26_genmt_blindset.json
echo "]" >> wmt26_genmt_blindset.json
vim wmt26_genmt_blindset.json  # just remove the last comma because bleh
python dev/wmt26-translate.py -i wmt26_genmt_blindset.json \
    -o ape-sme-eng-hyps.jsonl
    ape-sme-eng-hyps.json > ape-sme-eng-hyps.jsonl
wget https://raw.githubusercontent.com/wmt-conference/wmt-collect-translations/refs/heads/main/genmt_check_alignment.py
pip install ipdb
