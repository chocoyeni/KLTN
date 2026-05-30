import pymc as pm
import numpy as np
import pandas as pd
import pytensor.tensor as pt
import matplotlib.pyplot as plt

#load data
df = pd.read_csv("irt_rt_input_encoded2.csv").copy()

# Re-index 0 đến n-1
df["u"], _ = pd.factorize(df["user_idx"])
df["i"], _ = pd.factorize(df["item_idx"])

user_idx = df["u"].values.astype("int32")
item_idx = df["i"].values.astype("int32")

y_obs = df["is_correct"].values.astype("int8")
rt_obs = df["log_RT"].values.astype("float32")

# Normalize log time
rt_obs = (rt_obs - rt_obs.mean()) / rt_obs.std()
rt_obs = rt_obs.astype("float32")

n_users = df["u"].nunique()
n_items = df["i"].nunique()

print(f"Users: {n_users}")
print(f"Items: {n_items}")
print(f"Obs: {len(df)}")

#LNIRT

with pm.Model() as lnirt_model:

    # tạo tt cho theta zeta
    chol, corr, sigmas = pm.LKJCholeskyCov(
        "user_chol",
        n=2,
        eta=2,
        sd_dist=pm.Exponential.dist(1.0, shape=2),
        compute_corr=True
    )

    # tạo cho từng user theta với zeta
    user_latent = pm.MvNormal(
        "user_latent",
        mu=pt.zeros(2),
        chol=chol,
        shape=(n_users, 2)
    )

    #gán cột
    theta = pm.Deterministic("theta", user_latent[:, 0])
    zeta = pm.Deterministic("zeta", user_latent[:, 1])

    #tính corr
    rho_theta_zeta = pm.Deterministic("rho_theta_zeta", corr[0, 1])

    # tạo beta cho item
    beta = pm.Normal("beta", 0, 1, shape=n_items)

    log_alpha = pm.Normal("log_alpha", 0, 0.5, shape=n_items)
    alpha = pm.Deterministic("alpha", pm.math.exp(log_alpha))
    #e^log

    lambda_rt = pm.Normal("lambda_rt", 0, 1, shape=n_items)

    # phi theo từng item
    phi = pm.HalfNormal("phi", 1.0, shape=n_items)

    sigma_rt = pm.HalfNormal("sigma_rt", 1.0)

    # IRT α(θ−β)
    logit_p = alpha[item_idx] * (theta[user_idx] - beta[item_idx])
    pm.Bernoulli("y_lik", logit_p=logit_p, observed=y_obs)

    # RT λ−ϕζ
    mu_rt = lambda_rt[item_idx] - phi[item_idx] * zeta[user_idx]

    pm.Normal("rt_lik", mu=mu_rt, sigma=sigma_rt, observed=rt_obs)

    print("\n Running LNIRT ADVI (phi per item)...")

    approx = pm.fit(
        n=20000,
        method="advi",
        progressbar=True,
        callbacks=[pm.callbacks.CheckParametersConvergence(tolerance=1e-3)]
    )

    idata_lnirt = approx.sample(1000)

print("\n LNIRT done")

#kết quả

posterior = idata_lnirt.posterior

# user
theta_vals = posterior["theta"].mean(dim=("chain", "draw")).values
zeta_vals = posterior["zeta"].mean(dim=("chain", "draw")).values

# item
beta_vals = posterior["beta"].mean(dim=("chain", "draw")).values
alpha_vals = posterior["alpha"].mean(dim=("chain", "draw")).values
lambda_vals = posterior["lambda_rt"].mean(dim=("chain", "draw")).values
phi_vals = posterior["phi"].mean(dim=("chain", "draw")).values

# normalize
theta_vals = (theta_vals - theta_vals.mean()) / theta_vals.std()
zeta_vals = (zeta_vals - zeta_vals.mean()) / zeta_vals.std()

#corr

rho_model = posterior["rho_theta_zeta"].mean().values
rho_empirical = np.corrcoef(theta_vals, zeta_vals)[0, 1]
rho_item = np.corrcoef(beta_vals, lambda_vals)[0, 1]

print("\n=== CORRELATION ===")
print(f"Theta vs Speed (model): {rho_model:.3f}")
print(f"Theta vs Speed (empirical): {rho_empirical:.3f}")
print(f"Difficulty vs Time: {rho_item:.3f}")

#bảng tham số

df_item = pd.DataFrame({
    "item_idx": np.arange(n_items),
    "beta": beta_vals,
    "alpha": alpha_vals,
    "lambda": lambda_vals,
    "phi": phi_vals
})

print("\nTop hard items:")
print(df_item.sort_values("beta", ascending=False).head(10))

print("\nTop time-sensitive items (phi):")
print(df_item.sort_values("phi", ascending=False).head(10))

#dùng bảng

df_user = pd.DataFrame({
    "user_idx": np.arange(n_users),
    "theta": theta_vals,
    "zeta": zeta_vals
})

print("\nTop ability users:")
print(df_user.sort_values("theta", ascending=False).head(10))

#plot

plt.figure()
plt.scatter(beta_vals, lambda_vals, alpha=0.5)
plt.xlabel("Difficulty (beta)")
plt.ylabel("Time (lambda)")
plt.title("Item: Difficulty vs Time (LNIRT)")
plt.grid()
plt.show()

plt.figure()
plt.scatter(theta_vals, zeta_vals, alpha=0.5)
plt.xlabel("Ability (theta)")
plt.ylabel("Speed (zeta)")
plt.title("User: Ability vs Speed (LNIRT)")
plt.grid()
plt.show()

#lưu file

df_item.to_csv("lnirt_item.csv", index=False)
df_user.to_csv("lnirt_user.csv", index=False)

print("\nDONE")
