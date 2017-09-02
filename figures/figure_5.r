
library(ggmap)
languages = c('en','es','ko','zh')

# read csv file
MyData <- read.csv(file="../streetviewInterface/mySite/output/MapPoints.csv", header=TRUE, sep="\t",stringsAsFactors = FALSE)
is_ocr <- !is.na(MyData$en_count)
df <- data.frame(
  lon=MyData$longitude[is_ocr],
  lat=MyData$latitude[is_ocr],
  en=MyData$en_count[is_ocr],
  es=MyData$es_count[is_ocr],
  ko=MyData$ko_count[is_ocr],
  zh=MyData$zh_count[is_ocr],
  census_tracts=MyData$census_tracts[is_ocr]
)
df$total = df$es + df$ko + df$zh + df$en

#
original_df = MyData
for (language in languages) {
  original_df[[paste(language,"_percent",sep="")]] <- c(NA)
}

# 
for (census_tract in unique(df$census_tract)){
  idx = df$census_tracts == census_tract
  for (language in languages) {
    num_ethnic_word = sum(df[[language]][idx])
    num_total_word  = sum(df$total[idx])
    percent_ethnic_word = num_ethnic_word / num_total_word
    original_df[[paste(language,"_percent",sep="")]][original_df$census_tracts==census_tract] = percent_ethnic_word
  }
}





map <- get_map(location=c(lon=-118.27687109859778, lat=34.04464406169281), zoom = 13, color = "bw", scale = 2, maptype = "roadmap")

df = original_df
for (language in languages) {
  print(language)
  png(filename=paste("output/",language,".png",sep=""), width=1280, height=1280)
  print(ggmap(map) + geom_point(aes(x=df$lon,y=df$lat,color=df[[paste(language,"_percent",sep="")]]),data=df,na.rm = TRUE) + geom_point(size=3,alpha=0.3) + scale_color_gradientn(colors=rainbow(3)))
  dev.off()
}
