# Tables for census: https://www.socialexplorer.com/data/C2010/metadata/?ds=SF1
tmp <-acs.fetch(endyear = 2010, dataset='sf1', geography = geo,
                table.number = "P5", col.names = "pretty")

# to see columnn names: attr(tmp,'acs.colnames')

# convert to a data.frame for merging
df_race <- data.frame(paste0(str_pad(tmp@geography$state, 2, "left", pad="0"), 
                         str_pad(tmp@geography$county, 3, "left", pad="0"), 
                         str_pad(tmp@geography$tract, 6, "left", pad="0")), 
                         tmp@estimate[,c("P5. HISPANIC OR LATINO ORIGIN BY RACE: Total population",
                                                 "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   White alone",
                                                 "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Black or African American alone",
                                                 "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   American Indian and Alaska Native alone",
                                                 "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Asian alone",
                                                 "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Native Hawaiian and Other Pacific Islander alone",
                                                 "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Some Other Race alone",
                                                 "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Two or More Races"
                                                 
                 )],
                 stringsAsFactors = FALSE)





rownames(df_race)<-1:nrow(df_race)
names(df_race)<-c("FIPS", "total", "white","black","native","asian","pacific_islander","other","two_or_more")
df_race$hispanic = df_race$total - df_race$white - df_race$black - df_race$native - df_race$asian - df_race$pacific_islander - df_race$other - df_race$two_or_more
