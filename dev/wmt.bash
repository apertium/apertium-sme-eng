#!/bin/bash
if ! test -d wmt-venv ; then
    python -m venv wmt-venv
fi
wmt-venv/bin/activate
pip install 'mt[hf,xlsx]==0.5.1'
wget https://www.statmt.org/wmt26/mtdata/mtdata.recipes.wmt26-constrained.yml
mtdata get-recipe -ri "wmt26-eng-sme" -o "wmt26-eng-sme" --compress --no-merge -j 12
