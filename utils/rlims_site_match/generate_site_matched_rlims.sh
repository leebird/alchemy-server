#!/bin/sh
PYTHONPATH=../.. python3 generate_site_matched_rlims.py Gennorm data/rlims_uniprots.tab data/rlims_uniprots.fasta data/reviewed data/kinasekey data/site_matched $1
