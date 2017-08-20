# creates supporting_files/census.csv
#   This file gives demographic information for each census tract

# TODO: look at different datasets 
# https://www.socialexplorer.com/data/metadata/
# health, voting in presidential election, voting in senate election
# get language from ACS

# documentation: https://cran.r-project.org/web/packages/acs/acs.pdf

# read http://zevross.com/blog/2015/10/14/manipulating-and-mapping-us-census-data-in-r-using-the-acs-tigris-and-leaflet-packages-3/#census-data-the-easyer-way

library(tigris)
library(acs)
library(stringr)
library(dplyr)

# 06037 = Los Angeles County in California
# 06 = California
# 037 = LA county
# tracts <- tracts(state = 'CA', county = c(37), cb=TRUE)

# acs
api.key.install(key="d14c0e682b2d6357226f4a72665fe3c3ae9e9e91")
# create a geographic set to grab tabular data (acs)
geo<-geo.make(state=c("CA"),
              county=c(37), tract="*")

# to see columnn names: attr(census_data,'acs.colnames')

source('census_age.r')
source('census_race.r')
source('census_sex.r')
df <- merge(df_race, df_age, by="FIPS") 
df <- merge(df, df_sex, by="FIPS")




write.csv(df, file = "supporting_files/census.csv",row.names=F)
