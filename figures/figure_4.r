library(ggmap)

MyData <- read.csv(file="../streetviewInterface/mySite/output/MapPoints.csv", header=TRUE, sep="\t",stringsAsFactors = FALSE)
is_ocr <- !is.na(MyData$en_count)
df <- data.frame(
  lon=MyData$longitude[is_ocr],
  lat=MyData$latitud[is_ocr],
  en=MyData$en_count[is_ocr],
  es=MyData$es_count[is_ocr],
  ko=MyData$ko_count[is_ocr],
  zh=MyData$zh_count[is_ocr]
)
df$total = df$es + df$ko + df$zh + df$en






map <- get_map(location=c(lon=-118.27687109859778, lat=34.04464406169281), zoom = 14, color = "bw", scale = 2, maptype = "roadmap")


png(filename="output/linguistic_landscape.png", width=1280, height=1280)
#ggmap(map) + geom_point(aes(x=df$lon,y=df$lat,color=df$ko/df$total),data=df) + geom_point(size=3,alpha=0.3) + scale_colour_gradientn(colours = c("blue","red"),values=c(0,0.1)) 
(ggmap(map) + geom_point(aes(x=df$lon,y=df$lat),data=df,col="orange",size=df$ko/df$total*100,alpha=0.4)
            + geom_point(aes(x=df$lon,y=df$lat),data=df,col="blue",size=df$zh/df$total*100,alpha=0.4)
            + geom_point(aes(x=df$lon,y=df$lat),data=df,col="green",size=df$es/df$total*100,alpha=0.4)  
            + scale_size_continuous(range=c(0,.1)))
dev.off()

png(filename="output/linguistic_landscape.png", width=1280, height=1280)