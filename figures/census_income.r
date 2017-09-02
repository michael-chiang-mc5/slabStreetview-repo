# Tables for census: https://www.socialexplorer.com/data/ACS2015_5yr/metadata/?ds=ACS15_5yr
tmp <-acs.fetch(endyear = 2010, dataset='sf1', geography = geo,
                table.number = "P12", col.names = "pretty")

# to see columnn names: attr(tmp,'acs.colnames')

# convert to a data.frame for merging
df_sex <- data.frame(paste0(str_pad(tmp@geography$state, 2, "left", pad="0"), 
                            str_pad(tmp@geography$county, 3, "left", pad="0"), 
                            str_pad(tmp@geography$tract, 6, "left", pad="0")), 
                     tmp@estimate[,c("P12. Sex By Age: Male:",
                                     "P12. Sex By Age: Total population"
                     )],
                     stringsAsFactors = FALSE)



rownames(df_sex)<-1:nrow(df_sex)
names(df_sex)<-c("FIPS", "pop_male","pop_total")
df_sex$percent_male = df_sex$pop_male/df_sex$pop_total

# drop pop_male, pop_total columns
drops <- c("pop_male","pop_total")
df_sex <- df_sex[ !(names(df_sex) %in% drops)]