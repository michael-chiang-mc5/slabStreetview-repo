source('df_FIP.r')

# keep majority hispanic tracts
PERCENT_HISPANIC_THRESHOLD = 0

df <- df_FIP[df_FIP$percent_hispanic >= PERCENT_HISPANIC_THRESHOLD,]
nrow(df)

png('output/spanish_signage_vs_population.png')
plot(df$percent_hispanic , df$percent_lang_es)
dev.off()

png('output/korean_signage_vs_population.png')
plot(df$percent_asian , df$percent_lang_ko)
dev.off()
