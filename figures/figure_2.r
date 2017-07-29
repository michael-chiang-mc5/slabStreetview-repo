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
for (census_tract in unique(df$census_tract)){
  df$white[df$census_tract == census_tract] =  demographics$white[demographics$FIPS == census_tract]
  df$black[df$census_tract == census_tract] =  demographics$black[demographics$FIPS == census_tract]
  df$asian[df$census_tract == census_tract] =  demographics$asian[demographics$FIPS == census_tract] + demographics$pacific_islander[demographics$FIPS == census_tract]
  df$hispanic[df$census_tract == census_tract] =  demographics$hispanic[demographics$FIPS == census_tract]
  df$other[df$census_tract == census_tract] =  demographics$native[demographics$FIPS == census_tract] + demographics$other[demographics$FIPS == census_tract] + demographics$two_or_more[demographics$FIPS == census_tract]
  df$total[df$census_tract == census_tract] = demographics$total[demographics$FIPS == census_tract]
}


map <- get_map(location=c(lon=-118.27687109859778, lat=34.04464406169281), zoom = 13, color = "bw", scale = 2, maptype = "roadmap")


# plot number of signs on map
png(filename="output/demographic_hispanic.png", width=1280, height=1280)
ggmap(map) + geom_point(aes(x=df$lon,y=df$lat,color=df$hispanic/df$total),data=df) + geom_point(size=3,alpha=0.3) + scale_color_gradientn(colors=rainbow(3))
dev.off()

