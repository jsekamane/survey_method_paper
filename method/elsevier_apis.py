# coding=utf-8

# Request key from https://dev.elsevier.com
from api_key import key

# Libraries
import requests
import json
import re
import copy
from logger import log


# =================
# Fetch the data related to the specified scopus-id. Fetches data from either Elsevier's APIs or the local cache (if previously fetched). 
# =================
def fetch_data(s_id, **kwargs):
    verbose = kwargs.get('verbose', False)

    # Read the local cache register.
    with open('local_cache.txt', 'r') as local_cache:
        local_cache_register = local_cache.read().splitlines()
        
    # If local cache, then return this.
    if s_id in local_cache_register:
        if verbose:
            print('Retriving data from local cache (%s)' % s_id)
        with open('local_cache/metadata_%s.json'%s_id, 'r') as d:
            metadata = json.load(d)
        with open('local_cache/references_%s.json'%s_id, 'r') as d:
            references = json.load(d)
        with open('local_cache/citedby_%s.json'%s_id, 'r') as d:
            citedby = json.load(d)
       
    else:
        print('Retriving data from Elsevier (%s)' % s_id)
        # Retrives metadata, references and cited-by from Elsevier
        
        
        # -----------------
        # STEP 1: Retrive metadata and additional infomation on references ('view=FULL').
        # -----------------
        params_meta = {'view': 'FULL', 'httpAccept': 'application/json'}
        r_meta = requests.get('http://api.elsevier.com/content/abstract/scopus_id/%s'%s_id, headers=key, params=params_meta)
        log(r_meta)
        r_meta.raise_for_status()
        r_meta_raw = r_meta.json()
        
            
        # -----------------
        # STEP 2: Retrive references
        # -----------------
        params_ref = {'view': 'REF', 'httpAccept': 'application/json'}
        r_ref = requests.get('http://api.elsevier.com/content/abstract/scopus_id/%s'%s_id, headers=key, params=params_ref)
        log(r_ref)
        r_ref.raise_for_status()
        r_ref_raw = r_ref.json()
        
        # In case of no references
        references = {}
        total_references = None
        
        # If there is references
        if r_ref_raw['abstracts-retrieval-response'] is not None:
            
            # Resolve pagination. Elsevier restricts the number of references per API-response/page to X items per page depending on entitlement.
            # Create new JSON with the initial references. Later we expand it with the references for subsequent pages. 
            #references = r_ref_raw.copy()
            total_references = int(r_ref_raw['abstracts-retrieval-response']['references']['@total-references'])
            per_page_references = len(r_ref_raw['abstracts-retrieval-response']['references']['reference'])
            i_references = per_page_references
            while i_references < total_references:
                # Add/change the API parameters to include the index
                params_ref['startref'] = i_references+1
                r_ref_page = requests.get('http://api.elsevier.com/content/abstract/scopus_id/%s'%s_id, headers=key, params=params_ref)
                log(r_ref_page)
                # Add references to one joined JSON
                r_ref_raw['abstracts-retrieval-response']['references']['reference'].extend( r_ref_page.json()['abstracts-retrieval-response']['references']['reference'] )
                # Set index for next page of references
                i_references += per_page_references

        
        # -----------------
        # STEP 3: Retrive cited-by through a search for articles that reference the last name of the first author and the title.
        # -----------------
        # In case of no cited-by
        citedby = {}
        total_results = None
        
        # If there is cited-by
        if 'dc:creator' in r_meta_raw['abstracts-retrieval-response']['coredata']:
            surname = r_meta_raw['abstracts-retrieval-response']['coredata']['dc:creator']['author'][0]['ce:surname'] # last name of first author
            #title = r_meta_raw['abstracts-retrieval-response']['coredata']['dc:title']
            title_array = re.split(r'[!\#()*+./:;<=>?@\[\\\]^_{|}~"]|-?[0-9]*?%', r_meta_raw['abstracts-retrieval-response']['coredata']['dc:title']) # title without special characters; the seperator is either one of the following special character !\#()*+./:;<=>?@\[\\\]^_{|}~ or a percentage (-7% or 100%)
            title = '} {'.join(str(title_part.strip()) for title_part in title_array) # join array to form a string which will query exact phases/parts of title. First removes leading and traling whitespace.
            #title = re.split(r'[!\#()*+,./:;<=>?@\[\\\]^_{|}~]', r_meta_raw['abstracts-retrieval-response']['coredata']['dc:title'], 1)[0] # first part of title before any special characters.
            #year = r_meta_raw['abstracts-retrieval-response']['coredata']['prism:coverDate'].partition('-')[0] # return only the year, not entire date.
        
            params_cite = {'httpAccept': 'application/json', 'query': 'REFAUTHLASTNAME(%s) AND REFTITLE({%s})' % (surname, title)}
            r_cite = requests.get('http://api.elsevier.com/content/search/scopus', headers=key, params=params_cite)
            log(r_cite)
            r_cite.raise_for_status()
            r_cite_raw = r_cite.json()
        
            # Resolve pagination. Elsevier restricts the number of search results per API-response/page to X items per page depending on entitlement.
            # Create new JSON with the initial search results. Later we expand it with the search results for subsequent pages. 
            citedby = r_cite_raw.copy()
            total_results = int(r_cite_raw['search-results']['opensearch:totalResults'])
            per_page_results = int(r_cite_raw['search-results']['opensearch:itemsPerPage'])
            i_results = per_page_results
            if total_results > 500: raise Exception('Possible error: more than 500 papers cite this')
            while i_results < total_results:
                # Add/change the API parameters to include the index
                params_cite['start'] = i_results
                r_cite_page = requests.get('http://api.elsevier.com/content/search/scopus', headers=key, params=params_cite)
                log(r_cite_page)
                # Add search results to one joined JSON
                citedby['search-results']['entry'].extend( r_cite_page.json()['search-results']['entry'] )
                # Set index for next page of search results
                i_results += per_page_results
            
        
        # -----------------
        # Step 4: Slightly restucture metadata, combine references info, and save data
        # -----------------
        coredata = r_meta_raw['abstracts-retrieval-response']['coredata']
        authors = r_meta_raw['abstracts-retrieval-response']['authors']
        if authors is None: authors = {'author': []}
        metadata = coredata.copy()
        metadata.update(authors)
        metadata.update({'citedby-searchcount': str(total_results)})
        metadata.update({'reference-count': str(total_references)})
        # Combine reference data with the extra reference infomation (obtained through the abstract retrieval process in step 1)
        references = copy.deepcopy(r_ref_raw)
        # If there is references and extra references
        if r_ref_raw['abstracts-retrieval-response'] is not None and r_meta_raw['abstracts-retrieval-response']['item']['bibrecord']['tail'] is not None:
            # Secondary check to see if there are extra references
            if 'reference' in r_meta_raw['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']:
                refs_extra = r_meta_raw['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']['reference']
                # If there is only one reference, then it is not a list
                if isinstance(refs_extra, list):
                    # For each of the extra references copy infomation into references (assuming same ordering)
                    for i, ref in enumerate(refs_extra):
                        # New '@id_extra' duplicate of '@id' or None if '@id' does not exists (for debugging at later stage).
                        ref['@id_extra'] = ref.get('@id', None)
                                        
                        # CAUTION! Assumes that order of references is identical in the two lists.
                        references['abstracts-retrieval-response']['references']['reference'][i].update( ref )
                else:
                    ref = refs_extra.copy()
                    ref['@id_extra'] = ref.get('@id', None)
                    
                    # CAUTION! Assumes that order of references is identical in the two lists.
                    references['abstracts-retrieval-response']['references']['reference'][0].update( ref )
                    
        
                
        # Backup raw files
        with open('local_cache/_raw/raw_abstract_%s.json'%s_id, 'w') as f:
            json.dump(r_meta_raw, f)
        with open('local_cache/_raw/raw_ref_%s.json'%s_id, 'w') as f:
            json.dump(r_ref_raw, f)
        # Save files   
        with open('local_cache/metadata_%s.json'%s_id, 'w') as f:
            json.dump(metadata, f)
        with open('local_cache/references_%s.json'%s_id, 'w') as f:
            json.dump(references, f)
        with open('local_cache/citedby_%s.json'%s_id, 'w') as f:
            json.dump(citedby, f)
            
        # Save Scorpus ID to local cache register
        with open('local_cache.txt', 'a') as local_cache:
            local_cache.write(s_id + '\n')
    

    # return multiple JSON files
    return metadata, references, citedby