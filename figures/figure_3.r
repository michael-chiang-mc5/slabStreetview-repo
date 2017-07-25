library(ggmap)

MyData <- read.csv(file="../streetviewInterface/mySite/output/MapPoints.csv", header=TRUE, sep="\t",stringsAsFactors = FALSE)
df <- data.frame(
  lon=MyData[['longitude']],
  lat=MyData[['latitude']],
  census_tracts=MyData[['census_tracts']]
)


data <- read.csv("supporting_files/500_Cities__Census_Tract-level_Data__GIS_Friendly_Format_.csv", header=TRUE, sep=",",stringsAsFactors = FALSE)
# names:
#[1] "StateAbbr"              "PlaceName"              "PlaceFIPS"              "TractFIPS"              "Place_TractID"          "population2010"        
#[7] "ACCESS2_CrudePrev"      "ACCESS2_Crude95CI"      "ARTHRITIS_CrudePrev"    "ARTHRITIS_Crude95CI"    "BINGE_CrudePrev"        "BINGE_Crude95CI"       
#[13] "BPHIGH_CrudePrev"       "BPHIGH_Crude95CI"       "BPMED_CrudePrev"        "BPMED_Crude95CI"        "CANCER_CrudePrev"       "CANCER_Crude95CI"      
#[19] "CASTHMA_CrudePrev"      "CASTHMA_Crude95CI"      "CHD_CrudePrev"          "CHD_Crude95CI"          "CHECKUP_CrudePrev"      "CHECKUP_Crude95CI"     
#[25] "CHOLSCREEN_CrudePrev"   "CHOLSCREEN_Crude95CI"   "COLON_SCREEN_CrudePrev" "COLON_SCREEN_Crude95CI" "COPD_CrudePrev"         "COPD_Crude95CI"        
#[31] "COREM_CrudePrev"        "COREM_Crude95CI"        "COREW_CrudePrev"        "COREW_Crude95CI"        "CSMOKING_CrudePrev"     "CSMOKING_Crude95CI"    
#[37] "DENTAL_CrudePrev"       "DENTAL_Crude95CI"       "DIABETES_CrudePrev"     "DIABETES_Crude95CI"     "HIGHCHOL_CrudePrev"     "HIGHCHOL_Crude95CI"    
#[43] "KIDNEY_CrudePrev"       "KIDNEY_Crude95CI"       "LPA_CrudePrev"          "LPA_Crude95CI"          "MAMMOUSE_CrudePrev"     "MAMMOUSE_Crude95CI"    
#[49] "MHLTH_CrudePrev"        "MHLTH_Crude95CI"        "OBESITY_CrudePrev"      "OBESITY_Crude95CI"      "PAPTEST_CrudePrev"      "PAPTEST_Crude95CI"     
#[55] "PHLTH_CrudePrev"        "PHLTH_Crude95CI"        "SLEEP_CrudePrev"        "SLEEP_Crude95CI"        "STROKE_CrudePrev"       "STROKE_Crude95CI"      

# CHECKUP_CrudePrev: doctor checup
# DENTAL_CrudePrev: dental
# MHLTH_CrudePrev: mental helath
# PHLTH_CrudePrev: physical health


df$checkup <- c(0)
for (census_tract in unique(df$census_tracts)) {
  df$checkup[df$census_tracts == census_tract] =  data$CHECKUP_CrudePrev[data$TractFIPS == census_tract]
}


map <- get_map(location=c(lon=-118.27687109859778, lat=34.04464406169281), zoom = 14, color = "bw", scale = 2, maptype = "roadmap")


# plot number of signs on map
png(filename="output/checkups.png", width=1280, height=1280)
ggmap(map) + geom_point(aes(x=df$lon,y=df$lat,color=df$checkup),data=df) + geom_point(size=3,alpha=0.3) + scale_color_gradientn(colors=rainbow(3))
dev.off()
