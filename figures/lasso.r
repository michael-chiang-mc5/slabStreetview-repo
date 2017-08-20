source('df_FIP.r')

# keep majority hispanic tracts
PERCENT_HISPANIC_THRESHOLD = 0.75

df <- df_FIP[df_FIP$percent_hispanic >= PERCENT_HISPANIC_THRESHOLD,]
nrow(df)

plot(df$percent_hispanic , df$percent_lang_es)
hist(df$percent_lang_es)





X <- matrix( c(pop_hispanic, sign_spanish), byrow = F, ncol = 2)
Y <- df_FIP$health_physical

X <- matrix( c(sign_spanish[idx_pop_spanish]), byrow = F, ncol = 2)
Y <- df_FIP$health_physical[idx_pop_spanish]


plot(sign_spanish[idx_pop_spanish],Y)

# Do lasso
# https://stats.stackexchange.com/questions/188753/lasso-regression-for-predicting-continuous-variable-variable-selection
# install.packages("glmnet")
library(glmnet)
set.seed(1)
fit <-glmnet(x = X, y = Y, alpha = 1) 
plot(fit, xvar = "lambda")
coef(fit, s = 0.01)
# cross validation
crossval <-  cv.glmnet(x = X, y = Y, alpha = 1)
plot(crossval)
penalty <- crossval$lambda.min #optimal lambda
penalty #minimal shrinkage
fit1 <-glmnet(x = X, y = Y, alpha = 1, lambda = penalty ) #estimate the model with that
coef(fit1)




# Do ancova
# http://gribblelab.org/stats/notes/ANCOVA.pdf
# What would memory scores have been for placebo and drug groups IF their scores on IQ had been similar?.
# Does the amount of ethnic signage predict anything about health outcomes. Does the minority population predict anything about
# health outcomes? Is there an interaction between ethnic signage, minority population


# rivulus
# High vs low predation
# male or female
# brain size
# predation x sex interaction for brain size

# 
# high vs low signage
# asian or latino
# health


# Split data:
#   high spanish signage, low spanish signage
# Covariates:
#   income, sex ratio, 
# Measure
#   heatlh 

# Question:
#   Does high levels of ethnic signage predict 