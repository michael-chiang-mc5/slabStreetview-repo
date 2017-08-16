# creates supporting_files/census.csv
#   This file gives demographic information for each census tract


# census tracks language! https://www.census.gov/topics/population/language-use/about.html
# see https://www.socialexplorer.com/data/ACS2010/metadata/?ds=ACS10&table=B16005

# race including hispanic
# https://www.socialexplorer.com/data/C2010/metadata/?ds=SF1&table=P0050?

# documentation: https://cran.r-project.org/web/packages/acs/acs.pdf

# read http://zevross.com/blog/2015/10/14/manipulating-and-mapping-us-census-data-in-r-using-the-acs-tigris-and-leaflet-packages-3/#census-data-the-easyer-way

library(tigris)
library(acs)
library(stringr)
library(dplyr)

# 06037 = Los Angeles County in California
# 06 = California
# 037 = LA county
tracts <- tracts(state = 'CA', county = c(37), cb=TRUE)

# acs
api.key.install(key="d14c0e682b2d6357226f4a72665fe3c3ae9e9e91")
# create a geographic set to grab tabular data (acs)
geo<-geo.make(state=c("CA"),
              county=c(37), tract="*")


# Tables for census:
# https://www.socialexplorer.com/data/C2010/metadata/?ds=SF1
census_data<-acs.fetch(endyear = 2010, dataset='sf1', geography = geo,
                       table.number = "P5", col.names = "pretty")

# possible methods
#  acs.colnames
#  acs.units
#  currency.year
#  endyear
#  estimate
#  geography
#  modified
#  span
#  standard.error
#  sum
#  summary
#  confit
attr(census_data,'acs.colnames')
#  [1] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Total population"                                                          
#  [2] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:"                                                   
#  [3] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   White alone"                                     
#  [4] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Black or African American alone"                 
#  [5] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   American Indian and Alaska Native alone"         
#  [6] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Asian alone"                                     
#  [7] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Native Hawaiian and Other Pacific Islander alone"
#  [8] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Some Other Race alone"                           
#  [9] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Two or More Races"                               
#  [10] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Hispanic or Latino:   Two or More Races"                                   
#  [11] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Hispanic or Latino:   White alone"                                         
#  [12] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Hispanic or Latino:   Black or African American alone"                     
#  [13] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Hispanic or Latino:   American Indian and Alaska Native alone"             
#  [14] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Hispanic or Latino:   Asian alone"                                         
#  [15] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Hispanic or Latino:   Native Hawaiian and Other Pacific Islander alone"    
#  [16] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Hispanic or Latino:   Some Other Race alone"                               
#  [17] "P5. HISPANIC OR LATINO ORIGIN BY RACE: Hispanic or Latino:   Two or More Races"     


# convert to a data.frame for merging
df <- data.frame(paste0(str_pad(census_data@geography$state, 2, "left", pad="0"), 
                               str_pad(census_data@geography$county, 3, "left", pad="0"), 
                               str_pad(census_data@geography$tract, 6, "left", pad="0")), 
                                census_data@estimate[,c("P5. HISPANIC OR LATINO ORIGIN BY RACE: Total population",
                                                  "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   White alone",
                                                  "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Black or African American alone",
                                                  "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   American Indian and Alaska Native alone",
                                                  "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Asian alone",
                                                  "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Native Hawaiian and Other Pacific Islander alone",
                                                  "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Some Other Race alone",
                                                  "P5. HISPANIC OR LATINO ORIGIN BY RACE: Not Hispanic or Latino:   Two or More Races"
                                                 )],
                               stringsAsFactors = FALSE)



rownames(df)<-1:nrow(df)
names(df)<-c("FIPS", "total", "white","black","native","asian","pacific_islander","other","two_or_more")
df$hispanic = df$total - df$white - df$black - df$native - df$asian - df$pacific_islander - df$other - df$two_or_more
write.csv(df, file = "supporting_files/census.csv",row.names=F)
