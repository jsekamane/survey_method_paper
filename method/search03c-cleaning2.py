#!/usr/local/bin/python3
#coding=utf-8

# =================
# Search03: 'TITLE-ABS-KEY("market mechanism" OR "market design") AND TITLE-ABS-KEY(electricity) AND LANGUAGE(english) AND DOCTYPE(ar OR cp OR ch OR re)'
# search03c-cleaning.py: Loads the combined metadata, references and citedby data (search03b-links.py) and cleans the data.
# =================

import json
import csv

# Load the combined data
with open('data/search03_meta.json', 'r') as f:
    combined_metadata = json.load(f)
with open('data/search03_ref.json', 'r') as f:
    combined_references = json.load(f)
with open('data/search03_cby.json', 'r') as f:
    combined_citedby = json.load(f)


# -----------------
# Functions
# -----------------

# Test if article with Scopus ID already exsist in list of articles.
def absent(s_id):
    for item in articles['articles']:
        if item['id'] != s_id:
            continue
        else:
            return False
    return True

# Extract infomation from the references and format it for the list of articles.
def ref_entry(ref):
    s_id = ref['scopus-id']
    authors = None
    if ref['author-list'] is not None:
        authors = ref['author-list']['author'][0]['ce:surname']
        if len(ref['author-list']['author']) > 1:
            authors += ' et al.'
    title = None
    year = None
    if 'ref-info' in ref:
        if 'ref-title' in ref['ref-info']:
            title = ref['ref-info']['ref-title']['ref-titletext']
        if 'ref-publicationyear' in ref['ref-info']:
            year = ref['ref-info']['ref-publicationyear']['@first']
    source = None
    if 'sourcetitle' in ref:
        source = ref['sourcetitle']
    doi = None
    if 'ce:doi' in ref:
        doi = ref['ce:doi']
    ncitations = None
    if 'citedby-count' in ref:
        if isinstance(ref['citedby-count'], list):
            ncitations = int(ref['citedby-count'][0]['$'])
        else:
            ncitations = int(ref['citedby-count'])
    
    articles_entry = {'id': s_id, 'label': '%s: %s (%s)'%(s_id, authors, year), 'author': authors, 'title': title, 'source': source, 'year': year, 'doi': doi, 'cit_score': ncitations, 'incomplete_record': None, 'description': None}
    return articles_entry

# Extract infomation from the citedby and format it for the list of articles.
def cby_entry(cby):
    s_id = cby['dc:identifier'].split(':')[1]
    authors = None
    if 'dc:creator' in cby:
        authors = cby['dc:creator']
    title = cby['dc:title']
    source = None
    if 'prism:publicationName' in cby:
        source = cby['prism:publicationName']
    year = cby['prism:coverDate'].split('-',1)[0]
    doi = None
    if 'prism:doi' in cby:
        doi = cby['prism:doi']
    ncitations = None
    if 'citedby-count' in cby:
        ncitations = int(cby['citedby-count'])
    
    articles_entry = {'id': s_id, 'label': '%s: %s (%s)'%(s_id, authors, year), 'author': authors, 'title': title, 'source': source, 'year': year, 'doi': doi, 'cit_score': ncitations, 'incomplete_record': None, 'description': None}
    return articles_entry



# -----------------
# STEP 0: Check for errors in the data, particularly the references and cited-by.
# -----------------
# Already cleaned part of the data by adding DOCTYPE(ar OR cp OR ch OR re) to the search query. Possible objections: excludes 'Articles in Press' (ip).

# 63 articles have 'None' references. 
# -- those with DOI: Many of these are abstracts of conference papers, or full conference papers without any references. Some are false positive; 1) most notable the articles from the 'Electricity Journal' (all 2002-2004) where the atypical design probably broke the automatic reference extraction tool. 2) But there are also some articles using non-standard bibliography styles. In one article there are missing pages in the PDF (hence no references).
# -- those without DOI: Primarily conference procedings and trade journal articles. In addition there are 4 journal article; two are inaccisible while the last two do not contain references.

# 1 article where difference between Scopus citedby count and the number of search results is 163 (corrected this below). Other articles with large differences are almost exclusively conference proceedings (that have later been published as article).
for item in combined_citedby['combined']:
    if item['id'] == '84955105817':
        del item['opensearch:Query.@searchTerms']
        del item['opensearch:Query.@startPage']
        del item['entry']
        del item['opensearch:itemsPerPage']
        del item['opensearch:totalResults']
        del item['opensearch:Query.@role']
        del item['opensearch:startIndex']
for item in combined_metadata['combined']:
    if item['dc:identifier'] == 'SCOPUS_ID:84955105817':
        item['citedby-searchcount'] = None

# Possible TO-DO?
# * Duplicate titles? (remove conference procedding, ie. keep latest version).
# * Remove duplicate references



# -----------------
# STEP 1: Convert into network format
# -----------------

# Example of format of entry in articles:
##{
##    'id': 84877046264,
##    'label': '84877046264: Hirth (2014)',
##    'author': 'Hirth',
##    'title': 'The market value of variable renewables: The effect of solar wind power variability on their relative price',
##    'source': 'Energy Economics',
##    'year': 2014,
##    'doi': '10.1016/j.eneco.2013.02.004',
##    'cit_score': ...,
##    'incomplete_record': ...,
##    'description': 'This paper provides a comprehensive discussion of the market value of variable renewable energy (VRE) ... more difficult to accomplish than as many anticipate. © 2013 Elsevier B.V.'
##}

# Example of format of entry in citations 
# (using Scorpus IDs and where the direction is that the first item cites the second item):
##[84877046264, 79955884156]

# Empty containts for data on articles
articles = {'articles': []}

# Creates a list containing 5 lists, each of 8 items, all set to 0
citations = []


# -----------------
# STEP 1a: Initial articles from search result
# -----------------
print('METADATA')
for item in combined_metadata['combined']:
    s_id = item['dc:identifier'].split(':')[1]
    authors = None
    if 'author' in item and 'dc:creator' in item:
        authors = item['dc:creator']['author'][0]['ce:surname']
        if len(item['author']) > 1:
            authors += ' et al.'
    year = item['prism:coverDate'].split('-',1)[0]
    title = item['dc:title']
    source = item['prism:publicationName']
    doi = None
    if 'prism:doi' in item:
        doi = item['prism:doi']
    description = None
    if 'dc:description' in item:
        description = item['dc:description']
    ncitations = None
    if 'citedby-count' in item:
        ncitations = int(item['citedby-count'])
        
    articles_entry = {'id': s_id, 'label': '%s: %s (%s)'%(s_id, authors, year), 'author': authors, 'title': title, 'source': source, 'year': year, 'doi': doi, 'cit_score': ncitations, 'incomplete_record': None, 'description': description}
    
    #print(articles_entry)
    
    articles['articles'].append(articles_entry)

print('... articles: %s citations %s' % (len(articles['articles']),len(citations)) )


# -----------------
# STEP 1b: Go through citedby and extract citations and article infomation
# -----------------
# Citedby data is better than references, so add this first
print('CITEDBY')
for item in combined_citedby['combined']:
    # If there are citedby
    if len(item) > 1:
        if item['opensearch:totalResults'] != '0':
            # Loop through all citedby
            #print('### %s ###' % item['id'] )
            for cby in item['entry']:
                #print(cby)
                #print('\n')
                cby_id = cby['dc:identifier'].split(':')[1]
                # Add citation
                citations.append( [cby_id, item['id']] )
                # Add article (if currently absent)
                if absent(cby_id):
                    articles['articles'].append( cby_entry(cby) )

print('... articles: %s citations %s' % (len(articles['articles']),len(citations)) )


# -----------------
# STEP 1c: Go through references and extract citations and article infomation
# -----------------
print('REFERENCES')
for item in combined_references['combined']:
    # If there are references
    if len(item) > 1:
        # Loop through all references
        for ref in item['reference']:
            # Add citation
            citations.append( [item['id'], ref['scopus-id']] )
            # Add article (if currently absent)
            if absent(ref['scopus-id']):
                articles['articles'].append( ref_entry(ref) )

print('... articles: %s citations %s' % (len(articles['articles']),len(citations)) )
#print(len(articles['articles']))


# -----------------
# STEP 2: Save network
# -----------------

## Create dictionary that can replace Scopus IDs with sequentially numbered IDs
#replace = {} # {'84988382911': 1, '84987617437': 2, ... '0022929232': 19493}
#replace_inv = {} # {'1': '84988382911', '2': '84987617437', ... '19493': '0022929232'}
#i = 1
#for article in articles['articles']:
#    replace[article['id']] = i
#    replace_inv[str(i)] = article['id']
#    i += 1
## Save this (just in case):
#with open('_temp/search03_replace.json', 'w') as f:
#    json.dump(replace, f)
#with open('_temp/search03_replace_inv.json', 'w') as f:
#    json.dump(replace_inv, f)
    
    
# -----------------
# STEP 2a: Save in as PAJEK file
# -----------------

#with open('data/search03.net', 'w') as pajek:
#    pajek.write('*Vertices %s\n' % len(articles['articles']) )
#    for article in articles['articles']:
#        pajek.write('%s "%s"\n' % (replace[article['id']], article['label']) )
#    pajek.write('*Arcs \n')
#    for citation in citations:
#        pajek.write('%s %s\n' % (replace[citation[0]], replace[citation[1]]) )


# -----------------
# STEP 2b: Save as CitNetExplorer files
# -----------------

#earliest = 2016
#for article in articles['articles']:
#     if article['year'] is not None:
#        if int(article['year']) < earliest:
#            earliest = int(article['year'])
#print('Earliest article is from %s' % earliest)
#
#with open('data/search03_CitNetExplorer_pub.txt', 'w') as CNE_pub:
#    CNE_pub.write('authors\ttitle\tsource\tyear\tdoi\tcit_score\tincomplete_record\n')
#    for article in articles['articles']:
#        year = earliest-1 if article['year'] is None else article['year']
#        cit_score = 1 # if article['cit_score'] < 0 else article['cit_score']
#        incomplete_record = 1 #if article['incomplete_record'] ... 
#        CNE_pub.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (article['author'], article['title'], article['source'], year, article['doi'], cit_score, incomplete_record))
#
#with open('data/search03_CitNetExplorer_cite.txt', 'w') as CNE_cite:
#    CNE_cite.write('citing_pub_index\tcited_pub_index\n')
#    for citation in citations:
#        CNE_cite.write('%s\t%s\n' % (replace[citation[0]], replace[citation[1]]) )
    

# -----------------
# STEP 2c: Save as GraphML file
# -----------------

with open('data/search03_GraphML2.graphml', 'w') as GraphML:
    GraphML.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    GraphML.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n')
    GraphML.write('<key id="label" for="node" attr.name="label" attr.type="string" />\n')
    GraphML.write('<key id="year" for="node" attr.name="year" attr.type="int" />\n')
    GraphML.write('<graph id="G" edgedefault="directed">\n')
    for article in articles['articles']:
        GraphML.write('\t<node id="%s"><data key="label">%s</data>' % (article['id'], article['label']) )
        if article['year'] is not None:
            GraphML.write('<data key="year">%s</data>' % article['year'] )
        GraphML.write('</node>\n')
    for citation in citations:
        GraphML.write('\t<edge source="%s" target="%s" />\n' % (citation[0], citation[1]) )
    GraphML.write('</graph>\n')
    GraphML.write('</graphml>\n')


# -----------------
# STEP 2d: Save as GraphML file
# -----------------

with open('_temp/titles2.csv', 'w') as csvfile:
    titles = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    titles.writerow(['ID', 'Title', 'Description', 'Citations', 'Year'])
    for article in articles['articles']:
        titles.writerow([article['id'], article['title'], article['description'], article['cit_score'], article['year']])
    
### -----

# Remove conference procedeeings introduction (often has no author, often has no references) 
# [... Will these no be excluded automatically when looking at largest connected component in graph?]

## Fix articles with few, zero or 'None' references
#reference_error = []
#for item in combined_references['combined']:
#    # if the list of references was missing/none exsisting.
#    if 'reference' not in item:
#        reference_error.append(item['id'])
#    
#    # if the number of references is speciously low
#    # Defining speciously low: Manually sort articles according to number of references, then manually check if number of references in PDF matches the number reported. If not then jump down the list to the next number of references. There were inconsistencies in the articles with less than three references. In the data there are 14 articles with exactly 3 references, of these 12 also had 3 references in the PDF (unable to find PDF file for the last 2 remainng article).
#    elif len(item['reference']) < 3:
#        reference_error.append(item['id'])
#        
## This gives a total 105 articles (92 with none existing references and 13 with a speciously low number of references)
#print( reference_error )


# Fix articles with 'None' cited-by (e.g. no aurthor-field in metadata)

# Fix citedby for those articles where the difference in citedby-count and citedby-searchcount is outlier.

