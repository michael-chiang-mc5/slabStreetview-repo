# https://stats.stackexchange.com/questions/188753/lasso-regression-for-predicting-continuous-variable-variable-selection

# install.packages("glmnet")
library(glmnet)

set.seed(1)
x1 <- 100*rnorm(3000)
x2 <- rnorm(3000)
x3 <- rnorm(3000)
X <- matrix( c(x1, x2, x3), byrow = F, ncol = 3)

y <- 3 + 4*x1 + 3*x2 + 1*x3 + rnorm(3000)

fit <-glmnet(x = X, y = y, alpha = 1) 
plot(fit, xvar = "lambda")
coef(fit, s = 0.01)


crossval <-  cv.glmnet(x = X, y = y, alpha = 1)
plot(crossval)
penalty <- crossval$lambda.min #optimal lambda
penalty #minimal shrinkage
fit1 <-glmnet(x = X, y = y, alpha = 1, lambda = penalty ) #estimate the model with that
coef(fit1)




