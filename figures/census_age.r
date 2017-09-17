# Tables for census: https://www.socialexplorer.com/data/C2010/metadata/?ds=SF1
tmp <-acs.fetch(endyear = 2010, dataset='sf1', geography = geo,
                       table.number = "P13", col.names = "pretty")

# to see columnn names: attr(tmp,'acs.colnames')

# convert to a data.frame for merging
df_age <- data.frame(paste0(str_pad(tmp@geography$state, 2, "left", pad="0"), 
                        str_pad(tmp@geography$county, 3, "left", pad="0"), 
                        str_pad(tmp@geography$tract, 6, "left", pad="0")), 
                     tmp@estimate[,c("P13. MEDIAN AGE BY SEX [3] (1 expressed decimal): Both sexes"
                 )],
                 stringsAsFactors = FALSE)



rownames(df_age)<-1:nrow(df_age)
names(df_age)<-c("FIPS", "median_age")
