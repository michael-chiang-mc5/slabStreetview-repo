# run with Rscript createImages.r
# requires R ver >=3.4

# See https://github.com/dkahle/ggmap
# installing requires R v3.4, see https://cran.rstudio.com/bin/linux/ubuntu/README.html
#install.packages("ggmap", lib="Rpackages/")

# specific to server
library('crayon',lib.loc='Rpackages')
library('withr',lib.loc='Rpackages')
library('ggplot2',lib.loc='Rpackages')
library('ggmap',lib.loc='Rpackages')
library('labeling',lib.loc='Rpackages')


# read csv file
MyData <- read.csv(file="../../../media/Sign.csv", header=TRUE, sep="\t",stringsAsFactors = FALSE)
lon=MyData[['longitude']]
lat=MyData[['latitude']]

# Choose between stamen map and google map
map <- get_map(location=c(lon=-118.17687109859778, lat=34.00464406169281), zoom = 11, color = "bw", scale = 2, maptype = "roadmap")

# plot number of signs on map
png(filename="../../../media/Sign.png", width=1280, height=1280)
# See http://ggplot2.tidyverse.org/reference/geom_point.html for same aesthetic options
# Also see: https://rpubs.com/jiayiliu/ggmap_examples
df <- data.frame(lon=lon, lat=lat)
ggmap(map) + geom_point(aes(x=lon,y=lat),data=df) + geom_point(size=3,alpha=0.3)
dev.off()
