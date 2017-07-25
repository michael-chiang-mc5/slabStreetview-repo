library(ggmap)

# read csv file
MyData <- read.csv(file="../streetviewInterface/mySite/output/MapPoints.csv", header=TRUE, sep="\t",stringsAsFactors = FALSE)
df <- data.frame(
  lon=MyData[['longitude']],
  lat=MyData[['latitude']],
  census_tracts=MyData[['census_tracts']]
)



demographics <- read.csv(file="supporting_files/census.csv", header=TRUE, sep=",",stringsAsFactors = FALSE)
df$white <- c(0)
df$black <- c(0)
df$asian <- c(0)
df$other <- c(0)
df$hispanic <- c(0)
for (census_tract in unique(df$census_tracts)){
  df$white[df$census_tracts == census_tract] =  demographics$white[demographics$tract == census_tract]
  df$black[df$census_tracts == census_tract] =  demographics$black[demographics$tract == census_tract]
  df$asian[df$census_tracts == census_tract] =  demographics$asian[demographics$tract == census_tract] + demographics$pacific_islander[demographics$tract == census_tract]
  df$hispanic[df$census_tracts == census_tract] =  demographics$hispanic[demographics$tract == census_tract]
  df$other[df$census_tracts == census_tract] =  demographics$native[demographics$tract == census_tract] + demographics$other[demographics$tract == census_tract] + demographics$two_or_more[demographics$tract == census_tract]
  df$total[df$census_tracts == census_tract] = demographics$total[demographics$tract == census_tract]
}


map <- get_map(location=c(lon=-118.27687109859778, lat=34.04464406169281), zoom = 14, color = "bw", scale = 2, maptype = "roadmap")


# plot number of signs on map
png(filename="output/demographic_hispanic.png", width=1280, height=1280)
ggmap(map) + geom_point(aes(x=df$lon,y=df$lat,color=df$hispanic/df$total),data=df) + geom_point(size=3,alpha=0.3) + scale_color_gradientn(colors=rainbow(3))
dev.off()

