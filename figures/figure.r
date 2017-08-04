MapPointData <- read.csv(file="../streetviewInterface/mySite/output/MapPoints.csv", header=TRUE, sep="\t",stringsAsFactors = FALSE)
df <- data.frame(
  lon=MapPointData$longitude,
  lat=MapPointData$latitud,
  sign_en=MapPointData$en_count,
  sign_es=MapPointData$es_count,
  sign_ko=MapPointData$ko_count,
  sign_zh=MapPointData$zh_count,
  sign_total=MapPointData$en_count+MapPointData$es_count+MapPointData$ko_count+MapPointData$zh_count,
  FIP=MapPointData$census_tracts
)

CensusData <- read.csv(file="supporting_files/census.csv", header=TRUE, sep=",",stringsAsFactors = FALSE)
for (census_tract in unique(df$FIP)){
  CensusDataFIPS <- CensusData[CensusData$FIPS == census_tract,]
  df$pop_white[df$FIP == census_tract]    =  CensusDataFIPS$white
  df$pop_black[df$FIP == census_tract]    =  CensusDataFIPS$black
  df$pop_asian[df$FIP == census_tract]    =  CensusDataFIPS$asian + CensusDataFIPS$pacific_islander
  df$pop_hispanic[df$FIP == census_tract] =  CensusDataFIPS$hispanic
  df$pop_other[df$FIP == census_tract]    =  CensusDataFIPS$native + CensusDataFIPS$other + CensusDataFIPS$two_or_more
  df$pop_total[df$FIP == census_tract]    =  CensusDataFIPS$total
}


#is_ocr <- !is.na(df$sign_en)
#df <- df[is_ocr,]

df_FIP <- data.frame(
  FIP=unique(df$FIP)
)
for (FIP in df_FIP$FIP){
  idx = df$FIP == FIP
  tmp = df[idx,]
  tmp = colSums(tmp,na.rm=TRUE)
  
  fields = c('sign_en','sign_es','sign_ko','sign_zh','sign_total',
            'pop_white','pop_black','pop_asian','pop_hispanic','pop_other','pop_total')
  for (field in fields) {
    df_FIP[[field]][df_FIP$FIP == FIP] = tmp[[field]]    
  }
}

png(filename="output/sign_vs_pop_spanish", width=1280, height=1280)
plot( 
      df_FIP$pop_hispanic/df_FIP$pop_total,
      df_FIP$sign_es/df_FIP$sign_total, 
      xlab="fraction hispanic population",
      ylab="fraction spanish signage")
dev.off()


png(filename="output/sign_vs_pop_korean", width=1280, height=1280)
plot( 
  df_FIP$pop_asian/df_FIP$pop_total,
  df_FIP$sign_ko/df_FIP$sign_total, 
  xlab="fraction asian population",
  ylab="fraction korean signage")
dev.off()





