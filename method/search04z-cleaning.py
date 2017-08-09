#!/usr/local/bin/python3
#coding=utf-8

# =================
# For each ID in the largest component, check if local cache version. If yes, then combine (compressed) metadata. If not then consider data in search03_meta.json (search03_ref.json and search03_cby.json).
# =================

from elsevier_apis import fetch_data
from elsevier_extract import meta_entry, ref_entry, cby_entry
import json
import csv


# -----------------
# Load data
# -----------------

# Load IDs in largest component
largecomponent = []
with open('_temp/id_largestcomponent.csv', 'r') as f:
    next(f) # skip header
    csv_content = csv.reader(f)
    for row in csv_content:
        largecomponent.append(row[0])

# Local cache
localcache = []
with open('local_cache.txt', 'r') as f:
    csv_content = csv.reader(f)
    for row in csv_content:
        localcache.append(row[0])

# Load the combined data
with open('data/search03_meta.json', 'r') as f:
    combined_metadata = json.load(f)
with open('data/search03_ref.json', 'r') as f:
    combined_references = json.load(f)
with open('data/search03_cby.json', 'r') as f:
    combined_citedby = json.load(f)


# -----------------
# Extract metadata infomation form the data avaliable in local cache
# -----------------

# IDs for largest component that are avaliable in local cache
largecomponent_avaliable = [s_id for s_id in largecomponent if s_id in localcache]
print('The local cache consits of %s papers. There are %s IDs in the largest component, of these %s are avaliable in the local cache.\n' % (len(localcache),len(largecomponent),len(largecomponent_avaliable)))

# Empty containts for data on articles
articles = {'articles': []}

# Loop through IDs in local cache
#TEMP_I=0
print('LOCAL CACHE')
for s_id in largecomponent_avaliable:
    # Fetch data
    meta, _, _ = fetch_data(s_id)
    articles['articles'].append( meta_entry(meta) )
    
    #TEMP_I += 1
    #if TEMP_I == 10:
    #    break
print('Length of articles %s\n' % len(articles['articles']))


# -----------------
# Extract metadata infomation for the remaining articles
# -----------------

# Test if article with Scopus ID already exsist in list of articles.
def absent(s_id):
    for item in articles['articles']:
        if item['id'] != s_id:
            continue
        else:
            return False
    return True

# STEP 1a: Initial articles from search result
print('METADATA')
for item in combined_metadata['combined']:
    s_id = item['dc:identifier'].split(':')[1]
    if absent(s_id):
        articles['articles'].append( meta_entry(item) )
print('Length of articles %s\n' % len(articles['articles']))

# STEP 1b: Go through citedby and extract citations and article infomation
# Citedby data is better than references, so add this first
print('CITEDBY')
for item in combined_citedby['combined']:
    # If there are citedby
    if len(item) > 1:
        if item['opensearch:totalResults'] != '0':
            # Loop through all citedby
            for cby in item['entry']:
                cby_id = cby['dc:identifier'].split(':')[1]
                # Add citation
                #citations.append( [cby_id, item['id']] )
                # Add article (if currently absent)
                if absent(cby_id):
                    articles['articles'].append( cby_entry(cby) )
print('Length of articles %s\n' % len(articles['articles']))

# STEP 1c: Go through references and extract citations and article infomation
print('REFERENCES')
for item in combined_references['combined']:
    # If there are references
    if len(item) > 1:
        # Loop through all references
        for ref in item['reference']:
            # Add citation
            #citations.append( [item['id'], ref['scopus-id']] )
            # Add article (if currently absent)
            if absent(ref['scopus-id']):
                articles['articles'].append( ref_entry(ref) )
print('Length of articles %s\n' % len(articles['articles']))


# -----------------
# Save metadata
# -----------------
#print(articles)
with open('_temp/metadata.csv', 'w') as csvfile:
    metadata = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    metadata.writerow(['ID', 'author', 'year', 'title', 'source', 'description', 'citations'])
    for article in articles['articles']:
        metadata.writerow([article['id'], article['author'], article['year'], article['title'], article['source'], article['description'], article['cit_score']])