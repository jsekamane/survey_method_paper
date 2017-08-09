#!/usr/local/bin/python3
#coding=utf-8

# =================
# Search03: 'TITLE-ABS-KEY("market mechanism" OR "market design") AND TITLE-ABS-KEY(electricity) AND LANGUAGE(english) AND DOCTYPE(ar OR cp OR ch OR re)'
# search03a.py: Saves the search results in a JSON file for further processing (search03b-links.py).
# =================

# Request key from https://dev.elsevier.com
from api_key import key

import requests
import json


# Search for papers where 'eletricicty' as well as 'market mechanism' or 'market design' appears in the title, abstract or keyword.
# Only include articles in english, and only include documents of the type 'article', 'conference paper', 'book chapter' or 'review'.
params = {'httpAccept': 'application/json', 'query': 'TITLE-ABS-KEY("market mechanism" OR "market design") AND TITLE-ABS-KEY(electricity) AND LANGUAGE(english) AND DOCTYPE(ar OR cp OR ch OR re)'}
r = requests.get('http://api.elsevier.com/content/search/scopus', headers=key, params=params)
r_raw = r.json()

# Create new JSON with the initial search results. Later we expand it with the search results for subsequent pages. 
searchResults = r_raw.copy()

# Resolve pagination. Elsevier restricts the number of search results per API-response/page to X items per page depending on entitlement.
totalResults = int(r_raw['search-results']['opensearch:totalResults'])
itemsPerPage = int(r_raw['search-results']['opensearch:itemsPerPage'])
startIndex = itemsPerPage
while startIndex < totalResults:
    print('Item %s of %s'%(startIndex,totalResults))
    
    # Add/change the API parameters to include the index
    params['start'] = startIndex
    r_page = requests.get('http://api.elsevier.com/content/search/scopus', headers=key, params=params)
    
    # Add search results to one joined JSON
    searchResults['search-results']['entry'].extend( r_page.json()['search-results']['entry'] )
    
    # Set index for next page of search results
    startIndex += itemsPerPage

print( 'Search results: %s' % len(searchResults['search-results']['entry']) )

# Save response to local cache
with open('_temp/search03.json', 'w') as f:
    json.dump(searchResults, f)

print('done')

