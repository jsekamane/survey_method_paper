Title: ...  
Date: ... (v01 DRAFT)  
Author: Jonas K. Sekamane

---

**Abstract:** ... alternative to/extension of keyword search, which will miss papers without keyword ... this may happen if keyword not present in main fields (title, abstract, keyword), or in case where authors use different terms (synonyms) ... [particularly useful for XXX] ... This paper presents an approach that expands keyword search by including all references and all that refer to any of the papers containing the keyword, ie. both *backward chaining* and *forward chaining* (Larsen 2002). Possible to continue with severals degrees of chaining.  However, quickly uncover a baffling nnumber of papers. To arrive at a more manageable number of papers and to improve relevance, the method in this paper (mainly) uses classification. ... We find [a significant number of articles that simple keyword search was unable to uncover], with only slightly more manual work required.

However the number of articles uncovered grows exponentially[^exp].
[^exp]: Starting from a single paper the expected number of uncovered papers after $d$ chains is $<k>^d$ (assuming no overlap), where $<k>$ is average degree of the citation network.

---

...

## Scopus API

... incomplete graph ... more specifically using the definition *crawled network* from Yan and Gregory (2011) ... While it is possible in other applications of graph theory to obtain a complete graph, in applications of scientific journal articles it is often impossible (time aspect; old and newly published. coverage aspect; reports, working papers, conferences papers, etc. source aspects: Scopus, google scholar, WOS, etc.).

Most methods and theoretical work on graph theory focuses on complete graphs.

... Data cleaning ... while the process below solve some of the issue (such as [Z]) ... it may be necessary to do [X] and [Y] ... 

### Data in examples

From Scopus. Collected using API. ... The keyword-papers can be both conferences papers and journal articles... written in english... although when performing backward and forward chaining we don't discriminate, and any type of material (report, book, working paper, etc.) in any language can be included ...

## Classification based on citation network

... While this may depend on the particular objective, in the cases presented here, it was enough to consider papers that are "once or twice removed" from the keyword-papers ...

... focus on the *largest connected component* (van Eck and Waltman 2014) ... in the examples in this paper, the papers exclude by this often deal with a different subject (e.g. ... ) or the introduction in conference proceedings (with keyword in title but no references or citations) ... however manual inspect of the papers discard at this step is recommended ...

[include degree distribution of the incomplete graph] ... in our incomplete/crawled citation network a majority of papers have a single link to rest of network. ... Without further information about the complete graph, we will assume that the such a paper belongs to the same class/community as its only neighbour. ... such papers/single links presumably carry little information about the community structure of the remaining network ... papers with a single link to the network, are thus temporally removed before running the classification algorithm... instead we classify these papers "by association*, same as neighbour.

... Yan and Gregory (2011) compare classification methods[^class] in various incomplete graphs ... of the two methods, which do not require to be told the number of communities in advance, the *Louvian* algorithm preformed best on a crawled network... In other studies comparing classification methods, but on complete graphs, the *infomap* often performs well. [Why don't you use infomap given the comparison here: Burgess (2016)] ... In this paper we use *Louvian* algorithm.

[^class]: *classification* algorithms are also known as *community detection* algorithms or *clustering* methods ...

... use *common neighbour* measure to weighted edges: Yan and Gregory (2012), Burgess (2016) ...

... to evaluate classification we employ similar method as Shibata, Kajikawa, Takeda and Matsushima (2008), namely for each class/community we calculate the top 10 tf-idf words that appear in title or abstract, and list the 10 most well connected papers in each cluster/class/community (highest z-score) ... 


## Preliminary results

### Example: Electricity market mechanisms

### Example: Geology / sediment analysis


## Discussion

There is not a straightforward objective evaluation criteria for the classification method. (An issue broadly present in all *unsupervised learning* methods). ... it has been referred to as an art (Gulbahce and Lehmann 2008).

Perhaps use: https://www.metachris.com/pdfx/


*****