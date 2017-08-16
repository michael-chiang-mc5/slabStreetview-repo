source('df_mappoint.r')
source('df_FIP.r')

head(df_FIP)


# https://stats.stackexchange.com/questions/188753/lasso-regression-for-predicting-continuous-variable-variable-selection

# install.packages("glmnet")
library(glmnet)

set.seed(1)
x1 <- df_FIP$pop_white / df_FIP$pop_total
x2 <- df_FIP$pop_black / df_FIP$pop_total
x3 <- df_FIP$pop_asian / df_FIP$pop_total
x4 <- df_FIP$pop_hispanic / df_FIP$pop_total
x5 <- df_FIP$pop_other / df_FIP$pop_total
x6 <- df_FIP$sign_es / df_FIP$pop_total


X <- matrix( c(x4, x6), byrow = F, ncol = 2)
Y <- df_FIP$health_physical

fit <-glmnet(x = X, y = Y, alpha = 1) 
plot(fit, xvar = "lambda")
coef(fit, s = 0.01)


crossval <-  cv.glmnet(x = X, y = Y, alpha = 1)
plot(crossval)
penalty <- crossval$lambda.min #optimal lambda
penalty #minimal shrinkage
fit1 <-glmnet(x = X, y = Y, alpha = 1, lambda = penalty ) #estimate the model with that
coef(fit1)




