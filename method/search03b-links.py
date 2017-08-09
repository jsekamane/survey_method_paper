#!/usr/local/bin/python3
#coding=utf-8

# =================
# Search03: 'TITLE-ABS-KEY("market mechanism" OR "market design") AND TITLE-ABS-KEY(electricity) AND LANGUAGE(english) AND DOCTYPE(ar OR cp OR ch OR re)'
# search03b-links.py: Loads search results (search03a.py) and processes by fetching data for each item. Combines the data for saves metadata, references and citedby data in JSON files for further processing (search03c-cleaning.py).
# =================

from elsevier_apis import fetch_data
import json

# Function that flattens dict/JSON
# http://stackoverflow.com/a/6027703/1053612
def parse_dict(init, lkey=''):
    sep = '.'
    ret = {}
    for rkey,val in init.items():
        key = lkey+sep+rkey
        if isinstance(val, dict):
            ret.update(parse_dict(val, key+sep))
        else:
            ret[key] = val
    return ret


# Load search results
with open('_temp/search03.json', 'r') as f:
    searchResults = json.load(f)

# Create empty containers for the combined data
combined_metadata = {"combined": []}
combined_references = {"combined": []}
combined_citedby = {"combined": []}

# Get the metadata, references and citedby data for every search result
for item in searchResults['search-results']['entry']:
    # Reset varibles
    ref_s_id = {}
    cby_s_id = {}
    
    # Fetch data
    s_id = item['dc:identifier'].split(':')[1]
    meta, ref, cby = fetch_data(s_id)
    
    # Combine data for each artitle
    combined_metadata['combined'].append(meta)
    # Add ID to crossreference the references of each article
    if bool(ref) and ref['abstracts-retrieval-response'] is not None:
        ref_s_id = ref['abstracts-retrieval-response']['references']
    ref_s_id['id'] = s_id
    combined_references['combined'].append(ref_s_id)
    # Add ID to crossreference the cited-by of each article, and remove API navigation links and flatten structure of 'opensearch:Query'.
    if bool(cby):
        cby_s_id = cby['search-results']
        del cby_s_id['link']
        cby_s_id_query = parse_dict(cby_s_id['opensearch:Query'], 'opensearch:Query')
        del cby_s_id['opensearch:Query']
        cby_s_id.update(cby_s_id_query)
    cby_s_id['id'] = s_id
    combined_citedby['combined'].append(cby_s_id)


# Save the combined data
with open('data/search03_meta.json', 'w') as f:
    json.dump(combined_metadata, f)
with open('data/search03_ref.json', 'w') as f:
    json.dump(combined_references, f)
with open('data/search03_cby.json', 'w') as f:
    json.dump(combined_citedby, f)
    
    