# See https://github.com/dkahle/ggmap
library(ggmap)

# read csv file
MyData <- read.csv(file="../streetviewInterface/mySite/media/MapPoint.csv", header=TRUE, sep="\t",stringsAsFactors = FALSE)
lon=MyData[['longitude']]
lat=MyData[['latitude']]

# Choose between stamen map and google map
map <- get_map(location=c(lon=-118.17687109859778, lat=34.00464406169281), zoom = 11, color = "bw", scale = 2, maptype = "roadmap")

# plot number of signs on map
png(filename="output/total_mapPoints.png", width=1280, height=1280)
# See http://ggplot2.tidyverse.org/reference/geom_point.html for same aesthetic options
# Also see: https://rpubs.com/jiayiliu/ggmap_examples
df <- data.frame(lon=lon, lat=lat)
ggmap(map) + geom_point(aes(x=lon,y=lat),data=df) + geom_point(size=3,alpha=0.3)
dev.off()
