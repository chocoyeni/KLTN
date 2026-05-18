# install.packages("dplyr")

# load thư viện

library(rjags)
library(coda)
library(MASS)
library(dplyr)

set.seed(123)

# đọc dữ liệu

df <- read.csv("irt_rt_input_encoded2.csv")

# chuẩn hóa log rt

df$log_RT <- scale(
  df$log_RT
)[,1]



# đánh lại index

df$user_new <- as.integer(
  factor(df$user_idx)
) - 1

df$item_new <- as.integer(
  factor(df$item_idx)
) - 1

# thông tin dữ liệu

N <- nrow(df)

U <- length(
  unique(df$user_new)
)

I <- length(
  unique(df$item_new)
)

cat("\nThong tin du lieu\n")

cat("Users:", U, "\n")

cat("Items:", I, "\n")

cat("Obs:", N, "\n")

# dữ liệu cho jags

data_list <- list(

  N = N,

  U = U,

  I = I,

  user = df$user_new + 1,

  item = df$item_new + 1,

  Y = df$is_correct,

  RT = df$log_RT,

  R_person = diag(2),

  R_item = diag(4)
)

# full model

model_string <- "

model {

  # person hierarchy

  Tau_person[1:2,1:2] ~ dwish(
    R_person[,],
    3
  )

  Sigma_person[1:2,1:2] <-
    inverse(Tau_person[,])

  mu_person[1] <- 0

  mu_person[2] <- 0

  for(i in 1:U){

    person_par[i,1:2] ~ dmnorm(

      mu_person[],

      Tau_person[,]
    )

    theta[i] <- person_par[i,1]

    zeta[i] <- person_par[i,2]
  }

  # item hierarchy

  Tau_item[1:4,1:4] ~ dwish(

    R_item[,],

    5
  )

  Sigma_item[1:4,1:4] <-

    inverse(Tau_item[,])

  for(k in 1:4){

    mu_item[k] ~ dnorm(
      0,
      0.1
    )
  }

  for(j in 1:I){

    item_par[j,1:4] ~ dmnorm(

      mu_item[],

      Tau_item[,]
    )

    # item parameters

    log_alpha[j] <- item_par[j,1]

    beta[j] <- item_par[j,2]

    log_phi[j] <- item_par[j,3]

    lambda[j] <- item_par[j,4]

    alpha[j] <- exp(
      log_alpha[j]
    )

    phi[j] <- exp(
      log_phi[j]
    )

    sigma_rt[j] ~ dunif(
      0,
      5
    )

    tau_rt[j] <- pow(
      sigma_rt[j],
      -2
    )
  }

  # joint lnirt model

  for(n in 1:N){

    # probit irt

    eta[n] <-

      alpha[item[n]]

      *

      (
        theta[user[n]]

        -

        beta[item[n]]
      )

    p[n] <- phi(
      eta[n]
    )

    Y[n] ~ dbern(
      p[n]
    )

    # response time

    mu_rt[n] <-

      lambda[item[n]]

      -

      phi[item[n]]

      *

      zeta[user[n]]

    RT[n] ~ dnorm(

      mu_rt[n],

      tau_rt[item[n]]
    )
  }
}
"

# save model

dir.create(
  "models",
  showWarnings = FALSE
)

dir.create(
  "outputs",
  showWarnings = FALSE
)

writeLines(

  model_string,

  "models/full_50000.txt"
)

# timer start

start_time <- Sys.time()

# compile model

cat("\nDang compile model...\n")

model <- jags.model(

  "models/full_50000.txt",

  data = data_list,

  n.chains = 2,

  n.adapt = 1000
)

# burn-in

cat("\nDang burn-in...\n")

update(
  model,
  2000
)

# sampling

cat("\nDang sampling...\n")

samples <- coda.samples(

  model,

  variable.names = c(

    "theta",

    "zeta",

    "beta",

    "alpha",

    "lambda",

    "phi",

    "Sigma_person",

    "Sigma_item"
  ),

  n.iter = 3000
)

# timer end

end_time <- Sys.time()

runtime <- end_time - start_time

cat("\nThoi gian chay\n")

print(runtime)

# summary

summary_stats <- summary(
  samples
)

stats_df <- as.data.frame(
  summary_stats$statistics
)

stats_df$param <- rownames(
  stats_df
)

# hard items

beta_df <- stats_df[
  grepl("^beta\\[", stats_df$param),
]

beta_sorted <- beta_df[
  order(-beta_df$Mean),
]

cat("\nTop item kho\n")

print(
  head(beta_sorted, 20)
)

# high ability users

theta_df <- stats_df[
  grepl("^theta\\[", stats_df$param),
]

theta_sorted <- theta_df[
  order(-theta_df$Mean),
]

cat("\nTop user ability cao\n")

print(
  head(theta_sorted, 20)
)

# top phi items

phi_df <- stats_df[
  grepl("^phi\\[", stats_df$param),
]

phi_sorted <- phi_df[
  order(-phi_df$Mean),
]

cat("\nTop phi item\n")

print(
  head(phi_sorted, 20)
)

# person covariance

person_cov <- stats_df[
  grepl("^Sigma_person", stats_df$param),
]

cat("\nCovariance person\n")

print(person_cov)

# item covariance

item_cov <- stats_df[
  grepl("^Sigma_item", stats_df$param),
]

cat("\nCovariance item\n")

print(item_cov)

# clean item table

alpha_df <- stats_df[
  grepl("^alpha\\[", stats_df$param),
]

lambda_df <- stats_df[
  grepl("^lambda\\[", stats_df$param),
]

item_id <- as.numeric(
  gsub(
    "beta\\[|\\]",
    "",
    beta_df$param
  )
)

item_map <- df %>%
  distinct(
    item_new,
    item_idx
  ) %>%
  arrange(
    item_new
  )

df_item <- data.frame(

  item_idx_encoded = item_id - 1,

  item_idx_original = item_map$item_idx,

  beta = beta_df$Mean,

  alpha = alpha_df$Mean,

  lambda = lambda_df$Mean,

  phi = phi_df$Mean
)

# save clean item table

write.csv(

  df_item,

  "outputs/lnirt_item_clean.csv",

  row.names = FALSE
)

cat(
  "\nDa luu lnirt_item_clean.csv\n"
)

# save full summary

write.csv(

  stats_df,

  "full_50000_results.csv",

  row.names = FALSE
)

cat("\nDone\n")
