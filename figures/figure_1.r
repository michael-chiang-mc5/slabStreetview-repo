sign_count_threshold <- 20

# See https://github.com/dkahle/ggmap
library(ggmap)

# read csv file
MyData <- read.csv(file="../streetviewInterface/mySite/output/MapPoints.csv", header=TRUE, sep=",",stringsAsFactors = FALSE)
lon=MyData[['longitude']]
lat=MyData[['latitude']]
num_signs <- MyData[['num_boundingboxes']]
zone_code = MyData[['zone_code']]


num_signs_scaled <- num_signs
num_signs_scaled[num_signs_scaled> sign_count_threshold] <- sign_count_threshold

# categorizes zone codes
# Commercial = 1
# Industrial = 2
# Residential = 3
# Everything else = 0
categorize_zone_code <- function(zone_code){
	zone_code[zone_code == 'CR' | zone_code == 'C1' | zone_code == 'C1.5' | zone_code == 'C2' | zone_code == 'C4' | zone_code == 'C5' | zone_code == 'CM' ] = 1

	zone_code[zone_code == 'RE40' | zone_code == 'RE20' | zone_code == 'RE15' | zone_code == 'RE11' | zone_code == 'RE9' | zone_code == 'RS' | zone_code == 'R1' | zone_code == 'RU' | zone_code == 'RZ2.5' | zone_code == 'RZ3' | zone_code == 'RZ4' | zone_code == 'RW1' | zone_code == 'R2' | zone_code == 'RD1.5' | zone_code == 'RD2' | zone_code == 'RD3' | zone_code == 'RD4' | zone_code == 'RD5'| zone_code == 'RD6'| zone_code == 'RMP'| zone_code == 'RW2'| zone_code == 'R3'| zone_code == 'RAS3'| zone_code == 'R4'| zone_code == 'RAS4'| zone_code == 'R5' ] = 3
	
	zone_code[zone_code == 'MR1' | zone_code == 'M1' | zone_code == 'MR2' | zone_code == 'M2' | zone_code == 'M3' ] = 2

	zone_code[zone_code == 'A1' | zone_code == 'A2' | zone_code == 'RA' | zone_code == 'P' | zone_code == 'PB' | zone_code == 'OS'| zone_code == 'PF'| zone_code == 'SL'| zone_code == 'unknown'] = 0

	zone_code[zone_code != 0 & zone_code != 1 & zone_code != 2 & zone_code != 3 ] = 0

	zone_code = as.integer(zone_code)
	
	return(zone_code)
}

zone_code_categorized = categorize_zone_code(zone_code)

# Choose between stamen map and google map
map <- get_map(location = c(lon = -118.27687109859778, lat = 34.04464406169281), zoom = 14, color = "bw", scale = 2, maptype = "roadmap")
#map <- get_stamenmap(bbox = c(left = -118.324385, bottom = 33.991552, right = -118.223963, top = 34.065814), zoom = 13, maptype = "watercolor")





# The 'base' of this is ggmap(map). This will just 'print' your map.
png(filename="num_signs.png", width=1280, height=1280)

# create overlay
# See http://ggplot2.tidyverse.org/reference/geom_point.html for same aesthetic options
# Also see: https://rpubs.com/jiayiliu/ggmap_examples
#df <- data.frame(lon=c(-118.27687109859778), lat=c(34.04464406169281))
df <- data.frame(lon=lon, lat=lat)
#ggmap(map) + geom_point(aes(x=lon,y=lat),data=df) + geom_point(size=3,alpha=0.3)
ggmap(map) + geom_point(aes(x=lon,y=lat,color= num_signs_scaled),data=df) + geom_point(size=3,alpha=0.3) + scale_color_gradientn(colors=rainbow(3))
dev.off()



# 0 is unknown zone
# 1 is commercial
# 2 is industrial
# 3 is residential
png(filename="zones.png", width=1280, height=1280)
df <- data.frame(lon=lon, lat=lat)
ggmap(map) + geom_point(aes(x=lon,y=lat,color=zone_code_categorized),data=df) + geom_point(size=3,alpha=0.3) + scale_color_gradientn(colors=rainbow(4))
dev.off()



