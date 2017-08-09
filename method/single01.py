#!/usr/local/bin/python3
#coding=utf-8

from elsevier_apis import fetch_data

# Returns JSON files
meta, ref, cby = fetch_data('18744367507', verbose = True)
print('done')





