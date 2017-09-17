# creates a data frame "df_mappoint" containing mapPoint level data:
#  lon
#  lat
#  sign_*
#  FIP
#  pop_*

# read in sign language count
MapPointData <- read.csv(file="../streetviewInterface/mySite/output/MapPoints.csv", header=TRUE, sep="\t",stringsAsFactors = FALSE)
df_mappoint <- data.frame(
  lon=MapPointData$longitude,
  lat=MapPointData$latitude,
  sign_en=MapPointData$en_count,
  sign_es=MapPointData$es_count,
  sign_ko=MapPointData$ko_count,
  sign_zh=MapPointData$zh_count,
  sign_total=MapPointData$en_count+MapPointData$es_count+MapPointData$ko_count+MapPointData$zh_count,
  FIP=MapPointData$census_tracts
)



