#!/bin/bash


dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 ./src/repeating_donors.py /input/itcont.txt /input/percentile.txt /output/repeat_donors.txt
