source('df_mappoint.r')

# creates a data frame "df_FIP" containing census tract level data:
#   sign_*  :  language count for signage (en, es, ko,zh, total)
#   pop_*   :  population count for tract (white, black, asian, hispanic, other)
#   FIP     :  FIP code for census tract
#  

# initialize output
df_FIP <- data.frame(
  FIP=unique(df_mappoint$FIP)
)

# read in census demographic data
# census.csv created by r script "census.r"
CensusData <- read.csv(file="supporting_files/census.csv", header=TRUE, sep=",",stringsAsFactors = FALSE)
# load into output
for (FIP in df_FIP$FIP) {
  CensusDataFIPS = CensusData[CensusData$FIPS == FIP,]
  df_FIP$pop_white[df_FIP$FIP == FIP]    =  CensusDataFIPS$white
  df_FIP$pop_black[df_FIP$FIP == FIP]    =  CensusDataFIPS$black
  df_FIP$pop_asian[df_FIP$FIP == FIP]    =  CensusDataFIPS$asian + CensusDataFIPS$pacific_islander
  df_FIP$pop_hispanic[df_FIP$FIP == FIP] =  CensusDataFIPS$hispanic
  df_FIP$pop_other[df_FIP$FIP == FIP]    =  CensusDataFIPS$native + CensusDataFIPS$other + CensusDataFIPS$two_or_more
  df_FIP$pop_total[df_FIP$FIP == FIP]    =  CensusDataFIPS$total
}


# calculate race percentages
df_FIP$percent_white = df_FIP$pop_white / df_FIP$pop_total
df_FIP$percent_black = df_FIP$pop_black / df_FIP$pop_total
df_FIP$percent_asian = df_FIP$pop_asian / df_FIP$pop_total
df_FIP$percent_hispanic = df_FIP$pop_hispanic / df_FIP$pop_total
df_FIP$percent_other = df_FIP$pop_other / df_FIP$pop_total


# get map point level data (sign count, lon/lat, census tract)
source('df_mappoint.r')
# load in map point level data
for (FIP in df_FIP$FIP){
  idx = df_mappoint$FIP == FIP
  tmp_nosum = df_mappoint[idx,]
  tmp_sum = colSums(tmp_nosum,na.rm=TRUE)
  fields_sum = c('sign_en','sign_es','sign_ko','sign_zh','sign_total')
  for (field in fields_sum) {
    df_FIP[[field]][df_FIP$FIP == FIP] = tmp_sum[[field]]    
  }
}

# calculate sign percentages
df_FIP$percent_lang_en = df_FIP$sign_en / df_FIP$sign_total
df_FIP$percent_lang_es = df_FIP$sign_es / df_FIP$sign_total
df_FIP$percent_lang_ko = df_FIP$sign_ko / df_FIP$sign_total
df_FIP$percent_lang_zh = df_FIP$sign_zh / df_FIP$sign_total


# load 500 cities data
# CHECKUP_CrudePrev: doctor checup
# DENTAL_CrudePrev: dental
# MHLTH_CrudePrev: mental helath
# PHLTH_CrudePrev: physical health
df_500cities <- read.csv("supporting_files/500_Cities__Census_Tract-level_Data__GIS_Friendly_Format_.csv", header=TRUE, sep=",",stringsAsFactors = FALSE)
for (FIP in df_FIP$FIP){
  df_FIP$checkup_doctor[df_FIP$FIP == FIP] =  df_500cities$CHECKUP_CrudePrev[df_500cities$TractFIPS == FIP]
  df_FIP$checkup_dentist[df_FIP$FIP == FIP] =  df_500cities$DENTAL_CrudePrev[df_500cities$TractFIPS == FIP]
  df_FIP$health_mental[df_FIP$FIP == FIP] =  df_500cities$MHLTH_CrudePrev[df_500cities$TractFIPS == FIP]
  df_FIP$health_physical[df_FIP$FIP == FIP] =  df_500cities$PHLTH_CrudePrev[df_500cities$TractFIPS == FIP]  
}
