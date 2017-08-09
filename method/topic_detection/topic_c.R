setwd("~/Dropbox/PhD/Papers/Survey_test/topic detection")

library(dplyr)
library(lazyeval)
library(tidytext)



# Topic detection function ------------------------------------------------

topics = function(module, criteria) {
  # where module is a string with the column name in the dataframe content,
  # that contains the classification/categorisation. And criteria (optional) is string 
  # with the column name used to sort papers. If no criteria, then returns most cited papers.
  
  if(missing(criteria)) criteria = 'citations'
  
  # Create a list of all the words that appears in any title, 
  # and count the number of times the word appears in each module.
  title_words = content %>%
    filter_( interp(~ !is.na(x), x=as.name(module)) ) %>%
    unnest_tokens(word, text) %>%
    group_by_(module, 'word') %>%
    count(sort = TRUE) %>%
    ungroup()
  # Count the total number of times the word appears.
  total_words = title_words %>% 
    group_by_(module) %>% 
    summarize(total = sum(n))
  # Merge the total_words into one big table.
  title_words = left_join(title_words, total_words, by=module)
  
  # tf-idf: find the words that are important (i.e., common) in a text, but not too common (too general).
  title_words = title_words %>%
    bind_tf_idf_('word', module, 'n')
  
  # Find the top 10 most used words in each module (measued using the tf-idf score).
  dots = list(~desc(tf_idf), ~n)
  topic = title_words %>%
    arrange_(module, .dots=dots) %>%
    group_by_(module) %>%
    slice(1:10)
  
  print(topic[1:20,])
  
  # Join the top 10 words into one comma-seperated string for each module
  each_word_by_module = formula(paste0("word~",module))
  topic_module = aggregate(each_word_by_module, data = topic, paste, collapse=', ')
  
  # Top 10 most cited/highest z-score papers in each module
  paper = content %>%
    arrange_(module, interp(~desc(x), x=as.name(criteria)) ) %>%
    group_by_(module) %>%
    slice(1:10) %>%
    subset(select=c('ID', 'title', criteria, module))
  each_paper_by_module = formula(paste0("title~",module))
  paper_module = aggregate(each_paper_by_module, data = paper, paste, collapse='\r')
    
  
  # Count the number of papers in each module, and
  # add the topic string (top 10 words) to each module,
  # and sort modules according to the number of papers within.
  result = as.data.frame(table(content[module]))
  names(result)[1] = module
  result = merge(result, topic_module, by=module, all.x=TRUE)
  result = merge(result, paper_module, by=module, all.x=TRUE)
  result = result[order(-result$Freq), ]
}


# Load data ---------------------------------------------------------------

# Scopus IDs and titles of all articles
titles = read.csv('metadata.csv', fileEncoding="UTF-8", stringsAsFactors = FALSE, colClasses=c(ID="character")) # , na.strings=""
titles$text = with(titles, paste(title, description, sep=" "))
titles$author[titles$author == ""] = NA
titles$title[titles$title == ""] = NA
titles$description[titles$description == ""] = NA
titles$source[titles$source == ""] = NA
titles$text[titles$text == " "] = NA
#complete_text = complete.cases(titles[, c('title', 'description')])
#titles[!complete_text,'text'] = NA
#colSums(is.na(titles))

# In the following datasets only the largest component/giant component is considered.

# Scopus IDs and modules based on modularity (i.e. 'modularity class' in Gephi which uses the Louvain's method). #modularity=0.823 
#module_modularity = read.csv('Module_modularity.csv')
# Scopus IDs and modules from first level of hierarchy (using Moduland2 in Cytoscape).
#module_moduleland2 = read.csv('Module_moduleland2_level1.csv') 
# Scopus IDs and modules from first level of hierarchy (using the 'minimize_nested_blockmodel_dl' function in Graph-tool)
#module_nestedblockmodel = read.csv('Module_nestedblockmodel_level1.csv') 
# Scopus IDs and modules based on modularity (i.e. 'modularity class' in Gephi which uses the Louvain's method). The edges are weigthed according to the number of Common Neighbours. #modularity=0.824 
#module_modularity_CNweighted = read.csv('Module_modularity_CN-weighted.csv')
# Scopus IDs and modules based on modularity (using louvain-igraph). #modularity=0.8242 
#module_louvain_u_mod = read.csv('Module_louvain_u_mod.csv')
# Scopus IDs and modules based on directed modularity  (using louvain-igraph). #modularity=0.8243
#module_louvain_d_mod = read.csv('Module_louvain_d_mod.csv')
# Scopus IDs and modules based on directed and weighted modularity (using louvain-igraph). The edges are weigthed according to the number of Common Neighbours. #modularity=0.8279 
#module_louvain_dw_mod = read.csv('Module_louvain_dw_mod.csv')
# Scopus IDs and modules on filtered graph based on directed and weighted modularity (using louvain-igraph). The edges are weigthed according to the number of Common Neighbours. #modularity=0.6162
module_louvain_fdw_mod = read.csv('Module_louvain_fdw_mod.csv', colClasses=c(ID="character"))

rm(content)
#content = merge(titles, module_modularity, by='ID', all.x=TRUE)
#names(content)[length(content)] = 'Module.Modularity'
#content = merge(content, module_moduleland2, by='ID', all.x=TRUE)
#names(content)[length(content)] = 'Module.Moduleland2.level1'
#content = merge(content, module_nestedblockmodel, by='ID', all.x=TRUE)
#names(content)[length(content)] = 'Module.NestedBlockmodel.level1'
#content = merge(content, module_modularity_CNweighted, by='ID', all.x=TRUE)
#names(content)[length(content)] = 'Module.Modularity.CN'
#content = merge(content, module_louvain_u_mod, by='ID', all.x=TRUE)
#names(content)[length(content)] = 'Module.ModularityL.u'
#content = merge(content, module_louvain_d_mod, by='ID', all.x=TRUE)
#names(content)[length(content)] = 'Module.ModularityL.d'
#content = merge(content, module_louvain_dw_mod, by='ID', all.x=TRUE)
#names(content)[length(content)-1] = 'Module.ModularityL.dw'
#names(content)[length(content)] = 'z.dw'


content = merge(titles, module_louvain_fdw_mod, by='ID', all.x=TRUE)
names(content)[length(content)-1] = 'Module.ModularityL.fdw'
names(content)[length(content)] = 'z.fdw'

#content_missing = content

# Missing data?
colSums(is.na(content))
# Give the missing data its own category
#content$Module.Modularity[is.na(content$Module.Modularity)] = 999
#content$Module.Moduleland2.level1[is.na(content$Module.Moduleland2.level1)] = 999
#content$Module.NestedBlockmodel.level1[is.na(content$Module.NestedBlockmodel.level1)] = 999
#content$Module.Modularity.CN[is.na(content$Module.Modularity.CN)] = 999
#content$Module.ModularityL.u[is.na(content$Module.ModularityL.u)] = 999
#content$Module.ModularityL.d[is.na(content$Module.ModularityL.d)] = 999
#content$Module.ModularityL.dw[is.na(content$Module.ModularityL.dw)] = 9999
#content$Module.ModularityL.fdw[is.na(content$Module.ModularityL.fdw)] = 999

colSums(is.na(content[which(!is.na(content$Module.ModularityL.fdw)),]))

# Result ------------------------------------------------------------------

#topics_Modularity.CN = topics("Module.Modularity.CN")
#topics_ModularityL.u = topics("Module.ModularityL.u")
#topics_ModularityL.d = topics("Module.ModularityL.d")
#topics_ModularityL.dw = topics("Module.ModularityL.dw", 'z.dw')
topics_ModularityL.fdw = topics("Module.ModularityL.fdw", 'z.fdw')

#write.csv(topics_Modularity.CN, file='Topics_modularity_CN.csv',fileEncoding="UTF-8", row.names=FALSE)
#write.csv(topics_ModularityL.u, file='Topics_modularityL_u.csv',fileEncoding="UTF-8", row.names=FALSE)
#write.csv(topics_ModularityL.d, file='Topics_modularityL_d.csv',fileEncoding="UTF-8", row.names=FALSE)
#write.csv(topics_ModularityL.dw, file='Topics_modularityL_dw.csv',fileEncoding="UTF-8", row.names=FALSE)
write.csv(topics_ModularityL.fdw, file='Topics_modularityL_fdw.csv',fileEncoding="UTF-8", row.names=FALSE)


# Plots ------------------------------------------------------------------

#png(filename="Topics_modularity_CN.png", height=800, width=1600, bg="white")
#barplot(topics_Modularity.CN[,2], names.arg=topics_Modularity.CN[,1], xlab="Modularity.CN", ylab="Number of papers")
#dev.off()
#png(filename="Topics_modularityL_u.png", height=800, width=1600, bg="white")
#barplot(topics_ModularityL.u[,2], names.arg=topics_ModularityL.u[,1], xlab="ModularityL.u", ylab="Number of papers")
#dev.off()
#png(filename="Topics_modularityL_d.png", height=800, width=1600, bg="white")
#barplot(topics_ModularityL.d[,2], names.arg=topics_ModularityL.d[,1], xlab="ModularityL.d", ylab="Number of papers")
#dev.off()
#png(filename="Topics_modularityL_dw.png", height=800, width=1600, bg="white")
#barplot(topics_ModularityL.dw[,2], names.arg=topics_ModularityL.dw[,1], xlab="ModularityL.dw", ylab="Number of papers")
#dev.off()
#png(filename="Topics_modularityL_fdw.png", height=800, width=1600, bg="white")
#barplot(topics_ModularityL.fdw[,2], names.arg=topics_ModularityL.fdw[,1], xlab="ModularityL.fdw", ylab="Number of papers", col="red")
#dev.off()

#plot(table(content_missing$Module.Modularity))
#plot(table(content_missing$Module.Moduleland2.level1))
#plot(table(content_missing$Module.NestedBlockmodel.level1))
#plot(table(content_missing$Module.NestedBlockmodel.level1))
#plot(table(content_missing$Module.Modularity.CN))
#plot(table(content_missing$Module.ModularityL.u))
#plot(table(content_missing$Module.ModularityL.d))
#plot(table(content_missing$Module.ModularityL.dw))
#plot(table(content_missing$Module.ModularityL.fdw))



