# coding=utf-8

# =================
# Extract relevant infomation for the metadata, references or citedby and format it.
# =================

# Example of format of entry in articles:
##{
##    'id': 84877046264,
##    'label': '84877046264: Hirth (2014)',
##    'author': 'Hirth',
##    'title': 'The market value of variable renewables: The effect of solar wind power variability on their relative price',
##    'source': 'Energy Economics',
##    'year': 2014,
##    'doi': '10.1016/j.eneco.2013.02.004',
##    'cit_score': 102,
##    'incomplete_record': None,
##    'description': 'This paper provides a comprehensive discussion of the market value of variable renewable energy (VRE) ... more difficult to accomplish than as many anticipate. © 2013 Elsevier B.V.'
##}

# Extract infomation from the metadata and format it for the list of articles.
def meta_entry(meta):
    s_id = meta['dc:identifier'].split(':')[1]
    authors = None
    if 'author' in meta and 'dc:creator' in meta:
        authors = meta['dc:creator']['author'][0]['ce:surname']
        if len(meta['author']) > 1:
            authors += ' et al.'
    year = int(meta['prism:coverDate'].split('-',1)[0])
    title = None
    if 'dc:title' in meta:
        title = meta['dc:title']
    source = None
    if 'prism:publicationName' in meta:
        source = meta['prism:publicationName']
    doi = None
    if 'prism:doi' in meta:
        doi = meta['prism:doi']
    description = None
    if 'dc:description' in meta:
        description = meta['dc:description']
    ncitations = None
    if 'citedby-count' in meta:
        ncitations = int(meta['citedby-count'])
        
    articles_entry = {'id': s_id, 'label': '%s: %s (%s)'%(s_id, authors, year), 'author': authors, 'title': title, 'source': source, 'year': year, 'doi': doi, 'cit_score': ncitations, 'incomplete_record': None, 'description': description}
    return articles_entry
    
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
    year = int(cby['prism:coverDate'].split('-',1)[0])
    doi = None
    if 'prism:doi' in cby:
        doi = cby['prism:doi']
    ncitations = None
    if 'citedby-count' in cby:
        ncitations = int(cby['citedby-count'])
    
    articles_entry = {'id': s_id, 'label': '%s: %s (%s)'%(s_id, authors, year), 'author': authors, 'title': title, 'source': source, 'year': year, 'doi': doi, 'cit_score': ncitations, 'incomplete_record': None, 'description': None}
    return articles_entry