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

# CHECKUP_CrudePrev: doctor checkup - Model-based estimate for crude prevalence of visits to doctor for routine checkup within the past year among adults aged >=18 years
# DENTAL_CrudePrev: dental checkup - Model-based estimate for crude prevalence of visits to dentist for routine checkup within the past year among adults aged >=18 years
# MHLTH_CrudePrev: mental helath   - Model-based estimate for crude prevalence of mental health not good for >=14 days among adults aged >=18 years
# PHLTH_CrudePrev: physical health - Model-based estimate for crude prevalence of physical health not good for >=14 days among adults aged >=18 years


outputs <- c('CHECKUP_CrudePrev','DENTAL_CrudePrev','MHLTH_CrudePrev','PHLTH_CrudePrev')

for (output in outputs) {
  df[[output]] <- c(0)
}

for (census_tract in unique(df$census_tracts)) {
  
  for (output in outputs) {
    vals = data[[output]][data$TractFIPS == census_tract]
    if (length(vals)==0) {
      df[[output]][df$census_tracts == census_tract] = NA   
    } else {
      df[[output]][df$census_tracts == census_tract] = vals      
    }
  }
}


map <- get_map(location=c(lon=-118.27687109859778, lat=34.04464406169281), zoom = 13, color = "bw", scale = 2, maptype = "roadmap")


for (output in outputs) {
  print(output)
  png(filename=paste("output/",output,".png",sep=""), width=1280, height=1280)
  print(ggmap(map) + geom_point(aes(x=df$lon,y=df$lat,color=df[[output]]),data=df,na.rm = TRUE) + geom_point(size=3,alpha=0.3) + scale_color_gradientn(colors=rainbow(3)))
  dev.off()
}


