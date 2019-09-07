decay_average <- function(list, decay_function=decay_fn, consider=7, laplace=TRUE) {
    l <- rev(list)
    l <- if (laplace) l + laplace else l
    len <- length(l)
    consider <- if (consider < 1) len else consider
    coeff_sum <- 0
    for (n in 1:consider) {
        coeff_sum <- coeff_sum + decay_function(n)
    }

    avg <- 0
    for (n in 1:consider) {
        avg <- avg + l[n] * decay_function(n) / coeff_sum
    }
    return(avg)
}

# plot y = 1/exp(n)^0.5, 10 > n > 0 (http://www.wolframalpha.com/input/?i=plot+y+%3D+1%2Fexp(n)%5E0.5,+10+%3E+n+%3E+0)
decay_fn <- function(n) {
    # return(1/exp(n/3))
    return(1/sqrt(exp(n)))
    # return(1/exp(n)^2)
}

burstiness <- function(list, tf, decay_function=decay_fn, consider=7, laplace=FALSE) {
    l <- rev(list)
    l <- if (laplace) l + laplace else l
    len <- length(l)
    consider <- if (consider < 1) len else consider
    coeff_sum <- 0
    for (n in 1:consider) {
        coeff_sum <- coeff_sum + decay_function(n)
    }

    burst <- 0
    for (n in 1:consider) {
        burst <- burst + (tf - l[n]) * decay_function(n) / coeff_sum
    }
    return(burst)
}

# l <- c(19, 18, 15, 22, 5, 4, 5, 2, 1)
# l <- c(rep(10, times=8))
# decay_average(l, laplace=F)
# decay_average(rev(l), laplace=F)

# IMPORTANT: bounded by range of TF - if it is between 0 and 1, it is bounded between -1 and 1
# If the tf is smaller - say divided by 100 - the burstiness will also be much smaller
# This could help, giving more common terms a higher burstiness
# However, after burstiness is calculated for each term, the values may need to be rescaled between -1 and 1 (or some other values) again

tf <- c(1, 0.4, 0.7, 0.65, 0.4, 0.5, 0.67) # the TF in previous time windows - between 0 and 1, and rightmost being most recent
# tf <- c(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8) # the TF in previous time windows - between 0 and 1, and rightmost being most recent
tf_max <- c(rep(1, times=10))
tf_mid <- c(rep(0.5, times=10))
tf_min <- c(rep(0, times=10))
print("Random TF")
print(tf)
print("Max TF")
print(tf_max)
print("Min TF")
print(tf_min)
c <- 0.7 # the TF in this time window - between 0 and 1
c_max <- 1
c_min <- 0
sprintf("Random tf and c of %s", c)
burstiness(tf, c)
# burstiness(tf/100, c/100)

sprintf("Max/mid/min tf and c of %s", c)
burstiness(tf_max, c)
burstiness(tf_mid, c)
burstiness(tf_min, c)

sprintf("Max/mid/min tf and c of %s", c_max)
burstiness(tf_max, c_max)
burstiness(tf_mid, c_max)
burstiness(tf_min, c_max)

sprintf("Max/mid/min tf and c of %s", c_min)
burstiness(tf_max, c_min)
burstiness(tf_mid, c_min)
burstiness(tf_min, c_min)
